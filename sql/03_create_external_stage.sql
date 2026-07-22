USE DATABASE PROPERTY_ANALYTICS;
USE SCHEMA RAW;

CREATE STAGE IF NOT EXISTS LAND_REGISTRY_STAGE
    URL = 's3://spir23-uk-residential-property-analytics-dev/landing/land-registry/'
    STORAGE_INTEGRATION = LAND_REGISTRY_S3_INTEGRATION
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_DELIMITER = ','
        SKIP_HEADER = 1
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF = ('', 'NULL')
        EMPTY_FIELD_AS_NULL = TRUE
    );

LIST @LAND_REGISTRY_STAGE; -- List the files in the stage to verify that it has been created successfully