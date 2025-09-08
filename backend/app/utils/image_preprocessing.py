import numpy as np
import os


def get_default_segmentation_weights_path():
    """Get the default path to segmentation model weights"""
    return os.path.join("app", "models", "segmentation_model", "weights", "model_r2udensenet.hdf5")


def get_default_classifier_weights_path():
    """Get the default path to classifier model weights"""
    return os.path.join("app", "models", "classifier_model", "weights", "model_resnet50.hdf5")


def custom_normalize(image):
    """
    Custom min-max normalization for each image individually.
    Normalizes to [0, 1] based on image's own min/max values.
    
    Args:
        image: Input image array
        
    Returns:
        Normalized image array
    """
    if len(image.shape) == 4:  # Batch of images
        normalized_images = np.zeros_like(image)
        for i in range(image.shape[0]):
            sl = image[i]
            sl_min = np.min(sl)
            sl_max = np.max(sl)
            
            # Avoid division by zero
            if sl_max - sl_min == 0:
                sl_normalized = sl
            else:
                sl_normalized = (sl - sl_min) / (sl_max - sl_min)
            
            normalized_images[i] = sl_normalized
        return normalized_images
    else:  # Single image
        sl_min = np.min(image)
        sl_max = np.max(image)
        
        if sl_max - sl_min == 0:
            return image
        else:
            return (image - sl_min) / (sl_max - sl_min)
