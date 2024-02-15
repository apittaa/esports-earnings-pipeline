# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset

# BRONZE
resource "google_bigquery_dataset" "dataset_bronze" {
  dataset_id = var.DATASET_BRONZE
  project    = var.PROJECT_ID
  location   = var.REGION
}

resource "google_bigquery_table" "esports_tournaments_bronze_table" {
  dataset_id = var.DATASET_BRONZE
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_TOURNAMENTS_BRONZE
}

resource "google_bigquery_table" "esports_games_genre_bronze_table" {
  dataset_id = var.DATASET_BRONZE
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_GAMES_GENRE_BRONZE
}

resource "google_bigquery_table" "esports_games_awarding_prize_money_bronze_table" {
  dataset_id = var.DATASET_BRONZE
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_GAMES_AWARDING_PRIZE_MONEY_BRONZE
}

# SILVER
resource "google_bigquery_dataset" "dataset_silver" {
  dataset_id = var.DATASET_SILVER
  project    = var.PROJECT_ID
  location   = var.REGION
}

resource "google_bigquery_table" "esports_tournaments_silver_table" {
  dataset_id = var.DATASET_SILVER
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_TOURNAMENTS_SILVER
}

resource "google_bigquery_table" "esports_games_genre_silver_table" {
  dataset_id = var.DATASET_SILVER
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_GAMES_GENRE_SILVER
}

resource "google_bigquery_table" "esports_games_awarding_prize_money_silver_table" {
  dataset_id = var.DATASET_SILVER
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_GAMES_AWARDING_PRIZE_MONEY_SILVER
}

# GOLD
resource "google_bigquery_dataset" "dataset_gold" {
  dataset_id = var.DATASET_GOLD
  project    = var.PROJECT_ID
  location   = var.REGION
}

resource "google_bigquery_table" "esports_tournaments_with_genre_gold_table" {
  dataset_id = var.DATASET_GOLD
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_TOURNAMENTS_GOLD
}

resource "google_bigquery_table" "esports_games_awarding_prize_money_with_genre_gold_table" {
  dataset_id = var.DATASET_GOLD
  project    = var.PROJECT_ID
  table_id   = var.ESPORTS_GAMES_AWARDING_PRIZE_MONEY_GOLD
}
