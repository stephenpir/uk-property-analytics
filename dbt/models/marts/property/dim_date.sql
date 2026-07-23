WITH date_range AS (

    SELECT
        MIN(date_of_transfer) AS min_date,
        MAX(date_of_transfer) AS max_date

    FROM {{ ref('int_property_transactions') }}

),

date_spine AS (

    SELECT
        DATEADD(
            DAY,
            ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1,
            date_range.min_date
        ) AS date_day

    FROM date_range

    CROSS JOIN TABLE(
        GENERATOR(ROWCOUNT => 20000)
    )

)

SELECT
    date_day,

    YEAR(date_day) AS year,

    QUARTER(date_day) AS quarter,

    MONTH(date_day) AS month,

    MONTHNAME(date_day) AS month_name,

    WEEK(date_day) AS week,

    DAY(date_day) AS day,

    DAYOFWEEK(date_day) AS day_of_week,

    DAYNAME(date_day) AS day_name

FROM date_spine

WHERE date_day <= (
    SELECT max_date
    FROM date_range
)