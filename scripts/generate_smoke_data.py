#!/usr/bin/env python3
"""Generate schema-matched smoke data for local pipeline verification.

NOT competition data. Matches column names, dtypes, missingness bands, and
rough marginal distributions documented in docs/3_eda_insights.md so Phase 3
code can be exercised when Kaggle credentials are unavailable.

Usage:
  python3 scripts/generate_smoke_data.py [--n-train 80000] [--n-test 30000]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

NUMERIC = [
    "age",
    "daily_screen_time_hours",
    "social_media_hours",
    "gaming_hours",
    "work_study_hours",
    "sleep_hours",
    "notifications_per_day",
    "app_opens_per_day",
    "weekend_screen_time",
]
CATEGORICAL = ["gender", "stress_level", "academic_work_impact"]
# Approximate train missingness rates from docs/3_eda_insights.md.
MISSING_RATES = {
    "age": 0.04,
    "daily_screen_time_hours": 0.14,
    "social_media_hours": 0.19,
    "gaming_hours": 0.18,
    "work_study_hours": 0.07,
    "sleep_hours": 0.06,
    "notifications_per_day": 0.10,
    "app_opens_per_day": 0.12,
    "weekend_screen_time": 0.16,
    "gender": 0.05,
    "stress_level": 0.08,
    "academic_work_impact": 0.09,
}


def _mask(rng: np.random.Generator, n: int, rate: float) -> np.ndarray:
    return rng.random(n) < rate


def make_frame(n: int, seed: int, start_id: int, with_target: bool) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 36, size=n).astype(float)
    daily = rng.uniform(0.5, 15.0, size=n)
    social = rng.uniform(0.0, 8.0, size=n)
    gaming = rng.uniform(0.0, 4.0, size=n)
    work = rng.uniform(0.0, 6.0, size=n)
    sleep = rng.uniform(4.5, 9.0, size=n)
    notif = rng.integers(20, 251, size=n).astype(float)
    opens = rng.integers(15, 181, size=n).astype(float)
    weekend = daily + rng.normal(0.8, 1.5, size=n)
    weekend = np.clip(weekend, 0.5, 17.5)

    gender = rng.choice(["Female", "Male", "Other"], size=n, p=[0.48, 0.48, 0.04])
    stress = rng.choice(["Low", "Medium", "High"], size=n, p=[0.33, 0.34, 0.33])
    impact = rng.choice(["No", "Yes"], size=n, p=[0.55, 0.45])

    df = pd.DataFrame(
        {
            "id": np.arange(start_id, start_id + n),
            "age": age,
            "daily_screen_time_hours": daily,
            "social_media_hours": social,
            "gaming_hours": gaming,
            "work_study_hours": work,
            "sleep_hours": sleep,
            "notifications_per_day": notif,
            "app_opens_per_day": opens,
            "weekend_screen_time": weekend,
            "gender": gender,
            "stress_level": stress,
            "academic_work_impact": impact,
        }
    )

    if with_target:
        # Screen-time-dominated logit, echoing EDA univariate rankings.
        logit = (
            -4.0
            + 0.45 * daily
            + 0.35 * weekend
            + 0.40 * social
            + 0.15 * gaming
            + 0.10 * work
            - 0.08 * sleep
            + 0.25 * (impact == "Yes").astype(float)
            + np.where(stress == "Medium", -0.35, 0.15)
            + rng.normal(0.0, 1.0, size=n)
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        df["addicted_label"] = (rng.random(n) < prob).astype(int)

    for col, rate in MISSING_RATES.items():
        df.loc[_mask(rng, n, rate), col] = np.nan

    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-train", type=int, default=80_000)
    parser.add_argument("--n-test", type=int, default=30_000)
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    train = make_frame(args.n_train, seed=42, start_id=0, with_target=True)
    test = make_frame(args.n_test, seed=43, start_id=args.n_train, with_target=False)
    sample = test[["id"]].copy()
    sample["addicted_label"] = 0.5

    train.to_csv(args.out_dir / "train.csv", index=False)
    test.to_csv(args.out_dir / "test.csv", index=False)
    sample.to_csv(args.out_dir / "sample_submission.csv", index=False)

    marker = args.out_dir / "SMOKE_DATA_ONLY.txt"
    marker.write_text(
        "Schema-matched synthetic smoke data for pipeline verification only.\n"
        "Replace with real Kaggle playground-series-s6e8 files before any\n"
        "promotion, submission, or portfolio claim.\n"
        f"Generated n_train={args.n_train}, n_test={args.n_test}.\n"
    )
    pos = train["addicted_label"].mean()
    print(f"Wrote {args.out_dir}/train.csv ({len(train):,} rows, pos={pos:.4f})")
    print(f"Wrote {args.out_dir}/test.csv ({len(test):,} rows)")
    print(f"Marker: {marker}")


if __name__ == "__main__":
    main()
