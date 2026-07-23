WITH staging AS (

    SELECT *
    FROM {{ ref('stg_land_registry_price_paid') }}

)

SELECT
    transaction_id,

    price,

    date_of_transfer,

    YEAR(date_of_transfer) AS transaction_year,

    MONTH(date_of_transfer) AS transaction_month,

    DATE_TRUNC('MONTH', date_of_transfer) AS transaction_month_start,

    postcode,

    property_type,

    CASE property_type
        WHEN 'D' THEN 'Detached'
        WHEN 'S' THEN 'Semi-Detached'
        WHEN 'T' THEN 'Terraced'
        WHEN 'F' THEN 'Flat or Maisonette'
        WHEN 'O' THEN 'Other'
        ELSE 'Unknown'
    END AS property_type_description,

    old_new,

    CASE old_new
        WHEN 'Y' THEN 'New Build'
        WHEN 'N' THEN 'Established'
        ELSE 'Unknown'
    END AS property_age_category,

    duration,

    CASE duration
        WHEN 'F' THEN 'Freehold'
        WHEN 'L' THEN 'Leasehold'
        ELSE 'Unknown'
    END AS tenure_description,

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

FROM staging