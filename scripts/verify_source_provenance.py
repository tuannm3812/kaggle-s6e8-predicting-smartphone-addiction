#!/usr/bin/env python3
"""Reproduce the candidate-source-dataset comparison in
docs/5_source_dataset_provenance.md.

Compares the candidate source dataset (jayjoshi37/smartphone-usage-and-
addiction-prediction) against this competition's train.csv: schema, value
domains, target prevalence, missingness, the addiction_level <->
addicted_label cross-tab, and a row-hash join for literal duplicate rows.

Downloads the source dataset to a temp directory (not committed, not copied
into data/) via the Kaggle CLI, per docs/archive/4_codex_claude_review_log.md
Sections 13.3 / 15.6 / 15.7.3.

Usage: scripts/verify_source_provenance.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_SLUG = "jayjoshi37/smartphone-usage-and-addiction-prediction"

SHARED_FEATURES = [
    "age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
    "work_study_hours", "sleep_hours", "notifications_per_day",
    "app_opens_per_day", "weekend_screen_time", "gender", "stress_level",
    "academic_work_impact",
]


def find_kaggle_cli() -> str:
    for candidate in ("kaggle", "/Users/tuannm3812/Library/Python/3.9/bin/kaggle"):
        try:
            subprocess.run([candidate, "--version"], capture_output=True, check=True)
            return candidate
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise RuntimeError("kaggle CLI not found on PATH or at the known local install path.")


def download_source(kaggle_cli: str, dest_dir: Path) -> Path:
    subprocess.run(
        [kaggle_cli, "datasets", "download", "-d", SOURCE_SLUG, "-p", str(dest_dir)],
        check=True,
    )
    zips = list(dest_dir.glob("*.zip"))
    if not zips:
        raise RuntimeError(f"No zip file downloaded to {dest_dir}")
    subprocess.run(["unzip", "-o", str(zips[0]), "-d", str(dest_dir)], check=True)
    csvs = [p for p in dest_dir.glob("*.csv")]
    if not csvs:
        raise RuntimeError(f"No CSV found after unzip in {dest_dir}")
    return csvs[0]


def compare(source: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> None:
    print(f"Source shape: {source.shape}")
    print(f"Source columns: {list(source.columns)}")
    print()

    print("=== Value domain comparison ===")
    for col in ["gender", "stress_level", "academic_work_impact"]:
        print(f"{col}: source={sorted(source[col].dropna().unique())} "
              f"train={sorted(train[col].dropna().unique())}")
    for col in ["age", "daily_screen_time_hours", "social_media_hours",
                "gaming_hours", "work_study_hours", "sleep_hours",
                "notifications_per_day", "app_opens_per_day", "weekend_screen_time"]:
        print(f"{col}: source=[{source[col].min():.2f},{source[col].max():.2f}] "
              f"train=[{train[col].min():.2f},{train[col].max():.2f}]")
    print()

    print("=== Target prevalence ===")
    print(f"source: {source['addicted_label'].mean():.4f} "
          f"({source['addicted_label'].sum()} / {len(source)})")
    print(f"competition train: {train['addicted_label'].mean():.4f} "
          f"({train['addicted_label'].sum()} / {len(train)})")
    print()

    if "addiction_level" in source.columns:
        print("=== addiction_level <-> addicted_label cross-tab (source) ===")
        print(source.groupby("addiction_level", dropna=False)["addicted_label"]
              .agg(["count", "mean", "min", "max"]))
        print()

    print("=== Missingness in source (shared feature columns) ===")
    print(source[SHARED_FEATURES].isna().sum())
    print()

    print("=== Exact row overlap on shared feature columns ===")
    src_key = source[SHARED_FEATURES].astype(str).agg("|".join, axis=1)
    train_key = set(train[SHARED_FEATURES].astype(str).agg("|".join, axis=1))
    test_key = set(test[SHARED_FEATURES].astype(str).agg("|".join, axis=1))
    print(f"source rows also in competition train: {src_key.isin(train_key).sum()} / {len(src_key)}")
    print(f"source rows also in competition test: {src_key.isin(test_key).sum()} / {len(src_key)}")


def main() -> int:
    kaggle_cli = find_kaggle_cli()
    train = pd.read_csv(REPO_ROOT / "data" / "train.csv")
    test = pd.read_csv(REPO_ROOT / "data" / "test.csv")

    with tempfile.TemporaryDirectory(prefix="s6e8_source_provenance_") as tmp:
        source_csv = download_source(kaggle_cli, Path(tmp))
        source = pd.read_csv(source_csv)
        compare(source, train, test)

    return 0


if __name__ == "__main__":
    sys.exit(main())
