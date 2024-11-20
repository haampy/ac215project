# The docker-shell.sh script is used to determine whether to run train_model.py or infer_model.py based on the command-line argument passed when the Docker container is run.

# 1. If "train" is passed as an argument, the script will run train_model.py to train the model using the preprocessed data in GCS and save the trained model to GCS.
# 2. If "infer" is passed as an argument, the script will run infer_model.py to load the trained model from GCS and perform inference on the test dataset or other images.
# 3. This script ensures flexibility in choosing whether to train the model or run inference by using command-line arguments.

# Important notes:
# - We might want to set up a separate check to make sure the container actually set the "GOOGLE_APPLICATION_CREDENTIALS" environment variable 
# - Ensure that the correct environment variables (e.g., GCS bucket paths) are set before running each script.
# - Handle errors for invalid arguments to provide useful feedback to the user.

# docker_shell.sh
#!/bin/bash
COMMAND=$1
shift

case "$COMMAND" in
  "train")
    echo "Running training..."
    python main.py "$@"
    ;;
  "infer")
    echo "Running inference..."
    python infer.model.py "$@"
    ;;
  *)
    echo "Invalid command. Use 'train' or 'infer'."
    ;;
esac