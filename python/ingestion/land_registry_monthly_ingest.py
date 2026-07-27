import hashlib
import logging
import os
import sys
import tempfile
from pathlib import Path

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv

from python.utils.snowflake_ingestion_audit import (
    create_audit_record,
    get_successful_file_by_checksum,
    mark_audit_failed,
)


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


MONTHLY_FILE_NAME = "pp-monthly-update-new-version.csv"

MONTHLY_SOURCE_URL = (
    "https://price-paid-data.publicdata.landregistry.gov.uk/"
    "pp-monthly-update-new-version.csv"
)


def download_csv(url, local_filename):
    """Download a CSV file from a given URL."""
    try:
        logger.info("Starting download from %s", url)

        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()

            with open(local_filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        logger.info("Successfully downloaded file to %s", local_filename)
        return True

    except requests.exceptions.RequestException as exc:
        logger.error("Error downloading %s: %s", url, exc)
        return False

    except OSError as exc:
        logger.error(
            "Error writing downloaded file %s: %s",
            local_filename,
            exc,
        )
        return False


def upload_to_s3(local_filename, bucket_name, s3_object_name, region):
    """Upload a file to an S3 bucket."""
    try:
        logger.info(
            "Uploading %s to s3://%s/%s",
            local_filename,
            bucket_name,
            s3_object_name,
        )

        s3 = boto3.client("s3", region_name=region)

        s3.upload_file(
            local_filename,
            bucket_name,
            s3_object_name,
        )

        logger.info(
            "Successfully uploaded file to s3://%s/%s",
            bucket_name,
            s3_object_name,
        )

        return True

    except NoCredentialsError:
        logger.error(
            "AWS credentials not found. "
            "Please configure your AWS credentials."
        )
        return False

    except (BotoCoreError, ClientError) as exc:
        logger.error("AWS error while uploading file: %s", exc)
        return False

    except OSError as exc:
        logger.error(
            "Error accessing local file %s: %s",
            local_filename,
            exc,
        )
        return False


def calculate_file_checksum(local_filename):
    """Calculate SHA-256 checksum for a local file."""
    sha256 = hashlib.sha256()

    with open(local_filename, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def main():
    """Main monthly CDC ingestion process."""

    s3_bucket = os.getenv("S3_BUCKET")
    aws_region = os.getenv("AWS_REGION")
    snowflake_profile = os.getenv(
        "SNOWFLAKE_PROFILE",
        "uk_property_analytics",
    )
    snowflake_target = os.getenv(
        "SNOWFLAKE_TARGET",
        "dev",
    )

    required_config = {
        "S3_BUCKET": s3_bucket,
        "AWS_REGION": aws_region,
    }

    missing_config = [
        name
        for name, value in required_config.items()
        if not value
    ]

    if missing_config:
        logger.error(
            "Missing required environment variables: %s",
            ", ".join(missing_config),
        )
        return 1

    logger.info("Starting Land Registry monthly CDC ingestion")

    with tempfile.TemporaryDirectory() as temp_directory:

        local_file = os.path.join(
            temp_directory,
            MONTHLY_FILE_NAME,
        )

        # Step 1: Download
        if not download_csv(
            MONTHLY_SOURCE_URL,
            local_file,
        ):
            logger.error(
                "Monthly file download failed. "
                "Ingestion aborted."
            )
            return 1

        # Step 2: Calculate checksum
        file_checksum = calculate_file_checksum(local_file)
        file_size_bytes = Path(local_file).stat().st_size

        logger.info(
            "Monthly file checksum: %s",
            file_checksum,
        )

        logger.info(
            "Monthly file size: %s bytes",
            file_size_bytes,
        )

        # Step 3: Check audit table for successful processing
        if get_successful_file_by_checksum(
            profile_name=snowflake_profile,
            target_name=snowflake_target,
            file_type="MONTHLY",
            file_checksum=file_checksum,
        ):
            logger.info(
                "Monthly file has already been successfully "
                "processed. Skipping."
            )
            return 0

        # Step 4: S3 key based on checksum
        s3_key = (
            "landing/land-registry/monthly/"
            f"{file_checksum}/{MONTHLY_FILE_NAME}"
        )

        # Step 5: Create STARTED audit record
        audit_id = create_audit_record(
            profile_name=snowflake_profile,
            target_name=snowflake_target,
            file_name=MONTHLY_FILE_NAME,
            file_type="MONTHLY",
            source_url=MONTHLY_SOURCE_URL,
            source_year=None,
            source_month=None,
            file_checksum=file_checksum,
            file_size_bytes=file_size_bytes,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
        )

        try:
            # Step 6: Upload to S3
            if not upload_to_s3(
                local_file,
                s3_bucket,
                s3_key,
                aws_region,
            ):
                raise RuntimeError("S3 upload failed.")

        except Exception as exc:
            logger.error(
                "Monthly ingestion failed: %s",
                exc,
            )

            mark_audit_failed(
                profile_name=snowflake_profile,
                target_name=snowflake_target,
                audit_id=audit_id,
                error_message=str(exc),
            )

            return 1

    logger.info(
        "Monthly file successfully uploaded to S3. "
        "Audit ID: %s",
        audit_id,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())