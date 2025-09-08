import os
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image
import pydicom

from app.services.images import ensure_png_slices, get_png_path
from app.services.storage import get_study_subdir, get_study_dicom_source_dir
from app.models.segmentation_model.architectures.r2udensenet_inference import create_r2udensenet_model, IMAGE_ROW, IMAGE_COL
from app.utils.image_preprocessing import custom_normalize
from app.services.dicom import list_dicom_files


def run_segmentation_placeholder(study_id: str, threshold: float = 0.5) -> List[str]:
    # Ensure PNGs exist and create trivial masks by thresholding mid-intensity
    png_files = ensure_png_slices(study_id)
    masks_dir = get_study_subdir(study_id, "masks")
    saved: List[str] = []
    for idx_name in png_files:
        slice_index = int(os.path.splitext(idx_name)[0])
        img_path = get_png_path(study_id, slice_index)
        img = Image.open(img_path).convert('L')
        arr = np.array(img, dtype=np.float32) / 255.0
        mask = (arr > threshold).astype(np.uint8) * 255
        out_path = os.path.join(masks_dir, f"{slice_index}.png")
        Image.fromarray(mask).save(out_path)
        saved.append(out_path)
    return saved


def _load_volume_as_batch(study_id: str) -> np.ndarray:
    # Load DICOM slices directly, preserve as much information as possible, then resize to model input
    dicom_dir = get_study_dicom_source_dir(study_id)
    dcm_files = list_dicom_files(dicom_dir)
    batch: List[np.ndarray] = []
    for name in dcm_files:
        ds = pydicom.dcmread(os.path.join(dicom_dir, name))
        arr = ds.pixel_array.astype(np.float32)
        # Normalize slice to 0..1 per-volume normalization will follow
        # Resize if needed to model input
        if arr.shape[::-1] != (IMAGE_COL, IMAGE_ROW):
            img = Image.fromarray(arr)
            img = img.resize((IMAGE_COL, IMAGE_ROW))
            arr = np.array(img, dtype=np.float32)
        batch.append(arr)
    vol = np.stack(batch, axis=0)  # N,H,W
    # Apply custom normalization instead of z-score
    vol = custom_normalize(vol)
    vol = np.expand_dims(vol, axis=-1)  # N,H,W,1
    return vol


# Global model cache to avoid retracing
_segmentation_model_cache = {}

def run_segmentation_r2u(study_id: str, weights_path: str, threshold: float = 0.5) -> List[str]:
    # Load input volume
    x = _load_volume_as_batch(study_id)
    
    # Use cached model or create new one
    cache_key = weights_path
    if cache_key not in _segmentation_model_cache:
        model = create_r2udensenet_model()
        model.load_weights(weights_path)
        _segmentation_model_cache[cache_key] = model
    else:
        model = _segmentation_model_cache[cache_key]
    
    # Predict
    preds = model.predict(x, batch_size=1, verbose=0)  # N,H,W,1
    preds = np.squeeze(preds, axis=-1)  # N,H,W
    preds = (preds >= threshold).astype(np.uint8) * 255

    masks_dir = get_study_subdir(study_id, "masks")
    saved: List[str] = []
    # Save in original indexing order (1..N)
    for i in range(preds.shape[0]):
        out_path = os.path.join(masks_dir, f"{i+1}.png")
        Image.fromarray(preds[i]).save(out_path)
        saved.append(out_path)
    return saved


def run_classify_then_segment(
    study_id: str,
    classifier_predict_slice: callable,
    segmenter_weights_path: str,
    threshold: float = 0.5,
) -> Tuple[List[str], List[bool]]:
    """
    For each slice, run the classifier; if positive, segment; else save an empty mask of same size.
    classifier_predict_slice: function that takes (H,W) np.ndarray and returns bool (tumor present)
    """
    # Load and normalize volume once
    dicom_dir = get_study_dicom_source_dir(study_id)
    dcm_files = list_dicom_files(dicom_dir)
    if not dcm_files:
        return []
    masks_dir = get_study_subdir(study_id, "masks")

    # Pass 1: run classifier on all slices (original size)
    classifier_flags: List[bool] = []
    arrays: List[np.ndarray] = []
    for name in dcm_files:
        ds = pydicom.dcmread(os.path.join(dicom_dir, name))
        arr = ds.pixel_array.astype(np.float32)
        arrays.append(arr)
        has_tumor = bool(classifier_predict_slice(arr))
        classifier_flags.append(has_tumor)

    # Determine contiguous range from first to last positive
    if any(classifier_flags):
        first_pos = next(i for i, f in enumerate(classifier_flags) if f)
        last_pos = len(classifier_flags) - 1 - next(i for i, f in enumerate(reversed(classifier_flags)) if f)
    else:
        first_pos = -1
        last_pos = -2  # ensures no slice is segmented

    # Prepare segmenter model once
    seg_model = create_r2udensenet_model()
    seg_model.load_weights(segmenter_weights_path)

    # Pass 2: segment only within [first_pos, last_pos], zeros elsewhere
    saved: List[str] = []
    for idx0, arr in enumerate(arrays):
        idx = idx0 + 1  # 1-based for filenames
        if first_pos <= idx0 <= last_pos:
            arr_resized = arr
            if arr.shape[::-1] != (IMAGE_COL, IMAGE_ROW):
                img = Image.fromarray(arr)
                img = img.resize((IMAGE_COL, IMAGE_ROW))
                arr_resized = np.array(img, dtype=np.float32)
            x = custom_normalize(arr_resized)
            x = np.expand_dims(x, axis=(0, -1))  # 1,H,W,1
            pred = seg_model.predict(x, batch_size=1, verbose=0)
            mask_small = (np.squeeze(pred, axis=(0, -1)) >= threshold).astype(np.uint8) * 255
            mask_img = Image.fromarray(mask_small)
            mask_img = mask_img.resize((arr.shape[1], arr.shape[0]))
            out = np.array(mask_img, dtype=np.uint8)
        else:
            out = np.zeros_like(arr, dtype=np.uint8)
        out_path = os.path.join(masks_dir, f"{idx}.png")
        Image.fromarray(out).save(out_path)
        saved.append(out_path)
    return saved, classifier_flags


