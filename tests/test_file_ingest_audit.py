import logging

from python.utils.snowflake_connection import create_snowflake_connection

from python.utils.file_ingest_audit import create_audit_record


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main():

    conn = create_snowflake_connection(
        profile_name="uk_property_analytics",
        target_name="dev",
)

    try:
        cursor = conn.cursor()

        audit_id = create_audit_record(
            cursor,
            source_name="TEST",
            file_name="test_file.csv",
            file_type="MONTHLY",
            checksum="abc123testchecksum",
            s3_path="landing/test/test_file.csv",
        )

        conn.commit()

        logger.info(
            "Created audit record ID: %s",
            audit_id,
        )

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()