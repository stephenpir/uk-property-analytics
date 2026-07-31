USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA CONTROL;

CREATE TABLE IF NOT EXISTS CONTROL.FILE_INGEST_AUDIT
(
    AUDIT_ID NUMBER AUTOINCREMENT
        COMMENT 'Surrogate key uniquely identifying a file ingestion event',

    SOURCE_NAME VARCHAR(100)
        COMMENT 'Source system identifier, for example LAND_REGISTRY',

    FILE_NAME VARCHAR(500)
        COMMENT 'Immutable name of the processed file. For versioned files this should represent the archived filename',

    FILE_TYPE VARCHAR(50)
        COMMENT 'Type of source file ingestion, for example MONTHLY or ANNUAL',

    FILE_CHECKSUM VARCHAR(64)
        COMMENT 'SHA-256 checksum of the processed file used to identify duplicate file content',

    S3_PATH VARCHAR(1000)
        COMMENT 'S3 object path of the processed file version',

    STATUS VARCHAR(50)
        COMMENT 'Current ingestion lifecycle state: LANDED, STAGED, LOADED, or FAILED',

    ROW_COUNT NUMBER
        COMMENT 'Number of rows successfully processed from the file',

    ERROR_MESSAGE VARCHAR(4000)
        COMMENT 'Error details captured when ingestion fails',

    STARTED_TS TIMESTAMP_NTZ
        COMMENT 'Timestamp when ingestion processing started',

    COMPLETED_TS TIMESTAMP_NTZ
        COMMENT 'Timestamp when ingestion processing completed',

    UPDATED_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        COMMENT 'Timestamp when this audit record was last updated'
)
COMMENT = 'Generic file-level ingestion audit table tracking source files through the ingestion lifecycle from S3 landing to Snowflake loading';