"""VerifyAI — FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .dependencies import load_model
from .routers import analyze, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup."""
    load_model()
    yield


app = FastAPI(
    title="VerifyAI API",
    description="AI-powered fake news detection API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(health.router, tags=["Health"])


@app.get("/")
async def root():
    return {"message": "Welcome to VerifyAI API", "docs": "/docs"}
