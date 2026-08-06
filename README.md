# Predicting Smartphone Addiction

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Playground%20Series%20S6E8-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/playground-series-s6e8)
[![Modeling Phase](https://img.shields.io/badge/Modeling%20Phase-Champion%20Frozen-blue)](docs/10_final_lessons.md)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](requirements.txt)

Kaggle Playground Series S6E8 — predict smartphone addiction (ROC AUC):
https://www.kaggle.com/competitions/playground-series-s6e8

Public-notebook-first workflow: notebooks are executable sources of truth;
`docs/` records rationale, validation, and submission evidence.

## Current Result

| Item | Value |
| --- | --- |
| Working champion | `lightgbm_tuned` (`e01_lightgbm_c3`) |
| Config | `LGBMClassifier(n_estimators=400, learning_rate=0.05, num_leaves=63, random_state=42)` |
| OOF AUC | **0.96166** (5-fold stratified, seed 42) |
| First public baseline (HGB) | Public AUC **0.95865** (OOF 0.95733) |
| Champion public AUC | **0.96286** (submitted 2026-08-06 from public kernel v2) |

Deadline: **2026-08-31 23:59 UTC**. Exact metrics only — no unverified rank claims.

## Final Modeling Decision

Promote tuned LightGBM over the untuned HGB floor after comparable hand-designed
search with a paired-bootstrap promotion gate (`docs/9_experiment_ledger.md`).
Stop further diversity/ensemble work after Task 6: champion vs tuned HGB
Pearson correlation `0.997563` failed the predeclared `< 0.995` entry bar
(SKIP). Details: `docs/10_final_lessons.md`.

## What Worked

- Fixed folds + aligned OOF for every comparable model.
- Budget-aligned HGB / LightGBM / CatBoost grid (E01) instead of mismatched
  “strong model” defaults.
- Paired bootstrap + fold-consistency gate before champion changes.
- Private GPU kernel for search; public kernel for milestone submission-mode
  artifacts with log fingerprints and `scripts/verify_submission.py`.
- Explicit diversity entry check before spending budget on blends.

## Public Notebooks

- [EDA](https://www.kaggle.com/code/tuannm3812/smartphone-addiction-eda)
- [Baseline modeling](https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling)
  (v1 HGB public 0.95865; v2 `lightgbm_tuned` public **0.96286**)

## Repository Structure

- `docs/`: competition notes, EDA, modeling decisions, manifests, lessons.
- `notebooks/`: sources of truth, plus `notebooks/kernels/` push metadata.
- `scripts/`: `push_kaggle_kernel.sh <eda|baseline|experiments>`,
  `verify_submission.py`, provenance helpers.
- `data/`, `predictions/`, `scratch/`: local / generated, gitignored.

## Documentation Map

- [`docs/0_coding_standards.md`](docs/0_coding_standards.md) — project standards
- [`docs/1_instructions.md`](docs/1_instructions.md) — competition facts
- [`docs/2_implementation_plan.md`](docs/2_implementation_plan.md) — phased plan
- [`docs/3_eda_insights.md`](docs/3_eda_insights.md) — EDA findings
- [`docs/5_source_dataset_provenance.md`](docs/5_source_dataset_provenance.md) — source data
- [`docs/6_baseline_modeling.md`](docs/6_baseline_modeling.md) — early baselines
- [`docs/7_kaggle_run_manifest.md`](docs/7_kaggle_run_manifest.md) — Kaggle run evidence
- [`docs/8_submission_manifest.md`](docs/8_submission_manifest.md) — leaderboard rows
- [`docs/9_experiment_ledger.md`](docs/9_experiment_ledger.md) — E01/E02 ledger
- [`docs/10_final_lessons.md`](docs/10_final_lessons.md) — closeout narrative
- [`docs/collaboration/`](docs/collaboration/) — active task + archives
- [`docs/archive/4_codex_claude_review_log.md`](docs/archive/4_codex_claude_review_log.md) — early review log
