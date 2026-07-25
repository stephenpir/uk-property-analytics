USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;

COPY INTO LAND_REGISTRY_PRICE_PAID (
    transaction_id,
    price,
    date_of_transfer,
    postcode,
    property_type,
    old_new,
    duration,
    paon,
    saon,
    street,
    locality,
    town_city,
    district,
    county,
    ppd_category_type,
    record_status,
    _source_file
)
FROM (
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        $10,
        $11,
        $12,
        $13,
        $14,
        $15,
        $16,
        METADATA$FILENAME
    FROM @LAND_REGISTRY_STAGE
)
FILE_FORMAT = (
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 0
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('', 'NULL')
    EMPTY_FIELD_AS_NULL = TRUE
)
PATTERN = '.*annual/2025/pp-2025\.csv'
ON_ERROR = 'ABORT_STATEMENT';


-- SELECT COUNT(*) AS row_count
-- FROM LAND_REGISTRY_PRICE_PAID; -- Check the number of rows loaded into the LAND_REGISTRY_PRICE_PAID table

-- SELECT *
-- FROM LAND_REGISTRY_PRICE_PAID
-- LIMIT 10; -- Check the first 10 rows of the LAND_REGISTRY_PRICE_PAID table to verify the data has been loaded correctly

-- SELECT
--     _source_file,
--     COUNT(*) AS row_count
-- FROM LAND_REGISTRY_PRICE_PAID
-- GROUP BY _source_file; -- Verify the source file metadata has been captured correctly for each record loaded into the LAND_REGISTRY_PRICE_PAID table