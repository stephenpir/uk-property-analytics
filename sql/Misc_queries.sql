SELECT CURRENT_ACCOUNT();

SELECT *
FROM PROPERTY_ANALYTICS.RAW.STG_LAND_REGISTRY_PRICE_PAID
LIMIT 10;

DESCRIBE view PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID;
-- DROP VIEW IF EXISTS PROPERTY_ANALYTICS.RAW.STG_LAND_REGISTRY_PRICE_PAID;


SELECT COUNT(*) FROM PROPERTY_ANALYTICS.MART.DIM_DATE;

SELECT COUNT(*) FROM PROPERTY_ANALYTICS.MART.DIM_PROPERTY;

SELECT COUNT(*) FROM PROPERTY_ANALYTICS.MART.FACT_PROPERTY_TRANSACTIONS;


SELECT COUNT(*) AS unmatched_properties
FROM PROPERTY_ANALYTICS.MART.FACT_PROPERTY_TRANSACTIONS
WHERE property_key IS NULL;


SELECT
    COUNT(*) AS unmatched_rows,
    COUNT_IF(t.postcode IS NULL) AS null_postcodes,
    COUNT_IF(t.paon IS NULL) AS null_paon,
    COUNT_IF(t.saon IS NULL) AS null_saon
FROM PROPERTY_ANALYTICS.INTERMEDIATE.INT_PROPERTY_TRANSACTIONS t
LEFT JOIN PROPERTY_ANALYTICS.MART.DIM_PROPERTY p
    ON t.postcode IS NOT DISTINCT FROM p.postcode
    AND t.paon IS NOT DISTINCT FROM p.paon
    AND t.saon IS NOT DISTINCT FROM p.saon
WHERE p.property_key IS NULL;

SELECT
    t.postcode,
    t.paon,
    t.saon,
    COUNT(*) AS transaction_count
FROM PROPERTY_ANALYTICS.INTERMEDIATE.INT_PROPERTY_TRANSACTIONS t
LEFT JOIN PROPERTY_ANALYTICS.MART.DIM_PROPERTY p
    ON t.postcode IS NOT DISTINCT FROM p.postcode
    AND t.paon IS NOT DISTINCT FROM p.paon
    AND t.saon IS NOT DISTINCT FROM p.saon
WHERE p.property_key IS NULL
GROUP BY
    t.postcode,
    t.paon,
    t.saon
ORDER BY transaction_count DESC
LIMIT 20;


SELECT
    transaction_id,
    COUNT(*) AS transaction_count
FROM PROPERTY_ANALYTICS.INTERMEDIATE.INT_PROPERTY_TRANSACTIONS
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY transaction_count DESC
LIMIT 20;

SELECT
    transaction_id,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT price) AS distinct_prices,
    COUNT(DISTINCT date_of_transfer) AS distinct_dates,
    COUNT(DISTINCT postcode) AS distinct_postcodes
FROM PROPERTY_ANALYTICS.INTERMEDIATE.INT_PROPERTY_TRANSACTIONS
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY transaction_count DESC
LIMIT 20;

SELECT COUNT(*) FROM PROPERTY_ANALYTICS.MART.DIM_DATE;
-- truncate table PROPERTY_ANALYTICS.MART.DIM_DATE;

SELECT COUNT(*) FROM PROPERTY_ANALYTICS.MART.DIM_PROPERTY;
-- truncate table PROPERTY_ANALYTICS.MART.DIM_PROPERTY;

SELECT COUNT(*) FROM PROPERTY_ANALYTICS.MART.FACT_PROPERTY_TRANSACTIONS;
-- truncate table PROPERTY_ANALYTICS.MART.FACT_PROPERTY_TRANSACTIONS;

SELECT *
FROM PROPERTY_ANALYTICS.MART.FACT_PROPERTY_TRANSACTIONS
LIMIT 10;

select * 
from PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID
LIMIT 10;
-- truncate table PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID;

SELECT COUNT(*) FROM PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID;

DESC TABLE PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID;

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT TRANSACTION_ID) AS distinct_transaction_ids
FROM PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID;

SELECT *
FROM PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID
LIMIT 3;


USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;

INSERT INTO LAND_REGISTRY_PRICE_PAID_CDC (
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
VALUES
(
    '{50D10B84-0863-B8D0-E063-4704A8C08D98}',
    '350000',
    '2025-10-08 00:00',
    'HR4 7PR',
    'D',
    'N',
    'F',
    'WONDERLAND COTTAGE',
    '',
    'BREINTON',
    'HEREFORD',
    'HEREFORDSHIRE',
    'HEREFORDSHIRE',
    'HEREFORDSHIRE',
    'A',
    'C',
    'test/monthly-cdc-test.csv'
),
(
    '{50D10B83-B1E3-B8D0-E063-4704A8C08D98}',
    '335000',
    '2025-07-02 00:00',
    'N17 0LU',
    'F',
    'N',
    'L',
    '27B',
    '',
    'BARONET ROAD',
    '',
    'LONDON',
    'HARINGEY',
    'GREATER LONDON',
    'A',
    'D',
    'test/monthly-cdc-test.csv'
),
(
    '{TEST-CDC-ADD-001}',
    '425000',
    '2025-11-01 00:00',
    'HA9 6DN',
    'F',
    'N',
    'L',
    '999',
    '',
    'TEST ROAD',
    '',
    'WEMBLEY',
    'BRENT',
    'GREATER LONDON',
    'A',
    'A',
    'test/monthly-cdc-test.csv'
);


SELECT
    transaction_id,
    price,
    record_status,
    _source_file
FROM LAND_REGISTRY_PRICE_PAID_CDC
WHERE _source_file = 'test/monthly-cdc-test.csv';

SELECT
    transaction_id,
    price,
    record_status,
    _source_file
FROM LAND_REGISTRY_PRICE_PAID
WHERE transaction_id IN (
    '{50D10B84-0863-B8D0-E063-4704A8C08D98}',
    '{50D10B83-B1E3-B8D0-E063-4704A8C08D98}',
    '{TEST-CDC-ADD-001}'
);

DELETE FROM PROPERTY_ANALYTICS.RAW.LAND_REGISTRY_PRICE_PAID_CDC
WHERE _source_file = 'test/monthly-cdc-test.csv';