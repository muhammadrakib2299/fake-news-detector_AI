"""
Split the unified dataset into train/validation/test sets (80/10/10).

Usage:
    python data/split_data.py
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

PROCESSED_DIR = Path(__file__).parent / "processed"


def main():
    print("VerifyAI — Data Splitting")
    print("=" * 40)

    # Load unified dataset
    input_path = PROCESSED_DIR / "unified_dataset.csv"
    if not input_path.exists():
        print("[ERROR] unified_dataset.csv not found. Run preprocess.py first.")
        return

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} samples")

    # Encode labels: real=0, fake=1
    df["label_encoded"] = (df["label"] == "fake").astype(int)

    # Split: 80% train, 10% val, 10% test (stratified)
    train_df, temp_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label_encoded"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df["label_encoded"]
    )

    # Save splits
    train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
    val_df.to_csv(PROCESSED_DIR / "val.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test.csv", index=False)

    # Report
    print(f"\n=== Split Results ===")
    for name, split_df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        dist = split_df["label"].value_counts().to_dict()
        pct_fake = split_df["label_encoded"].mean() * 100
        print(f"  {name:5s}: {len(split_df):>6} samples | {dist} | {pct_fake:.1f}% fake")

    print(f"\nSaved to: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
