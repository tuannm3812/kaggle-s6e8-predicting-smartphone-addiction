# Model Optimization And Ensemble

Phase 3 of `docs/2_implementation_plan.md`. Started 2026-08-04 on branch
`cursor/phase3-tuning-16f2`.

## Status

**Code ready; competition OOF pending a local re-run with real Kaggle data.**

The cloud agent that scaffolded this phase could not read Mac-local credentials
at `/Users/tuannm3812/Documents/GitHub/2. Kaggle`. Pipeline verification used
schema-matched smoke data only (`data/SMOKE_DATA_ONLY.txt`). Those AUCs must
not be treated as competition results.

## What Was Implemented

1. **Hand-designed search** in `notebooks/02_baseline_modeling.ipynb` (§10–13)
   and the local runner `scripts/run_phase3_hand_tune.py` — same 13 configs:
   3× HGB, 5× LightGBM, 5× CatBoost, aligned learning rates / iteration
   budgets (addresses `docs/6_baseline_modeling.md` §8).
2. **Engineered-feature A/B** on the best hand-tuned config.
3. **Paired-bootstrap promotion gate** + fold-consistency check (replaces the
   borrowed `+0.0002` threshold).
4. **Evidence gates** for Optuna / XGBoost / ensemble (off by default;
   Optuna opens only when best−second-best *within a family* exceeds fold
   noise — a weak failed config alone does not open it).
5. Helpers: `scripts/download_competition_data.sh`,
   `scripts/generate_smoke_data.py`.

## How To Finish On Desktop (Cursor IDE)

```bash
# 1. Pull this branch
git fetch origin
git checkout cursor/phase3-tuning-16f2

# 2. Point Kaggle CLI at tuannm3812 credentials
mkdir -p ~/.kaggle
cp "/Users/tuannm3812/Documents/GitHub/2. Kaggle/<tuannm3812-json>" ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
# or: export KAGGLE_USERNAME=tuannm3812 KAGGLE_KEY=...

# 3. Replace smoke data with competition files
bash scripts/download_competition_data.sh
# confirm data/SMOKE_DATA_ONLY.txt is gone

# 4. Re-run Phase 3 on real data
python3 scripts/run_phase3_hand_tune.py
# and/or execute notebooks/02_baseline_modeling.ipynb with
# RUN_V4_* flags True (Phase 2 flags can stay False)

# 5. Write real numbers into this doc + docs/10_..., then Codex review
```

## Smoke-Only Pipeline Check (not competition claims)

On 80k-row synthetic smoke data the runner completed end-to-end; champion was
a CatBoost shallow/long config, engineered features were slightly negative,
ensemble gate stayed closed. **Discard these numbers after the real re-run.**

## Next After Real OOF

Record accepted/rejected rows in `docs/10_leaderboard_improvement_insights.md`,
apply Optuna/XGBoost/ensemble only if gates open, then Phase 4 first
hypothesis-gated submission.
