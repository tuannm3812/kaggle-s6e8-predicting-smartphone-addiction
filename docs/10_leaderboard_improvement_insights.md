# Leaderboard Improvement Insights

Experiment ledger for Phases 3–5. Findings first; exact OOF numbers only from
competition-data runs.

## Convention

| Column | Meaning |
| --- | --- |
| Decision | `accepted` / `rejected` / `pending_real_data` |
| Evidence | OOF AUC, fold std, paired-bootstrap CI / P(Δ>0), fold-consistency |

## Phase 3 — Hand-Designed Search

| Experiment | Decision | Evidence |
| --- | --- | --- |
| v4 hand grid (HGB / LGBM / CatBoost, 13 configs) | `pending_real_data` | Code in `02_baseline_modeling.ipynb` §10 + `scripts/run_phase3_hand_tune.py`. Smoke verification only on 2026-08-04. |
| Engineered A/B on best v4 | `pending_real_data` | Same runner; Phase 2 had +0.0005 on real data (below fold std). |
| Optuna | `pending` | Opens only if best−second-best within a family exceeds fold noise on **real** data. |
| XGBoost challenger | `pending` | Only if complementary residuals vs LGBM/CatBoost. |
| Ensemble blend | `pending` | Only if top families close in OOF and not near-collinear. |

## Phase 2 Carry-Forward (real data, 2026-08-01)

| Experiment | Decision | Evidence |
| --- | --- | --- |
| `v1c_hist_gradient_boosting` | accepted as Phase 2 floor / interim leader | OOF AUC **0.95733**, fold std 0.00076 |
| `_is_missing` flags | rejected | Δ +0.000004 vs native NaN LGBM |
| `class_weight=balanced` | rejected | Δ −0.000169 |
| Engineered pack (v3) | open candidate | Δ +0.000529 (< fold std) |
| Untuned LGBM/CatBoost vs HGB | not a family verdict | mismatched LR/budget; motivates Phase 3 |
