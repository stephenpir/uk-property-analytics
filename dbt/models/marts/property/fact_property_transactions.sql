WITH transactions AS (

    SELECT *
    FROM {{ ref('int_property_transactions') }}

),

property_dimension AS (

    SELECT
        property_key,
        postcode,
        paon,
        saon

    FROM {{ ref('dim_property') }}

),

date_dimension AS (

    SELECT
        date_day

    FROM {{ ref('dim_date') }}

)

SELECT
    transactions.transaction_id,

    property_dimension.property_key,

    transactions.date_of_transfer,

    transactions.transaction_year,

    transactions.transaction_month,

    transactions.transaction_month_start,

    transactions.price,

    transactions.ppd_category_type,

    transactions.record_status,

    transactions._source_file,

    transactions._loaded_at

FROM transactions

LEFT JOIN property_dimension

    ON transactions.postcode IS NOT DISTINCT FROM property_dimension.postcode

    AND transactions.paon IS NOT DISTINCT FROM property_dimension.paon

    AND transactions.saon IS NOT DISTINCT FROM property_dimension.saon

LEFT JOIN date_dimension

    ON transactions.date_of_transfer = date_dimension.date_day