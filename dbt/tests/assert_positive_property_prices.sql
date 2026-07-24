SELECT
    transaction_id,
    price
FROM {{ ref('int_property_transactions') }}
WHERE price <= 0