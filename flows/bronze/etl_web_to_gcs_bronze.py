import logging
import os
import re
import requests
import urllib3

from bs4 import BeautifulSoup

from dotenv import load_dotenv

import pandas as pd

from google.cloud import storage

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark
from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F


def write_to_local(df: DataFrame, dataset_file: str) -> str:
    """Get the offset from cloud storage."""
    local_path = f"data/bronze/{dataset_file}"
    path = f"data/bronze/{dataset_file}"
    
    if dataset_file == "esports_tournaments":
        df.coalesce(1).write.format("parquet").option("header", "true").mode("append").save(local_path)
    else:
        df.coalesce(1).write.format("parquet").option("header", "true").mode("overwrite").save(local_path)
    
    return path


def write_to_gcs(path: str) -> None:
    """Upload local parquet file to Google Cloud Storage"""
    gcs_block = GcsBucket.load("gcs-bucket-esports-pipeline")
    gcs_block.upload_from_folder(
        from_folder=path,
        to_folder=path
    )  


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


def get_tournament_offset(credentials: str, bucket: str) -> int | None:
    """Get the offset from a file."""
    print("Starting get offset")
    gcp_credentials = credentials
    client = storage.Client.from_service_account_json(json_credentials_path=gcp_credentials)
    gcs_bucket = storage.Bucket(client, bucket)
    blob = gcs_bucket.blob('data/bronze/offset/offset.parquet')
    
    print("Checking blob")
    if blob.exists() is False:
        print("Blob does not exist")
        offset = 0
        print(offset)
        return offset
    else:
        try:
            print("Starting Try block")
            gcs_block = GcsBucket.load('esports')
            gcs_block.download_object_to_path(
                from_path='data/bronze/offset/offset.parquet',
                to_path='data/bronze/offset/offset.parquet')
            with open("data/bronze/offset/offset.parquet", "r") as offset_file:
                offset = int(offset_file.read())
                return offset
        except Exception as e:
            return print(f"An error occurred: {e}")


def write_tournament_offset(offset: int) -> None:
    with open("data/bronze/offset/offset.parquet", "w") as offset_file:
        offset_file.write(str(offset))
    gcs_block = GcsBucket.load("gcs-bucket-esports-pipeline")
    gcs_block.upload_from_folder(
        from_folder='data/bronze/offset',
        to_folder='data/bronze/offset'
    )


@task(retries=3, log_prints=True)
def get_tournaments_data(spark: pyspark, api_key: str, credentials: str, bucket: str) -> None:
    """Retrieve data from the API."""
    
    # Disable warnings
    urllib3.disable_warnings()
    
    # Initialize parameters
    batch_size = 100
    tournaments_data = []
    
    # Set your API key and the API endpoint URL
    tournaments_endpoint = "http://api.esportsearnings.com/v0/LookupRecentTournaments"
    
    # Add the offset function to set the offset
    offset = get_tournament_offset(credentials, bucket)

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
                    print(response.content)
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


def get_games_ids(spark: pyspark) -> list:
    """Get the game_ids from a file."""
    
    esports_tournaments_path = extract_from_gcs("esports_tournaments")
    
    # Read the parquet file to obtain the game_id values
    parquet_data = spark.read.format('parquet').load(esports_tournaments_path)

    # Extract the game_id column values into game_ids
    game_ids = parquet_data.select('GameId').distinct().rdd.flatMap(lambda x: x).collect()
    
    return game_ids


@task(retries=3, log_prints=True)
def get_games_awarding_prize_money_data(spark: pyspark, api_key: str) -> None:
    """Retrieve game data from the API."""

    # Disable warnings
    urllib3.disable_warnings()
    
    # Construct the URL for the current game ID
    games_endpoint = "http://api.esportsearnings.com/v0/LookupGameById"

    # Initialize the list to store game data
    prize_money_data = []
    
    # Add the game_ids function to get the game_ids
    games_ids = get_games_ids(spark)

    for game_id in games_ids:

        # Set up the request parameters
        params = {
            "apikey": api_key,
            "gameid": game_id,
        }   

        while True:
            try:
                # Send a GET request to the API
                response = requests.get(games_endpoint, params=params, verify=False)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Check if response content is b'' (empty bytes)
                    if response.content == b'':
                        print("No more data to retrieve")
                        break
                    # Parse the JSON response
                    data = response.json()
                    # Add the GameId to the data
                    data["GameId"] = game_id
                    # Append the data to the list of data entries
                    prize_money_data.append(data)
                    # Print the status
                    print(f"Processed game ID {game_id}")
                    break
                else:
                    logging.error(f"Request for game ID {game_id} failed with status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                # Handle connection and request exceptions
                logging.error(f"Request error for game ID {game_id}: {e}")

    data = pd.DataFrame(prize_money_data)
    
    if data.empty:
        return None
    else:
        df = spark.createDataFrame(data)

    path = write_to_local(df, "esports_games_awarding_prize_money")
    write_to_gcs(path)


def get_games_genre_data() -> list:
    """Get data from the website."""
    games_genre_endpoint = 'https://www.esportsearnings.com/games/browse-by-genre'
    html = requests.get(games_genre_endpoint).text
    soup = BeautifulSoup(html, 'html.parser')

    # Find all genre titles, game statistics, and game boxes
    genre_titles = soup.find_all('span', class_='games_main_genre_title')
    genre_stats = soup.find_all('span', class_='games_main_genre_stats')
    game_boxes = soup.find_all('div', class_='games_main_game_box')
    game_links = soup.find_all('a')

    # Extract text and statistics as lists
    genre_titles = [genre_title.text for genre_title in genre_titles]
    genre_num = [int(re.search(r'\d+', genre_stat.text).group()) for genre_stat in genre_stats]
    game_titles = [game_box['title'] for game_box in game_boxes if 'title' in game_box.attrs]
    game_ids = [int(match.group(1)) for link in game_links if (match := re.compile(r'^/games/(\d+)').match(link.get('href')))]
    
    return [genre_titles, genre_num, game_titles, game_ids]


@task()
def create_games_genre_df(spark: pyspark):
    """Create a DataFrame from the list of dictionaries."""
    
    # Add the get_data function to get the data
    genre_titles, genre_num, game_titles, game_ids = get_games_genre_data()
    
    # Initialize an empty list to store dictionaries
    games_genre_data = []

    # Iterate through the pairs of genre titles and game boxes
    position = 0
    for genre_title, num_games in zip(genre_titles, genre_num):
        game_titles_list = game_titles[position:position + num_games]
        game_ids_list = game_ids[position:position + num_games]
        
        # Create a dictionary for each game and add it to the data list
        for game_title, game_id in zip(game_titles_list, game_ids_list):
            games_genre_data.append({'Genre': genre_title, 'GameName': game_title, 'GameId': game_id})
        
        position += num_games
    
    data = pd.DataFrame(games_genre_data)

    if data.empty:
        return None
    else:
        df = spark.createDataFrame(data)

    path = write_to_local(df, "esports_games_genre")
    write_to_gcs(path)


@flow()
def etl_web_to_gcs(spark, api_key: str, credentials: str, bucket: str) -> None:
    """The main ETL function"""
    
    get_tournaments_data(spark, api_key, bucket, credentials)
    get_games_awarding_prize_money_data(spark, api_key)
    create_games_genre_df(spark)
    

if __name__ == '__main__':
    etl_web_to_gcs()
