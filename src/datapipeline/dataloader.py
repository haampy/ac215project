""" 

Summary of what this script should do:
This script downloads, extracts, and uploads the raw images to a GCS bucket, and tracks the raw dataset with DVC for versioning.

More details steps:
- Download the ZIP file from the provided link: https://ftp.nlm.nih.gov/projects/pillbox/pillbox_production_images_full_202008.zip?_gl=1*m0p1ms*_ga*MTY4ODI3NzM3MC4xNzI1MDQyMTEy*_ga_7147EPK006*MTcyODU3NTk3NC41LjEuMTcyODU3NjA2OC4wLjAuMA..*_ga_P1FPTH9PL4*MTcyODU3NTk3NC41LjEuMTcyODU3NjA2OC4wLjAuMA
- Extract it into a local folder.
- Upload each extracted image file to your GCS bucket. 
- Use DVC to track the raw images (after downloading and extracting) to ensure data versioning.
- Push the raw images to remote storage (GCS) via DVC to maintain version control.

Important notes:
- Ensure this script is using the GOOGLE_APPLICATION_CREDENTIALS environment variable
- Make sure that the upload to GCS handles errors and retries (in case of connection issues).
- Organize the images in the GCS bucket in a way that they are easily retrievable for the next script.
- After uploading the raw images, track the dataset with DVC and push the versioned data to the GCS bucket using `dvc push`.

"""

import os
import requests
import zipfile
from google.cloud import storage
import subprocess

def download_and_extract_zip(url, extract_to):
    """Downloads and extracts a ZIP file."""
    #defining full path and creating partial path
    zip_path = os.path.join(extract_to, 'pillbox_images.zip') # defines (doesn't create yet) the full path (data/raw_images/pillbox_images.zip) where the ZIP file will be saved after downloading
    os.makedirs(extract_to, exist_ok=True) # meant to create the directory (data/raw_images) if it doesn't exist, but since this script will be running in the same container as dataloader.py and that script had already made this directory with all the raw images, the effect of this line will be that it just skips making this directory
    
    # Download the ZIP file from the NIH URL and saves it at the full path data/raw_images/pillbox_images.zip
    print("Downloading the ZIP file...")
    response = requests.get(url, stream=True) # url is the link to the NIH where the zip can be downloaded
    with open(zip_path, 'wb') as f: 
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Download completed.")

    # Extract the ZIP file which makes the image files are available in the data/raw_images/ folder, then deleted zip folder
    print("Extracting the ZIP file...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)  # Remove the ZIP file after extraction
    print(f"Extracted files to {extract_to}")

def upload_to_gcs(bucket_name, source_folder):
    """Uploads image files from the local folder to a GCS bucket (if the image does not already exist in the bucket)"""
    print(f"Uploading images to GCS bucket: {bucket_name}")
    # the client initialization below relies on having the GOOGLE_APPLICATION_CREDENTIALS environment variable available
    client = storage.Client() # initializes a client object from the Google Cloud Storage library (google.cloud.storage) - this client allows us to interact with your GCS buckets
    bucket = client.bucket(bucket_name) # bucket_name is pillrx-raw-images
    
    # the below for loop uploads each image from the extracted folder to the pillrx-raw-images bucket one at a time
    for root, _, files in os.walk(source_folder):
        for file_name in files:
            if file_name.endswith('.jpg'):
                file_path = os.path.join(root, file_name)
                blob = bucket.blob(file_name)  # Create a reference to the blob (file) in GCS
                
                # Check if the file already exists in the GCS bucket
                if blob.exists(client):
                    print(f"File {file_name} already exists in GCS bucket {bucket_name}, skipping upload.")
                else:
                    try:
                        blob.upload_from_filename(file_path)  # Upload the file if it doesn't exist
                        print(f"Uploaded {file_name} to GCS bucket {bucket_name}")
                    except Exception as e:
                        print(f"Error uploading {file_name}: {e}")

def track_and_push_dvc(data_path):
    """Uses DVC to track the raw images and push them to the remote storage."""
    print("Tracking raw images with DVC...")
    subprocess.run(["dvc", "add", data_path], check=True) # Add the data folder to DVC for tracking - creates a .dvc file which stores metadata (not actual raw images)
    data_dir = os.path.dirname(data_path)
    gitignore_path = os.path.join(data_dir, '.gitignore')
    # Check if the .gitignore file exists:
    if not os.path.exists(gitignore_path):
        print(f"Warning: .gitignore file not found at {gitignore_path}")
        #figure out how to handle this case as needed
    subprocess.run(["git", "add", f"{data_path}.dvc", gitignore_path], check=True) # Stage the .dvc file and .gitignore file in Git
    subprocess.run(["git", "commit", "-m", "Add raw images"], check=True) # creates a git commit which tracks the .dvc file, not the actual raw images.
    # Capture output from dvc push
    try:
        result = subprocess.run(["dvc", "push"], check=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error during 'dvc push': {e}")
        print(e.stdout)
        print(e.stderr)
        raise  # Correctly raise the exception
    print("Raw images tracked and pushed with DVC.")

def main():
    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

    # Set your GCS bucket name and raw data path
    gcs_bucket = os.getenv('GCS_RAW_BUCKET', 'pillrx-raw-images') # uses environment variable GCS_RAW_BUCKET if available, otherwise defaults to pillrx-raw-images
    raw_data_path = 'data/raw_images' #path where we will put the raw images in the container

    # Download the ZIP file and extract images
    url = 'https://ftp.nlm.nih.gov/projects/pillbox/pillbox_production_images_full_202008.zip'
    download_and_extract_zip(url, raw_data_path)

    # Upload extracted images to GCS
    upload_to_gcs(gcs_bucket, raw_data_path)

    # Track the raw images with DVC and push to GCS for versioning
    track_and_push_dvc(raw_data_path)

if __name__ == "__main__":
    main()