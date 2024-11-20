""" 

Summary of what this script should do:
This script downloads the raw images from the GCS bucket that dataloader.py uploaded, processes (resizes) them, 
splits them into train/validate/test sets, uploads the processed images to a new GCS bucket, and tracks the preprocessed dataset with DVC.


More detailed steps:
- Load images from the GCS bucket using google-cloud-storage (the images should have been uploaded by dataloader.py before this script runs).
- Resize each image (e.g., 128x128) - the library Pillow is useful for this.
- Split the images into training, validation, and test sets (e.g., 70% train, 15% validate, 15% test) - this will be useful: sklearn.model_selection.train_test_split.
- Save the resized and split images directly to respective GCS buckets or folders:
  - Train images in `train/`
  - Validation images in `val/`
  - Test images in `test/`
- Use DVC to track the preprocessed images and push the versioned data to GCS storage.

Important notes:
- Ensure this script is using the GOOGLE_APPLICATION_CREDENTIALS environment variable
- Consider adding logging to track which images have been processed successfully (maybe have a mechanism to catch and log those failures)
- Track the preprocessed images with DVC after processing them to ensure version control.
- After saving the processed images, use `dvc add` and `dvc push` to version the data and store it in GCS.

"""

import os
import random
from google.cloud import storage
from PIL import Image
import io
import subprocess
from sklearn.model_selection import train_test_split

def download_images_from_gcs(bucket_name, local_folder):
    """Downloads images from a GCS bucket ('pillrx-raw-images') and adds them to a local folder ('data/raw_images') in the container."""
    print(f"Downloading images from GCS bucket: {bucket_name}")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs() #all images from pillrx-raw-images GCS bucket

    os.makedirs(local_folder, exist_ok=True)

    for blob in blobs: #iterates over each image from the GCS bucket
        if blob.name.endswith('.jpg'):
            file_path = os.path.join(local_folder, os.path.basename(blob.name))
            if not os.path.exists(file_path): #check if that image already exists in the local path (data/raw_images), which it should since we ran dataloader.py in this same container previously, but this is just to be comprehensive in case we decide to run this script independently from dataloader.py in the future 
                blob.download_to_filename(file_path)
                print(f"Downloaded {blob.name} to {file_path}")
            else: # doesn't save the image into the data/raw_images path if it already exists!
                print(f"File {file_path} already exists locally, skipping download.")
        else:
            print("Downloaded image (from GCS bucket pillrx-raw-images) doesn't end with .jpg")

def process_and_split_images(source_folder, processed_folder, image_size=(128, 128)):
    """Resizes images and splits them into train, val, and test sets."""
    print("Processing and splitting images...")
    images = [f for f in os.listdir(source_folder) if f.endswith('.jpg')] # source_folder = 'data/raw_images'
    # random.shuffle(images) # MUST BE COMMENTED OUT, OTHERWISE AN IMAGE MIGHT BE UPLOADED TO ALL THREE DATASETS (TRAIN, TEST, VALIDATE) IF THIS SCRIPT IS RUN MULTIPLE TIMES!!!!! random.shuffle randomly reorders the elements (image filenames) in the list.

    # Split into train, validation, and test sets
    train_val_images, test_images = train_test_split(images, test_size=0.15, random_state=42)
    train_images, val_images = train_test_split(train_val_images, test_size=0.1765, random_state=42)  # 0.1765 * (1 - 0.15) ≈ 0.15

    splits = {
        'train': train_images,
        'val': val_images,
        'test': test_images
    }

    for split_name, split_images in splits.items():
        split_folder = os.path.join(processed_folder, split_name) # processed_folder = 'data/processed_images'. NB!: does not create an actual directory by itself. It simply constructs a string that represents the path to a folder and stores that string in the variable split_folder. The 3 string will be:'data/processed_images/train', 'data/processed_images/val' and 'data/processed_images/test'  
        os.makedirs(split_folder, exist_ok=True) # creates these directories per for loop cycle if they don't exist: 'data/processed_images/train', 'data/processed_images/val' and 'data/processed_images/test'  
        for image_name in split_images:
            try:
                image_path = os.path.join(source_folder, image_name)
                with Image.open(image_path) as img:
                    img = img.resize(image_size)
                    img.save(os.path.join(split_folder, image_name)) # this line overwrites existing preprocessed images with the same name (like if we run this script 2 times in the same container)
                print(f"Processed and saved {image_name} to {split_folder}")
            except Exception as e:
                print(f"Error processing {image_name}: {e}")

def upload_processed_images_to_gcs(bucket_name, processed_folder):
    """Uploads processed images from local folders to a GCS bucket."""
    print(f"Uploading processed images to GCS bucket: {bucket_name}...")
    client = storage.Client() # creates an instance of the Google Cloud Storage client, which is needed to later interact with the GCS buckets we want to upload to (pillrx-processed-images)
    bucket = client.bucket(bucket_name) # bucket_name = 'pillrx-processed-images' (client will use your service account's credentials to access this bucket)

    for root, _, files in os.walk(processed_folder): # processed_folder = 'data/processed_images' (This line of code iterates over every file inside data/processed_images/ and its subdirectories (train/, val/, test/)
        for file_name in files: # loops through all the file names in the current root directory (which would be the train, validation, or test folders)
            if file_name.endswith('.jpg'):
                local_file_path = os.path.join(root, file_name)
                # Construct the blob path by using the folder structure after 'processed_folder'
                blob_name = os.path.relpath(local_file_path, processed_folder)
                blob = bucket.blob(blob_name)
                if not blob.exists(client):
                    blob.upload_from_filename(local_file_path)
                    print(f"Uploaded {blob_name} to GCS bucket {bucket_name}")
                else:
                    print(f"File {blob_name} already exists in GCS bucket {bucket_name}, skipping upload.")
            else:
                print("Not a .jpg file!")

def track_and_push_dvc(data_path):
    """Uses DVC to track the processed images and push them to the remote storage."""
    print("Tracking processed images with DVC...")
    subprocess.run(["dvc", "add", data_path], check=True)
    data_dir = os.path.dirname(data_path)
    gitignore_path = os.path.join(data_dir, '.gitignore')
    if not os.path.exists(gitignore_path):
        print(f"Warning: .gitignore file not found at {gitignore_path}")
    subprocess.run(["git", "add", f"{data_path}.dvc", gitignore_path], check=True)
    subprocess.run(["git", "commit", "-m", "Add processed images"], check=True)
    try:
        result = subprocess.run(["dvc", "push"], check=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error during 'dvc push': {e}")
        print(e.stdout)
        print(e.stderr)
        raise
    print("Processed images tracked and pushed with DVC.")

def main():
    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

    # Set GCS bucket names
    raw_bucket = 'pillrx-raw-images'
    processed_bucket = 'pillrx-processed-images'

    # Local paths
    raw_local_folder = 'data/raw_images'
    processed_local_folder = 'data/processed_images'

    # Step 1: Download raw images from GCS
    download_images_from_gcs(raw_bucket, raw_local_folder)

    # Step 2: Process images and split into train/val/test
    process_and_split_images(raw_local_folder, processed_local_folder)

    # Step 3: Upload processed images (from processed_local_folder) to GCS bucket
    upload_processed_images_to_gcs(processed_bucket, processed_local_folder)

    # Step 4: Track processed images with DVC and push to remote storage
    track_and_push_dvc(processed_local_folder)

if __name__ == "__main__":
    main()