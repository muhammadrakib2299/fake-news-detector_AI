"""Baseline classifier using TF-IDF + Logistic Regression."""

import joblib


class BaselineClassifier:
    def __init__(self, model_path: str):
        self.pipeline = joblib.load(model_path)

    def predict(self, text: str) -> dict:
        """Classify text as real or fake."""
        probabilities = self.pipeline.predict_proba([text])[0]
        fake_prob = float(probabilities[1])
        real_prob = float(probabilities[0])

        # Determine verdict
        if fake_prob >= 0.65:
            verdict = "Fake"
        elif fake_prob >= 0.35:
            verdict = "Misleading"
        else:
            verdict = "Real"

        confidence = max(fake_prob, real_prob)

        return {
            "verdict": verdict,
            "confidence": confidence,
            "fake_probability": fake_prob,
            "real_probability": real_prob,
            "model": "baseline",
        }
