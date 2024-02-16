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
