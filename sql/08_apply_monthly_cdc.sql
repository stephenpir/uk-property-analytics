USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;

BEGIN TRANSACTION;

-- Apply additions and changes
MERGE INTO LAND_REGISTRY_PRICE_PAID AS target
USING (
    SELECT
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
    FROM LAND_REGISTRY_PRICE_PAID_CDC
    WHERE record_status IN ('A', 'C')
) AS source
ON target.transaction_id = source.transaction_id

WHEN MATCHED
    AND source.record_status = 'C'
THEN UPDATE SET
    target.price = source.price,
    target.date_of_transfer = source.date_of_transfer,
    target.postcode = source.postcode,
    target.property_type = source.property_type,
    target.old_new = source.old_new,
    target.duration = source.duration,
    target.paon = source.paon,
    target.saon = source.saon,
    target.street = source.street,
    target.locality = source.locality,
    target.town_city = source.town_city,
    target.district = source.district,
    target.county = source.county,
    target.ppd_category_type = source.ppd_category_type,
    target.record_status = source.record_status,
    target._source_file = source._source_file,
    target._loaded_at = source._loaded_at

WHEN NOT MATCHED
    AND source.record_status = 'A'
THEN INSERT (
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
    source._loaded_at
);


-- Apply deletions
DELETE FROM LAND_REGISTRY_PRICE_PAID AS target
USING LAND_REGISTRY_PRICE_PAID_CDC AS source
WHERE target.transaction_id = source.transaction_id
  AND source.record_status = 'D';


COMMIT;