from delta import *
from delta.tables import *

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark


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
def wite_to_bq(spark: pyspark, path: Path, df_name: str) -> None:
    """write DataFrame to BigQuery"""
    df = spark.read.format('delta').load(path)
    df.write.format("bigquery") \
            .option("writeMethod", "direct") \
            .option('table', f'esports_silver.{df_name}') \
            .mode('overwrite') \
            .save()


@flow()
def etl_gcs_silver_to_bq():
    """The main ETL function"""
   
    builder = pyspark.sql.SparkSession.builder.appName("test") \
        .config("spark.executor.memory", "64g") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars", "spark-bigquery-with-dependencies_2.12-0.34.0.jar") \

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    dfs_name = ['esports_tournaments',
                'esports_games_genre',
                'esports_games_awarding_prize_money'
                ]

    for df_name in dfs_name:
        path = extract_from_gcs(df_name)
        wite_to_bq(spark, path, df_name)
        
    # End spark session
    spark.stop()


if __name__ == '__main__':
    etl_gcs_silver_to_bq()
