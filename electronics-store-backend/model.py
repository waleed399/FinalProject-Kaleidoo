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
        existing_users = self.model.recommendForAllUsers(1).select("user_id").rdd.flatMap(lambda x: x).collect()

        if user_id in existing_users:
            # Existing user recommendations
            user_recs_for_user = self.model.recommendForUserSubset(self.spark.createDataFrame([(user_id,)], ["user_id"]), top_n)
            recommendations = user_recs_for_user.select("recommendations").rdd.flatMap(lambda x: x).collect()[0]
            recommended_item_ids = [row.item_id_numeric for row in recommendations]
            recommended_items_df = self.product_df.filter(col("item_id_numeric").isin(recommended_item_ids))

            # If new interactions are provided, consider them for additional recommendations
            if new_user_interactions:
                new_item_ids = [item_id for item_id in new_user_interactions.keys()]
                new_items_df = self.product_df.filter(col("item_id_numeric").isin(new_item_ids))
                if new_items_df:
                    recommended_items_df = recommended_items_df.union(new_items_df)
        
        else:
            if new_user_interactions:
                # New user with interactions
                recommended_items_df = self.recommend_for_new_user_interactions(new_user_interactions, top_n)
            else:
                # New user without interactions
                recommended_items_df = self.recommend_for_new_user(top_n)
        
        if recommended_items_df:
            recommendations_list = recommended_items_df.select("id", "name").rdd.map(lambda row: (row["id"], row["name"])).collect()
            recommendations_df = self.spark.createDataFrame([(user_id, recommendations_list)], ["user_id", "recommendations"])
            return recommendations_df
        else:
            return None

    def recommend_for_new_user(self, top_n=3):
        popular_items = (
            self.product_df.groupBy("item_id_numeric")
            .count()
            .orderBy(desc("count"))
            .limit(top_n)
            .select("item_id_numeric")
            .rdd.flatMap(lambda x: x)
            .collect()
        )
        popular_items_df = self.product_df.filter(col("item_id_numeric").isin(popular_items))
        return popular_items_df.limit(top_n)

    def recommend_for_new_user_interactions(self, new_user_interactions, top_n=3):
        # Create a DataFrame from new_user_interactions
        interaction_data = [(0, int(item_id), interaction) for item_id, interaction in new_user_interactions.items()]
        interactions_df = self.spark.createDataFrame(interaction_data, ["user_id", "item_id_numeric", "interaction"])
        
        # Generate predictions using the ALS model
        new_user_model = self.model.transform(interactions_df)
        
        # Filter predictions for positive values and order by prediction
        new_user_recs = new_user_model.filter(col("prediction") > 0).orderBy(desc("prediction")).select("item_id_numeric").limit(top_n)
        
        # Fetch the recommended items
        recommended_item_ids = new_user_recs.rdd.flatMap(lambda x: x).collect()
        recommended_items_df = self.product_df.filter(col("item_id_numeric").isin(recommended_item_ids))
        
        return recommended_items_df.limit(top_n)
