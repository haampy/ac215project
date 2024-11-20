import pytest
from api.service import preprocess_image, predict

def test_preprocess_image():
    from PIL import Image
    import os

    image_path = "tests/test_image.jpg"  # Ensure you have a test image
    image_tensor = preprocess_image(image_path)
    assert image_tensor.shape == (1, 3, 224, 224)  # Expected shape for a ResNet model

def test_predict():
    import torch
    from api.service import initialize_model

    # Mock input tensor
    input_tensor = torch.rand((1, 3, 224, 224))
    device = torch.device("cpu")

    # Initialize a test model
    model = initialize_model(num_colors=10, device=device)
    prediction = predict(model, input_tensor)
    assert isinstance(prediction, int)  # Ensure output is an integer class
