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

**Status: complete — entry check ran, result is SKIP. Conditional scope
(Steps 2–5: XGBoost, blend sweep) not implemented, per the plan's own
entry-condition gate.**
**Commits: `f5a81c8` (hypothesis + code, before any run), `71ae1d5`
(results)**

### Entry check implementation

Added Section 10 to `notebooks/02_baseline_modeling.ipynb`: recreates
`e02_lightgbm_tuned` and `e02_hgb_c3` (same `LGBM_CONFIGS[2]`/
`HGB_CONFIGS[2]` dictionaries Section 9 uses — not duplicated literals)
under fresh names, then reports fold-by-fold deltas, a direct paired
bootstrap between the two candidates themselves, Pearson and Spearman
correlation, top/bottom-decile ranking disagreement, and a 0.5-threshold
error-set Jaccard overlap. `docs/9_experiment_ledger.md`'s E02 section
predeclares the recreation method, which correlation metric the `0.995`
threshold applies to, and a concrete operationalization of "meaningful
complementary residuals" (error-set Jaccard `<= 0.90`) — the plan itself
does not give a numeric definition for that term, so I defined one before
running rather than judging it post-hoc.

**Provenance fix applied proactively:** committed the hypothesis and code
(`f5a81c8`) *before* pushing to Kaggle, and the results (`71ae1d5`) in a
separate commit afterward — directly addressing the same class of finding
Codex raised in Task 5's re-review (there, the E01 hypothesis and first
results entered git in the same commit, so ordering wasn't provable from
history alone). This time it genuinely is.

### Run and evidence

Pushed to the same private Kaggle kernel (version 4). This run also
re-executed the full E01 search from scratch (`RUN_MODE = "evaluate"`
runs everything unconditionally), so it took ~80 minutes like versions
1–3; all 12 E01 candidates' numbers matched version 3 exactly — an
incidental third-time reproducibility confirmation, not something I set
out to re-verify.

- Kaggle kernel status: `complete`, 0 errors.
- Log: 15,303 bytes, SHA-256
  `f3cd078e5e58f76104b0f92e28e2befeec8ac84f89876077007dcf8544fab8ed`.
- Both `e02_*` candidates' fold AUCs are byte-identical to their `e01_*`
  counterparts from prior versions.

### Results

- Direct paired bootstrap (lightgbm vs. hgb): mean delta `+0.000267`,
  95% interval `[0.000140, 0.000410]` (entirely positive), 200/200
  resamples positive.
- Pearson correlation `0.997563` — **fails** the `< 0.995` threshold.
- Error-set Jaccard overlap `0.8772` — **passes** the `<= 0.90` threshold.
- Fold-by-fold: LightGBM ahead on 4/5 folds; fold 1 is a near-tie (HGB
  ahead by `0.00002`).

### Entry decision: SKIP

Both predeclared conditions are required; only one holds. The correlation
condition fails (`0.9976` is not `< 0.995`), so per the plan's own entry
gate, Task 6 does not proceed to XGBoost evaluation or the blend-weight
sweep. Full reasoning and all measured numbers are in
`docs/9_experiment_ledger.md`'s "E02 — Entry Check Results" section — not
just this summary.

**Champion unchanged:** `lightgbm_tuned` remains `CHAMPION_NAME`. No
notebook/model state changed in this task; the only notebook changes are
the new Section 10 (entry check) and the resulting renumbering of
Sections 10–12 to 11–13, plus one cross-reference fix.

### Status and evidence

```
$ git log --oneline -2
71ae1d5 docs(ledger): record Task 6 entry check (E02) results — SKIP decision
f5a81c8 feat(modeling): add Task 6 entry check (E02) hypothesis and code

$ git status --short --branch
## main...origin/main [ahead 60]
```

Clean working tree. `RUN_MODE = "evaluate"`, `CHAMPION_NAME =
"lightgbm_tuned"` unchanged. All code cells have `execution_count = None`
and empty outputs locally (no local re-execution occurred; Kaggle is the
sole execution venue, per the established pattern). No competition data,
credentials, generated artifacts, or public/leaderboard action occurred.

## Codex Review

Pending.

## User Promotion Decision

Pending.
