# GCP VARIABLES
variable "PROJECT_ID" {
    description = "GCP Project ID."
    type = string
}

variable "SERVICE_ACCOUNT_NAME" {
    description = "Service account name."
    type = string
}

variable "REGION" {
    description = "GCP resources region."
    type = string
}

variable "ZONE" {
    description = "GCP resources zone."
    type = string
}

variable "BUCKET_NAME" {
    description = "Bucket name."
    type = string
}

variable "STORAGE_CLASS" {
  description = "Storage class type for the bucket."
  default = "STANDARD"
}

variable "SERVICE_ACCOUNT_CREDENTIAL_PATH" {
    description = "GCP credentials."
    type = string
}

# BIGQUERY VARIABLES - DATASETS
variable "DATASET_BRONZE" {
    description = "Dataset name to store bronze data"
    type = string
}

variable "DATASET_SILVER" {
    description = "Dataset name to store silver data"
    type = string
}

variable "DATASET_GOLD" {
    description = "Dataset name to store gold data"
    type = string
}

# BIGQUERY VARIABLES - TABLES
variable "ESPORTS_TOURNAMENTS_BRONZE" {
    description = "Table name to store esports tournaments bronze data"
    type = string 
}

variable "ESPORTS_GAMES_GENRE_BRONZE" {
    description = "Table name to store esports games genre bronze data"
    type = string 
}

variable "ESPORTS_GAMES_AWARDING_PRIZE_MONEY_BRONZE" {
    description = "Table name to store esports games awarding prize money bronze data"
    type = string 
}

variable "ESPORTS_TOURNAMENTS_SILVER" {
    description = "Table name to store esports tournaments silver data"
    type = string 
}

variable "ESPORTS_GAMES_GENRE_SILVER" {
    description = "Table name to store esports games genre silver data"
    type = string 
}

variable "ESPORTS_GAMES_AWARDING_PRIZE_MONEY_SILVER" {
    description = "Table name to store esports games awarding prize money silver data"
    type = string 
}

variable "ESPORTS_TOURNAMENTS_GOLD" {
    description = "Table name to store esports tournaments with genre gold data"
    type = string 
}

variable "ESPORTS_GAMES_AWARDING_PRIZE_MONEY_GOLD" {
    description = "Table name to store esports games awarding prize money with genre gold data"
    type = string 
}
