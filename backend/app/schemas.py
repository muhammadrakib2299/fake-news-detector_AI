"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class InputType(str, Enum):
    TEXT = "text"
    URL = "url"
    CLAIM = "claim"


class AnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Text, URL, or claim to analyze")
    input_type: InputType = Field(default=InputType.TEXT, description="Type of input")


class AnalyzeResponse(BaseModel):
    id: Optional[str] = None
    verdict: str = Field(..., description="Real, Misleading, or Fake")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    fake_probability: float = Field(..., ge=0, le=1)
    real_probability: float = Field(..., ge=0, le=1)
    input_text: str
    input_type: str
    model_used: str = "baseline"


class HealthResponse(BaseModel):
    status: str = "healthy"
    model_loaded: bool = False
    version: str = "0.1.0"
