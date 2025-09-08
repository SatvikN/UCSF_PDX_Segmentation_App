import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalMaxPooling2D
from tensorflow.keras.applications import ResNet50
import numpy as np
from app.utils.image_preprocessing import custom_normalize

K = tf.keras.backend
K.set_image_data_format('channels_last')

# Image dimensions for classifier
CLASSIFIER_IMAGE_ROWS = 192
CLASSIFIER_IMAGE_COLS = 192
CLASSIFIER_IMAGE_DEPTH = 1

def create_resnet50_classifier():
    """
    Create ResNet50-based binary classifier for tumor detection.
    Returns model ready for inference (no compilation needed).
    """
    base_model = ResNet50(
        weights=None, 
        include_top=False, 
        input_shape=(CLASSIFIER_IMAGE_ROWS, CLASSIFIER_IMAGE_COLS, CLASSIFIER_IMAGE_DEPTH)
    )
    
    # Add custom layers for binary classification
    gmp = GlobalMaxPooling2D()(base_model.output)
    output = Dense(1, activation='sigmoid')(gmp)
    
    # Create final model
    model = Model(inputs=base_model.input, outputs=output)
    
    return model


def load_classifier_with_weights(weights_path: str):
    """
    Load classifier model with weights for inference.
    
    Args:
        weights_path: Path to .hdf5 weights file
        
    Returns:
        Loaded model ready for inference
    """
    model = create_resnet50_classifier()
    model.load_weights(weights_path)
    return model


def predict_tumor_presence(model, image_array: tf.Tensor, threshold: float = 0.5) -> bool:
    """
    Predict if image contains tumor.
    
    Args:
        model: Loaded classifier model
        image_array: Preprocessed image tensor of shape (1, H, W, 1)
        threshold: Classification threshold (default 0.5)
        
    Returns:
        True if tumor detected, False otherwise
    """
    # Apply custom normalization
    image_array = custom_normalize(image_array)
    
    prediction = model.predict(image_array, verbose=0)
    return float(prediction[0][0]) >= threshold
