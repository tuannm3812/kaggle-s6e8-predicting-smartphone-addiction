# Cursor–Claude–Codex Active Task Log

This file is the shared handoff and review channel for the current task.
Only one agent modifies the repository at a time.

## Workflow Rules

1. Work from shared `main`; inspect status/log first.
2. **Roles (effective 2026-08-05):** Cursor implements and commits.
   Claude reviews independently, then Codex reviews independently. Both
   review passes must be addressed before the user makes a promotion
   decision. (Tasks 1–6 above this line were implemented by Claude under
   the prior arrangement — Claude was implementer, Codex was sole
   reviewer. That history stands as-is; only new work follows the roles
   above.)
3. Use separate fix commits; never amend reviewed commits or use destructive
   checkout/reset restoration.
4. Keep the canonical notebook source-only until a trusted public run.
5. Keep generated OOF arrays, predictions, submissions, data, logs, and
   credentials uncommitted.
6. Private Kaggle experimentation is allowed; public publication and
   leaderboard submission are not authorized without an explicit user
   go-ahead for that specific artifact.
7. Do not begin the next task while a prior task's review or the user's
   promotion decision remains unresolved.

## Branch Note (2026-08-05)

A separate branch, `cursor/phase3-tuning-16f2`, contains independent prior
work by Cursor with its own "Phase 1/2/3" structure and doc set
(`docs/4_codex_claude_review_log.md`, `docs/7_model_optimization_and_
ensemble.md`, `docs/10_leaderboard_improvement_insights.md`), diverged from
this line of work on 2026-08-01. It is **not merged and not in use** —
`main` (this file's branch) is the authoritative line of work going
forward. That branch's uncommitted changes are preserved in a git stash on
that branch (not on `main`), untouched. Cursor should work from `main` and
this file for all new tasks; do not pull work from
`cursor/phase3-tuning-16f2` without an explicit user decision to reconcile
the two histories.

## Previous Milestone

Task 6 was approved on 2026-08-05. The discussion is archived at
`docs/collaboration/archive/2026-08-05-task-6-conditional-diversity.md`.

Working champion (unchanged by Task 6 SKIP):

- Model: `lightgbm_tuned` (`e01_lightgbm_c3`)
- Config: 400 estimators, learning rate 0.05, 63 leaves, seed 42
- OOF AUC: `0.96166`
- Close tuned HGB candidate (not combined): `e01_hgb_c3`, OOF AUC `0.96139`
- Diversity entry check: Pearson `0.997563` (fails `< 0.995`); error-set
  Jaccard `0.8772` (passes `<= 0.90`) → **SKIP** conditional ensemble scope

## Current Task

- Plan: `docs/superpowers/plans/2026-08-01-s6e8-implementation-plan.md`
- Task: Task 7 — Publish Champion And Close The Project
- Status: **open for Cursor implementation**
- Implementer: Cursor (Claude then Codex review after the implementation report)
- Public promotion / leaderboard submission: **not** authorized until the
  user explicitly approves the exact public artifact (workflow rule 6;
  plan step 4)

### Champion to publish

Confirmed from the Task 6 promotion decision:

- `CHAMPION_NAME = "lightgbm_tuned"`
- `LGBMClassifier(n_estimators=400, learning_rate=0.05, num_leaves=63,
  random_state=42)` via `LGBM_CONFIGS[2]` / `build_model("lightgbm_tuned")`
- OOF AUC `0.96166`

### Files

Modify `notebooks/02_baseline_modeling.ipynb`, `docs/7_kaggle_run_manifest.md`,
`docs/8_submission_manifest.md`; create `docs/10_final_lessons.md` (not the
unrelated `docs/10_leaderboard_improvement_insights.md` on
`cursor/phase3-tuning-16f2`); modify `README.md`.

### Steps (from the plan)

1. Freeze the champion configuration: set `CHAMPION_NAME`, exact parameters,
   `RUN_MODE = "submission"`, seed, and `NOTEBOOK_VERSION` in one
   configuration cell. Disable rejected experiment blocks without deleting
   their documented results.
2. Run locally and validate: execute the notebook, validate notebook JSON,
   run `scripts/verify_submission.py submission.csv`. All checks must pass.
3. Push and rerun publicly: push the baseline kernel (the *public* one,
   `scripts/push_kaggle_kernel.sh baseline` — not the private `experiments`
   kernel used for Tasks 5–6), wait for completion, download its output, run
   the independent validator against the Kaggle-generated artifact.
4. Submit the exact reviewed artifact only after the user explicitly
   authorizes that specific submission. Record its notebook URL/version and
   public score in both manifests immediately.
5. Write `docs/10_final_lessons.md`: final OOF and public scores; accepted
   and rejected hypotheses; local/Kaggle reproducibility findings;
   limitations and private-leaderboard risks; explicit reason further
   experiments were stopped (the Task 6 SKIP rationale).
6. Update `README.md`: `Current Result`, `What Worked`, `Final Modeling
   Decision`, public notebook links, documentation map. Exact metrics only,
   no unverified rank claims.
7. Final verification:
   ```bash
   pytest tests/test_verify_submission.py -v
   python3 -c "import nbformat; [nbformat.validate(nbformat.read(p, 4)) for p in ['notebooks/01_eda.ipynb', 'notebooks/02_baseline_modeling.ipynb']]"
   git diff --check
   git status --short
   ```
   Expected: tests pass, notebooks validate, no whitespace errors, only
   intended final documentation/notebook changes remain.
8. Commit, append an implementation report to this file, and stop for
   Claude's review, then Codex's, then the user's final approval.
   ```bash
   git add README.md notebooks/02_baseline_modeling.ipynb docs/7_kaggle_run_manifest.md docs/8_submission_manifest.md docs/10_final_lessons.md
   git commit -m "docs(project): freeze final S6E8 champion"
   ```

**Do not** submit to the competition leaderboard without the user's explicit
go-ahead on the exact artifact — steps 1–3 and 5–7 do not require that
authorization; step 4 does.

## Cursor Implementation Report

Pending.
