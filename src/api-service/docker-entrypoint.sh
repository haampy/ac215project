#!/bin/bash

echo "Container is running!!!"

if [ -f "/secrets/service_account.json" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="/secrets/service_account.json"
    echo "Service account key set to: $GOOGLE_APPLICATION_CREDENTIALS"
else
    echo "Service account key not found in /secrets/. Exiting."
    exit 1
fi

# Ensure the /app/model directory exists
mkdir -p /app/model

# Run the model download script
echo "Running model download script..."
pipenv run python /app/download_models.py
pipenv run pip install paddlepaddle

echo "Model files are ready."



# this will run the api/infer.py file with the instantiated app FastAPI
uvicorn_server() {
    uvicorn api.infer:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"
}

uvicorn_server_production() {
    pipenv run uvicorn api.infer:app --host 0.0.0.0 --port 9000 --lifespan on
}

export -f uvicorn_server
export -f uvicorn_server_production

echo -en "\033[92m
The following commands are available:
    uvicorn_server
        Run the Uvicorn Server
\033[0m
"

if [ "${DEV}" = 1 ]; then
  pipenv shell
else
  uvicorn_server_production
fi