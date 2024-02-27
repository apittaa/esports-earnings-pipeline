from pathlib import Path

from delta import *
from delta.tables import *

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark
from pyspark.sql import DataFrame
from pyspark.sql.types import *


@task()
def extract_from_gcs(dataset_file: str) -> str:
    """Download data from GCS"""
    gcs_path = f"data/silver/{dataset_file}"
    local_path = ""
    gcs_block = GcsBucket.load("gcs-bucket-esports-pipeline")
    gcs_block.get_directory(
        from_path=gcs_path,
        local_path=local_path
    )

    return gcs_path


@task()
def write_to_local(df: DataFrame, dataset_file: str) -> str:
    """Write dataframe as delta locally"""
    path = f"data/gold/{dataset_file}"
    
    df.coalesce(1).write.format("delta").option("header", "true").mode("overwrite").save(path)
    
    return path


@task()
def write_to_gcs(path: Path) -> None:
    """Upload local parquet file to Google Cloud Storage"""
    gcs_block = GcsBucket.load("gcs-bucket-esports-pipeline")
    gcs_block.upload_from_folder(
        from_folder=path,
        to_folder=path
    )


@task()
def join_dfs(spark: pyspark, dfs_path: dict) -> dict:
    
    esports_tournaments = spark.read.format('parquet').load(dfs_path['esports_tournaments'])
    esports_games_genre = spark.read.format('parquet').load(dfs_path['esports_games_genre'])
    esports_games_awarding_prize_money = spark.read.format('parquet').load(dfs_path['esports_games_awarding_prize_money'])
    
    esports_tournaments_genre = esports_tournaments.join(esports_games_genre.select("GameId", "GameName", "Genre"), on="GameId", how="inner")
    
    esports_games_awarding_prize_money_genre = esports_games_awarding_prize_money.join(esports_games_genre.select("GameId", "Genre"), on="GameId", how="inner")
    
    joined_dfs = {'esports_tournaments': esports_tournaments_genre, 
                  'esports_games_awarding_prize_money': esports_games_awarding_prize_money_genre
                  }
    
    return joined_dfs
    
    
@flow()
def etl_gcs_silver_to_gcs_gold(spark) -> None:
    """The main ETL function"""
    
    dfs_path = {'esports_tournaments': '',
                'esports_games_genre': '',
                'esports_games_awarding_prize_money': ''
                }
    
    for df_name in dfs_path.keys():  
        silver_path = extract_from_gcs(df_name)
        dfs_path[df_name] = silver_path
        
    joined_dfs = join_dfs(spark, dfs_path)
    
    for df_name, joined_df in joined_dfs.items():
        gold_path = write_to_local(joined_df, df_name)
        write_to_gcs(gold_path)


if __name__ == '__main__':
    etl_gcs_silver_to_gcs_gold()
