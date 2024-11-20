import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from torch.utils.data import DataLoader
from torchvision import transforms
import pandas as pd
from PIL import Image
import argparse
from utils import PillDataset, load_data
from models import initialize_model
from train import train_model
from google.cloud import storage

def initialize_model(num_colors, device):
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_colors)
    model = model.to(device)
    return model

if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'
    
def main(args):
    device = torch.device("cuda:2" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load training and validation data
    print("Loading data...")
    color_train_dataloader = load_data(args.train_csv_file, os.path.join(args.data_dir, 'train'), batch_size=args.batch_size, shuffle=True)
    color_val_dataloader = load_data(args.val_csv_file, os.path.join(args.data_dir, 'val'), batch_size=args.batch_size, shuffle=False)
    shape_train_dataloader = load_data(args.train_csv_file, os.path.join(args.data_dir, 'train'), batch_size=args.batch_size, shuffle=True, color=False)
    shape_val_dataloader = load_data(args.val_csv_file, os.path.join(args.data_dir, 'val'), batch_size=args.batch_size, shuffle=False, color=False)

    print(f"Number of training samples: {len(color_train_dataloader.dataset)}")
    print(f"Number of validation samples: {len(color_val_dataloader.dataset)}")

    # Initialize color model
    print("Initializing color model...")

    num_colors = pd.read_csv(args.annotation_csv_file)['splcolor_text'].nunique()
    color_model = initialize_model(num_colors, device)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(color_model.parameters(), lr=args.learning_rate)

    # Train model
    print(f"Starting training color model for {args.num_epochs} epochs.")
    color_model = train_model(color_model, color_train_dataloader, color_val_dataloader, criterion, optimizer, device, args.num_epochs)
    # color_model.load_state_dict(torch.load('color_model.pth', map_location=device))

    # Save color model
    torch.save(color_model.state_dict(), 'color_model.pth')
    print("Color model saved.")

    print("Initializing shape model...")

    num_shapes = pd.read_csv(args.annotation_csv_file)['splshape_text'].nunique()
    shape_model = initialize_model(num_shapes, device)

    # Define loss function and optimizer
    shape_criterion = nn.CrossEntropyLoss()
    shape_optimizer = optim.Adam(shape_model.parameters(), lr=args.learning_rate)

    # Train model
    print(f"Starting training shape model for {args.num_epochs} epochs.")
    shape_model = train_model(shape_model, shape_train_dataloader, shape_val_dataloader, shape_criterion, shape_optimizer, device, args.num_epochs)

    # Save shape model
    torch.save(shape_model.state_dict(), 'shape_model.pth')
    print("Shape model saved.")

    # Upload model to GCP bucket
    def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {bucket_name}/{destination_blob_name}")

    # Upload color model
    upload_to_gcs(args.bucket_name, 'color_model.pth', 'models/color_model.pth')
    print("Color model uploaded to GCP bucket.")

    # Upload shape model
    upload_to_gcs(args.bucket_name, 'shape_model.pth', 'models/shape_model.pth')
    print("Shape model uploaded to GCP bucket.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train a ResNet model.')
    parser.add_argument('--annotation_csv_file', type=str, default='encoded_annotations.csv', help='Path to the training CSV file.')

    parser.add_argument('--train_csv_file', type=str, default='encoded_train_annotations.csv',help='Path to the training CSV file.')
    parser.add_argument('--val_csv_file', type=str, default='encoded_val_annotations.csv', help='Path to the validation CSV file.')
    parser.add_argument('--data_dir', type=str, default="local_data", help='Path to the image data directory.')
    parser.add_argument('--batch_size', type=int, default=512, help='Batch size for training.')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate for the optimizer.')
    parser.add_argument('--num_epochs', type=int, default=100, help='Number of epochs for training.')
    parser.add_argument('--bucket_name', type=str,default="pillrx-models", help='GCP bucket name to upload the models.')

    args = parser.parse_args()
    main(args)


