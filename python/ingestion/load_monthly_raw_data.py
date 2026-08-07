import argparse
import logging

from python.utils.snowflake_execute_sql import execute_sql_file
from python.utils.snowflake_connection import create_snowflake_connection
from python.utils.file_ingest_audit import update_audit_status


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


SQL_FILE = "/app/sql/07_load_monthly_raw_data.sql"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--param",
        action="append",
        default=[],
    )

    args = parser.parse_args()

    parameters = {}

    for parameter in args.param:
        name, value = parameter.split("=", 1)
        parameters[name] = value

    year = parameters["YEAR"]
    archive_file_name = parameters["ARCHIVE_FILE_NAME"]
    audit_id = int(parameters["AUDIT_ID"])

    logger.info(
        "Starting monthly raw load for file %s",
        archive_file_name,
    )

    conn = create_snowflake_connection(
        profile_name="uk_property_analytics",
        target_name="dev",
    )

    try:
        execute_sql_file(
            sql_file=SQL_FILE,
            profile_name="uk_property_analytics",
            target_name="dev",
            parameters=[
                f"YEAR={year}",
                f"ARCHIVE_FILE_NAME={archive_file_name}",
            ],
        )

        with conn.cursor() as cursor:
            update_audit_status(
                cursor,
                audit_id,
                "STAGED",
            )

        conn.commit()

        logger.info(
            "Monthly raw load completed. Audit %s updated to STAGED",
            audit_id,
        )

    except Exception as e:
        logger.error(
            "Monthly raw load failed: %s",
            e,
        )

        with conn.cursor() as cursor:
            update_audit_status(
                cursor,
                audit_id,
                "FAILED",
                error_message=str(e),
            )

        conn.commit()

        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()