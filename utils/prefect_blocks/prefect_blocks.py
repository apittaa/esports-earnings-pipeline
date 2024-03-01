import json
import os

from dotenv import load_dotenv

from prefect.infrastructure.container import DockerContainer
from prefect_gcp import GcpCredentials, GcsBucket

from utils.secret_manager.secret_manager import load_secret()


# load_dotenv(override=True)

# GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME") 
# GCP_CREDENTIALS_BLOCK = os.getenv("GCP_CREDENTIALS_BLOCK") 
# GCS_BUCKET_BLOCK = os.getenv("GCS_BUCKET_BLOCK") 
# DOCKER_BLOCK = os.getenv("DOCKER_BLOCK")
# GCP_SERVICE_ACCOUNT_INFO = os.getenv("GCP_SERVICE_ACCOUNT_INFO")

secret_value, error_message = load_secret(PROJECT_ID, SECRET_ID)
if secret_value is not None:
    print("Secret loaded successfully:", json.loads(secret_value))
else:
    print("Failed to load secret:", error_message)


# GCP CREDENTIALS BLOCK
GcpCredentials(service_account_info=json.loads(GCP_SERVICE_ACCOUNT_INFO)).save(GCP_CREDENTIALS_BLOCK, overwrite=True)

# GCS BUCKET BLOCK
gcp_credentials = GcpCredentials.load(GCP_CREDENTIALS_BLOCK)
GcsBucket(gcp_credentials=gcp_credentials, bucket=GCS_BUCKET_NAME).save(GCS_BUCKET_BLOCK, overwrite=True)

# DOCKER BLOCK
docker_block = DockerContainer(
    image="devpitta/prefect:esports_pipeline",
    image_pull_policy="ALWAYS",
    auto_remove=True,
)

docker_block.save(DOCKER_BLOCK, overwrite=True)
