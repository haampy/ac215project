# The docker-shell.sh script is what controls the sequence of execution inside the container we define with the Dockerfile in this folder . 
# This script ensures the container performs dataloading, preprocessing, and data versioning via DVC.

# 1. Run dataloader.py first, to download, extract, and upload the raw images to GCS.
# 2. Use DVC to track and push the raw images to GCS (versioned with DVC).
# 3. Run preprocess_cv.py next, to download the raw images from GCS, preprocess them, and upload the resized images back to GCS.
# 4. Use DVC to track and push the preprocessed images to GCS (versioned with DVC).

# Important Note:
# - We might want to write a check to make sure the container actually set the "GOOGLE_APPLICATION_CREDENTIALS" environment variable 
# - Make sure that `dvc add` and `dvc push` commands are executed after each major step (e.g., after downloading and after preprocessing) to version the data properly.

#!/bin/bash

# Exit script on error
set -e

# Check if GOOGLE_APPLICATION_CREDENTIALS is set
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. Exiting."
  exit 1
fi

# Configure Git (DVC requires Git)
GIT_USER_EMAIL=${GIT_USER_EMAIL:-"default-user@example.com"}
GIT_USER_NAME=${GIT_USER_NAME:-"Default User"}

git config --global user.email "$GIT_USER_EMAIL"
git config --global user.name "$GIT_USER_NAME"

# Initialize Git repository if not already initialized
if [ ! -d ".git" ]; then
  git init
  git add .
  git commit -m "Initial commit"
fi

# Initialize DVC (if not already initialized)
if [ ! -d ".dvc" ]; then
  dvc init -q  # Initialize DVC quietly
fi

# Configure DVC remote (GCS bucket: pillrx-dvc-storage)
dvc remote add -d myremote gs://pillrx-dvc-storage  # Replace with your GCS bucket name

# Modifying the remote to specify the credential path:
dvc remote modify myremote credentialpath /app/apcomp-215-435803-f083fd847577.json

# Run the dataloader.py script
python dataloader.py

# Run the preprocess_cv.py script
python preprocess_cv.py