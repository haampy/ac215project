import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.preprocessing import LabelEncoder
import json
import argparse

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# usage:
# loaded_encoders = {column: joblib.load(f'{column}_label_encoder.pkl') for column in columns_to_encode}

def encode_new_data(new_data, loaded_encoders):
    for column, le in loaded_encoders.items():
        new_data[column] = new_data[column].astype(str)  # Ensure all values are of string type
        new_data[column + '_encoded'] = le.transform(new_data[column])
    return new_data

# Example: Encode the validation dataset in the same way
# val_data = pd.read_csv('val_annotations.csv')
# val_data_encoded = encode_new_data(val_data, loaded_encoders)
# val_data_encoded.to_csv('encoded_val_annotations.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate image annotations.')
    parser.add_argument('--csv_file', type=str, default="./local_data/annotations.csv", help='Path to the CSV file.')
    parser.add_argument('--data_dir', type=str, default="./local_data" , help='Path to the image data directory.')

    args = parser.parse_args()


    data = pd.read_csv(args.csv_file)
    image_list = []
    for root, dirs, files in os.walk(args.data_dir):
        for file in files:
            if file.endswith('.jpg'):
                image_list.append(file)

    image_set = set(image_list)
        
    # Filter rows that have corresponding images
    filtered_data = data[data['splimage'].apply(lambda x: f"{x}.jpg" in image_set)]

    # Write to a new file
    filtered_file_path = 'filtered_annotations.csv'
    filtered_data.to_csv(filtered_file_path, index=False)
    print(f"Filtered annotations have been saved to {filtered_file_path}")

    # Annotate the three datasets in local_data based on the newly generated file
    # Read the CSV file containing annotations for all datasets
    data = pd.read_csv(filtered_file_path)
    columns_to_encode = ['splshape_text', 'splcolor_text', 'medicine_name']

    # Initialize a dictionary to save all encoders to ensure consistency
    encoders = {}
    for column in columns_to_encode:
        le = LabelEncoder()
        # Fit the entire data to ensure consistent encoding for train, val, and test
        data[column] = data[column].astype(str)  # Ensure all values are of string type
        le.fit(data[column])
        encoders[column] = le
        
        # Transform the column using the encoder
        data[column + '_encoded'] = le.transform(data[column])

    # Save the encoders to disk for use during validation and testing
    for column, le in encoders.items():
        joblib.dump(le, f'{column}_label_encoder.pkl')

    # Save the unsegmented version of the data as annotations.csv
    data.to_csv('encoded_annotations.csv', index=False)
    print("Unsegmented annotations have been saved to annotations.csv")

    # Split the encoded data into three files
    train_files = set(os.listdir(os.path.join(args.data_dir, 'train')))
    val_files = set(os.listdir(os.path.join(args.data_dir, 'val')))
    test_files = set(os.listdir(os.path.join(args.data_dir, 'test')))

    def filter_data_by_files(data, files):
        return data[data['splimage'].apply(lambda x: f"{x}.jpg" in files)]

    train_data = filter_data_by_files(data, train_files)
    val_data = filter_data_by_files(data, val_files)
    test_data = filter_data_by_files(data, test_files)

    train_data.to_csv('encoded_train_annotations.csv', index=False)
    val_data.to_csv('encoded_val_annotations.csv', index=False)
    test_data.to_csv('encoded_test_annotations.csv', index=False)

    print("Encoded annotations have been saved to encoded_train_annotations.csv, encoded_val_annotations.csv, and encoded_test_annotations.csv")
