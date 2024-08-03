from datetime import datetime 
import threading
from flask import Flask, json, jsonify, request
from pymongo import MongoClient
import certifi
import os
from sklearn.preprocessing import LabelEncoder
from pyspark.sql.functions import col
from pyspark.sql import SparkSession
from pyspark.sql import Row
from kafka import KafkaProducer, KafkaConsumer
from pyspark.sql import SparkSession
from model import RecommendationEngine
from flask_cors import CORS
from pyspark.ml.recommendation import ALS
from dotenv import load_dotenv
import bcrypt
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
from apscheduler.schedulers.background import BackgroundScheduler
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
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("RecommendationEngine") \
    .config("spark.mongodb.read.connection.uri", app.config["MONGO_URI"]) \
    .config("spark.mongodb.write.connection.uri", app.config["MONGO_URI"]) \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1")\
    .getOrCreate()



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
        search_query = data.get('search_query')
        interaction_type = data.get('interaction_type')
        score = data.get('score')

        if not user_id or not interaction_type or not score:
            return jsonify({'error': 'Missing required fields'}), 400

        if interaction_type == "search" and not search_query:
            return jsonify({'error': 'Missing search query for search interaction'}), 400

        interaction_score = 0
        if interaction_type == "click":
            interaction_score = 1
        elif interaction_type == "search":
            interaction_score = 3
        elif interaction_type == "purchase":
            interaction_score = 5
        else:
            return jsonify({'error': 'Invalid interaction type'}), 400

        interaction_doc = {
            'interaction_type': interaction_type,
            'score': interaction_score,
            'timestamp': datetime.utcnow()
        }
        if interaction_type != "search":
            interaction_doc['product_id'] = product_id

        if interaction_type == "search":
            interaction_doc['search_query'] = search_query

        user_interactions = interactions_collection.find_one({'user_id': user_id})

        if user_interactions:
            if interaction_type == "search":
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
                            '$push': {'interactions': interaction_doc},
                            '$inc': {'action_count': 1}
                        },
                        upsert=True
                    )
            else:
                existing_interaction = next((i for i in user_interactions.get('interactions', []) if i.get('product_id') == product_id and i['interaction_type'] == interaction_type), None)
                if existing_interaction:
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
                    result = interactions_collection.update_one(
                        {'user_id': user_id},
                        {
                            '$push': {'interactions': interaction_doc},
                            '$inc': {'action_count': 1}
                        },
                        upsert=True
                    )
        else:
            if interaction_type == "search":
                interaction_doc['search_query'] = search_query
            result = interactions_collection.insert_one(
                {
                    'user_id': user_id,
                    'interactions': [interaction_doc],
                    'action_count': 1 
                }
            )

        user = interactions_collection.find_one({'user_id': user_id})
        if user and user.get('action_count', 0) >= 5:
            product_scores = {interaction['product_id']: interaction['score'] for interaction in user.get('interactions', []) if 'product_id' in interaction}
            print("Sending to Kafka:", {'user_id': user_id, 'product_scores': product_scores})
            interaction_data = {
                'user_id': user_id,
                'product_scores': product_scores
            }
            producer.send('user-interactions', value=interaction_data)
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

def retrain_model(interactions_collection, model_path):
    # Load data from MongoDB into a DataFrame
       
    def load_data_from_mongo():
        # Specify the MongoDB database and collection names
        df = spark.read \
            .format("mongo") \
            .option("uri",app.config["MONGO_URI"]) \
            .option("spark.mongodb.input.collection", "electronics_data") \
            .load()
        return df

    # Load the existing data into a DataFrame
    electronics_data_df = load_data_from_mongo()
    # Prepare existing DataFrame
    prepared_existing_df = electronics_data_df.select(
        col("user_id").cast(IntegerType()),  # Ensure user_id is cast to IntegerType
        col("encoded_product_id").alias("product_id").cast(IntegerType()),  # Ensure product_id is cast to IntegerType
        col("interaction").alias("score").cast(FloatType())  # Ensure score is cast to FloatType
    )

    # Process new interactions data
    interactions = list(interactions_collection.find({}))
    if not interactions:
        print("No interactions found in MongoDB.")
        return

    # Define schema for the interactions data
    schema = StructType([
        StructField("user_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("score", FloatType(), True)
    ])

    # Extract and flatten the interactions data
    processed_data = []
    for user_interactions in interactions:
        user_id = user_interactions.get('user_id')
        interactions_list = user_interactions.get('interactions', [])
        for interaction in interactions_list:
            product_id = interaction.get('product_id')
            score = interaction.get('score')
            processed_data.append({
                'user_id': user_id,
                'product_id': product_id,
                'score': float(score)  # Ensure the score is a float
            })

    if not processed_data:
        print("No processed data available for DataFrame creation.")
        return

    # Create DataFrame from processed data
    interactions_df = spark.createDataFrame(processed_data, schema=schema)

    # Convert PySpark DataFrame to Pandas DataFrame for encoding
    pandas_df = interactions_df.toPandas()

    # Apply LabelEncoder to 'product_id'
    id_encoder = LabelEncoder()
    pandas_df['encoded_product_id'] = id_encoder.fit_transform(pandas_df['product_id'])

    # Convert back to PySpark DataFrame
    interactions_df_encoded = spark.createDataFrame(pandas_df)

    # Convert columns to IntegerType
    interactions_df_encoded = interactions_df_encoded.withColumn("user_id", col("user_id").cast(IntegerType())) \
                                                     .withColumn("encoded_product_id", col("encoded_product_id").cast(IntegerType())) \
                                                     .withColumn("score", col("score").cast(FloatType()))

    # Select and rename columns to match the existing DataFrame schema
    interactions_df_encoded = interactions_df_encoded.select(
        col("user_id"),
        col("encoded_product_id").alias("product_id"),
        col("score")
    )

    # Combine new and existing data
    combined_df = prepared_existing_df.union(interactions_df_encoded)

    # Check if combined_df is empty
    if combined_df.count() == 0:
        print("No data available for training.")
        return

    # Train the ALS model with combined data
    als = ALS(userCol="user_id", itemCol="product_id", ratingCol="score", coldStartStrategy="drop")
    model = als.fit(combined_df)

    if model:
        # Save model with overwrite mode
        model.write().overwrite().save(model_path)
        print("Model retrained and saved successfully.")
    else:
        print("No model to save.")
        
# Wrapper function to provide arguments for the retrain_model function
def retrain_model_wrapper():
    retrain_model(interactions_collection, model_path)

# Setup the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(retrain_model_wrapper, 'interval', weeks=1)  # Run retrain_model_wrapper every week
scheduler.start()

# Run Kafka consumer in a background thread
consumer_thread = threading.Thread(target=kafka_consumer)
consumer_thread.start()

if __name__ == "__main__":
    app.run(debug=True, port=5555)