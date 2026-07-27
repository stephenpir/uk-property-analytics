from datetime import datetime, timezone

from python.utils.snowflake_connection import create_snowflake_connection


def get_successful_file_by_checksum(
    profile_name: str,
    target_name: str,
    file_type: str,
    file_checksum: str,
) -> bool:
    connection = create_snowflake_connection(
        profile_name=profile_name,
        target_name=target_name,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_FILE_INGESTION_AUDIT
                WHERE FILE_TYPE = %s
                  AND FILE_CHECKSUM = %s
                  AND PROCESSING_STATE = 'SUCCESS'
                LIMIT 1
                """,
                (file_type, file_checksum),
            )

            return cursor.fetchone() is not None

    finally:
        connection.close()


def create_audit_record(
    profile_name: str,
    target_name: str,
    file_name: str,
    file_type: str,
    source_url: str,
    source_year: int,
    source_month: int | None,
    file_checksum: str,
    file_size_bytes: int,
    s3_bucket: str,
    s3_key: str,
) -> int:

def mark_audit_success(
    profile_name: str,
    target_name: str,
    audit_id: int,
    source_row_count: int,
    rows_inserted: int,
    rows_updated: int,
    rows_deleted: int,
) -> None:

    connection = create_snowflake_connection(
        profile_name=profile_name,
        target_name=target_name,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_FILE_INGESTION_AUDIT
                SET
                    PROCESSING_STATE = 'SUCCESS',
                    PROCESSING_COMPLETED_AT = CURRENT_TIMESTAMP(),
                    SOURCE_ROW_COUNT = %s,
                    ROWS_INSERTED = %s,
                    ROWS_UPDATED = %s,
                    ROWS_DELETED = %s,
                    ERROR_MESSAGE = NULL
                WHERE FILE_INGESTION_ID = %s
                """,
                (
                    source_row_count,
                    rows_inserted,
                    rows_updated,
                    rows_deleted,
                    audit_id,
                ),
            )

            connection.commit()

    finally:
        connection.close()


def mark_audit_failed(
    profile_name: str,
    target_name: str,
    audit_id: int,
    error_message: str,
) -> None:

    connection = create_snowflake_connection(
        profile_name=profile_name,
        target_name=target_name,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_FILE_INGESTION_AUDIT
                SET
                    PROCESSING_STATE = 'FAILED',
                    PROCESSING_COMPLETED_AT = CURRENT_TIMESTAMP(),
                    ERROR_MESSAGE = %s
                WHERE FILE_INGESTION_ID = %s
                """,
                (
                    error_message[:5000],
                    audit_id,
                ),
            )

            connection.commit()

    finally:
        connection.close()

    connection = create_snowflake_connection(
        profile_name=profile_name,
        target_name=target_name,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_FILE_INGESTION_AUDIT (
                    FILE_NAME,
                    FILE_TYPE,
                    SOURCE_URL,
                    SOURCE_YEAR,
                    SOURCE_MONTH,
                    FILE_CHECKSUM,
                    FILE_SIZE_BYTES,
                    S3_BUCKET,
                    S3_KEY,
                    PROCESSING_STATE,
                    PROCESSING_STARTED_AT
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, 'STARTED', %s
                )
                """,
                (
                    file_name,
                    file_type,
                    source_url,
                    source_year,
                    source_month,
                    file_checksum,
                    file_size_bytes,
                    s3_bucket,
                    s3_key,
                    datetime.now(timezone.utc),
                ),
            )

            cursor.execute(
                """
                SELECT MAX(FILE_INGESTION_ID)
                FROM PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_FILE_INGESTION_AUDIT
                WHERE FILE_TYPE = %s
                  AND FILE_CHECKSUM = %s
                """,
                (file_type, file_checksum),
            )

            audit_id = cursor.fetchone()[0]

            connection.commit()

            return audit_id

    finally:
        connection.close()