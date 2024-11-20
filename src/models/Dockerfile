# This Dockerfile in the models folder is used to define the environment for running both train_model.py and infer_model.py in a flexible setup.
# The user can specify whether to train the model or run inference by passing a command-line argument when running the Docker container.

# 1. Use a GPU-enabled base image, such as PyTorch with GPU support (e.g., pytorch/pytorch:latest).
# 2. Install the necessary libraries, including PyTorch (for model training), CUDA libraries for GPU support, and google-cloud-storage to interact with Google Cloud Storage (GCS).
# 3. Copy the Python files and dependencies from the models folder into the container.
# 4. Set the entry point to run docker-shell.sh, which will handle command-line arguments to execute either train_model.py or infer_model.py.
# 5. Ensure that the environment is optimized for GPU execution (including installing CUDA, cuDNN if needed, and setting up PyTorch for GPU usage).

# Important notes:
# - Ensure that the CUDA version is compatible with the version of PyTorch used.
# - This Dockerfile ensures that the container can be flexibly used for both training and inference based on the command-line argument provided.


FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and project dependencies from Pipfile
RUN pip install pipenv

# Explicitly tell Pipenv to use the system Python version
RUN pipenv --python /usr/local/bin/python3.9

# 安装系统工具和依赖项
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from Pipfile
RUN pipenv install --deploy --system
RUN apt-get update && apt-get install -y libgl1 && apt-get install -y libglib2.0-dev

# Install additional packages (e.g., Git for DVC)
RUN apt-get update && apt-get install -y git

# Install DVC with GCS support
#RUN pipenv install dvc[gdrive,gs]
RUN pipenv install dvc[gdrive,gs] dvc-gs

# Copy the source code into the container
COPY . /app/

# Copy the JSON key file into the container
COPY service_account.json /app/service_account.json

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to the JSON key
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json"

# Initialize Git repository
RUN git init

# Check if DVC is installed correctly
RUN dvc --version

# Initialize DVC in the container
RUN dvc init -q

# Set the entry point to run the docker-shell.sh script when the container starts

ENTRYPOINT ["bash", "docker-shell.sh"]