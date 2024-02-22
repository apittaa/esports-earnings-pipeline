from prefect import flow

from etl_gcs_silver_to_gcs_gold import etl_gcs_silver_to_gcs_gold
from etl_gcs_gold_to_bq import etl_gcs_gold_to_bq


@flow()
def main_flow_silver():
    etl_gcs_silver_to_gcs_gold()
    etl_gcs_gold_to_bq()


if __name__ == "__main__":
    main_flow_silver()
    