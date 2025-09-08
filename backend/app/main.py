from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.upload import router as upload_router
from app.api.images import router as images_router
from app.api.segment import router as segment_router
from app.api.results import router as results_router
from app.api.export import router as export_router
from app.api.studies import router as studies_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="PDX Segmentation API",
        version="0.1.0",
        description="Backend API for DICOM upload, segmentation, and export",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(upload_router)
    app.include_router(images_router)
    app.include_router(segment_router)
    app.include_router(results_router)
    app.include_router(export_router)
    app.include_router(studies_router)

    # Serve built frontend if present
    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    @app.get("/health", tags=["system"])
    async def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


