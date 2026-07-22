-- ============================================================
-- UK Property Analytics Platform
-- Database and Schema Setup
-- ============================================================

-- Step 1: Create database
CREATE DATABASE IF NOT EXISTS PROPERTY_ANALYTICS;

-- Use the database
USE DATABASE PROPERTY_ANALYTICS;


-- Step 2: Create schemas

-- Raw / Bronze layer
-- Contains data loaded from the S3 landing zone with
-- minimal or no transformation.
CREATE SCHEMA IF NOT EXISTS RAW;

-- Silver layer
-- Contains cleaned, standardised and transformed data.
CREATE SCHEMA IF NOT EXISTS SILVER;

-- Gold layer
-- Contains business-ready analytical models.
CREATE SCHEMA IF NOT EXISTS GOLD;

-- Control schema
-- Contains pipeline metadata, ingestion audit information,
-- and operational control tables.
CREATE SCHEMA IF NOT EXISTS CONTROL;