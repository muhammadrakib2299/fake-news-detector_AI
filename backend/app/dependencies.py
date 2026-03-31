"""Shared dependencies — model loading and singleton access."""

from .services.classifier import BaselineClassifier
from pathlib import Path

_classifier = None


def load_model():
    """Load the ML model at startup."""
    global _classifier
    model_path = Path(__file__).parent.parent / "ml" / "models" / "baseline_tfidf_logreg.joblib"

    if model_path.exists():
        _classifier = BaselineClassifier(str(model_path))
        print(f"Model loaded from {model_path}")
    else:
        print(f"WARNING: Model not found at {model_path}. Run train_baseline.py first.")
        _classifier = None


def get_classifier():
    """Get the loaded classifier instance."""
    return _classifier
