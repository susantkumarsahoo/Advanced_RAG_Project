import boto3
import os
from dotenv import load_dotenv

# Load your credentials
load_dotenv()

def ingest_from_s3_to_local(bucket_name, s3_prefix, local_folder):
    """
    Downloads all files from an S3 folder (prefix) to your local PC.
    """
    # Initialize S3 Client
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    # Create local folder if it doesn't exist
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    try:
        # List all objects in the S3 prefix
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

        print(f"--- Starting Ingestion from s3://{bucket_name}/{s3_prefix} ---")
        
        file_count = 0
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3_key = obj['Key']
                    
                    # Skip if the key is just a folder name (ends with /)
                    if s3_key.endswith('/'):
                        continue
                    
                    # Create local file path
                    # This removes the S3 prefix from the local filename to keep it clean
                    filename = os.path.basename(s3_key)
                    local_file_path = os.path.join(local_folder, filename)

                    print(f"Downloading: {s3_key} ...")
                    s3.download_file(bucket_name, s3_key, local_file_path)
                    file_count += 1
        
        print(f"\n✅ Ingestion Complete! {file_count} files saved to '{local_folder}'")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

# --- Configuration ---
BUCKET_NAME = 'rag-s3-docs-bucket'
S3_FOLDER_PREFIX = 'data/'          # The 'folder' in S3 you want to pull from
LOCAL_TARGET_DIR = './data_from_s3' # Where files will go on your PC

if __name__ == "__main__":
    ingest_from_s3_to_local(BUCKET_NAME, S3_FOLDER_PREFIX, LOCAL_TARGET_DIR)


# python rag_project/data_ingestion/loader.py