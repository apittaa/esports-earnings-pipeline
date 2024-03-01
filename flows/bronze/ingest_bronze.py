import os

from dotenv import load_dotenv

from prefect import flow

from pyspark.sql import SparkSession

from etl_web_to_gcs_bronze import etl_web_to_gcs
from etl_gcs_bronze_to_bq import etl_gcs_bronze_to_bq


@flow()
def main_flow_bronze():
    """The main flow function"""
    
    # Retrieve env variables
    load_dotenv(override=True)
    API_KEY = os.getenv("API_KEY")
    BUCKET = os.getenv("GCS_BUCKET_NAME")
    CREDENTIALS = os.getenv("LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH")
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    
    # Create a SparkSession
    spark = SparkSession.builder \
        .appName("esports_tournaments_bronze") \
        .config("parentProject", GCP_PROJECT_ID) \
        .config("spark.executor.memory", "64g") \
        .config("spark.jars", "utils/spark/spark-bigquery-with-dependencies_2.12-0.34.0.jar") \
        .getOrCreate()
    
    etl_web_to_gcs(spark, API_KEY, BUCKET, CREDENTIALS)
    etl_gcs_bronze_to_bq(spark, CREDENTIALS)
    
    # End spark session
    spark.stop()


if __name__ == "__main__":
    main_flow_bronze()
