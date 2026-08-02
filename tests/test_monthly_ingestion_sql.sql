/*
===============================================================================
MONTHLY LAND REGISTRY MERGE TEST
===============================================================================

Purpose
-------
Manually validate the monthly incremental merge process.

The monthly Price Paid file contains:

    A = Addition
    C = Change
    D = Delete

This test verifies that the MERGE behaves correctly for each record type.

Process
-------
1. Backup the target table.
2. Load the monthly file into LAND_REGISTRY_PRICE_PAID_STAGE.
3. Run the validation queries BEFORE the merge.
4. Execute the monthly MERGE.
5. Run the validation queries AFTER the merge.
6. Restore the target table if required.

===============================================================================
*/

USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;

/*
===============================================================================
STEP 1
Create backup

Purpose
-------
Create a rollback point before testing.

Restore using the statement at the end of this script.
===============================================================================
*/

CREATE OR REPLACE TABLE RAW.LAND_REGISTRY_PRICE_PAID_BACKUP
CLONE RAW.LAND_REGISTRY_PRICE_PAID;


/*
===============================================================================
STEP 2
Run the monthly load script until the COPY INTO has populated

    LAND_REGISTRY_PRICE_PAID_STAGE

Do NOT execute the MERGE yet.

===============================================================================
*/


COPY INTO LAND_REGISTRY_PRICE_PAID_STAGE (
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
FROM (
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        $10,
        $11,
        $12,
        $13,
        $14,
        $15,
        $16,
        METADATA$FILENAME
    FROM @LAND_REGISTRY_STAGE
)
FILE_FORMAT = (
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 0
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('', 'NULL')
    EMPTY_FIELD_AS_NULL = TRUE
)
PATTERN = '.*monthly/archive/2026/20260801_pp-monthly-update-new-version_bc3820652783e81e83b3635092493d7e426f2282349cee5c91b42557b7af4811.csv'
ON_ERROR = 'ABORT_STATEMENT';

/*
===============================================================================
STEP 3 BEFORE MERGE VALIDATION
These queries record the expected behaviour of the MERGE.
===============================================================================
*/
SELECT
    record_status,
    COUNT(*) AS record_count
FROM LAND_REGISTRY_PRICE_PAID_STAGE
GROUP BY record_status
ORDER BY record_status;
-- RECORD_STATUS	RECORD_COUNT
-- A	85791
-- C	3057
-- D	1439

SELECT COUNT(*) AS rows_before_merge
FROM LAND_REGISTRY_PRICE_PAID;
-- ROWS_BEFORE_MERGE
-- 907694

/*
----------------------------------------------------------------------------
A - ADDITIONS
Rows in the source that do not already exist in the target.
Record this value.
Expected AFTER merge:
0
----------------------------------------------------------------------------
*/

-- SELECT COUNT(*) AS additions_before
-- FROM LAND_REGISTRY_PRICE_PAID_STAGE source
-- LEFT JOIN LAND_REGISTRY_PRICE_PAID target
--     ON target.transaction_id = source.transaction_id
-- WHERE source.record_status = 'A'
-- AND target.transaction_id IS NULL;

SELECT COUNT(*) AS additions_before
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
WHERE source.record_status = 'A';
-- ADDITIONS_BEFORE
-- 85791

SELECT COUNT(*) AS additions_before
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
LEFT JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'A'
AND target.transaction_id IS NULL;
-- ADDITIONS_BEFORE
-- 85791

SELECT COUNT(*) AS additions_before
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
INNER JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'A';
-- ADDITIONS_BEFORE
-- 0

/*
----------------------------------------------------------------------------
C - CHANGES

Rows which already exist in the target and are about to be updated.

Record this value.

Expected AFTER merge:
Same count should now have target.record_status = 'C'
----------------------------------------------------------------------------
*/

SELECT COUNT(*) AS changes_before
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'C';
-- CHANGES_BEFORE
-- 801

/*
----------------------------------------------------------------------------
D - DELETES

Rows currently existing in the target which should be deleted.

Record this value.

Expected AFTER merge:
0
----------------------------------------------------------------------------
*/

SELECT COUNT(*) AS deletes_before
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'D';
-- DELETES_BEFORE
-- 850

/*
===============================================================================
STEP 4

Execute the MERGE statement.

===============================================================================
*/

-- number of rows inserted	number of rows updated	number of rows deleted
-- 85791	801	850

/*
===============================================================================
STEP 5

AFTER MERGE VALIDATION

===============================================================================
*/



/*
----------------------------------------------------------------------------
A - ADDITIONS

The same query should now return zero because all additions
should now exist in the target.
----------------------------------------------------------------------------
*/

SELECT COUNT(*) AS additions_after
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
LEFT JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'A'
AND target.transaction_id IS NULL;
-- ADDITIONS_AFTER
-- 0
/*
Expected:

0
*/



/*
----------------------------------------------------------------------------
C - CHANGES

Every source C record identified before the merge should now
have record_status = 'C' in the target.

Expected:

changes_after = changes_before
----------------------------------------------------------------------------
*/

SELECT COUNT(*) AS changes_after
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'C'
AND target.record_status = 'C';
-- CHANGES_AFTER
-- 801


/*
----------------------------------------------------------------------------
D - DELETES

The same join used before the merge should now return zero
because the rows should have been deleted.

Expected:

0
----------------------------------------------------------------------------
*/

SELECT COUNT(*) AS deletes_after
FROM LAND_REGISTRY_PRICE_PAID_STAGE source
JOIN LAND_REGISTRY_PRICE_PAID target
    ON target.transaction_id = source.transaction_id
WHERE source.record_status = 'D';
-- DELETES_AFTER
-- 0

/*
===============================================================================
STEP 6

ROLLBACK

Run only if you want to restore the dataset to its original state.

===============================================================================
*/

CREATE OR REPLACE TABLE RAW.LAND_REGISTRY_PRICE_PAID
CLONE RAW.LAND_REGISTRY_PRICE_PAID_BACKUP;