import argparse
import logging
import subprocess

from python.utils.snowflake_connection import create_snowflake_connection
from python.utils.file_ingest_audit import update_audit_status


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_dbt():

    subprocess.run(
        [
            "dbt",
            "run",
            "--project-dir",
            "/app/dbt",
        ],
        check=True,
    )


def update_audit(audit_id, status, error_message=None):

    conn = create_snowflake_connection(
        profile_name="uk_property_analytics",
        target_name="dev",
    )

    try:
        with conn.cursor() as cursor:
            update_audit_status(
                cursor,
                audit_id=audit_id,
                status=status,
                error_message=error_message,
            )

            conn.commit()

    finally:
        conn.close()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--param",
        action="append",
        default=[],
    )

    args = parser.parse_args()

    params = {}

    for parameter in args.param:
        name, value = parameter.split("=", 1)
        params[name] = value

    audit_id = params["AUDIT_ID"]

    try:
        run_dbt()

        update_audit(
            audit_id,
            "LOADED",
        )

        logger.info(
            "dbt completed successfully. Audit %s updated to LOADED",
            audit_id,
        )

    except Exception as e:

        logger.error(
            "dbt failed: %s",
            e,
        )

        update_audit(
            audit_id,
            "FAILED",
            error_message=str(e),
        )

        raise


if __name__ == "__main__":
    main()