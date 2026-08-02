# Claude–Codex Active Task Log

This file is the shared handoff and review channel for the current task.
Only one agent modifies the repository at a time.

## Workflow Rules

1. Work from the shared `main` checkout and inspect status/log first.
2. Claude implements and commits; Codex independently reviews.
3. Use separate fix commits; do not amend reviewed commits.
4. Never use checkout/reset restoration in the shared checkout.
5. Keep public artifacts reader-facing and keep generated OOF arrays,
   predictions, data, submissions, and credentials uncommitted.
6. Do not publish or submit another Kaggle artifact in this task.

## Previous Milestone

Task 4 established the first public leaderboard baseline and was completed on
2026-08-02. The discussion is archived at
`docs/collaboration/archive/2026-08-02-task-4-public-baseline.md`.

Baseline evidence:

- HGB OOF AUC: `0.95733`
- Public AUC: `0.95865`
- Public-minus-OOF: `+0.00132`
- Public notebook: https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling

## Current Task

- Plan: `docs/superpowers/plans/2026-08-01-s6e8-implementation-plan.md`
- Task: Task 5 — Run Comparable Hand-Designed Tuning
- Status: ready for Claude implementation
- Public publication/submission: not authorized in this task

## Scope

1. Create `docs/9_experiment_ledger.md` and write the E01 hypothesis before
   recording results.
2. Add no more than four compact configurations per HGB, LightGBM, and
   CatBoost family, using comparable boosting budgets. Do not use Optuna.
3. Reuse the exact seeded five-fold splits and aligned OOF row order.
4. Add the deterministic stratified paired AUC bootstrap from the plan with
   200 resamples, sample size 100,000, and seed 42.
5. Report configuration, overall and fold AUCs, runtime, paired delta and 95%
   interval versus HGB, probability of positive delta, and prediction
   correlation.
6. Promote only with positive fold consistency and persuasive paired
   evidence; otherwise retain HGB and record every rejection.
7. Preserve `RUN_MODE = "evaluate"`, public-facing prose quality, and the
   submission-mode contract established in Task 3.

## Required Evidence

- Exact configuration dictionaries and experiment budget.
- Confirmation of identical folds and OOF alignment across candidates.
- Notebook validation, sequential execution counts, and zero error outputs.
- Complete experiment table and paired-bootstrap parameters/results.
- A reasoned promotion or retention decision tied to the predeclared gate.
- Commit hash, exact file list, clean status, and no generated artifacts.

## Claude Implementation Report

Pending.

## Codex Review

Pending.

## User Promotion Decision

Pending.
