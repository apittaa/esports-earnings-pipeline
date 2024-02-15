variable "API_KEY" {}
variable "GCP_PROJECT_ID" {}
variable "GCP_SERVICE_ACCOUNT_NAME" {}
variable "GCP_REGION" {}
variable "GCP_ZONE" {}
variable "GCS_BUCKET_NAME" {}
variable "LOCAL_SERVICE_ACCOUNT_FILE_PATH" {}
variable "STORAGE_CLASS" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}