import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import requests
from io import BytesIO

def get_shape_from_image(image_input):
    """
    Identifies the geometric shape in an image using a pre-trained model.

    Args:
        image_input: The input image, which can be a string (URL) or a
                     file-like object (e.g., from an uploaded file).

    Returns:
        A string representing the predicted shape label (e.g., "Circle", "Square").
    """
    labels = [
        "None",
        "Circle",
        "Triangle",
        "Square",
        "Pentagon",
        "Hexagon"
    ]
    
    if isinstance(image_input, str):
        # Assume it's a URL
        image = Image.open(requests.get(image_input, stream=True).raw)
    else:
        # Assume it's a file-like object
        image = Image.open(image_input)
    
    feature_extractor = AutoImageProcessor.from_pretrained('0-ma/mobilenet-v2-geometric-shapes')
    model = AutoModelForImageClassification.from_pretrained('0-ma/mobilenet-v2-geometric-shapes')
    
    inputs = feature_extractor(images=image, return_tensors="pt")
    logits = model(**inputs)['logits'].cpu().detach().numpy()
    
    prediction = np.argmax(logits, axis=1)[0]
    predicted_label = labels[prediction]
    
    return predicted_label
