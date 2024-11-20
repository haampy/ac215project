import os
from google.cloud import storage

def download_model(bucket_name, source_blob_name, destination_file_name):
    """
    Download a file from GCP bucket to local directory.
    """
    print(f"Checking if {destination_file_name} exists locally...")
    if not os.path.exists(destination_file_name):
        print(f"{destination_file_name} not found. Downloading from GCS...")
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded {source_blob_name} to {destination_file_name}")
    else:
        print(f"{destination_file_name} already exists. Skipping download.")

if __name__ == "__main__":
    # GCP bucket and file configurations
    GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "pillrx-models")
    MODEL_DIR = "/app/model"
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Define models to download
    MODELS = {
        "color_model": "models/color_model.pth",
        "shape_model": "models/shape_model.pth",
    }

    # Download each model
    for model_name, blob_path in MODELS.items():
        local_path = os.path.join(MODEL_DIR, f"{model_name}.pth")
        download_model(GCS_BUCKET_NAME, blob_path, local_path)

    print("All models are ready.")
