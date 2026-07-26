USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;


-- Temporary staging table for the annual Land Registry file.
-- This is recreated for each execution and disappears when
-- the Snowflake session ends.
CREATE OR REPLACE TEMPORARY TABLE LAND_REGISTRY_PRICE_PAID_STAGE
LIKE LAND_REGISTRY_PRICE_PAID;


-- Load the annual source file into the temporary staging table.
COPY INTO LAND_REGISTRY_PRICE_PAID_STAGE (
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
PATTERN = '.*annual/{{ YEAR }}/pp-{{ YEAR }}\.csv'
ON_ERROR = 'ABORT_STATEMENT';


-- Merge staged records into the raw table.
-- TRANSACTION_ID is the unique business key.
-- Existing records are left unchanged.
-- New records are inserted.
MERGE INTO LAND_REGISTRY_PRICE_PAID AS target
USING LAND_REGISTRY_PRICE_PAID_STAGE AS source
    ON target.transaction_id = source.transaction_id

WHEN NOT MATCHED THEN
    INSERT (
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
        _source_file,
        _loaded_at
    )
    VALUES (
        source.transaction_id,
        source.price,
        source.date_of_transfer,
        source.postcode,
        source.property_type,
        source.old_new,
        source.duration,
        source.paon,
        source.saon,
        source.street,
        source.locality,
        source.town_city,
        source.district,
        source.county,
        source.ppd_category_type,
        source.record_status,
        source._source_file,
        CURRENT_TIMESTAMP()
    );