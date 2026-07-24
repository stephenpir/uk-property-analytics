SELECT
    transaction_id,
    date_of_transfer
FROM {{ ref('int_property_transactions') }}
WHERE date_of_transfer > CURRENT_DATE()