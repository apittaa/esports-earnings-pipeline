from pathlib import Path

from delta import *
from delta.tables import *

from esports_schema import ESPORTS_TOURNAMENTS_TYPES, ESPORTS_GAMES_GENRE_TYPES, ESPORTS_GAMES_AWARDING_PRIZE_MONEY_TYPES

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *


@task()
def extract_from_gcs(dataset_file: str) -> str:
    """Download data from GCS"""
    gcs_path = f"data/bronze/{dataset_file}"
    local_path = f""
    gcs_block = GcsBucket.load("esports")
    gcs_block.get_directory(
        from_path=gcs_path,
        local_path=local_path
    )

    return gcs_path


@task()
def write_to_local(df: DataFrame, dataset_file: str) -> str:
    """Write dataframe as delta locally"""
    path = f"data/silver/{dataset_file}"
    
    df.coalesce(1).write.format("delta").option("header", "true").mode("overwrite").save(path)
    
    return path


@task()
def write_to_gcs(path: Path) -> None:
    """Upload local parquet file to Google Cloud Storage"""
    gcs_block = GcsBucket.load("esports")
    gcs_block.upload_from_folder(
        from_folder=path,
        to_folder=path
    )


@task()
def transform_columns_type(df: DataFrame, df_name: str, column_types: dict) -> DataFrame:
    """Transform columns type"""   
    for col_name, col_type in column_types.items():
        if df_name == "esports_tournaments" and col_name == 'StartDate':
            df = df.withColumn(col_name, F.when((df[col_name] == '0202-05-07') & (df['GameId'] == 785), '2022-05-07').otherwise(df[col_name]))
            df = df.withColumn(col_name, df[col_name].cast(col_type))
        else:
            df = df.withColumn(col_name, df[col_name].cast(col_type))
    return df


@task()
def clean_data(spark: pyspark, path: str) -> DataFrame:
    """Clean data"""
    df = spark.read.format('parquet').load(path)
    print(f"Pre - na rows: {df.count() - df.na.drop().count()}")
    print(f"Pre - duplicated rows: {df.count() - df.dropDuplicates().count()}")
    cleaned_df = df.na.drop().dropDuplicates()
    print(f"Pos - na rows: {cleaned_df.count() - cleaned_df.na.drop().count()}")
    print(f"Pos - duplicated rows: {cleaned_df.count() - cleaned_df.dropDuplicates().count()}")
    
    return cleaned_df


@flow()
def etl_gcs_bronze_to_gcs_silver() -> None:
    """The main ETL function""" 

    #  Create a spark session with Delta
    builder = pyspark.sql.SparkSession.builder.appName("esports_tournaments_silver") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

    # Create spark context
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    dfs = {'esports_tournaments': ESPORTS_TOURNAMENTS_TYPES,
           'esports_games_genre': ESPORTS_GAMES_GENRE_TYPES,
           'esports_games_awarding_prize_money': ESPORTS_GAMES_AWARDING_PRIZE_MONEY_TYPES}
    
    for df_name, df_types in dfs.items():  
        bronze_path = extract_from_gcs(df_name)
        cleaned_df = clean_data(spark, bronze_path)
        transformed_df = transform_columns_type(cleaned_df, df_name, df_types)
        silver_path = write_to_local(transformed_df, df_name)
        write_to_gcs(silver_path)


if __name__ == '__main__':
    etl_gcs_bronze_to_gcs_silver()
