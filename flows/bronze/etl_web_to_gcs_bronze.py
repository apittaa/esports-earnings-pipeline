import logging
import os
import re
import requests
import urllib3

from bs4 import BeautifulSoup

from dotenv import load_dotenv

import pandas as pd

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark
from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F


# Create a function to retrieve the offset from a file
def write_to_local(df: DataFrame, dataset_file: str) -> str:
    """Get the offset from cloud storage."""
    local_path = f"../../data/bronze/{dataset_file}"
    path = f"../../data/bronze/{dataset_file}"
    
    if dataset_file == "esports_tournaments":
        df.coalesce(1).write.format("parquet").option("header", "true").mode("append").save(local_path)
    else:
        df.coalesce(1).write.format("parquet").option("header", "true").mode("overwrite").save(local_path)
    
    return path


def write_to_gcs(path: str) -> None:
    """Upload local parquet file to Google Cloud Storage"""
    gcs_block = GcsBucket.load("esports")
    gcs_block.upload_from_folder(
        from_folder=path,
        to_folder=path
    )


def get_tournament_offset() -> int:
    """Get the offset from a file."""
    try:
        gcs_block = GcsBucket.load('esports')
        gcs_block.download_object_to_path(
            from_path='../../data/bronze/offset/offset.parquet',
            to_path='../../data/bronze/offset/offset.parquet')
        with open("../../data/bronze/offset/offset.parquet", "r") as offset_file:
            offset = int(offset_file.read())
    except Exception as e:
        print(f"An error occurred: {e}")
        offset = 0  # or handle the error in a way that makes sense for your use case
    return offset


def write_tournament_offset(offset: int) -> None:
    with open("../../data/bronze/offset/offset.parquet", "w") as offset_file:
        offset_file.write(str(offset))
    gcs_block = GcsBucket.load("esports")
    gcs_block.upload_from_folder(
        from_folder='../../data/bronze/offset',
        to_folder='../../data/bronze/offset'
    )


@task(retries=3)
# Refactor the code in the previous cell into a function
def get_tournaments_data(spark: pyspark, api_key: str) -> None:
    """Retrieve data from the API."""
    
    # Disable warnings
    urllib3.disable_warnings()
    
    # Initialize parameters
    batch_size = 100
    tournaments_data = []
    
    # Set your API key and the API endpoint URL
    tournaments_endpoint = "http://api.esportsearnings.com/v0/LookupRecentTournaments"
    
    # Add the offset function to set the offset
    offset = get_tournament_offset()

    while True:
        # Set up the request parameters
        params = {
            "apikey": api_key,
            "offset": offset,
        }

        try:
            # Make the API request
            response = requests.get(tournaments_endpoint, params=params, verify=False)

            # Check for successful response
            if response.status_code == 200:
                # Check if response content is b'' (empty bytes)
                if response.content == b'':
                    print("No more data to retrieve")
                    break
                data = response.json()
                if not data:
                    break  # No more data to retrieve
                tournaments_data.extend(data)  # Append the batch to the list
                offset += batch_size  # Increment the offset for the next batch
                print(f"Processed {offset} records")
            else:
                logging.error(f"API request failed with status code: {response.status_code}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

    write_tournament_offset(offset)
    
    data = pd.DataFrame(tournaments_data)
    
    if data.empty:
        return None
    else:
        df = spark.createDataFrame(data)
   
    path = write_to_local(df, "esports_tournaments")
    write_to_gcs(path)


# Create a function to retrieve game_ids from a file
def get_games_ids(spark: pyspark) -> list:
    """Get the game_ids from a file."""
    
    # Read the parquet file to obtain the game_id values
    parquet_data = spark.read.format('parquet').load('/../..data/bronze/esports_tournaments')

    # Extract the game_id column values into game_ids
    game_ids = parquet_data.select('GameId').distinct().rdd.flatMap(lambda x: x).collect()
    
    return game_ids
