from typing import List

from typing import Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    study_id: str
    files: List[str]


class SegmentRequest(BaseModel):
    study_id: str
    model: Optional[str] = None
    threshold: Optional[float] = 0.5
    segmenter_weights_path: Optional[str] = None
    classifier_weights_path: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str


