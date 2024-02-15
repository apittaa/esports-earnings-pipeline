# passed in by env vars (TF_VAR)
variable "PROJECT_ID" {}
variable "SERVICE_ACCOUNT_NAME" {}
variable "REGION" {}
variable "ZONE" {}
variable "BUCKET_NAME" {}
variable "SERVICE_ACCOUNT_CREDENTIAL_PATH" {}
variable "STORAGE_CLASS" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}