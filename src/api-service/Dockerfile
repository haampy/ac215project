# Use the official Debian-hosted Python image
FROM python:3.9-slim

ARG DEBIAN_PACKAGES="build-essential git screen vim"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Tell pipenv where the shell is. This allows us to use "pipenv shell" as a
# container entry point.
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs.
ENV PYTHONUNBUFFERED=1


ENV COLOR_MODEL_PATH="model/color_model.pth"
ENV SHAPE_MODEL_PATH="model/shape_model.pth"
ENV DATABASE_CSV="model/drug_database.csv"
ENV LABEL_ENCODER_PATH="model/label_encoder.pkl"

# Ensure we have an up to date baseline, install dependencies and
# create a user so we don't run the app as root
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    chown app:app /persistent && \
    chown app:app /app


RUN apt-get update && apt-get install -y libgl1 && apt-get install -y libglib2.0-dev

# Ensure gsutil is available in PATH
ENV PATH="/root/google-cloud-sdk/bin:$PATH"

# Install gsutil (Google Cloud SDK)
RUN curl https://dl.google.com/dl/cloudsdk/release/install_google_cloud_sdk.bash | bash
# Switch to the new user
USER app
WORKDIR /app

# Install python packages
ADD --chown=app:app Pipfile Pipfile.lock /app/

RUN pipenv sync

# Add the rest of the source code. This is done last so we don't invalidate all
# layers when we change a line of code.
ADD --chown=app:app . /app

# Entry point
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]