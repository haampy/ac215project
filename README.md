## Milestone 4 Template

```
Never commit large data files,trained models, personal API Keys/secrets to GitHub
```

#### Project Milestone 4 Organization

```
├── Readme.md
├── data # DO NOT UPLOAD DATA TO GITHUB, only .gitkeep to keep the directory or a really small sample
├── notebooks
│   └── eda.ipynb
├── references
├── reports
│   └── Statement of Work_Sample.pdf
└── src
    ├── datapipeline
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── dataloader.py
    │   ├── docker-shell.sh
    │   ├── preprocess_cv.py
    │   ├── preprocess_rag.py
    ├── docker-compose.yml
    └── models
        ├── Dockerfile      
        ├── Pipfile
        ├── Pipfile.lock
        ├── docker-shell.sh
        ├── infer_model.py
        ├── model_rag.py
        ├── utils.py
        └── train_model.py
        
```

# AC215 - Milestone4 - PillRx

**Team Members**
John Jun, Maya (Maida) Sijaric, Shuo Cai

**Group Name**
PillRx

**Project**
This Computer Vision project will be used for detecting pill identity from uploaded images of pills, followed by a warning about potentially dangerous interaction with alcohol. Our model will be finetuned using image data that includes several annotations for each image, including the pill identity, imprint, color and shape. A particular emphasis will be placed on acurately predicting the pill identity of the top 5-10 drugs associated with death due to alcohol interaction. Time permitting (considering our team size), we may incorporate a RAG model as we are motivated to create a chat feature for follow up discussions about a selection of the most important pills, as far as their danger if consumed with alcohol is concerned.

**Wireframe:**
The app wireframe/design can be found following this path: references/Wireframe.png

**Data:**
We gathered a dataset of 8,694 pill images representing approximately 2000 different varieties. The dataset, approximately 1,160,882,917 bytes (1.08 GB) in size, was collected from the the NIH's National Library of Medicine Pillbox project. Our dataloader.py script downloads that data from their link (https://ftp.nlm.nih.gov/projects/pillbox/pillbox_production_images_full_202008.zip). Due to the limitations of their metadata API, we uploaded the csv file containing the annotations into the GCS bucket "pillrx-all-annotations" directly, but will be investigating automated upload mechanisms for this.
- Note: We might collect information for the purposes of a RAG later on, subject to the limitations of our team size.

**Google Cloud Resources - Context:**
***GCS Buckets:***
- pillrx-raw-images: Stores the raw images uploaded by dataloader.py.
- pillrx-processed-images: Intended to store the processed images after running preprocess_cv.py. Images are either stored in the train, test, or val subfolder of this bucket.
- pillrx-all-annotations: Used to store the CSV file containing annotations for our images, as well as the modified annotations.
- pillrx-dvc-storage: Will be used by DVC to store versioned data for both raw and processed images for later milestones - for now, we are using GCP bucket versioning, as it is not entirely clear whether we will require further data and therefore more advanced versioning capabilities.
- pillrx-models: Used to store models, as well as validation and test results.

***DVC Remote Storage:***
- pillrx-dvc-storage bucket is configured to be used as the remote storage for DVC in this pipeline, BUT WE ARE NOT RELYING ON THIS FOR THIS MILESTONE! DVC tracks datasets and stores them in this bucket, using it to version control our data.

***Service Account and Credentials:***
- We are using the same service account and credentials (apcomp-215-435803-f083fd847577.json) for accessing all GCS buckets. We have put checks in place through .gitignore to ensure that this will not be committed to the repo in the future. For now, to build the image, it's necessary to place the json key for the service account in both the folder src/datapipeline and src/models, but we are aware that this is not the most secure method and plan to improve this for the next milestone (milestone 4) (by passing these details via environment variables and storing the credentials in a more secure location, like a secret store).

**Data Pipeline Container (defined in src/datapipeline folder)**
This container downloads the images from the link and uploads them into a GCS bucket, then loads the images back from the GCS bucket to processes the dataset by resizing the images and storing them into train, validate and test destinations in a new GCS bucket.

	**Input:** GCS bucket locations, resizing parameters, and required secrets (provided via Docker).

	**Output:** Resized images stored in the specified GCS location.

**Model Container (defined in src/models folder)**
This container will first runs the train_model.py script which trains a CNN model using Pytorch and GPU from Google Cloud, then uploads the model into a GCS bucket, then this container runs the infer_model.py file which will test the model using the test data that was preprocedded and uploaded by the Data Pipeline container earlier. Due to credit issues with GCP, we trained it on colab as discussed with Shivas, but of course this will not be the long term solution - I'm just outlining our plan that we will act on for the next steps here. For now, the results from the training and validation and testing can be found in the notebooks folder, or by following this link: https://github.com/maidasijaric/AC215_PillRx/commit/32b60dd11443ce43412325728da552f885be31fb 

## Data Pipeline Overview

1. **`src/datapipeline/dataloader.py`**
   This script downloads the data from the previously specified link, and adds it to our GCS bucket, which already contains the annotation CVS (we will determine a way to automate this later.)

