import os
import tempfile
import uuid
from typing import List, Tuple

from fastapi import UploadFile
from app.services.dicom import list_dicom_files


BASE_STORAGE_DIR = os.environ.get("PDX_STORAGE_DIR") or os.path.join(
    tempfile.gettempdir(), "pdx_segmentation_app"
)


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_study_dir(study_id: str) -> str:
    study_dir = os.path.abspath(os.path.join(BASE_STORAGE_DIR, "studies", study_id))
    _ensure_dir(study_dir)
    return study_dir


def get_study_subdir(study_id: str, subdir_name: str) -> str:
    path = os.path.join(get_study_dir(study_id), subdir_name)
    _ensure_dir(path)
    return path


def set_study_source_dir(study_id: str, source_dir: str) -> None:
    study_dir = get_study_dir(study_id)
    meta_path = os.path.join(study_dir, "source_path.txt")
    with open(meta_path, "w") as f:
        f.write(os.path.abspath(source_dir).strip())


def get_study_dicom_source_dir(study_id: str) -> str:
    study_dir = get_study_dir(study_id)
    meta_path = os.path.join(study_dir, "source_path.txt")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                p = f.read().strip()
            if os.path.isdir(p):
                return p
        except Exception:
            pass
    # Fallback to managed dicom folder (for uploaded studies)
    return get_study_subdir(study_id, "dicom")


async def save_uploads(files: List[UploadFile]) -> Tuple[str, List[str]]:
    study_id = str(uuid.uuid4())
    dicom_dir = get_study_subdir(study_id, "dicom")
    saved_filenames: List[str] = []

    for f in files:
        # Sanitize filename
        filename = os.path.basename(f.filename)
        dest_path = os.path.join(dicom_dir, filename)
        content = await f.read()
        with open(dest_path, "wb") as out:
            out.write(content)
        saved_filenames.append(filename)

    return study_id, saved_filenames


def ingest_local_directory(directory_path: str) -> Tuple[str, List[str]]:
    # In-place: record source folder; do not copy DICOMs
    study_id = str(uuid.uuid4())
    filenames: List[str] = []
    if not os.path.isdir(directory_path):
        return study_id, filenames
    set_study_source_dir(study_id, directory_path)
    filenames = list_dicom_files(directory_path)
    return study_id, filenames

