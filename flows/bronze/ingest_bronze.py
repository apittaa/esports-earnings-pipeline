from prefect import flow

from etl_web_to_gcs_bronze import etl_web_to_gcs
from etl_gcs_bronze_to_bq import etl_gcs_bronze_to_bq


@flow()
def main_flow_bronze():
    etl_web_to_gcs()
    etl_gcs_bronze_to_bq()


if __name__ == "__main__":
    main_flow_bronze()
