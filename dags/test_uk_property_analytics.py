from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id="uk_property_analytics_docker_test",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["uk-property-analytics", "infrastructure-test"],
) as dag:

    test_project_container = DockerOperator(
        task_id="test_project_container",
        image="uk-property-analytics:latest",
        command="python --version",
        auto_remove="success",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )