#!/usr/bin/env python3
"""Run Phase 3 hand-designed tuning locally (same configs as the notebook).

Writes a JSON summary to predictions/phase3_hand_tune_summary.json for the
docs ledger. Respects data/SMOKE_DATA_ONLY.txt.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

SEED = 42
N_FOLDS = 5
N_BOOTSTRAP = 2000

NUMERIC_FEATURES = [
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
CATEGORICAL_FEATURES = ["gender", "stress_level", "academic_work_impact"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

V4_CONFIGS = [
    ("v4a_hgb_phase2_ref", "hgb", {"max_iter": 200}),
    ("v4b_hgb_lr05_iter400", "hgb", {"learning_rate": 0.05, "max_iter": 400}),
    ("v4c_hgb_lr05_iter600_leaf31", "hgb", {
        "learning_rate": 0.05, "max_iter": 600, "max_leaf_nodes": 31
    }),
    ("v4d_lgbm_match_hgb", "lgbm", {
        "n_estimators": 200, "num_leaves": 31, "learning_rate": 0.1
    }),
    ("v4e_lgbm_phase2_ref", "lgbm", {
        "n_estimators": 200, "num_leaves": 31, "learning_rate": 0.05
    }),
    ("v4f_lgbm_deeper", "lgbm", {
        "n_estimators": 500, "num_leaves": 63, "learning_rate": 0.05,
        "min_child_samples": 20,
    }),
    ("v4g_lgbm_regularized", "lgbm", {
        "n_estimators": 800, "num_leaves": 31, "learning_rate": 0.03,
        "min_child_samples": 50, "subsample": 0.8, "colsample_bytree": 0.8,
    }),
    ("v4h_lgbm_shallow", "lgbm", {
        "n_estimators": 600, "num_leaves": 15, "learning_rate": 0.05,
        "min_child_samples": 40,
    }),
    ("v4i_cb_match_hgb", "cb", {"iterations": 200, "depth": 6, "learning_rate": 0.1}),
    ("v4j_cb_phase2_ref", "cb", {"iterations": 200, "depth": 6, "learning_rate": 0.05}),
    ("v4k_cb_more_iters", "cb", {"iterations": 600, "depth": 6, "learning_rate": 0.05}),
    ("v4l_cb_deeper", "cb", {"iterations": 400, "depth": 8, "learning_rate": 0.05}),
    ("v4m_cb_shallow_long", "cb", {"iterations": 800, "depth": 4, "learning_rate": 0.03}),
]


def catboost_ready(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in CATEGORICAL_FEATURES:
        out[col] = out[col].astype("object").fillna("missing").astype(str)
    return out


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    daily = out["daily_screen_time_hours"].replace(0, np.nan)
    out["social_to_screen_ratio"] = out["social_media_hours"] / daily
    out["gaming_to_screen_ratio"] = out["gaming_hours"] / daily
    out["time_budget_residual"] = 24 - (
        out["sleep_hours"] + out["work_study_hours"] + out["daily_screen_time_hours"]
    )
    out["weekend_escalation"] = out["weekend_screen_time"] - out["daily_screen_time_hours"]
    return out


def make_fit(family: str, params: dict):
    if family == "hgb":
        def fit_predict(X_tr, y_tr, X_val):
            model = HistGradientBoostingClassifier(
                random_state=SEED, categorical_features="from_dtype", **params
            )
            model.fit(X_tr, y_tr)
            return model.predict_proba(X_val)[:, 1]
        return fit_predict
    if family == "lgbm":
        def fit_predict(X_tr, y_tr, X_val):
            model = LGBMClassifier(random_state=SEED, verbose=-1, **params)
            model.fit(X_tr, y_tr, categorical_feature=CATEGORICAL_FEATURES)
            return model.predict_proba(X_val)[:, 1]
        return fit_predict
    if family == "cb":
        def fit_predict(X_tr, y_tr, X_val):
            model = CatBoostClassifier(
                random_seed=SEED,
                cat_features=CATEGORICAL_FEATURES,
                verbose=False,
                **params,
            )
            model.fit(catboost_ready(X_tr), y_tr)
            return model.predict_proba(catboost_ready(X_val))[:, 1]
        return fit_predict
    raise ValueError(family)


def run_cv(name, fit_predict, X_df, y_ser, results, oof_store):
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof = np.zeros(len(X_df), dtype=float)
    fold_aucs = []
    t0 = time.time()
    for fold, (tr, va) in enumerate(skf.split(X_df, y_ser), start=1):
        pred = fit_predict(X_df.iloc[tr], y_ser.iloc[tr], X_df.iloc[va])
        oof[va] = pred
        fold_aucs.append(roc_auc_score(y_ser.iloc[va], pred))
    oof_auc = roc_auc_score(y_ser, oof)
    row = {
        "name": name,
        "oof_auc": float(oof_auc),
        "fold_auc_mean": float(np.mean(fold_aucs)),
        "fold_auc_std": float(np.std(fold_aucs, ddof=1)),
        "fold_aucs": [float(a) for a in fold_aucs],
        "elapsed_sec": float(time.time() - t0),
    }
    results.append(row)
    oof_store[name] = oof
    print(
        f"{name}: OOF={oof_auc:.5f} fold_std={row['fold_auc_std']:.5f} "
        f"time={row['elapsed_sec']:.1f}s"
    )
    return oof


def paired_bootstrap_auc_delta(y_true, pred_a, pred_b, n_boot=N_BOOTSTRAP, seed=SEED):
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    n = len(y_true)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if y_true[idx].min() == y_true[idx].max():
            continue
        deltas.append(
            roc_auc_score(y_true[idx], pred_b[idx])
            - roc_auc_score(y_true[idx], pred_a[idx])
        )
    deltas = np.asarray(deltas)
    return {
        "mean_delta": float(deltas.mean()),
        "ci_low": float(np.quantile(deltas, 0.025)),
        "ci_high": float(np.quantile(deltas, 0.975)),
        "p_positive": float((deltas > 0).mean()),
        "n_boot_used": int(len(deltas)),
    }


def fold_auc_deltas(y_true, pred_a, pred_b):
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    out = []
    for _, va in skf.split(np.zeros(len(y_true)), y_true):
        out.append(
            roc_auc_score(y_true.iloc[va], pred_b[va])
            - roc_auc_score(y_true.iloc[va], pred_a[va])
        )
    return out


def family_of(name: str) -> str | None:
    if "hgb" in name:
        return "hgb"
    if "lgbm" in name:
        return "lgbm"
    if "_cb_" in name:
        return "cb"
    return None


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    smoke = (data_dir / "SMOKE_DATA_ONLY.txt").exists()
    train = pd.read_csv(data_dir / "train.csv")
    for col in CATEGORICAL_FEATURES:
        train[col] = train[col].astype("category")
    X = train[ALL_FEATURES]
    y = train["addicted_label"]

    results: list[dict] = []
    oof_store: dict[str, np.ndarray] = {}

    print(f"train={len(train):,} pos={y.mean():.4f} smoke={smoke}")
    for name, family, params in V4_CONFIGS:
        run_cv(name, make_fit(family, params), X, y, results, oof_store)

    # Engineered A/B on best hand-tuned config.
    best = max(results, key=lambda r: r["oof_auc"])
    best_cfg = next(c for c in V4_CONFIGS if c[0] == best["name"])
    _, fam, params = best_cfg
    eng_name = f"{best['name']}_plus_engineered"
    run_cv(eng_name, make_fit(fam, params), add_engineered_features(X), y, results, oof_store)
    eng = next(r for r in results if r["name"] == eng_name)
    print(f"Engineered delta: {eng['oof_auc'] - best['oof_auc']:+.6f}")

    champion = max(results, key=lambda r: r["oof_auc"])
    ranked = sorted(results, key=lambda r: r["oof_auc"], reverse=True)
    second = ranked[1]
    gate_rows = []
    for chall in [second]:
        boot = paired_bootstrap_auc_delta(
            y.to_numpy(), oof_store[champion["name"]], oof_store[chall["name"]]
        )
        # chall relative to champion: recompute with pred_b=chall, pred_a=champ
        # (already that order above — wait, that gives chall-champ only if we swap)
        boot = paired_bootstrap_auc_delta(
            y.to_numpy(), oof_store[champion["name"]], oof_store[chall["name"]]
        )
        # Actually pred_b - pred_a with a=champ, b=chall => chall - champ. Good.
        # But if chall is second place, delta should be negative.
        fold_d = fold_auc_deltas(y, oof_store[champion["name"]], oof_store[chall["name"]])
        gate_rows.append({
            "candidate": chall["name"],
            "candidate_oof": chall["oof_auc"],
            "delta_vs_champion": chall["oof_auc"] - champion["oof_auc"],
            "boot_mean_delta": boot["mean_delta"],
            "boot_ci_low": boot["ci_low"],
            "boot_ci_high": boot["ci_high"],
            "boot_p_positive": boot["p_positive"],
            "fold_deltas": [round(d, 6) for d in fold_d],
            "n_folds_positive": int(sum(d > 0 for d in fold_d)),
        })

    by_family_rows: dict[str, list[dict]] = {"hgb": [], "lgbm": [], "cb": []}
    for r in results:
        fam = family_of(r["name"])
        if fam and "engineered" not in r["name"]:
            by_family_rows[fam].append(r)
    # Full min-max spread (includes failed configs) — diagnostic only.
    family_spreads = {
        fam: float(max(r["oof_auc"] for r in rows) - min(r["oof_auc"] for r in rows))
        for fam, rows in by_family_rows.items()
        if len(rows) >= 2
    }
    # Headroom = best − second-best within family. A weak failed config must
    # not open Optuna; only a still-contested top of the hand grid does.
    family_top_gaps = {}
    for fam, rows in by_family_rows.items():
        if len(rows) < 2:
            continue
        ordered = sorted((r["oof_auc"] for r in rows), reverse=True)
        family_top_gaps[fam] = float(ordered[0] - ordered[1])
    fold_noise = champion["fold_auc_std"]
    optuna_justified = bool(
        family_top_gaps
        and max(family_top_gaps.values()) > max(0.0010, 1.5 * fold_noise)
    )

    top_by_family = {}
    for fam in ("hgb", "lgbm", "cb"):
        rows = [
            r for r in results
            if family_of(r["name"]) == fam and "engineered" not in r["name"]
        ]
        if rows:
            top_by_family[fam] = max(rows, key=lambda r: r["oof_auc"])

    corrs = []
    fams = list(top_by_family)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            a = oof_store[top_by_family[fams[i]]["name"]]
            b = oof_store[top_by_family[fams[j]]["name"]]
            corrs.append({
                "a": fams[i],
                "b": fams[j],
                "corr": float(np.corrcoef(a, b)[0, 1]),
            })
    ensemble_justified = False
    if len(top_by_family) >= 2 and not smoke:
        best_two = sorted(top_by_family.values(), key=lambda r: r["oof_auc"], reverse=True)[:2]
        gap = best_two[0]["oof_auc"] - best_two[1]["oof_auc"]
        min_corr = min(c["corr"] for c in corrs)
        ensemble_justified = bool(min_corr < 0.98 and gap < 0.002)

    summary = {
        "data_is_smoke": smoke,
        "n_train": int(len(train)),
        "positive_rate": float(y.mean()),
        "results": results,
        "champion": champion["name"],
        "champion_oof": champion["oof_auc"],
        "gate_rows": gate_rows,
        "family_spreads": family_spreads,
        "family_top_gaps": family_top_gaps,
        "fold_noise": fold_noise,
        "optuna_justified": optuna_justified,
        "xgboost_justified": False,
        "ensemble_justified": ensemble_justified,
        "family_oof_correlations": corrs,
        "top_by_family": {k: v["name"] for k, v in top_by_family.items()},
    }

    out_dir = root / "predictions"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "phase3_hand_tune_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {out_path}")
    print(f"Champion: {champion['name']} OOF={champion['oof_auc']:.5f}")
    print(f"Optuna justified: {optuna_justified}")
    print(f"Ensemble justified: {ensemble_justified}")
    print(f"Family spreads: {family_spreads}")


if __name__ == "__main__":
    main()