1. **`src/datapipeline/preprocess_cv.py`**
   This script preprocessing on our ~1GB dataset by reducing the image sizes to 128x128 (a parameter that can be changed later) to enable faster iteration during processing. The preprocessed dataset is then stored on GCS. Re-running this container will not change the raw nor processed images in the GCS bucket if we're trying to push the same images that already exist in the bucket, so logic was put in place to avoid duplicates.

2. **`src/datapipeline/preprocess_rag.py`**
   Not included in this milestone - RAG is TBD for our project, due to our team size.

3. **`src/models`**
   This section will be uploaded with the final details as soon as we've had a chance to train the model with GCP - for now, you can find the results from training the model and validating+testing it via this link: https://github.com/maidasijaric/AC215_PillRx/commit/32b60dd11443ce43412325728da552f885be31fb

## Instructions for Running the Project

**Prerequisites:**
You will need the Google Cloud service account key in JSON format. Ensure you have this file ready and accessible.
- Environment Variables: When running the Docker containers, you will not need to pass the environment variable GOOGLE_APPLICATION_CREDENTIALS to access Google Cloud Storage (GCS) for now, but soon we will change this setup so that it is required as a environment variable passed as an argument when running the container.
- Versioning: See comments under "4. DVC Data Versioning" below.

**1. Clone the Repository:**
```
git clone git@github.com:maidasijaric/AC215_PillRx.git
cd AC215_PillRx
```

**2. Building the Docker Containers:**
You will need to build 2 Docker containers in the future - one for the datapipeline stage and one for the models stage. For now, the instructions regarding the datapipeline stage are correct and working - all of that functionality has been containerized, so please disregard details regarding the Models container for M2, but note that this will change for the next Milestone (M4)!

***Build the Datapipeline Container:***
Navigate to the datapipeline folder and build the Docker image:
```
cd src/datapipeline
docker build -t datapipeline-container .
```

***Build the Models Container (disregard for M2):***
Next, navigate to the models folder and build the Docker image:
```
cd ../models
docker build -t models-container .
```

**3. Running the Containers:**

***Step 1: Run the Datapipeline Container:***
To run the data preprocessing steps, execute the following:
```
docker run datapipeline-container
```

This will:
Download the raw images, preprocess them (resize, split into train/validate/test), and upload the processed images to several GCS bucket (pillrx-raw-images bucket for raw images, while final split and processed images will go into pillrx-processed-images bucket).

``` 
NOTE: the CVS file with annotations was uploaded directly into the bucket, because there's a limitation with the NIH's API for pulling the CVS. 
```

This is the number of objects inside each subfolder in the pillrx-processed-images bucket after this container runs:
- pillrx-processed-images/test —> 1304 objects
- pillrx-processed-images/train —> 6084 object
- pillrx-processed-images/val —> 1305 objects

***Step 2: Run the Models Container (disregard for M2):***
The models container can be run for either training the model or running inference on the trained model. You specify the task by passing either train or infer as a command-line argument.

To Train the Model:
```
docker run models-container train
```

This will:
Load the preprocessed images from the GCS bucket and train the model.
Save the trained model to the GCS bucket.

To Run Inference:
```
# need run chromaDB before LLM-RAG task:
docker pull chromadb/chroma
docker run -d \
   --name chromadb \
   -p 16990:8080 \
   -v src/model/database_chroma/:/study/ai/chroma \
   -e IS PERSISTENT=TRUE \

-e ANONYMIZED TELEMETRY=TRUE \
chromadb/chroma:latest

docker run models-container infer
```

This will:
Load the trained model from the GCS bucket.
Run inference on the preprocessed test images (dafault in local_data/test, set using --new_images_dir) and output the results with basic query to LLM with RAG.

**4. DVC Data Versioning:**
We have set up data versioning with DVC for the datapipeline folder, but have decided to use GCS bucket versioning feature for the whole project for this milestone. This is due to the simplicity and relatively small data size, and due to the fact that it is not clear that we will need to modify our dataset futher in the future. GCS bucket versioning will allow us to test the performance with different sets of data, if we decide to add further images. For now, if we decide to add more images, we will create a new "v2" path in the GCS raw images bucket. If our dataset grows in complexity, however, we will be moving over to DVC for storage efficiency purposes - this is to be determined.

**notebooks folder:**
This folder contains code that is not part of container - you'll find a screenshot showing the colab model training and validation/test results being uploaded to the GCS bucket afterwards. The two files can be viewed here: https://github.com/maidasijaric/AC215_PillRx/commit/32b60dd11443ce43412325728da552f885be31fb.

**progress folder:**
This folder contains a screenshot of the following:
 - File "dataloader.py effect in bucket pillrx-raw-images.png": This image shows how the raw images were uploaded into the relevant GCS bucket after the datapipeline docker container ran
 - File "Datapipeline docker container in GCP VM": This image shows how I pulled the datapipeline docker image from dockerhub onto the GCP VM (I had built the image locally and pushed to docker hub previously), and how the container starts the process of downloading the images from the source and skipping uploading to the GCS bucket, because the images were already uploaded before (the script checks if the images exists first to avoid duplicates)
 - File "<TBD:>file name of the model training and inference container running in GCP VM": <TBD>

**Important next steps for M4:**
 - Improve how we build the containers (we will NOT be passing the secret key file into the docker image as that is of course not secure, but we did it for now so we can allocate resources and time to the other aspects of the project)
