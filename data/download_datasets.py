"""
Download datasets for VerifyAI fake news detection.

Datasets:
1. LIAR dataset - 12.8K labeled statements from PolitiFact
2. ISOT Fake News dataset - 44K articles (Reuters real + fake sources)
3. FakeNewsNet - Political and celebrity fake news articles

Usage:
    python data/download_datasets.py
"""

import os
import zipfile
import requests
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path, desc: str = ""):
    """Download a file with progress indication."""
    if dest.exists():
        print(f"  [SKIP] {desc or dest.name} already exists")
        return
    print(f"  [DOWNLOADING] {desc or dest.name}...")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = (downloaded / total) * 100
                print(f"\r  [DOWNLOADING] {desc}: {pct:.1f}%", end="", flush=True)
    print(f"\r  [DONE] {desc}: {dest.stat().st_size / 1024 / 1024:.1f} MB")


def download_liar():
    """Download LIAR dataset as a zip and extract TSV files."""
    print("\n=== LIAR Dataset ===")
    liar_dir = RAW_DIR / "liar"
    liar_dir.mkdir(exist_ok=True)

    # Check if already extracted
    if (liar_dir / "train.tsv").exists():
        print("  [SKIP] LIAR dataset already exists")
        for f in ["train.tsv", "valid.tsv", "test.tsv"]:
            path = liar_dir / f
            if path.exists():
                df = pd.read_csv(path, sep="\t", header=None)
                print(f"  {f}: {len(df)} rows")
        return

    # Download the zip file
    zip_url = "https://www.cs.ucsb.edu/~william/data/liar_dataset.zip"
    zip_path = liar_dir / "liar_dataset.zip"
    download_file(zip_url, zip_path, "LIAR dataset zip")

    # Extract
    print("  [EXTRACTING] liar_dataset.zip...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(liar_dir)
    zip_path.unlink()  # Remove zip after extraction

    # Verify
    for f in ["train.tsv", "valid.tsv", "test.tsv"]:
        path = liar_dir / f
        if path.exists():
            df = pd.read_csv(path, sep="\t", header=None)
            print(f"  {f}: {len(df)} rows")
        else:
            print(f"  [WARN] {f} not found after extraction")


def download_isot():
    """
    ISOT Fake News dataset requires manual download from Kaggle.
    Creates instructions file for the user.
    """
    print("\n=== ISOT Fake News Dataset ===")
    isot_dir = RAW_DIR / "isot"
    isot_dir.mkdir(exist_ok=True)

    # Check if already downloaded
    if (isot_dir / "True.csv").exists() and (isot_dir / "Fake.csv").exists():
        print("  [SKIP] ISOT dataset already exists")
        true_df = pd.read_csv(isot_dir / "True.csv")
        fake_df = pd.read_csv(isot_dir / "Fake.csv")
        print(f"  True.csv: {len(true_df)} rows")
        print(f"  Fake.csv: {len(fake_df)} rows")
        return

    # Try downloading via Kaggle CLI
    try:
        print("  [INFO] Attempting Kaggle CLI download...")
        result = os.system(
            f'kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset '
            f'-p "{isot_dir}" --unzip'
        )
        if result == 0 and (isot_dir / "True.csv").exists():
            true_df = pd.read_csv(isot_dir / "True.csv")
            fake_df = pd.read_csv(isot_dir / "Fake.csv")
            print(f"  True.csv: {len(true_df)} rows")
            print(f"  Fake.csv: {len(fake_df)} rows")
            return
    except Exception:
        pass

    # Create manual download instructions
    readme = isot_dir / "DOWNLOAD_INSTRUCTIONS.md"
    readme.write_text(
        "# ISOT Fake News Dataset\n\n"
        "## Option 1: Kaggle CLI\n"
        "```bash\n"
        "pip install kaggle\n"
        "kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset "
        f"-p data/raw/isot --unzip\n"
        "```\n\n"
        "## Option 2: Manual Download\n"
        "1. Go to: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset\n"
        "2. Download and extract the zip\n"
        "3. Place `True.csv` and `Fake.csv` in this directory\n"
    )
    print("  [MANUAL] ISOT requires Kaggle download.")
    print("  Please download from: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset")
    print(f"  Place True.csv and Fake.csv in: {isot_dir}")
    print("  See DOWNLOAD_INSTRUCTIONS.md for details.")


def download_fakenewsnet():
    """Download FakeNewsNet dataset CSVs from GitHub."""
    print("\n=== FakeNewsNet Dataset ===")
    fnn_dir = RAW_DIR / "fakenewsnet"
    fnn_dir.mkdir(exist_ok=True)

    base_url = "https://raw.githubusercontent.com/KaiDMML/FakeNewsNet/master/dataset"
    files = {
        "politifact_real.csv": f"{base_url}/politifact_real.csv",
        "politifact_fake.csv": f"{base_url}/politifact_fake.csv",
        "gossipcop_real.csv": f"{base_url}/gossipcop_real.csv",
        "gossipcop_fake.csv": f"{base_url}/gossipcop_fake.csv",
    }

    for filename, url in files.items():
        try:
            download_file(url, fnn_dir / filename, f"FakeNewsNet {filename}")
        except Exception as e:
            print(f"  [ERROR] Failed to download {filename}: {e}")

    # Verify
    for filename in files:
        path = fnn_dir / filename
        if path.exists():
            df = pd.read_csv(path)
            print(f"  {filename}: {len(df)} rows, columns: {list(df.columns)}")


if __name__ == "__main__":
    print("VerifyAI — Dataset Downloader")
    print("=" * 40)

    download_liar()
    download_isot()
    download_fakenewsnet()

    print("\n" + "=" * 40)
    print("Dataset download complete!")
    print(f"Check {RAW_DIR} for downloaded files.")
