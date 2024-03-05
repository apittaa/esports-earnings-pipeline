import json
import os

from dotenv import load_dotenv

from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile, DbtCoreOperation
from prefect.infrastructure.container import DockerContainer
from prefect_gcp import GcpCredentials, GcsBucket, BigQueryWarehouse


load_dotenv()

# Load global env variables
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCP_SERVICE_ACCOUNT_INFO = os.getenv("GCP_SERVICE_ACCOUNT_INFO")

GCP_CREDENTIALS_BLOCK = os.getenv("GCP_CREDENTIALS_BLOCK") 
GCS_BUCKET_BLOCK = os.getenv("GCS_BUCKET_BLOCK") 
DOCKER_BLOCK = os.getenv("DOCKER_BLOCK")
BQ_BLOCK = os.getenv("BQ_BLOCK")

DBT_CLI_TARGET_DEV_BLOCK = os.getenv("DBT_CLI_TARGET_DEV_BLOCK")
DBT_CLI_TARGET_PROD_BLOCK = os.getenv("DBT_CLI_TARGET_PROD_BLOCK")
DBT_CLI_PROFILE_DEV_BLOCK = os.getenv("DBT_CLI_PROFILE_DEV_BLOCK")
DBT_CLI_PROFILE_PROD_BLOCK = os.getenv("DBT_CLI_PROFILE_PROD_BLOCK")
DBT_CLI_COMMAND_DEV_BLOCK = os.getenv("DBT_CLI_COMMAND_DEV_BLOCK")
DBT_CLI_COMMAND_PROD_BLOCK = os.getenv("DBT_CLI_COMMAND_PROD_BLOCK")

BQ_DATASET_DEV = str(os.getenv("BQ_ENV_DATASET"))
BQ_DATASET_PROD = str(os.getenv("BQ_PROD_DATASET"))
DBT_TARGET_DEV_BLOCK = os.getenv("DBT_CLI_TARGET_DEV_BLOCK")
DBT_TARGET_PROD_BLOCK = os.getenv("DBT_CLI_TARGET_PROD_BLOCK")
DBT_PROFILE_DEV_BLOCK = os.getenv("DBT_CLI_PROFILE_DEV_BLOCK")
DBT_PROFILE_PROD_BLOCK = os.getenv("DBT_CLI_PROFILE_PROD_BLOCK")
DBT_CLI_COMMAND_DEV_BLOCK = os.getenv("DBT_CLI_COMMAND_DEV_BLOCK")
DBT_CLI_COMMAND_PROD_BLOCK = os.getenv("DBT_CLI_COMMAND_PROD_BLOCK")
DBT_DIR = os.getenv("DBT_ENV_PROJECT_DIR")
DBT_DIR_PATH = f"{os.getcwd()}/{DBT_DIR}"

# GCP CREDENTIALS BLOCK
GcpCredentials(service_account_info=json.loads(GCP_SERVICE_ACCOUNT_INFO)).save(GCP_CREDENTIALS_BLOCK, overwrite=True)

# LOAD GCP CREDENTIALS BLOCK
gcp_credentials = GcpCredentials.load(GCP_CREDENTIALS_BLOCK)

# GCS BUCKET BLOCK
GcsBucket(gcp_credentials=gcp_credentials, bucket=GCS_BUCKET_NAME).save(GCS_BUCKET_BLOCK, overwrite=True)

# DOCKER BLOCK
docker_block = DockerContainer(
    image="devpitta/prefect:esports_pipeline",
    image_pull_policy="ALWAYS",
    auto_remove=True,
)

docker_block.save(DOCKER_BLOCK, overwrite=True)

# BQ BUCKET BLOCK
BigQueryWarehouse(gcp_credentials=gcp_credentials).save(BQ_BLOCK, overwrite=True)

# DBT CORE CLI BLOCKS

# DEVELOPMENT BLOCKS
# 1.TARGET
target_configs_dev = BigQueryTargetConfigs(
    schema=BQ_DATASET_DEV,  # also known as dataset
    credentials=gcp_credentials,
)
target_configs_dev.save(DBT_TARGET_DEV_BLOCK, overwrite=True)

# 2.PROFILE
dbt_cli_profile_dev = DbtCliProfile(
    name="default",  # find this in the profiles.yml or under name in dbt_project.yml
    target="dev",
    target_configs=target_configs_dev,
)
dbt_cli_profile_dev.save(DBT_PROFILE_DEV_BLOCK, overwrite=True)

# 3.OPERATION / COMMANDS
# dbt_cli_profile_dev_block = config("DBT_CLI_PROFILE_DEV_BLOCK")
dbt_cli_command_dev_block = DBT_CLI_COMMAND_DEV_BLOCK

# dbt_cli_profile_dev = DbtCliProfile.load(dbt_cli_profile_dev_block)
dbt_core_operation_dev = DbtCoreOperation(
    commands=["dbt deps", "dbt build"],
    dbt_cli_profile=dbt_cli_profile_dev,
    working_dir=DBT_DIR_PATH,
    project_dir=DBT_DIR_PATH,
    overwrite_profiles=True,
)
dbt_core_operation_dev.save(dbt_cli_command_dev_block, overwrite=True)

# PRODUCTION BLOCKS
# 1.TARGET
target_configs_prod = BigQueryTargetConfigs(
    schema=BQ_DATASET_PROD,  # also known as dataset
    credentials=gcp_credentials,
)
target_configs_prod.save(DBT_TARGET_PROD_BLOCK, overwrite=True)

# 2.PROFILE
dbt_cli_profile_prod = DbtCliProfile(
    name="default",  # find this in the profiles.yml or under name in dbt_project.yml
    target="prod",
    target_configs=target_configs_prod,
)
dbt_cli_profile_prod.save(DBT_PROFILE_PROD_BLOCK, overwrite=True)

# 3.OPERATION / COMMANDS
dbt_cli_command_prod_block = DBT_CLI_COMMAND_PROD_BLOCK

dbt_core_operation_prod = DbtCoreOperation(
    commands=["dbt deps", "dbt build"],
    dbt_cli_profile=dbt_cli_profile_prod,
    working_dir=DBT_DIR_PATH,
    project_dir=DBT_DIR_PATH,
    overwrite_profiles=True,
)
dbt_core_operation_prod.save(dbt_cli_command_prod_block, overwrite=True)

# https://docs.prefect.io/concepts/blocks/
# if a block has been created in a .py file, the block can also be registered with the CLI command:
# NOTE: Log into prefect cloud before running the below command
# prefect block register --file flows/create_prefect_blocks.py
# Then log into prefect cloud and check that the blocks are available in the UI
