from prefect import flow

from etl_gcs_bronze_to_gcs_silver import etl_gcs_bronze_to_gcs_silver
from etl_gcs_silver_to_bq import etl_gcs_silver_to_bq


@flow()
def main_flow_silver():
    etl_gcs_bronze_to_gcs_silver()
    etl_gcs_silver_to_bq()


if __name__ == "__main__":
    main_flow_silver()
