import logging
import os
import sys
import tempfile
import hashlib
import pickle

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv
from datetime import datetime

from python.utils.snowflake_connection import create_snowflake_connection
from python.utils.file_ingest_audit import create_audit_record, update_audit_status

import json # Not used in the end but perhaps in the future if we want to return more than just the archive filename.

# Load environment variables from .env
load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


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

    except requests.exceptions.RequestException as e:
        logger.error("Error downloading %s: %s", url, e)
        return False

    except OSError as e:
        logger.error("Error writing downloaded file %s: %s", local_filename, e)
        return False
    
def calculate_checksum(filename):
    """Calculate SHA-256 checksum for a file."""
    sha256 = hashlib.sha256()

    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

def upload_to_s3(
    local_filename,
    bucket_name,
    s3_object_name,
    region,
    checksum,
):
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
            ExtraArgs={
                "Metadata": {
                    "sha256": checksum,
        }
    },
        )

        logger.info(
            "Successfully uploaded file to s3://%s/%s",
            bucket_name,
            s3_object_name,
        )

        return True

    except NoCredentialsError:
        logger.error(
            "AWS credentials not found. Please configure your AWS credentials."
        )
        return False

    except (BotoCoreError, ClientError) as e:
        logger.error("AWS error while uploading file: %s", e)
        return False

    except OSError as e:
        logger.error("Error accessing local file %s: %s", local_filename, e)
        return False

def get_existing_checksum(bucket_name, s3_object_name, region):
    """Get checksum stored in S3 object metadata."""

    try:
        s3 = boto3.client("s3", region_name=region)

        response = s3.head_object(
            Bucket=bucket_name,
            Key=s3_object_name,
        )

        return response.get("Metadata", {}).get("sha256")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")

        if error_code in ("404", "NoSuchKey", "NotFound"):
            return None

        raise

def create_archive_key(filename, checksum):
    """Create archive S3 key for processed file."""

    processed_date = datetime.utcnow().strftime("%Y%m%d")
    year = datetime.utcnow().strftime("%Y")

    return (
        f"landing/land-registry/monthly/archive/{year}/"
        f"{processed_date}_{filename}_{checksum}.csv"
    )

def main():
    """Main ingestion process."""

    s3_bucket = os.getenv("S3_BUCKET")
    aws_region = os.getenv("AWS_REGION")

    csv_url = (
        "https://price-paid-data.publicdata.landregistry.gov.uk/"
        "pp-monthly-update-new-version.csv"
    )

    current_key = (
        "landing/land-registry/monthly/current/"
        "pp-monthly-update-new-version.csv"
    )

    # Validate required configuration
    required_config = {
        "S3_BUCKET": s3_bucket,
        "AWS_REGION": aws_region,
    }

    missing_config = [
        name for name, value in required_config.items() if not value
    ]

    if missing_config:
        logger.error(
            "Missing required environment variables: %s",
            ", ".join(missing_config),
        )
        return 1

    logger.info("Starting Land Registry ingestion process")

    conn = create_snowflake_connection(
        profile_name="uk_property_analytics",
        target_name="dev",
    )

    cursor = conn.cursor()

    # Create a temporary file that is automatically removed
    # when the context manager exits.
    with tempfile.TemporaryDirectory() as temp_directory:

        local_file = os.path.join(
            temp_directory,
            "pp-monthly-update-new-version.csv",
        )

        # Step 1: Download
        if not download_csv(csv_url, local_file):
            logger.error("Download failed. Ingestion process aborted.")
            return 1

        checksum = calculate_checksum(local_file)

        logger.info(
            "Calculated SHA-256 checksum: %s",
            checksum,
        )

        existing_checksum = get_existing_checksum(
            s3_bucket,
            current_key,
            aws_region,
        )

        if existing_checksum == checksum:
            logger.info(
                "File checksum matches current S3 file. Skipping ingestion."
            )
            return None

        # Step 2: Upload archive copy

        archive_key = create_archive_key(
            "pp-monthly-update-new-version",
            checksum,
        )
        
        archive_filename = os.path.basename(archive_key)

        if not upload_to_s3(
            local_file,
            s3_bucket,
            archive_key,
            aws_region,
            checksum,
        ):
            logger.error("Archive upload failed. Ingestion process aborted.")
            return 1


        # Step 3: Upload current copy

        if not upload_to_s3(
            local_file,
            s3_bucket,
            current_key,
            aws_region,
            checksum,
        ):
            logger.error("Current upload failed. Ingestion process aborted.")
            return 1

        # Step 4: Create ingestion audit record

        try:
            audit_id = create_audit_record(
                cursor,
                source_name="LAND_REGISTRY",
                file_name=archive_filename,
                file_type="MONTHLY",
                checksum=checksum,
                s3_path=archive_key,
            )

            conn.commit()

        except Exception as e:
            conn.rollback()

            logger.error(
                "Failed creating audit record: %s",
                e,
            )

            return 1

        logger.info(
            "Created LAND_REGISTRY audit record %s",
            audit_id,
        )

    cursor.close()
    conn.close()        
    logger.info("Land Registry ingestion completed successfully")

    return {"archive_file_name": archive_filename, "audit_id": audit_id} # The use of a dictionary allows for future extensibility if more return values are needed but is currently redundant since only the archive filename is being returned and explicitly converted to a string in the print statement.

if __name__ == "__main__":
    result = main()
    # print(f"{result['archive_file_name']}")  # Add this line
    # print(json.dumps(result))

    with open("/tmp/return.pkl", "wb") as f:
        # json.dump(result, f)
        pickle.dump(result, f)
