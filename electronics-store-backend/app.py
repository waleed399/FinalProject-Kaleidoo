from datetime import datetime 
import threading
from flask import Flask, json, jsonify, request
from pymongo import MongoClient
import certifi
import os
from kafka import KafkaProducer, KafkaConsumer
from pyspark.sql import SparkSession
from model import RecommendationEngine
from flask_cors import CORS
from dotenv import load_dotenv
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

app.config["MONGO_URI"] = os.getenv('MONGO_URI')
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')  # Add a secret key for JWT

# Initialize JWT Manager
jwt = JWTManager(app)

# Connect to MongoDB
client = MongoClient(
    app.config["MONGO_URI"],
    tls=True,
    tlsCAFile=certifi.where()
)
db = client.electronics_store
electronics_data_collection = db.electronics_data
users_collection = db.users
counters_collection = db.counters  # Collection to keep track of counters
interactions_collection = db.interactions
products_names_collection = db.products_names
recommendations_collection = db.recommendations
# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Initialize SparkSession
spark = SparkSession.builder.appName("RecommendationEngine").getOrCreate()

# Load product DataFrame
product_data = list(products_names_collection.find({}, {'_id': 0}))
product_df = spark.createDataFrame(product_data)

# Initialize the recommendation engine
model_path = "./recommendation_model"
print(f"Model path: {model_path}")
recommendation_engine = RecommendationEngine(model_path, product_df)

