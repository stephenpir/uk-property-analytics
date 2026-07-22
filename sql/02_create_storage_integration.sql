USE ROLE ACCOUNTADMIN; -- SYSADMIN does not have permission to create storage integrations

USE DATABASE PROPERTY_ANALYTICS;

CREATE OR REPLACE STORAGE INTEGRATION LAND_REGISTRY_S3_INTEGRATION
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::444697930808:role/snowflake-property-analytics-role'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://spir23-uk-residential-property-analytics-dev/landing/land-registry/'
    );

DESC INTEGRATION LAND_REGISTRY_S3_INTEGRATION; -- Check the integration has been created successfully