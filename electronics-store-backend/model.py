from pyspark.ml.recommendation import ALSModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc


class RecommendationEngine:
    def __init__(self, model_path, product_df):
        self.spark = SparkSession.builder.appName("RecommendationEngine").getOrCreate()
        
        # Try loading the model and handle exceptions
        try:
            self.model = ALSModel.load(model_path)
        except Exception as e:
            print(f"Error loading model from {model_path}: {e}")
            raise e

        self.product_df = product_df

    def recommend_items(self, user_id, new_user_interactions=None, top_n=3):
        try:
            # Check if user_id is an existing user
            existing_users = self.model.recommendForAllUsers(1).select("user_id").rdd.flatMap(lambda x: x).collect()
            
            if user_id in existing_users:
                # Recommendations for an existing user
                user_recs_for_user = self.model.recommendForUserSubset(self.spark.createDataFrame([(user_id,)], ["user_id"]), top_n)
                recommendations = user_recs_for_user.select("recommendations").rdd.flatMap(lambda x: x).collect()[0]
                recommended_item_ids = [row.item_id_numeric for row in recommendations]
                recommended_items_df = self.product_df.filter(col("item_id_numeric").isin(recommended_item_ids))
            
                # If new interactions are provided, combine with new items
                if new_user_interactions:
                    new_item_ids = [item_id for item_id in new_user_interactions.keys()]
                    new_items_df = self.product_df.filter(col("item_id_numeric").isin(new_item_ids))
                    if new_items_df.count() > 0:
                        recommended_items_df = recommended_items_df.union(new_items_df)
            
            else:
                # Recommendations for a new user
                if new_user_interactions:
                    recommended_items_df = self.recommend_for_new_user_interactions(new_user_interactions, top_n)
                else:
                    recommended_items_df = self.recommend_for_new_user(top_n)
            
            # Limit and collect recommendations
            if recommended_items_df:
                recommended_items_df = recommended_items_df.limit(top_n)
                recommendations_list = recommended_items_df.select("item_id_numeric", "name").rdd.map(lambda row: {'item_id_numeric': row['item_id_numeric'], 'name': row['name']}).collect()
                return recommendations_list
            
            return []
        
        except Exception as e:
            print(f"Error in recommend_items: {e}")
            raise e



    def recommend_for_new_user(self, top_n=3):
        try:
            popular_items = (
                self.product_df.groupBy("item_id_numeric")
                .count()
                .orderBy(desc("count"))
                .limit(top_n)  # This should limit the number of rows
                .join(self.product_df, on="item_id_numeric", how="inner")
                .select("item_id_numeric", "name")
            )
            print("Popular items count:", popular_items.count())  # Debug print
            return popular_items
        except Exception as e:
            print(f"Error in recommend_for_new_user: {e}")
            raise e




    def recommend_for_new_user_interactions(self, new_user_interactions, top_n=3):
        try:
            # Create a DataFrame from new_user_interactions
            interaction_data = [(0, int(item_id), interaction) for item_id, interaction in new_user_interactions.items()]
            interactions_df = self.spark.createDataFrame(interaction_data, ["user_id", "item_id_numeric", "interaction"])
            
            # Generate predictions using the ALS model
            new_user_model = self.model.transform(interactions_df)
            
            # Filter predictions for positive values and order by prediction
            new_user_recs = new_user_model.filter(col("prediction") > 0).orderBy(desc("prediction")).select("item_id_numeric").limit(top_n)
            
            # Fetch the recommended item IDs
            recommended_item_ids = new_user_recs.rdd.flatMap(lambda x: x).collect()
            
            print(f"Recommended Item IDs from interactions: {recommended_item_ids}")

            if len(recommended_item_ids) < top_n:
                # If not enough recommendations, fall back to popular items
                missing_count = top_n - len(recommended_item_ids)
                print(f"Not enough recommendations. Need {missing_count} more items.")
                
                popular_items = self.recommend_for_new_user(missing_count)  # Get additional popular items
                
                # Combine recommendations with popular items
                recommended_items_df = self.product_df.filter(col("item_id_numeric").isin(recommended_item_ids))
                if recommended_items_df.count() < top_n:
                    additional_items_df = popular_items.filter(~col("item_id_numeric").isin(recommended_item_ids))
                    recommended_items_df = recommended_items_df.union(additional_items_df.limit(missing_count))
            else:
                # Enough recommendations found
                recommended_items_df = self.product_df.filter(col("item_id_numeric").isin(recommended_item_ids))
            
            final_count = recommended_items_df.count()
            print(f"Final number of recommendations: {final_count}")
            
            return recommended_items_df.limit(top_n)
        
        except Exception as e:
            print(f"Error in recommend_for_new_user_interactions: {e}")
            raise e
        
    def save_model(self):
        """Save the model to the specified path."""
        if self.model:
            self.model.save(self.model_path)
        else:
            print("No model to save.")


