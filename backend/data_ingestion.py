"""
Step 1: Download all 7 NYC Open Data datasets via Socrata API.
Handles pagination for large datasets (LL84 has 2.2M rows).
"""
import os
import time
import requests
import pandas as pd
from config import SOCRATA_BASE, DATASETS, RAW_DATA_DIR


def download_dataset(dataset_key: str, limit: int = 50000) -> pd.DataFrame:
    """Download a single dataset, paginating if necessary."""
    info = DATASETS[dataset_key]
    dataset_id = info["id"]
    label = info["label"]

    print(f"[DOWNLOAD] {label} ({dataset_id})...")

    all_rows = []
    offset = 0

    while True:
        url = f"{SOCRATA_BASE}/{dataset_id}.json?$limit={limit}&$offset={offset}"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        batch = resp.json()

        if not batch:
            break

        all_rows.extend(batch)
        print(f"  ... fetched {len(all_rows)} rows so far")

        if len(batch) < limit:
            break

        offset += limit
        time.sleep(0.5)  # be polite to the API

    df = pd.DataFrame(all_rows)
    print(f"[DONE] {label}: {len(df)} rows, {len(df.columns)} columns\n")
    return df


def save_raw(df: pd.DataFrame, name: str):
    """Save raw DataFrame to CSV."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    path = os.path.join(RAW_DATA_DIR, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"[SAVED] {path}")


def download_all():
    """Download all datasets and save as CSVs."""
    for key in DATASETS:
        df = download_dataset(key)
        save_raw(df, key)
    print("\n=== All datasets downloaded ===")


if __name__ == "__main__":
    download_all()
