import os
from tqdm import tqdm
from google.cloud import storage

if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'


def download_data_from_gcs(bucket_name, prefix, local_dir):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    for blob in blobs:
        # Download the blob to a local file
        local_path = os.path.join(local_dir, blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        print(f"Downloaded {blob.name} to {local_path}")

def download_annotations_from_gcs(bucket_name, file_path, local_path):
    local_dir = os.path.dirname(local_path)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)  
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.download_to_filename(local_path)
    print(f"Downloaded {file_path} to {local_path}")

def list_buckets():
    client = storage.Client()
    buckets = client.list_buckets()

    print("Available buckets:")
    for bucket in buckets:
        print(bucket.name)


def list_files_in_bucket(bucket_name, prefix=None):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    print(f"Files in bucket '{bucket_name}':")
    for blob in blobs:
        print(blob.name)


if __name__ == "__main__":
    print("Starting to download annotations file...")
    download_annotations_from_gcs('pilllrx-all-annotations', 'raw/Pillbox__retired_January_28__2021__20241016.csv', 'local_data/annotations.csv')
    print("Annotations file download completed.")

    print("Starting to download training and validation datasets...")
    
    print("Downloading training dataset...")
    blobs = storage.Client().get_bucket('pillrx-processed-images').list_blobs(prefix='train/')
    for blob in tqdm(blobs, desc="Training dataset"):
        local_path = os.path.join('local_data', blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
    print("Training dataset download completed.")
    
    print("Downloading validation dataset...")
    blobs = storage.Client().get_bucket('pillrx-processed-images').list_blobs(prefix='val/')
    for blob in tqdm(blobs, desc="Validation dataset"):
        local_path = os.path.join('local_data', blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
    print("Validation dataset download completed.")

    print("Downloading test dataset...")
    blobs = storage.Client().get_bucket('pillrx-processed-images').list_blobs(prefix='test/')
    for blob in tqdm(blobs, desc="Test dataset"):
        local_path = os.path.join('local_data', blob.name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
    print("Test dataset download completed.")