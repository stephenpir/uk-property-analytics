WITH transactions AS (

    SELECT *
    FROM {{ ref('int_property_transactions') }}

),

properties AS (

    SELECT
        postcode,
        paon,
        saon,

        ANY_VALUE(street) AS street,
        ANY_VALUE(locality) AS locality,
        ANY_VALUE(town_city) AS town_city,
        ANY_VALUE(district) AS district,
        ANY_VALUE(county) AS county,

        ANY_VALUE(property_type) AS property_type,
        ANY_VALUE(property_type_description) AS property_type_description,

        ANY_VALUE(property_age_category) AS property_age_category,

        ANY_VALUE(tenure_description) AS tenure_description

    FROM transactions

    GROUP BY
        postcode,
        paon,
        saon

)

SELECT
    {{ dbt_utils.generate_surrogate_key([
        'postcode',
        'paon',
        'saon'
    ]) }} AS property_key,

    postcode,
    paon,
    saon,

    street,
    locality,
    town_city,
    district,
    county,

    property_type,
    property_type_description,

    property_age_category,
    tenure_description

FROM properties