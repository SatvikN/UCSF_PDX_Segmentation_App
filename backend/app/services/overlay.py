from typing import Sequence, Tuple

import numpy as np
from PIL import Image


def overlay_mask_on_image(
    image_gray: np.ndarray,
    mask_binary: np.ndarray,
    color_rgb: Sequence[int] = (255, 255, 0),
    alpha: float = 0.4,
) -> Image.Image:
    # image_gray expected shape: (H, W), values 0-255 or 0-1
    # mask_binary expected shape: (H, W), values {0,1}
    if image_gray.ndim != 2:
        raise ValueError("image_gray must be 2D")
    if mask_binary.ndim != 2:
        raise ValueError("mask_binary must be 2D")
    if image_gray.shape != mask_binary.shape:
        raise ValueError("image_gray and mask_binary must have the same shape")

    img = image_gray.astype(np.float32)
    if img.max() <= 1.0:
        img = img * 255.0
    img = np.clip(img, 0, 255).astype(np.uint8)
    base_rgb = np.stack([img, img, img], axis=-1).astype(np.float32)

    mask = (mask_binary > 0).astype(np.float32)[..., None]
    overlay_color = np.array(color_rgb, dtype=np.float32)
    overlay_layer = np.ones_like(base_rgb) * overlay_color

    blended = base_rgb * (1.0 - alpha * mask) + overlay_layer * (alpha * mask)
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    return Image.fromarray(blended, mode='RGB')


