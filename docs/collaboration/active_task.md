# Claude–Codex Active Task Log

This tracked file is the shared handoff and review channel for the current
task. Claude and Codex must read it before starting work. Only one agent
modifies the repository at a time.

## Workflow Rules

1. Work from the shared `main` checkout and inspect status/log before acting.
2. Claude implements and commits; Codex reviews without editing the
   implementation.
3. Address findings in separate commits; do not amend reviewed commits.
4. Never use `git checkout --`, reset, or another destructive restoration
   command in the shared checkout. Use a temporary copy or explicit patch.
5. Keep public notebooks and documentation self-contained and reader-facing.
6. Do not submit any artifact to the competition leaderboard until Codex has
   reviewed the exact Kaggle-generated file and the user explicitly approves
   that submission.

## Previous Milestone

Task 3 was approved on 2026-08-02. The full discussion is archived at
`docs/collaboration/archive/2026-08-02-task-3-submission-ready-baseline.md`.

## Current Task

- Plan: `docs/superpowers/plans/2026-08-01-s6e8-implementation-plan.md`
- Task: Task 4 — Publish Baseline And Establish The First Score
- Status: ready for Claude implementation through the pre-submission gate
- Public notebook publication authorized: yes
- Competition submission authorized now: no; exact-artifact approval required

## Scope Before The User Submission Gate

1. Address the two public-wording follow-ups from Task 3 before publication:
   label fit times as reference/local timings that vary with system load, and
   replace “can never silently diverge” with precise estimator-configuration
   parity language.
2. Create a promoted notebook copy/configuration with:
   `RUN_MODE = "submission"`,
   `CHAMPION_NAME = "hist_gradient_boosting"`, and the recorded
   `NOTEBOOK_VERSION`.
3. Verify `notebooks/kernels/baseline_modeling/kernel-metadata.json` is
   public, internet-disabled, and attached only to the S6E8 competition.
4. Push the public baseline notebook and wait for Kaggle status `complete`.
5. Download the Kaggle-generated `submission.csv` to a temporary directory.
6. Validate that exact file with `scripts/verify_submission.py` against the
   local test/sample contract.
7. Update `docs/7_kaggle_run_manifest.md` and create
   `docs/8_submission_manifest.md` with actual URL, version, runtime,
   environment, OOF AUC, artifact checks, and pending submission status.
8. Commit the reviewed public-run evidence and append Claude's report here.

Do not commit the submission CSV, prediction arrays, data, or credentials.
Do not call `kaggle competitions submit` during this phase.

## Required Evidence

- Public notebook URL, Kaggle version, UTC execution timestamp, and final
  `complete` status.
- Downloaded artifact path in a temporary directory and validator output:
  296,302 rows, exact IDs/order, finite probabilities within `[0, 1]`.
- Confirmation that the published notebook uses the shared champion factory
  and submission mode.
- Public prose sweep showing no internal agent/review/checklist narration.
- Exact file list and commit hash, plus clean repository status.
- A clear stop at the leaderboard submission gate.

## Claude Implementation Report

Pending.

## Codex Review And Exact-Artifact Gate

Pending.

## User Leaderboard Submission Decision

Pending.

## Leaderboard Result

Pending; record only after an explicitly approved submission finishes.