# Kafka consumer configuration
consumer = KafkaConsumer(
    'user-interactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

from pyspark.sql import SparkSession
from pyspark.sql import Row

# Initialize Spark session
spark = SparkSession.builder.appName("KafkaConsumerApp").getOrCreate()

def kafka_consumer():
    consumer = KafkaConsumer(
        'user-interactions',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        interaction_data = message.value
        user_id = interaction_data['user_id']
        product_scores = interaction_data['product_scores']

        # Convert user_id to integer if necessary
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = int(user_id)

        # Fetch the user from MongoDB
        user = electronics_data_collection.find_one({'user_id': user_id})

        if user:
            print("It's not a new user !!!!!!")
            # Generate recommendations for an existing user
            recommendations_df = recommendation_engine.recommend_items(user_id, product_scores)
        else:
            print("It's a new user !!!!!!")
            # Handle new users
            recommendations_df = recommendation_engine.recommend_for_new_user()

        # Check if recommendations_df is a list
        if isinstance(recommendations_df, list):
            # Convert the list to a DataFrame
            recommendations_df = spark.createDataFrame([Row(**rec) for rec in recommendations_df])

        # Collect recommendations as a list of dictionaries
        if recommendations_df:
            recommendations_list = recommendations_df.select("item_id_numeric", "name").rdd.map(lambda row: {'item_id_numeric': row['item_id_numeric'], 'name': row['name']}).collect()

            # Store recommendations in MongoDB or cache
            recommendations_collection.update_one(
                {'user_id': user_id},
                {'$set': {'recommendations': recommendations_list}},
                upsert=True
            )


# Helper function to get the next sequence value for user_id
def get_next_sequence_value(sequence_name):
    counter = counters_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=True,
        upsert=True
    )
    return counter['sequence_value']

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        page = int(request.args.get('page', 1))
        limit = 13 if page == 1 else 12  # Return 13 products on the first page, 12 on subsequent pages
        skip = (page - 1) * 12  # Skip should be based on the size of pages after the first one
        
        # Get distinct products with shortest names, limit to 50 products
        pipeline = [
            {"$group": {
                "_id": "$id",
                "name": {"$first": "$name"},
                "description": {"$first": "$categories"},
                "image": {"$first": "$image"},
                "brand": {"$first": "$brand"}
            }},
            {"$addFields": {
                "nameLength": {"$strLenCP": "$name"}  # Calculate length of the name
            }},
            {"$sort": {"nameLength": 1}},  # Sort by name length (ascending)
            {"$limit": 50}  # Limit to 50 distinct products
        ]

        products = list(electronics_data_collection.aggregate(pipeline))

        # Apply pagination
        paginated_products = products[skip: skip + limit]

        total_products = len(products)
        total_pages = (total_products // 12) + (1 if total_products % 12 > 0 else 0)
        if page == 1:
            total_pages = (total_products // 13) + (1 if total_products % 13 > 0 else 0)

        products_list = [{
            'id': product.get('_id'),
            'name': product.get('name'),
            'description': product.get('description'),
            'image': product.get('image', ''),
            'brand': product.get('brand')
        } for product in paginated_products]

        return jsonify({
            'products': products_list,
            'totalPages': total_pages
        })
    except Exception as e:
        print(f"Error: {e}")  # Log error message
        return jsonify({'error': str(e)}), 500



@app.route('/api/products/<id>', methods=['GET'])
def get_product(id):
    try:
        product = electronics_data_collection.find_one({'id': id})
        if product:
            product_data = {
                'id': product.get('id'),
                'name': product.get('name'),
                'description': product.get('categories'),  # Adjust if needed
                'image': product.get('image', ''),  # Ensure 'image' field is correct
                'brand': product.get('brand')
            }
            return jsonify(product_data)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400

        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_id = get_next_sequence_value('user_id')

        users_collection.insert_one({
            'user_id': user_id,
            'username': username,
            'password': hashed_password,
            'email': email
        })

        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            access_token = create_access_token(identity={'username': username})
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user_id': str(user['user_id'])  # Return the user ID
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/update-interactions', methods=['POST'])
def update_interactions():
    try:
        data = request.get_json()
        print("Request data:", data)

        user_id = data.get('user_id')
        product_id = data.get('product_id')
        search_query = data.get('search_query')  # New field for search queries
        interaction_type = data.get('interaction_type')
        score = data.get('score')

        if not user_id or not interaction_type or not score:
            return jsonify({'error': 'Missing required fields'}), 400

        if interaction_type == "search" and not search_query:
            return jsonify({'error': 'Missing search query for search interaction'}), 400

        # Determine interaction score
        interaction_score = 0
        if interaction_type == "click":
            interaction_score = 1
        elif interaction_type == "search":
            interaction_score = 3
        elif interaction_type == "purchase":
            interaction_score = 5
        else:
            return jsonify({'error': 'Invalid interaction type'}), 400

        # Define interaction document
        interaction_doc = {
            'product_id': product_id,
            'interaction_type': interaction_type,
            'score': interaction_score,
            'timestamp': datetime.utcnow()
        }

        if interaction_type == "search":
            interaction_doc.pop('product_id', None)  # Remove product_id for search interactions

        # Update or insert the interaction record
        user_interactions = interactions_collection.find_one({'user_id': user_id})

        if user_interactions:
            if interaction_type == "search":
                # Update or insert search interaction
                existing_interaction = next((i for i in user_interactions.get('interactions', []) if i['interaction_type'] == interaction_type and i.get('search_query') == search_query), None)
                if existing_interaction:
                    result = interactions_collection.update_one(
                        {
                            'user_id': user_id,
                            'interactions.interaction_type': interaction_type,
                            'interactions.search_query': search_query
                        },
                        {
                            '$inc': {'interactions.$.score': interaction_score},
                            '$set': {'interactions.$.timestamp': datetime.utcnow()}
                        }
                    )
                else:
                    result = interactions_collection.update_one(
                        {'user_id': user_id},
                        {
                            '$push': {'interactions': {**interaction_doc, 'search_query': search_query}},
                            '$inc': {'action_count': 1}
                        },
                        upsert=True
                    )
            else:
                # Check if interaction already exists
                existing_interaction = next((i for i in user_interactions.get('interactions', []) if i['product_id'] == product_id and i['interaction_type'] == interaction_type), None)
                
                if existing_interaction:
                    # Update existing interaction
                    result = interactions_collection.update_one(
                        {
                            'user_id': user_id,
                            'interactions.product_id': product_id,
                            'interactions.interaction_type': interaction_type
                        },
                        {
                            '$inc': {'interactions.$.score': interaction_score},
                            '$set': {'interactions.$.timestamp': datetime.utcnow()}
                        }
                    )
                else:
                    # Add new interaction
                    result = interactions_collection.update_one(
                        {'user_id': user_id},
                        {
                            '$push': {'interactions': interaction_doc},
                            '$inc': {'action_count': 1}
                        },
                        upsert=True
                    )
        else:
            # User doesn't have any interactions yet, create a new record
            if interaction_type == "search":
                interaction_doc['search_query'] = search_query
            result = interactions_collection.insert_one(
                {
                    'user_id': user_id,
                    'interactions': [interaction_doc],
                    'action_count': 1 
                }
            )

        # Check if the user has reached the action threshold
        user = interactions_collection.find_one({'user_id': user_id})
        if user and user.get('action_count', 0) >= 5:
            product_scores = {interaction['product_id']: interaction['score'] for interaction in user.get('interactions', []) if 'product_id' in interaction}
            print("Sending to Kafka:", {'user_id': user_id, 'product_scores': product_scores})
            # Send to Kafka
            interaction_data = {
                'user_id': user_id,
                'product_scores': product_scores
            }
            producer.send('user-interactions', value=interaction_data)
            
            # Reset user action count
            interactions_collection.update_one({'user_id': user_id}, {'$set': {'action_count': 0}})

        return jsonify({'message': 'Interactions updated successfully'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

    
@app.route('/get-recommendations', methods=['GET'])
def get_recommendations():
    user_id_str = request.args.get('user_id')
    
    if not user_id_str:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        user_id = int(user_id_str)  # Convert user_id to integer
    except ValueError:
        return jsonify({'error': 'Invalid user_id format'}), 400

    # Fetch recommendations from MongoDB
    recommendations = recommendations_collection.find_one({'user_id': user_id})
    
    if recommendations and 'recommendations' in recommendations:
        return jsonify({'recommendations': recommendations['recommendations']}), 200
    else:
        # Return an empty array to indicate no recommendations found
        return jsonify({'recommendations': []}), 200

 
# Run Kafka consumer in a background thread
consumer_thread = threading.Thread(target=kafka_consumer)
consumer_thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=5555)



# # Initialize SparkSession
# spark = SparkSession.builder.appName("RecommendationEngine").getOrCreate()
# products_names_collection = db.products_names
# # Load product DataFrame
# product_data = list(products_names_collection.find({}, {'_id': 0}))
# product_df = spark.createDataFrame(product_data)

# # Print product_df to ensure it's loaded correctly
# print(product_df.show())

# # Initialize the recommendation engine
# model_path = "electronics-store-backend/recommendation_model"
# print(f"Model path: {model_path}")

# # Add debugging to check model path and contents
# import os

# if os.path.exists(model_path):
#     print(f"Model directory exists: {model_path}")
#     print("Contents of model directory:")
#     print(os.listdir(model_path))
# else:
#     print(f"Model directory does not exist: {model_path}")

# try:
#     recommendation_engine = RecommendationEngine(model_path, product_df)
# except Exception as e:
#     print(f"Failed to initialize RecommendationEngine: {e}")

# def serialize_document(doc):
#     """Convert BSON document to a JSON serializable format."""
#     if doc is None:
#         return None
#     doc_copy = doc.copy()
#     doc_copy.pop("_id", None)
#     return doc_copy

# #########################################
# @app.route("/", methods=["GET"])
# def index():
#     try:
#         user_id = 1  # For testing purposes, setting a static user_id
#         new_user_interactions = {
#             '11': 9,
#             '23': 9,
#             '232': 4,
#             '156': 3
#         }

#         if user_id is None:
#             return "Missing user_id parameter", 400

#         user = electronics_data_collection.find_one({"user_id": user_id})
#         if user:
#             recommendations_df = recommendation_engine.recommend_items(user_id, new_user_interactions)
#         else:
#             recommendations_df = recommendation_engine.recommend_for_new_user()

#         recommendations_list = recommendations_df.collect() if recommendations_df else []
        
#         return jsonify({
#             "user": serialize_document(user) if user else user_id,
#             "recommendations": recommendations_list
#         })
#     except Exception as e:
#         return str(e), 500