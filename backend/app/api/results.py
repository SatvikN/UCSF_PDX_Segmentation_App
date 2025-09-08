import os
import numpy as np
from PIL import Image
from fastapi import APIRouter, HTTPException

from app.services.jobs import jobs
from app.services.metadata import read_spacing_and_thickness_mm, read_study_info
from app.services.volume import compute_raw_areas, scale_all_areas
from app.services.storage import get_study_subdir


router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{job_id}")
async def get_results(job_id: str):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=404, detail="job not completed")
    study_id = job["payload"].get("study_id")
    classifier_results = job["payload"].get("classifier_results")
    masks_dir = get_study_subdir(study_id, "masks")
    # Load masks volume
    # Sort numerically by slice index (filenames are like "1.png", "2.png", ...)
    mask_files = sorted(
        (f for f in os.listdir(masks_dir) if f.lower().endswith('.png')),
        key=lambda x: int(os.path.splitext(x)[0])
    )
    if not mask_files:
        return {
            "study_id": study_id,
            "total_volume_cc": 0,
            "slice_areas_cc": [],
            "classifier_results": classifier_results,
        }
    vol = []
    for name in mask_files:
        arr = np.array(Image.open(os.path.join(masks_dir, name)).convert('L'))
        vol.append((arr > 127).astype(np.uint8))
    vol = np.stack(vol, axis=0)  # N,H,W
    print("Vol shape", vol.shape)
    # Compute unscaled areas (sum per slice). vol is (N,H,W)
    raw_areas = compute_raw_areas(vol)
    spacing_mm, thickness_mm = read_spacing_and_thickness_mm(study_id)
    meta = read_study_info(study_id)
    scaled_cc = scale_all_areas(raw_areas, thickness_mm, spacing_mm)
    total_cc = float(np.sum(scaled_cc))

    # Ensure classifier_results aligns with masks order; if missing or length-mismatched,
    # derive booleans directly from per-slice areas in mask order
    if not isinstance(classifier_results, list) or len(classifier_results) != len(scaled_cc):
        classifier_results = [bool(float(a) > 0) for a in scaled_cc]
    return {
        "study_id": study_id,
        "total_volume_cc": total_cc,
        "slice_areas_cc": scaled_cc,
        "pixel_spacing_mm": spacing_mm,
        "slice_thickness_mm": thickness_mm,
        "classifier_results": classifier_results,
        **meta,
    }


