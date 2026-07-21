import requests
import boto3
from botocore.exceptions import NoCredentialsError

def download_csv(url, local_filename):
    """Downloads a CSV file from a given URL."""
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Successfully downloaded {url} to {local_filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def upload_to_s3(local_filename, bucket_name, s3_object_name):
    """Uploads a file to an S3 bucket."""
    s3 = boto3.client('s3', region_name='eu-west-2') # Specify your desired region
    try:
        s3.upload_file(local_filename, bucket_name, s3_object_name)
        print(f"Successfully uploaded {local_filename} to s3://{bucket_name}/{s3_object_name}")
        return True
    except NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
        return False
    except Exception as e:
        print(f"Error uploading {local_filename} to S3: {e}")
        return False

if __name__ == "__main__":
    csv_url = "https://price-paid-data.publicdata.landregistry.gov.uk/pp-2025.csv"
    local_file = "pp-2025.csv"
    s3_bucket = "spir23-uk-residential-property-analytics-dev"
    s3_key = "landing/land-registry/annual/2025/pp-2025.csv"

    if download_csv(csv_url, local_file):
        upload_to_s3(local_file, s3_bucket, s3_key)
