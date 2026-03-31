"""
Train the baseline TF-IDF + Logistic Regression model.

Usage:
    python backend/ml/train_baseline.py
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("VerifyAI — Baseline Model Training")
    print("=" * 40)

    # Load data
    train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DIR / "val.csv")
    test_df = pd.read_csv(PROCESSED_DIR / "test.csv")

    X_train, y_train = train_df["text"], train_df["label_encoded"]
    X_val, y_val = val_df["text"], val_df["label_encoded"]
    X_test, y_test = test_df["text"], test_df["label_encoded"]

    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

    # Build pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=50000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
            solver="lbfgs",
        )),
    ])

    # Train
    print("\nTraining...")
    pipeline.fit(X_train, y_train)

    # Evaluate on validation
    y_val_pred = pipeline.predict(X_val)
    print("\n=== Validation Results ===")
    print(f"Accuracy:  {accuracy_score(y_val, y_val_pred):.4f}")
    print(f"Precision: {precision_score(y_val, y_val_pred):.4f}")
    print(f"Recall:    {recall_score(y_val, y_val_pred):.4f}")
    print(f"F1 Score:  {f1_score(y_val, y_val_pred):.4f}")

    # Evaluate on test
    y_test_pred = pipeline.predict(X_test)
    print("\n=== Test Results ===")
    print(f"Accuracy:  {accuracy_score(y_test, y_test_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_test_pred):.4f}")
    print(f"Recall:    {recall_score(y_test, y_test_pred):.4f}")
    print(f"F1 Score:  {f1_score(y_test, y_test_pred):.4f}")
    print()
    print(classification_report(y_test, y_test_pred, target_names=["Real", "Fake"]))

    # Save
    model_path = MODEL_DIR / "baseline_tfidf_logreg.joblib"
    joblib.dump(pipeline, model_path)
    print(f"Model saved to: {model_path}")
    print(f"Model size: {model_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
