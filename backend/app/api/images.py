import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.services.images import ensure_png_slices, get_png_path
from app.services.overlay import overlay_mask_on_image
from app.services.storage import get_study_subdir
from PIL import Image


router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{study_id}/{slice_index}.png")
async def get_image(study_id: str, slice_index: int):
    files = ensure_png_slices(study_id)
    if slice_index < 1 or slice_index > len(files):
        raise HTTPException(status_code=404, detail="slice index out of range")
    path = get_png_path(study_id, slice_index)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="image not found")
    return FileResponse(path, media_type="image/png")


@router.get("/{study_id}/{slice_index}/overlay.png")
async def get_overlay(
    study_id: str,
    slice_index: int,
    alpha: float = Query(0.4, ge=0.0, le=1.0),
    v: str = Query(None, description="Cache busting parameter"),
):
    base_path = get_png_path(study_id, slice_index)
    if not os.path.exists(base_path):
        files = ensure_png_slices(study_id)
        if slice_index < 1 or slice_index > len(files):
            raise HTTPException(status_code=404, detail="slice index out of range")
    # Load base and mask if present
    base_img = Image.open(base_path).convert('L')
    masks_dir = get_study_subdir(study_id, "masks")
    mask_path = os.path.join(masks_dir, f"{slice_index}.png")
    overlays_dir = get_study_subdir(study_id, "overlays")
    overlay_path = os.path.join(overlays_dir, f"{slice_index}.png")

    # Serve cached overlay if present (unless cache busting parameter is provided)
    if os.path.exists(overlay_path) and not v:
        return FileResponse(overlay_path, media_type="image/png")

    # If no mask yet, just return original
    if not os.path.exists(mask_path):
        return FileResponse(base_path, media_type="image/png")

    # Generate and persist overlay
    mask_img = Image.open(mask_path).convert('L')
    import numpy as np
    overlaid = overlay_mask_on_image(
        np.array(base_img),
        (np.array(mask_img) > 127).astype(np.uint8),
        color_rgb=(0, 255, 0),  # Green overlay
        alpha=alpha,
    )
    overlaid.save(overlay_path)
    return FileResponse(overlay_path, media_type="image/png")


