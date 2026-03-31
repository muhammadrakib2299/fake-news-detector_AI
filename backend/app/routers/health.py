"""Health check endpoint."""

from fastapi import APIRouter
from ..schemas import HealthResponse
from ..dependencies import get_classifier

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """Return service health status."""
    classifier = get_classifier()
    return HealthResponse(
        status="healthy",
        model_loaded=classifier is not None,
        version="0.1.0",
    )
