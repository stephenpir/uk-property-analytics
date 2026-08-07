from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

from airflow.operators.python import ShortCircuitOperator

def check_new_file(**context):
    result = context["ti"].xcom_pull(
        task_ids="ingest_land_registry_monthly",
        key="return_value",
    )

    return result is not None and "archive_file_name" in result


with DAG(
    dag_id="uk_property_analytics_monthly_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "year": 2026,
    },
    tags=["uk-property-analytics"],
) as dag:

    ingest_land_registry_monthly = DockerOperator(
        task_id="ingest_land_registry_monthly",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "-m",
            "python.ingestion.land_registry_monthly_ingest",
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

    load_monthly_raw_data = DockerOperator(
        task_id="load_monthly_raw_data",
        image="uk-property-analytics:latest",
        command=[
            "python",
            "-m",
            "python.ingestion.load_monthly_raw_data",
            "--param",
            "YEAR={{ params.year }}",
            "--param",
            "ARCHIVE_FILE_NAME={{ ti.xcom_pull(task_ids='ingest_land_registry_monthly', key='return_value')['archive_file_name'] }}",
            "--param",
            "AUDIT_ID={{ ti.xcom_pull(task_ids='ingest_land_registry_monthly', key='return_value')['audit_id'] }}",
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
            "AUDIT_ID={{ ti.xcom_pull(task_ids='ingest_land_registry_monthly', key='return_value')['audit_id'] }}",
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


    ingest_land_registry_monthly >> check_new_file >> load_monthly_raw_data >> dbt_run