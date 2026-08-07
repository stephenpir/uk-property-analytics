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


def main(parameters):
    """
    Load annual Land Registry data into RAW schema
    and update audit lifecycle state.
    """

    year = None
    audit_id = None

    for parameter in parameters:
        name, value = parameter.split("=", 1)

        if name == "YEAR":
            year = value

        elif name == "AUDIT_ID":
            audit_id = value

    if not year or not audit_id:
        raise ValueError(
            "YEAR and AUDIT_ID parameters are required"
        )

    logger.info(
        "Starting raw load for year %s with audit id %s",
        year,
        audit_id,
    )

    try:

        execute_sql_file(
            sql_file="/app/sql/05_load_raw_data.sql",
            profile_name="uk_property_analytics",
            target_name="dev",
            parameters=parameters,
        )

        conn = create_snowflake_connection(
            profile_name="uk_property_analytics",
            target_name="dev",
        )

        cursor = conn.cursor()

        try:
            update_audit_status(
                cursor,
                audit_id,
                "STAGED",
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

        logger.info(
            "Completed raw load successfully for audit id %s",
            audit_id,
        )

    except Exception as e:

        logger.error(
            "Raw load failed for audit id %s: %s",
            audit_id,
            e,
        )

        conn = create_snowflake_connection(
            profile_name="uk_property_analytics",
            target_name="dev",
        )

        cursor = conn.cursor()

        try:
            update_audit_status(
                cursor,
                audit_id,
                "FAILED",
                error_message=str(e),
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

        raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--param",
        action="append",
        default=[],
    )

    args = parser.parse_args()

    main(args.param)