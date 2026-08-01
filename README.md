# Predicting Smartphone Addiction

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Playground%20Series%20S6E8-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/playground-series-s6e8)
[![Modeling Phase](https://img.shields.io/badge/Modeling%20Phase-EDA%20Complete-blue)](docs/2_implementation_plan.md)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](requirements.txt)

Kaggle Playground Series S6E8 project for predicting smartphone addiction:
https://www.kaggle.com/competitions/playground-series-s6e8

This repository uses a public-notebook-first Kaggle workflow. The notebooks
generate reproducible outputs, while `docs/` records the modeling rationale,
validation checks, leaderboard submissions, and next-step strategy.

## Status

Planning and EDA complete (2026-08-01); baseline modeling not yet started.
Deadline: **2026-08-31 23:59 UTC**. Evaluation metric confirmed as ROC AUC.
See `docs/2_implementation_plan.md` for the full phased plan,
`docs/1_instructions.md` for competition facts, and `docs/3_eda_insights.md`
for EDA findings. `docs/4_codex_claude_review_log.md` records an in-progress
Codex/Claude collaborative review of the plan and EDA before baseline
modeling starts.

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
