from delta import *
from delta.tables import *

from prefect import flow, task
from prefect_dbt.cli import DbtCoreOperation
from prefect_gcp.cloud_storage import GcsBucket

import pyspark

from schemas.esports_schemas import ESPORTS_GAMES_AWARDING_PRIZE_MONEY_WITH_GENRE_SCHEMA, ESPORTS_TOURNAMENTS_WITH_GENRE_SCHEMA


def extract_from_gcs(dataset_file: str) -> str:
    """Download data from GCS"""
    gcs_path = f"data/gold/{dataset_file}"
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
    df = spark.read.format('delta').load(path)
    df.write.format("bigquery") \
            .option("credentialsFile", credentials) \
            .option("writeMethod", "direct") \
            .option('table', f'esports_gold.{df_name}') \
            .option("schema", schema) \
            .mode("overwrite") \
            .save()
   
            
@task()
def dbt_transform(dbt_dev_block: str, dbt_prod_block: str, target_dbt: str) -> None:
    """Run dbt transformations on data in BQ by building dbt models"""
    print('LOGGING: dbt TRANSFORMATIONS STARTING')
    if target_dbt == 'dev':
        dbt_op = DbtCoreOperation.load(dbt_dev_block)
    else:
        dbt_op = DbtCoreOperation.load(dbt_prod_block)
    dbt_op.run()
    print('LOGGING: dbt TRANSFORMATIONS COMPLETE')
            
            
@flow()
def etl_gcs_gold_to_bq(spark, credentials: str, dbt_dev_block: str, dbt_prod_block: str, target_dbt: str) -> None:
    """The main ETL function"""  
    
    dfs_name = {'esports_tournaments': ESPORTS_TOURNAMENTS_WITH_GENRE_SCHEMA, 
                'esports_games_awarding_prize_money': ESPORTS_GAMES_AWARDING_PRIZE_MONEY_WITH_GENRE_SCHEMA
                }

    for df, schema in dfs_name.items():
        path = extract_from_gcs(df)
        wite_to_bq(spark, path, df, schema, credentials)
    dbt_transform(dbt_dev_block, dbt_prod_block, target_dbt)


if __name__ == '__main__':
    etl_gcs_gold_to_bq()
