from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount


with DAG(
    dag_id="uk_property_analytics_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "year": 2025,
    },
    tags=["uk-property-analytics"],
) as dag:

    ingest_land_registry = DockerOperator(
        task_id="ingest_land_registry",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "-m",
            "python.ingestion.land_registry_ingest",
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        auto_remove="success",
        mount_tmp_dir=False,
        environment={
            "AWS_REGION": "eu-west-2",
            "S3_BUCKET": "spir23-uk-residential-property-analytics-dev",
            "YEAR": "{{ params.year }}",
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

    load_raw_data = DockerOperator(
        task_id="load_raw_data",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "-m",
            "python.utils.snowflake_execute_sql",
            "--sql-file",
            "/app/sql/05_load_raw_data.sql",
            "--profile",
            "uk_property_analytics",
            "--target",
            "dev",
            "--year",
            "{{ params.year }}",
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        auto_remove="success",
        mount_tmp_dir=False,
        # environment={
        #     "YEAR": "{{ params.year }}",
        # },        
        mounts=[
            Mount(
                source="/Users/stephenpir/.dbt",
                target="/root/.dbt",
                type="bind",
                read_only=True,
            ),
        ],
    )

    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="uk-property-analytics:latest",
        command=[
            "dbt",
            "run",
            "--project-dir",
            "/app/dbt",
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        auto_remove="success",
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source="/Users/stephenpir/.dbt",
                target="/root/.dbt",
                type="bind",
                read_only=True,
            ),
        ],
    )

ingest_land_registry >> load_raw_data >> dbt_run