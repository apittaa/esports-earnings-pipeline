import os

from dotenv import load_dotenv

from prefect.infrastructure.container import DockerContainer
from prefect_gcp import GcpCredentials, GcsBucket


load_dotenv()

GCP_CREDENTIALS = os.getenv("LOCAL_SERVICE_ACCOUNT_CREDENTIAL_PATH")
GCP_CREDENTIALS_BLOCK = os.getenv("GCP_CREDENTIALS_BLOCK")
GCS_BUCKET_BLOCK = os.getenv("GCS_BUCKET_BLOCK")
DOCKER_BLOCK = os.getenv("DOCKER_BLOCK")
BUCKET = os.getenv("GCS_BUCKET_NAME")

# GCP CREDENTIALS BLOCK
GcpCredentials(service_account_file=GCP_CREDENTIALS).save(GCP_CREDENTIALS_BLOCK, overwrite=True)

# GCS BUCKET BLOCK
gcp_credentials = GcpCredentials.load(GCP_CREDENTIALS_BLOCK)
GcsBucket(gcp_credentials=gcp_credentials, bucket=BUCKET).save(GCS_BUCKET_BLOCK, overwrite=True)

# DOCKER BLOCK
docker_block = DockerContainer(
    image="devpitta/prefect:esports_pipeline",
    image_pull_policy="ALWAYS",
    auto_remove=True,
)

docker_block.save(DOCKER_BLOCK, overwrite=True)
