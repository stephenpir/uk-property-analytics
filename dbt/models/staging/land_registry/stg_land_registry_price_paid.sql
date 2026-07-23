WITH source_data AS (

    SELECT *
    FROM {{ source('land_registry', 'land_registry_price_paid') }}

)

SELECT
    transaction_id,

    TRY_TO_NUMBER(price) AS price,

    TRY_TO_DATE(date_of_transfer) AS date_of_transfer,

    UPPER(TRIM(postcode)) AS postcode,

    UPPER(TRIM(property_type)) AS property_type,

    UPPER(TRIM(old_new)) AS old_new,

    UPPER(TRIM(duration)) AS duration,

    NULLIF(TRIM(paon), '') AS paon,

    NULLIF(TRIM(saon), '') AS saon,

    NULLIF(TRIM(street), '') AS street,

    NULLIF(TRIM(locality), '') AS locality,

    NULLIF(TRIM(town_city), '') AS town_city,

    NULLIF(TRIM(district), '') AS district,

    NULLIF(TRIM(county), '') AS county,

    UPPER(TRIM(ppd_category_type)) AS ppd_category_type,

    UPPER(TRIM(record_status)) AS record_status,

    _source_file,

    _loaded_at

FROM source_data