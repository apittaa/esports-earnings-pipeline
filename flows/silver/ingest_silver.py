import os
from dotenv import load_dotenv

from prefect import flow

from pyspark.sql import SparkSession

from etl_gcs_bronze_to_gcs_silver import etl_gcs_bronze_to_gcs_silver
from etl_gcs_silver_to_bq import etl_gcs_silver_to_bq


@flow()
def main_flow_silver():
    """The main flow function"""
    
    load_dotenv()
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    CREDENTIALS = os.getenv("LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH")
   
    builder = SparkSession.builder.appName("esports_tournaments_silver") \
        .config("spark.executor.memory", "64g") \
        .config("parentProject", GCP_PROJECT_ID) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars", "utils/spark-bigquery-with-dependencies_2.12-0.34.0.jar")
        
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    etl_gcs_bronze_to_gcs_silver(spark)
    etl_gcs_silver_to_bq(spark, CREDENTIALS)
    
    # End spark session
    spark.stop()


if __name__ == "__main__":
    main_flow_silver()
