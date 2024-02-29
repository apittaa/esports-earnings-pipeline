import os

from dotenv import load_dotenv

from prefect.infrastructure.container import DockerContainer
from prefect_gcp import GcpCredentials, GcsBucket


load_dotenv(override=True)

API_KEY =os.getenv("API_KEY") 
GCP_PROJECT_ID =os.getenv("GCP_PROJECT_ID") 
GCP_SERVICE_ACCOUNT_NAME =os.getenv("GCP_SERVICE_ACCOUNT_NAME") 
GCP_REGION =os.getenv("GCP_REGION") 
GCP_ZONE =os.getenv("GCP_ZONE") 
GCS_BUCKET_NAME =os.getenv("GCS_BUCKET_NAME") 
GCP_CREDENTIALS =os.getenv("LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH") 
GCP_CREDENTIALS_BLOCK =os.getenv("GCP_CREDENTIALS_BLOCK") 
GCS_BUCKET_BLOCK =os.getenv("GCS_BUCKET_BLOCK") 
DOCKER_BLOCK =os.getenv("DOCKER_BLOCK") 

# GCP CREDENTIALS BLOCK
GcpCredentials(service_account_file=GCP_CREDENTIALS).save(GCP_CREDENTIALS_BLOCK, overwrite=True)

# GCS BUCKET BLOCK
gcp_credentials = GcpCredentials.load(GCP_CREDENTIALS_BLOCK)
GcsBucket(gcp_credentials=gcp_credentials, bucket=GCS_BUCKET_NAME).save(GCS_BUCKET_BLOCK, overwrite=True)

# DOCKER BLOCK
docker_block = DockerContainer(
    image="devpitta/prefect:esports_pipeline",
    image_pull_policy="ALWAYS",
    env={
        "API_KEY": API_KEY,
        "GCP_PROJECT_ID": GCP_PROJECT_ID,
        "GCP_SERVICE_ACCOUNT_NAME": GCP_SERVICE_ACCOUNT_NAME,
        "GCP_REGION": GCP_REGION,
        "GCP_ZONE": GCP_ZONE,
        "GCS_BUCKET_NAME": GCS_BUCKET_NAME,
        "LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH": GCP_CREDENTIALS,
        "GCP_CREDENTIALS_BLOCK": GCP_CREDENTIALS_BLOCK,
        "GCS_BUCKET_BLOCK": GCS_BUCKET_BLOCK,
        "DOCKER_BLOCK": DOCKER_BLOCK,
    },
    auto_remove=True,
)

docker_block.save(DOCKER_BLOCK, overwrite=True)
