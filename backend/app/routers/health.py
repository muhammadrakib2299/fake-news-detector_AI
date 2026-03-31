"""Health check endpoint."""

from fastapi import APIRouter
from ..schemas import HealthResponse
from ..dependencies import get_classifier

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """Return service health status."""
    classifiers = get_classifier()
    model_loaded = classifiers is not None and classifiers.get("primary") is not None

    primary_model = None
    if model_loaded:
        primary = classifiers["primary"]
        primary_model = getattr(primary, "__class__", type(primary)).__name__

    return HealthResponse(
        status="healthy",
        model_loaded=model_loaded,
        primary_model=primary_model,
        version="0.2.0",
    )
