import os

from dotenv import load_dotenv

from prefect import flow

from etl_gcs_silver_to_gcs_gold import etl_gcs_silver_to_gcs_gold
from etl_gcs_gold_to_bq import etl_gcs_gold_to_bq


@flow()
def main_flow_gold():
    """The main flow function"""
    
    load_dotenv()
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    CREDENTIALS = os.getenv("LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH")
   
    builder = SparkSession.builder.appName("esports_tournaments_gold_to_bq") \
        .config("spark.executor.memory", "64g") \
        .config("parentProject", GCP_PROJECT_ID) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars", "utils/spark-bigquery-with-dependencies_2.12-0.34.0.jar") \

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR") 
    
    etl_gcs_silver_to_gcs_gold(spark)
    etl_gcs_gold_to_bq(spark, CREDENTIALS)
    
    # End spark session
    spark.stop()


if __name__ == "__main__":
    main_flow_gold()
    