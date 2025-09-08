from fastapi import APIRouter, HTTPException

from app.services.metadata import read_study_info


router = APIRouter(prefix="/studies", tags=["studies"])


@router.get("/{study_id}/info")
async def get_study_info(study_id: str):
    info = read_study_info(study_id)
    if not info:
        raise HTTPException(status_code=404, detail="study info not found")
    return info


