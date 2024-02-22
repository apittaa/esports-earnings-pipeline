import os

from dotenv import load_dotenv

from delta import *
from delta.tables import *

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark

from schemas.esports_schemas import ESPORTS_TOURNAMENTS_SCHEMA, ESPORTS_GAMES_AWARDING_PRIZE_MONEY_TYPES, ESPORTS_GAMES_GENRE_SCHEMA


@task()
def extract_from_gcs(dataset_file: str) -> str:
    """Download data from GCS"""
    gcs_path = f"data/silver/{dataset_file}"
    local_path = ""
    gcs_block = GcsBucket.load("esports")
    gcs_block.get_directory(
        from_path=gcs_path,
        local_path=local_path
    )

    return gcs_path


@task()
def wite_to_bq(spark: pyspark, path: str, df_name: str, schema: str, credentials: str) -> None:
    """write DataFrame to BigQuery"""
    df = spark.read.format('delta').load(path)
    df.write.format("bigquery") \
            .option("credentialsFile", credentials) \
            .option("writeMethod", "direct") \
            .option('table', f'esports_silver.{df_name}') \
            .option("schema", schema) \
            .mode('overwrite') \
            .save()


@flow()
def etl_gcs_silver_to_bq():
    """The main ETL function"""
    
    load_dotenv()
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH = os.getenv("LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH")
   
    builder = pyspark.sql.SparkSession.builder.appName("esports_tournaments_silver_to_bq") \
        .config("spark.executor.memory", "64g") \
        .config("parentProject", GCP_PROJECT_ID) \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars", "utils/spark-bigquery-with-dependencies_2.12-0.34.0.jar") \

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    dfs_name = {'esports_tournaments': ESPORTS_TOURNAMENTS_SCHEMA,
                'esports_games_genre': ESPORTS_GAMES_GENRE_SCHEMA,
                'esports_games_awarding_prize_money': ESPORTS_GAMES_AWARDING_PRIZE_MONEY_TYPES
                }

    for df, schema in dfs_name.items():
        path = extract_from_gcs(df)
        wite_to_bq(spark, path, df, schema, LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH)
        
    # End spark session
    spark.stop()


if __name__ == '__main__':
    etl_gcs_silver_to_bq()
