import logging

logger = logging.getLogger(__name__)


def create_audit_record(
    cursor,
    source_name,
    file_name,
    file_type,
    checksum,
    s3_path,
):
    """
    Create a new file ingestion audit record.

    Returns:
        AUDIT_ID
    """

    sql = """
        INSERT INTO CONTROL.FILE_INGEST_AUDIT
        (
            SOURCE_NAME,
            FILE_NAME,
            FILE_TYPE,
            FILE_CHECKSUM,
            S3_PATH,
            STATUS,
            STARTED_TS
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            'LANDED',
            CURRENT_TIMESTAMP()
        )
    """

    cursor.execute(
        sql,
        (
            source_name,
            file_name,
            file_type,
            checksum,
            s3_path,
        ),
    )

    cursor.execute(
        """
        SELECT MAX(AUDIT_ID)
        FROM CONTROL.FILE_INGEST_AUDIT
        WHERE FILE_CHECKSUM = %s
        """,
        (checksum,),
    )

    audit_id = cursor.fetchone()[0]

    logger.info(
        "Created audit record %s for file %s",
        audit_id,
        file_name,
    )

    return audit_id


def update_audit_status(
    cursor,
    audit_id,
    status,
    row_count=None,
    error_message=None,
):
    """
    Update file ingestion audit lifecycle state.
    """

    sql = """
        UPDATE CONTROL.FILE_INGEST_AUDIT
        SET
            STATUS = %s,
            ROW_COUNT = COALESCE(%s, ROW_COUNT),
            ERROR_MESSAGE = COALESCE(%s, ERROR_MESSAGE),
            COMPLETED_TS =
                CASE
                    WHEN %s IN ('LOADED', 'FAILED')
                    THEN CURRENT_TIMESTAMP()
                    ELSE COMPLETED_TS
                END,
            UPDATED_TS = CURRENT_TIMESTAMP()
        WHERE AUDIT_ID = %s
    """

    cursor.execute(
        sql,
        (
            status,
            row_count,
            error_message,
            status,
            audit_id,
        ),
    )

    logger.info(
        "Updated audit record %s to status %s",
        audit_id,
        status,
    )