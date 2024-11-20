from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
import torch
from torchvision import transforms
from PIL import Image
from paddleocr import PaddleOCR
from Levenshtein import distance as levenshtein_distance
import numpy as np
import pandas as pd
import joblib
import os

# Initialize FastAPI app
app = FastAPI()

# Load models and configurations at startup
class InferConfig:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Paths for required files
        self.color_model_path = os.getenv("COLOR_MODEL_PATH", "color_model.pth")
        self.shape_model_path = os.getenv("SHAPE_MODEL_PATH", "shape_model.pth")
        self.database_csv = os.getenv("DATABASE_CSV", "drug_database.csv")
        self.label_encoder_path = os.getenv("LABEL_ENCODER_PATH", "label_encoder.pkl")

        # Load models
        self.color_model = self.load_model(self.color_model_path)
        self.shape_model = self.load_model(self.shape_model_path)

        # Load drug database
        self.database_data = pd.read_csv(self.database_csv)
        self.splimprint_database = self.database_data['splimprint'].fillna("").tolist()
        self.splcolor_text_encoded = np.array(self.database_data['splcolor_text_encoded'].tolist())
        self.splshape_text_encoded = np.array(self.database_data['splshape_text_encoded'].tolist())
        self.medicine_name_list = np.array(self.database_data['medicine_name_encoded'].tolist())

        # Load label encoder
        with open(self.label_encoder_path, 'rb') as file:
            self.label_encoder = joblib.load(file)

        # Initialize OCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=torch.cuda.is_available())

    def load_model(self, model_path):
        return torch.load(model_path, map_location=self.device)

config = InferConfig()

# Image preprocessing function
def preprocess_image(image_file):
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
    ])
    image = Image.open(image_file).convert("RGB")
    return transform(image).unsqueeze(0)  # Add batch dimension

# Prediction function
def predict(model, image_tensor):
    with torch.no_grad():
        image_tensor = image_tensor.to(config.device)
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the drug identification service!"}

# Inference endpoint
@app.post("/infer/")
async def infer(file: UploadFile):
    try:
        # Preprocess image
        image_tensor = preprocess_image(file.file)

        # Run predictions
        color_prediction = predict(config.color_model, image_tensor)
        shape_prediction = predict(config.shape_model, image_tensor)

        # Extract imprint using OCR
        ocr_result = config.ocr.ocr(file.file.name, cls=True)
        ocr_res = ""
        if ocr_result[0]:
            res = sorted(ocr_result, key=lambda line: (line[0][0][0], line[0][0][1]))
            ocr_res = ";".join(line[1][0] for line in res[0])  # Join all labels with ';'

        # Match predictions with the database
        color_matches = (config.splcolor_text_encoded == color_prediction).astype(np.float64) * 0.5
        shape_matches = (config.splshape_text_encoded == shape_prediction).astype(np.float64) * 0.5
        ocr_res_len = len(ocr_res)
        total_length = np.array([len(imprint) + ocr_res_len for imprint in config.splimprint_database])
        edit_distances = np.array([levenshtein_distance(ocr_res, imprint) for imprint in config.splimprint_database])
        normalize_similarity = np.where(
            (total_length == 0) & (edit_distances == 0),
            1,
            np.where(total_length != 0, 1 - edit_distances / total_length, 0)
        )
        overlapped_scores = np.array([
            2 * len(set(imprint) & set(ocr_res)) for imprint in config.splimprint_database
        ])
        overlapped_similarity = np.where(
            (total_length == 0) & (overlapped_scores == 0),
            1,
            np.where(total_length != 0, overlapped_scores / total_length, 0)
        )
        score = color_matches + shape_matches + normalize_similarity + overlapped_similarity
        idx = np.argmax(score)
        medicine_name = config.label_encoder.inverse_transform([config.medicine_name_list[idx]])[0]

        return {
            "predicted_color": color_prediction,
            "predicted_shape": shape_prediction,
            "predicted_imprint": ocr_res,
            "identified_drug_name": medicine_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
