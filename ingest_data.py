from prefect import flow

from flows.bronze.etl_web_to_gcs_bronze import etl_web_to_gcs
from flows.bronze.etl_gcs_bronze_to_bq import etl_gcs_bronze_to_bq
from flows.silver.etl_gcs_bronze_to_gcs_silver import etl_gcs_bronze_to_gcs_silver
from flows.silver.etl_gcs_silver_to_bq import etl_gcs_silver_to_bq
from flows.gold.etl_gcs_silver_to_gcs_gold import etl_gcs_silver_to_gcs_gold
from flows.gold.etl_gcs_gold_to_bq import etl_gcs_gold_to_bq


@flow()
def main_flow():
    etl_web_to_gcs()
    etl_gcs_bronze_to_bq()
    etl_gcs_bronze_to_gcs_silver()
    etl_gcs_silver_to_bq()
    etl_gcs_silver_to_gcs_gold()
    etl_gcs_gold_to_bq()


if __name__ == "__main__":
    main_flow()
