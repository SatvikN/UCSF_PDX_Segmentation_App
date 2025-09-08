import os
from typing import List, Tuple, Dict, Any

import pydicom

from app.services.storage import get_study_subdir, get_study_dicom_source_dir
from app.services.dicom import list_dicom_files


def read_spacing_and_thickness_mm(study_id: str) -> Tuple[List[float], float]:
    dicom_dir = get_study_dicom_source_dir(study_id)
    files = list_dicom_files(dicom_dir)
    if not files:
        return [1.0, 1.0], 1.0
    ds = pydicom.dcmread(os.path.join(dicom_dir, files[0]))
    pixel_spacing = ds.get("PixelSpacing", [1.0, 1.0])
    try:
        spacing = [float(pixel_spacing[0]), float(pixel_spacing[1])]
    except Exception:
        spacing = [1.0, 1.0]
    try:
        slice_thickness = float(ds.get("SliceThickness", 1.0))
    except Exception:
        slice_thickness = 1.0
    return spacing, slice_thickness


def read_study_info(study_id: str) -> Dict[str, Any]:
    dicom_dir = get_study_dicom_source_dir(study_id)
    files = list_dicom_files(dicom_dir)
    info: Dict[str, Any] = {}
    if not files:
        return info
    ds = pydicom.dcmread(os.path.join(dicom_dir, files[0]))
    spacing, thickness = read_spacing_and_thickness_mm(study_id)
    # Dimensions
    try:
        rows = int(ds.get("Rows", 0))
        cols = int(ds.get("Columns", 0))
    except Exception:
        rows, cols = 0, 0
    # Helpers to jsonify sequences
    def to_list(val: Any) -> Any:
        if val is None:
            return None
        if isinstance(val, (str, bytes)):
            return str(val)
        try:
            iter(val)  # type: ignore[arg-type]
            return [to_list(v) for v in list(val)]  # flatten nested
        except Exception:
            return val
    # Basic tags
    info.update({
        "pixel_spacing_mm": spacing,
        "slice_thickness_mm": thickness,
        "height": rows,
        "width": cols,
        "study_date": str(ds.get("StudyDate", "")),
        "patient_id": str(ds.get("PatientID", "")),
        "patient_weight": str(ds.get("PatientWeight", "")),
        # Geometry / orientation
        "spacing_between_slices_mm": ds.get("SpacingBetweenSlices", None),
        "image_orientation_patient": to_list(ds.get("ImageOrientationPatient", None)),
        "image_position_patient": to_list(ds.get("ImagePositionPatient", None)),
        # Acquisition details
        "modality": str(ds.get("Modality", "")),
        "body_part_examined": str(ds.get("BodyPartExamined", "")),
        "study_description": str(ds.get("StudyDescription", "")),
        "series_description": str(ds.get("SeriesDescription", "")),
        "echo_time": ds.get("EchoTime", None),
        "repetition_time": ds.get("RepetitionTime", None),
        "inversion_time": ds.get("InversionTime", None),
        "flip_angle": ds.get("FlipAngle", None),
        "sequence_name": str(ds.get("SequenceName", "")),
        "sequence_variant": str(ds.get("SequenceVariant", "")),
        "echo_train_length": ds.get("EchoTrainLength", None),
    })
    return info


