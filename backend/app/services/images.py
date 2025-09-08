import os
from typing import List

import numpy as np
from PIL import Image
import pydicom

from app.services.storage import get_study_subdir, get_study_dicom_source_dir
from app.services.dicom import list_dicom_files


def _read_dicom_pixel_array(dicom_path: str) -> np.ndarray:
    ds = pydicom.dcmread(dicom_path)
    arr = ds.pixel_array.astype(np.float32)
    # Normalize to 0-255
    arr = arr - arr.min()
    if arr.max() > 0:
        arr = arr / arr.max()
    arr = (arr * 255.0).clip(0, 255).astype(np.uint8)
    return arr


def ensure_png_slices(study_id: str) -> List[str]:
    dicom_dir = get_study_dicom_source_dir(study_id)
    png_dir = get_study_subdir(study_id, "png")
    dcm_files = list_dicom_files(dicom_dir)
    generated: List[str] = []
    for idx, name in enumerate(dcm_files, start=1):
        src = os.path.join(dicom_dir, name)
        out_name = f"{idx}.png"
        dst = os.path.join(png_dir, out_name)
        if not os.path.exists(dst):
            arr = _read_dicom_pixel_array(src)
            Image.fromarray(arr, mode='L').save(dst)
        generated.append(out_name)
    return generated


def get_png_path(study_id: str, slice_index: int) -> str:
    png_dir = get_study_subdir(study_id, "png")
    path = os.path.join(png_dir, f"{slice_index}.png")
    return path


