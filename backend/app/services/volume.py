from typing import Iterable, List, Sequence, Tuple

import numpy as np


def compute_raw_areas(mask_volume: np.ndarray) -> List[float]:
    # mask_volume expected shape: (num_slices, height, width)
    raw_areas = np.sum(mask_volume, axis=(1, 2))
    return raw_areas.tolist()


def scale_single_area(raw_area: float, slice_thickness_mm: float, pixel_spacing_mm: Sequence[float]) -> float:
    scaled_area_mm3 = raw_area * slice_thickness_mm * pixel_spacing_mm[0] * pixel_spacing_mm[1]
    scaled_area_cc = scaled_area_mm3 / 1000.0
    return float(scaled_area_cc)


def scale_all_areas(raw_areas: Iterable[float], slice_thickness_mm: float, pixel_spacing_mm: Sequence[float]) -> List[float]:
    return [scale_single_area(area, slice_thickness_mm, pixel_spacing_mm) for area in raw_areas]


