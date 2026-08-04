# Predicting Smartphone Addiction

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Playground%20Series%20S6E8-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/playground-series-s6e8)
[![Modeling Phase](https://img.shields.io/badge/Modeling%20Phase-Baseline%20Complete-blue)](docs/2_implementation_plan.md)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](requirements.txt)

Kaggle Playground Series S6E8 project for predicting smartphone addiction:
https://www.kaggle.com/competitions/playground-series-s6e8

This repository uses a public-notebook-first Kaggle workflow. The notebooks
generate reproducible outputs, while `docs/` records the modeling rationale,
validation checks, leaderboard submissions, and next-step strategy.

## Status

Planning, EDA, and baseline modeling complete (2026-08-01). Phase 3
hand-designed tuning is **scaffolded** on branch `cursor/phase3-tuning-16f2`
(`docs/7_model_optimization_and_ensemble.md`) and needs a **local re-run on
real competition data** before any promotion decision. Deadline:
**2026-08-31 23:59 UTC**. Evaluation metric confirmed as ROC AUC. Current
best *competition* OOF AUC: **0.9573** (untuned
`HistGradientBoostingClassifier` — see `docs/6_baseline_modeling.md`). See
`docs/2_implementation_plan.md` for the phased plan,
`docs/4_codex_claude_review_log.md` for the Codex/Claude review, and
`docs/10_leaderboard_improvement_insights.md` for the experiment ledger.

## Repository Structure

- `docs/`: competition notes, EDA findings, modeling decisions, submission
  manifest, and next-step strategy.
- `notebooks/`: executable Kaggle/local notebooks, plus `notebooks/kernels/`
  holding each notebook's Kaggle push config.
- `scripts/`: `push_kaggle_kernel.sh <eda|baseline>`, a one-command wrapper
  around `kaggle kernels push` for each notebook.
- `data/`: local competition files, intentionally ignored.
- `predictions/`: OOF/test prediction matrices, intentionally ignored.
- `scratch/`: temporary helper scripts and automation, intentionally ignored.

## Documentation Map

- [`docs/0_coding_standards.md`](docs/0_coding_standards.md): project-specific
  standards on top of the shared baseline.
- [`docs/1_instructions.md`](docs/1_instructions.md): official task, metric,
  files, and deadline.
- [`docs/2_implementation_plan.md`](docs/2_implementation_plan.md): the
  phased day-1 plan from EDA through final submission.

Further docs (`3_eda_insights.md` onward) are created as each phase produces
results — see the table at the end of `docs/2_implementation_plan.md`.
