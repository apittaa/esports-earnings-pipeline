from prefect import flow, task

import pyspark
from prefect_gcp.cloud_storage import GcsBucket

from schemas.esports_schemas import ESPORTS_TOURNAMENTS_SCHEMA, ESPORTS_GAMES_AWARDING_PRIZE_MONEY_SCHEMA, ESPORTS_GAMES_GENRE_SCHEMA


@task()
def extract_from_gcs(dataset_file: str) -> str:
    """Download data from GCS"""
    gcs_path = f"data/bronze/{dataset_file}"
    local_path = ""
    gcs_block = GcsBucket.load("gcs-bucket-esports-pipeline")
    gcs_block.get_directory(
        from_path=gcs_path,
        local_path=local_path
    )

    return gcs_path


@task()
def wite_to_bq(spark: pyspark, path: str, df_name: str, schema: str, credentials: str) -> None:
    """write DataFrame to BigQuery"""
    df = spark.read.format('parquet').load(path)
    df.write.format("bigquery") \
            .option("credentialsFile", credentials) \
            .option("writeMethod", "direct") \
            .option("schema", schema) \
            .option("table", f'esports_bronze.{df_name}') \
            .mode("overwrite") \
            .save()
    

@flow()
def etl_gcs_bronze_to_bq(spark, credentials):
    """The main ETL function"""
    
    dfs_name = {'esports_tournaments': ESPORTS_TOURNAMENTS_SCHEMA,
                'esports_games_genre': ESPORTS_GAMES_GENRE_SCHEMA,
                'esports_games_awarding_prize_money': ESPORTS_GAMES_AWARDING_PRIZE_MONEY_SCHEMA
                }

    for df, schema in dfs_name.items():
        path = extract_from_gcs(df)
        wite_to_bq(spark, path, df, schema=schema, credentials=credentials)
    

if __name__ == '__main__':
    etl_gcs_bronze_to_bq()
