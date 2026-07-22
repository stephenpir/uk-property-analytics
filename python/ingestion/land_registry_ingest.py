import logging
import os
import sys
import tempfile

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv


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
            "AWS credentials not found. Please configure your AWS credentials."
        )
        return False

    except (BotoCoreError, ClientError) as e:
        logger.error("AWS error while uploading file: %s", e)
        return False

    except OSError as e:
        logger.error("Error accessing local file %s: %s", local_filename, e)
        return False


def main():
    """Main ingestion process."""

    csv_url = os.getenv("CSV_URL")
    s3_bucket = os.getenv("S3_BUCKET")
    s3_key = os.getenv("S3_KEY")
    aws_region = os.getenv("AWS_REGION")

    # Validate required configuration
    required_config = {
        "CSV_URL": csv_url,
        "S3_BUCKET": s3_bucket,
        "S3_KEY": s3_key,
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

    # Create a temporary file that is automatically removed
    # when the context manager exits.
    with tempfile.TemporaryDirectory() as temp_directory:

        local_file = os.path.join(
            temp_directory,
            "pp-2025.csv",
        )

        # Step 1: Download
        if not download_csv(csv_url, local_file):
            logger.error("Download failed. Ingestion process aborted.")
            return 1

        # Step 2: Upload to S3
        if not upload_to_s3(
            local_file,
            s3_bucket,
            s3_key,
            aws_region,
        ):
            logger.error("S3 upload failed. Ingestion process aborted.")
            return 1

    logger.info("Land Registry ingestion completed successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
