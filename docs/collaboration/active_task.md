# Claude–Codex Active Task Log

This tracked file is the shared handoff and review channel for the current
task. Claude and Codex must read it before starting work. Only one agent
modifies the repository at a time.

## Workflow Rules

1. Work from the shared `main` checkout.
2. Before acting, read `git status`, recent `git log`, the implementation
   plan, and this file.
3. Claude implements and commits one coherent task; Codex reviews without
   editing the implementation.
4. Address review findings in separate commits. Do not amend reviewed
   commits.
5. Do not begin the next task while findings or the user's promotion decision
   remain unresolved.
6. Keep public notebooks and documentation reader-facing; internal agent,
   checklist, and review-log narration belongs only in this collaboration
   log.

## Previous Milestone

Task 2 (tested submission-contract validator) was approved by the user on
2026-08-02. The full discussion is archived at
`docs/collaboration/archive/2026-08-02-task-2-submission-validator.md`.

## Current Task

- Plan: `docs/superpowers/plans/2026-08-01-s6e8-implementation-plan.md`
- Task: Task 3 — Make The Baseline Notebook Submission-Ready
- Status: ready for Claude implementation
- Public promotion required: no; this task only runs both notebook modes
  locally (Kaggle publication is Task 4)
- User decision required after Codex review: yes

## Scope

Give `notebooks/02_baseline_modeling.ipynb` an explicit, reproducible
evaluate/submission mode without changing its trusted OOF result:

- Add an explicit `RUN_MODE: Literal["evaluate", "submission"]`,
  `CHAMPION_NAME`, and `NOTEBOOK_VERSION` to the top configuration cell;
  reject an unsupported `RUN_MODE` immediately.
- Stabilize or retire the logistic-regression sanity baseline: try
  `solver="saga", penalty="l2", C=0.1, max_iter=2_000, random_state=SEED,
  n_jobs=-1`; if it still emits numerical/convergence warnings, set
  `RUN_LOGISTIC = False`, drop it from the trusted comparison table, and
  document it as retired rather than measured.
- Add a single `build_model(name)` factory used by both the evaluation and
  submission paths — no separate model-construction code per mode.
- Add `fit_champion_and_predict(...)`: fit the champion configuration on all
  training rows, predict on test.
- Add `build_submission(...)`: schema-safe submission construction in
  test-row order, validating columns, ID order, finite predictions, and the
  `[0, 1]` range before returning.
- In submission mode, write to `/kaggle/working/submission.csv` if that path
  exists, else `../submission.csv`.
- Do not commit data, submissions, credentials, or generated prediction
  artifacts.

## Required Development Evidence

1. Evaluation mode: `python3 -m jupyter nbconvert --to notebook --execute
   --inplace 02_baseline_modeling.ipynb` exits `0`, no error outputs,
   `nbformat.validate` passes, and the HGB OOF AUC stays within `0.0001` of
   `0.95733` — or the difference is explained (e.g. a dependency/version
   change).
2. Submission mode: run with `RUN_MODE = "submission"`, then
   `python3 scripts/verify_submission.py submission.csv` confirms 296,302
   rows, correctly ordered IDs, and finite probabilities in `[0, 1]`.
3. `RUN_MODE` restored to `"evaluate"` before committing.
4. Confirmation that `build_model` is the single factory both modes call
   (not two separate code paths that happen to agree).
5. The implementation commit hash and clean `git status`.

## Claude Implementation Report

Pending.

## Codex Review

Pending.

## User Promotion Decision

**Approved on 2026-08-02 (Australia/Sydney).**

The user accepted the tested submission validator after Claude implementation
and Codex verification. Task 2 is complete.
