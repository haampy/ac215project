import torch
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import os

class PillDataset(Dataset):
    def __init__(self, annotations_file, data_dir, transform=None, color=True):
        self.data = pd.read_csv(annotations_file)
        self.data_dir = data_dir
        self.transform = transform
        self.col_idx = -2 if color else -3

    def __getitem__(self, idx):
        img_path = os.path.join(self.data_dir, self.data.loc[idx, 'splimage'] + ".jpg")
        image = Image.open(img_path).convert("RGB")
        label = int(self.data.iloc[idx, self.col_idx])  # 整数编码后的标签

        if self.transform:
            image = self.transform(image)

        return image, label

    def __len__(self):
        return len(self.data)


def load_data(csv_file, data_dir, batch_size, shuffle=True, color=True):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    dataset = PillDataset(annotations_file=csv_file, data_dir=data_dir, transform=transform, color=color)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

    return dataloader