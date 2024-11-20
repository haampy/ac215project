# The Dockerfile is used to define the environment that will run your pipeline scripts. Since both scripts (dataloader.py and preprocess_cv.py) are in the same folder, this Dockerfile will:

# 1. Install the necessary libraries, such as python image, requests library (for downloading the ZIP), Pillow (for image resizing), 
#    google-cloud-storage (for interacting with GCS), and DVC for data versioning.
# 2. Copy the files from the folder into the container.
# 3. Initialize DVC in the container and ensure DVC can track and push datasets to the GCS bucket.
# 4. Set the entry point or command to execute your scripts, which should include DVC operations like `dvc add` and `dvc push` to version the datasets.

# Use a Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and project dependencies from Pipfile
RUN pip install pipenv

# Explicitly tell Pipenv to use the system Python version
RUN pipenv --python /usr/local/bin/python3.9

# Install dependencies from Pipfile
RUN pipenv install --deploy --system

# Install additional packages (e.g., Git for DVC)
RUN apt-get update && apt-get install -y git

# Install DVC with GCS support
#RUN pipenv install dvc[gdrive,gs]
RUN pipenv install dvc[gdrive,gs] dvc-gs

# Copy the source code into the container
COPY . /app/

# Copy the JSON key file into the container
COPY apcomp-215-435803-f083fd847577.json /app/apcomp-215-435803-f083fd847577.json

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to the JSON key
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/apcomp-215-435803-f083fd847577.json"

# Initialize Git repository
RUN git init

# Check if DVC is installed correctly
RUN dvc --version

# Initialize DVC in the container
RUN dvc init -q

# Set the entry point to run the docker-shell.sh script when the container starts
ENTRYPOINT ["bash", "docker-shell.sh"]