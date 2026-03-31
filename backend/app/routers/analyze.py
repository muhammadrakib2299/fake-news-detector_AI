"""Analysis endpoints."""

from fastapi import APIRouter, HTTPException
from ..schemas import AnalyzeRequest, AnalyzeResponse
from ..dependencies import get_classifier

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """Analyze text, URL, or claim for fake news."""
    classifier = get_classifier()

    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        result = classifier.predict(request.content)
        return AnalyzeResponse(
            verdict=result["verdict"],
            confidence=result["confidence"],
            fake_probability=result["fake_probability"],
            real_probability=result["real_probability"],
            input_text=request.content,
            input_type=request.input_type.value,
            model_used=result.get("model", "baseline"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
