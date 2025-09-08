import os
from typing import List


def list_dicom_files(directory: str) -> List[str]:
    files: List[str] = []
    for filename in os.listdir(directory):
        if not filename.startswith('._') and filename.lower().endswith('.dcm'):
            files.append(filename)
    files.sort()
    return files


