# Claude–Codex Active Task Log

This file is the shared handoff and review channel for the current task.
Only one agent modifies the repository at a time.

## Workflow Rules

1. Work from shared `main`; inspect status/log first.
2. Claude implements and commits; Codex independently reviews.
3. Use separate fix commits; never amend reviewed commits or use destructive
   checkout/reset restoration.
4. Keep the canonical notebook source-only until a trusted public run.
5. Keep generated OOF arrays, predictions, submissions, data, logs, and
   credentials uncommitted.
6. Private Kaggle experimentation is allowed; public publication and
   leaderboard submission are not authorized in this task.

## Previous Milestone

Task 5 was approved on 2026-08-02. The discussion is archived at
`docs/collaboration/archive/2026-08-02-task-5-gbdt-tuning.md`.

Working champion:

- Model: `lightgbm_tuned` (`e01_lightgbm_c3`)
- Config: 400 estimators, learning rate 0.05, 63 leaves, seed 42
- OOF AUC: `0.96166`
- Close tuned HGB candidate: `e01_hgb_c3`, OOF AUC `0.96139`
- Difference: approximately `0.00027`, not yet directly confirmed

## Current Task

- Plan: `docs/superpowers/plans/2026-08-01-s6e8-implementation-plan.md`
- Task: Task 6 — Conditional Diversity And Ensemble Pass
- Status: ready for Claude implementation

## Entry Check — Must Run First

Recreate aligned OOF predictions for only the promoted LightGBM c3 and tuned
HGB c3 on the same fixed folds. Report:

- exact fold AUCs and fold-by-fold deltas;
- direct paired row-bootstrap delta and limitations;
- Pearson and Spearman prediction correlation;
- top- and bottom-decile ranking disagreement;
- complementary residual/error evidence.

Proceed beyond this check only if the models are both strong and have
correlation below `0.995` with meaningful complementary residuals. Otherwise
record a skip decision to protect the time budget.

## Conditional Scope

If the entry condition passes:

1. Write E02's diversity hypothesis before results.
2. Evaluate at most one XGBoost family with no more than four hand-designed
   configurations; do not use Optuna.
3. Report standalone AUC, Pearson/Spearman correlation, and top/bottom-decile
   disagreement for each serious challenger.
4. Sweep exactly 21 convex blend weights for justified pairs.
5. Compare the selected blend directly against `lightgbm_tuned` with paired
   evidence. A grid-best score without paired support is rejected.

If the entry condition fails, do not run XGBoost or a blend sweep.

## Required Evidence

- Fixed-fold and OOF-alignment proof.
- Exact configurations and run venue/version/log fingerprint.
- Complete direct-comparison and, if applicable, blend tables.
- Explicit selection/refit/multiple-comparison caveats.
- Source-only valid notebook, reader-facing ledger update, clean status, and
  no generated artifacts.
- A decision to promote a blend/challenger or retain `lightgbm_tuned`.

## Claude Implementation Report

Pending.

## Codex Review

Pending.

## User Promotion Decision

Pending.
