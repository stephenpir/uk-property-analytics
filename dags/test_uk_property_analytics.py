from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount


with DAG(
    dag_id="uk_property_analytics_ingestion",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["uk-property-analytics", "ingestion"],
) as dag:

    ingest_land_registry = DockerOperator(
        task_id="ingest_land_registry",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "python/ingestion/land_registry_ingest.py",
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        auto_remove="success",
        mount_tmp_dir=False,
        environment={
            "AWS_REGION": "eu-west-2",
            "S3_BUCKET": "spir23-uk-residential-property-analytics-dev",
            "CSV_URL": "https://price-paid-data.publicdata.landregistry.gov.uk/pp-2025.csv",
            "S3_KEY": "landing/land-registry/annual/2025/pp-2025.csv",
        },
        mounts=[
            Mount(
                source="/Users/stephenpir/.aws",
                target="/root/.aws",
                type="bind",
                read_only=True,
            ),
        ],
    )