from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

from airflow.operators.python import ShortCircuitOperator

def check_new_file(**context):
    result = context["ti"].xcom_pull(
        task_ids="ingest_land_registry",
        key="return_value",
    )

    return result is not None and "audit_id" in result

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
        do_xcom_push=True,
        retrieve_output=True,
        retrieve_output_path="/tmp/return.pkl",
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
            Mount(
                source="/Users/stephenpir/.dbt",
                target="/root/.dbt",
                type="bind",
                read_only=True,
            ),
        ],   
    )

    check_new_file = ShortCircuitOperator(
        task_id="check_new_file",
        python_callable=check_new_file,
    )

    load_raw_data = DockerOperator(
        task_id="load_raw_data",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "-m",
            "python.ingestion.load_raw_data",
            "--param",
            "YEAR={{ params.year }}",
            "--param",
            "AUDIT_ID={{ ti.xcom_pull(task_ids='ingest_land_registry', key='return_value')['audit_id'] }}",
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

    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "-m",
            "python.dbt.run_dbt_with_audit",
            "--param",
            "AUDIT_ID={{ ti.xcom_pull(task_ids='ingest_land_registry', key='return_value')['audit_id'] }}",
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

ingest_land_registry >> check_new_file >> load_raw_data >> dbt_run