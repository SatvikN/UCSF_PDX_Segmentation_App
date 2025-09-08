from typing import List

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from app.schemas.jobs import UploadResponse
from app.services.storage import save_uploads, ingest_local_directory


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)) -> UploadResponse:
    study_id, saved_files = await save_uploads(files)
    return UploadResponse(study_id=study_id, files=saved_files)


class IngestLocalRequest(BaseModel):
    path: str


@router.post("/ingest_local", response_model=UploadResponse)
async def ingest_local(req: IngestLocalRequest) -> UploadResponse:
    study_id, saved_files = ingest_local_directory(req.path)
    return UploadResponse(study_id=study_id, files=saved_files)


