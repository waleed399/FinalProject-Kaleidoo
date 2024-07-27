from flask import Flask, jsonify, request
from pymongo import MongoClient
import certifi
import os
from flask_cors import CORS

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

app.config["MONGO_URI"] = os.getenv('MONGO_URI')

# Connect to MongoDB
client = MongoClient(
    app.config["MONGO_URI"],
    tls=True,
    tlsCAFile=certifi.where()
)
db = client.electronics_store
electronics_data_collection = db.electronics_data

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))  # Default to 10 products per page
        skip = (page - 1) * limit

        # Get distinct products with shortest names, limited to 50 products
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
            {"$limit": 50}  # Limit to 50 products with shortest names
        ]

        products = list(electronics_data_collection.aggregate(pipeline))

        # Apply pagination on the 50 products
        paginated_products = products[skip: skip + limit]

        total_pages = (len(products) // limit) + (1 if len(products) % limit > 0 else 0)

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

##########################################
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