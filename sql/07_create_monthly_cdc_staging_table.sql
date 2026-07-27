USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS LAND_REGISTRY_PRICE_PAID_CDC (
    transaction_id VARCHAR
        COMMENT 'A unique reference number generated automatically for each published sale.',

    price VARCHAR
        COMMENT 'Sale price stated on the transfer deed.',

    date_of_transfer VARCHAR
        COMMENT 'Date when the sale was completed, as stated on the transfer deed.',

    postcode VARCHAR
        COMMENT 'Postcode used at the time of the original transaction.',

    property_type VARCHAR
        COMMENT 'Type of property: D = Detached, S = Semi-Detached, T = Terraced, F = Flats/Maisonettes, O = Other.',

    old_new VARCHAR
        COMMENT 'Indicates whether the property is newly built (Y) or an established residential building (N).',

    duration VARCHAR
        COMMENT 'Property tenure type, including F = Freehold and L = Leasehold.',

    paon VARCHAR
        COMMENT 'Primary Addressable Object Name, typically the house number or name.',

    saon VARCHAR
        COMMENT 'Secondary Addressable Object Name, identifying a separate unit or flat where a property is divided into multiple units.',

    street VARCHAR
        COMMENT 'Street name of the property address.',

    locality VARCHAR
        COMMENT 'Locality associated with the property address.',

    town_city VARCHAR
        COMMENT 'Town or city associated with the property address.',

    district VARCHAR
        COMMENT 'Administrative district associated with the property address.',

    county VARCHAR
        COMMENT 'County associated with the property address.',

    ppd_category_type VARCHAR
        COMMENT 'Price Paid Data category: A = Standard Price Paid entry, B = Additional Price Paid entry.',

    record_status VARCHAR
        COMMENT 'Monthly file record status: A = Addition, C = Change, D = Delete.',

    _source_file VARCHAR
        COMMENT 'S3 object path of the monthly CDC source file from which the record was loaded.',

    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        COMMENT 'Timestamp when the CDC record was loaded into Snowflake.'
);


-- SELECT
--     table_name,
--     column_name,
--     data_type,
--     comment
-- FROM PROPERTY_ANALYTICS.INFORMATION_SCHEMA.COLUMNS
-- WHERE table_schema = 'RAW'
--   AND table_name = 'LAND_REGISTRY_PRICE_PAID_CDC'
-- ORDER BY ordinal_position;