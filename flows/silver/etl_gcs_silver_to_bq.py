from delta import *
from delta.tables import *

from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

import pyspark


@task()
def extract_from_gcs(dataset_file: str) -> str:
    """Download data from GCS"""
    gcs_path = f"data/silver/{dataset_file}"
    local_path = f""
    gcs_block = GcsBucket.load("esports")
    gcs_block.get_directory(
        from_path=gcs_path,
        local_path=local_path
    )

    return gcs_path