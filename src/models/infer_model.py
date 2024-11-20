import os
import torch
import logging
import argparse
import numpy as np
import pandas as pd
from torchvision import transforms
from PIL import Image
from paddleocr import PaddleOCR
from Levenshtein import distance as levenshtein_distance
import joblib

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load the trained model
def load_model(model_path, device):
    model = torch.load(model_path, map_location=device)
    return model

# Function to preprocess new images
def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)  # Add batch dimension

# Function to make predictions
def predict(model, image_tensor, device):
    with torch.no_grad():
        image_tensor = image_tensor.to(device)
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Identify drug name from image.')
    parser.add_argument('--color_model_path', type=str, required=True, help='Path to the trained color model.')
    parser.add_argument('--shape_model_path', type=str, required=True, help='Path to the trained shape model.')
    parser.add_argument('--database_csv', type=str, required=True, help='Path to the drug database CSV.')
    parser.add_argument('--label_encoder_path', type=str, required=True, help='Path to the label encoder file.')
    parser.add_argument('--image_path', type=str, required=True, help='Path to the drug image for recognition.')
    args = parser.parse_args()

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load models
    color_model = load_model(args.color_model_path, device)
    shape_model = load_model(args.shape_model_path, device)
    logging.info("Models loaded successfully.")

    # Load drug database
    database_data = pd.read_csv(args.database_csv)
    splimprint_database = database_data['splimprint'].fillna("").tolist()
    splcolor_text_encoded = np.array(database_data['splcolor_text_encoded'].tolist())
    splshape_text_encoded = np.array(database_data['splshape_text_encoded'].tolist())
    medicine_name_list = np.array(database_data['medicine_name_encoded'].tolist())

    # Load label encoder
    with open(args.label_encoder_path, 'rb') as file:
        le = joblib.load(file)

    # Preprocess image and predict color and shape
    image_tensor = preprocess_image(args.image_path)
    color_prediction = predict(color_model, image_tensor, device)
    shape_prediction = predict(shape_model, image_tensor, device)

    # Extract imprint using OCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=torch.cuda.is_available())
    ocr_result = ocr.ocr(args.image_path, cls=True)
    ocr_res = ""
    if ocr_result[0]:
        res = sorted(ocr_result, key=lambda line: (line[0][0][0], line[0][0][1]))
        ocr_res = ";".join(line[1][0] for line in res[0])  # Join all labels with ';'

    # Match predictions with the database
    color_matches = (splcolor_text_encoded == color_prediction).astype(np.float64) * 0.5
    shape_matches = (splshape_text_encoded == shape_prediction).astype(np.float64) * 0.5
    ocr_res_len = len(ocr_res)
    total_length = np.array([len(imprint) + ocr_res_len for imprint in splimprint_database])
    edit_distances = np.array([levenshtein_distance(ocr_res, imprint) for imprint in splimprint_database])
    normalize_similarity = np.where(
        (total_length == 0) & (edit_distances == 0),
        1,
        np.where(total_length != 0, 1 - edit_distances / total_length, 0)
    )
    overlapped_scores = np.array([
        2 * len(set(imprint) & set(ocr_res)) for imprint in splimprint_database
    ])
    overlapped_similarity = np.where(
        (total_length == 0) & (overlapped_scores == 0),
        1,
        np.where(total_length != 0, overlapped_scores / total_length, 0)
    )
    score = color_matches + shape_matches + normalize_similarity + overlapped_similarity
    idx = np.argmax(score)
    medicine_name = le.inverse_transform([medicine_name_list[idx]])[0]

    # Output result
    logging.info(f"Predicted Color Class: {color_prediction}")
    logging.info(f"Predicted Shape Class: {shape_prediction}")
    logging.info(f"Predicted Imprint: {ocr_res}")
    logging.info(f"Identified Drug Name: {medicine_name}")
