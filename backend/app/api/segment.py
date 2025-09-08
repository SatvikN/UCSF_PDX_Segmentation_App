import threading
from fastapi import APIRouter, HTTPException

from app.schemas.jobs import SegmentRequest, JobResponse, JobStatusResponse
from app.services.jobs import jobs
from app.services.segmentation import run_classify_then_segment
from app.models.classifier_model.architectures.resnet50 import (
    load_classifier_with_weights,
    predict_tumor_presence,
    CLASSIFIER_IMAGE_ROWS,
    CLASSIFIER_IMAGE_COLS,
)
from app.utils.image_preprocessing import get_default_segmentation_weights_path, get_default_classifier_weights_path, custom_normalize
import numpy as np
from PIL import Image
from fastapi import Body
import os
from app.services.images import ensure_png_slices, get_png_path
from app.services.storage import get_study_subdir
from app.models.segmentation_model.architectures.r2udensenet import create_r2udensenet_model, IMAGE_ROW, IMAGE_COL


router = APIRouter(prefix="/segment", tags=["segment"])


def _run_job(job_id: str, study_id: str, threshold: float) -> None:
    try:
        jobs.set_status(job_id, "running", progress=0)
        # Load models/weights
        seg_weights_path = get_default_segmentation_weights_path()
        clf_weights_path = get_default_classifier_weights_path()
        clf_model = load_classifier_with_weights(clf_weights_path)

        # Classifier slice wrapper
        def clf_predict(arr_2d: np.ndarray) -> bool:
            if arr_2d.shape != (CLASSIFIER_IMAGE_ROWS, CLASSIFIER_IMAGE_COLS):
                img = Image.fromarray(arr_2d.astype(np.float32))
                img = img.resize((CLASSIFIER_IMAGE_COLS, CLASSIFIER_IMAGE_ROWS))
                arr_2d = np.array(img, dtype=np.float32)
            x = np.expand_dims(arr_2d, axis=(0, -1))  # (1,H,W,1)
            return predict_tumor_presence(clf_model, x, threshold=0.5)

        saved, clf_flags = run_classify_then_segment(
            study_id=study_id,
            classifier_predict_slice=clf_predict,
            segmenter_weights_path=seg_weights_path,
            threshold=threshold or 0.5,
        )
        jobs.set_result(job_id, {"study_id": study_id, "classifier_results": clf_flags})
    except Exception as exc:  # noqa: BLE001
        jobs.set_error(job_id, str(exc))


@router.post("/start", response_model=JobResponse)
async def start_segmentation(req: SegmentRequest) -> JobResponse:
    if not req.study_id:
        raise HTTPException(status_code=400, detail="study_id required")
    job_id = jobs.create({"study_id": req.study_id, "model": req.model, "threshold": req.threshold})
    thread = threading.Thread(target=_run_job, args=(job_id, req.study_id, req.threshold or 0.5), daemon=True)
    thread.start()
    return JobResponse(job_id=job_id)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def segmentation_status(job_id: str) -> JobStatusResponse:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobStatusResponse(job_id=job_id, status=job["status"])


@router.post("/resegment", tags=["segment"])
async def resegment_slices(
    payload: dict = Body(..., example={"study_id": "<id>", "slices": [1,2,3]})
):
    study_id = payload.get("study_id")
    slices = payload.get("slices") or []
    if not study_id or not isinstance(slices, list):
        raise HTTPException(status_code=400, detail="study_id and slices[] required")

    # Ensure PNGs exist
    ensure_png_slices(study_id)

    # Load segmenter once
    seg_weights_path = get_default_segmentation_weights_path()
    seg_model = create_r2udensenet_model()
    seg_model.load_weights(seg_weights_path)

    masks_dir = get_study_subdir(study_id, "masks")

    updated = []
    for idx in slices:
        try:
            png_path = get_png_path(study_id, int(idx))
            if not os.path.exists(png_path):
                continue
            arr = np.array(Image.open(png_path).convert('L'), dtype=np.float32)
            # Resize if needed
            if arr.shape[::-1] != (IMAGE_COL, IMAGE_ROW):
                img = Image.fromarray(arr)
                img = img.resize((IMAGE_COL, IMAGE_ROW))
                arr = np.array(img, dtype=np.float32)
            x = custom_normalize(arr)
            x = np.expand_dims(x, axis=(0, -1))  # (1,H,W,1)
            pred = seg_model.predict(x, batch_size=1, verbose=0)
            mask_small = (np.squeeze(pred, axis=(0, -1)) >= 0.5).astype(np.uint8) * 255
            # Save mask in mask index order (idx.png)
            mask_img = Image.fromarray(mask_small)
            # Match original PNG size for consistency
            orig = Image.open(png_path).convert('L')
            if mask_img.size != orig.size:
                mask_img = mask_img.resize(orig.size)
            out_path = os.path.join(masks_dir, f"{int(idx)}.png")
            mask_img.save(out_path)
            updated.append(int(idx))
        except Exception:
            # skip problematic slice
            continue

    # Return which slices were updated
    return {"study_id": study_id, "updated_slices": sorted(updated)}


