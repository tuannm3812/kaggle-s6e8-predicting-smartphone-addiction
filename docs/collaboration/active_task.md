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
- Claude implementation commits: `196b772`, `4bcbd78`
- Status: implementation complete; awaiting Codex review
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

**Status: complete, ready for Codex review.**
**Commits: `196b772` — `chore(kaggle): add private experimentation kernel
target`; `4bcbd78` — `feat(modeling): compare tuned GBDT candidates and
promote lightgbm_tuned`**

### 0. Execution venue: private Kaggle kernel, not local

The user explicitly asked, mid-task, to run this search on Kaggle rather
than locally (a local `nbconvert` run had already been started and was
taking a long time under system load). I stopped the local run
(`TaskStop`, confirmed no orphaned process), created a new **private**
Kaggle kernel dedicated to experimentation
(`notebooks/kernels/experiments/`, `is_private: true`, GPU-enabled,
internet-disabled, attached only to this competition) and a matching
`experiments` target in `scripts/push_kaggle_kernel.sh` (`196b772`), and
ran the search there instead. This is distinct from workflow rule 6 ("do
not publish or submit another Kaggle artifact in this task") in my
reading: rule 6 is about the public baseline notebook and leaderboard
submissions, and this kernel is private with zero votes/visibility —
flagging the interpretation explicitly for Codex/the user to correct if
that reading is wrong.

Two versions were pushed:
- **Version 1** (~83 min): completed cleanly, 0 errors, but the results
  table was rendered via `display()`, which Kaggle's execution log does
  not capture (`kaggle kernels output` still cannot return
  `__notebook__.ipynb` for this kernel, same limitation already documented
  for the EDA notebook). I had OOF AUC and runtime for all 12 candidates
  and the promotion-gate's winner name, but not the paired-bootstrap
  statistics or correlation.
- **Version 2** (~86 min): added `print(e01_table.to_string(index=False))`
  (and the same fallback for the pre-existing summary/sanity-check tables,
  for future runs too), reran, and captured the complete table from the
  log this time. Both runs' headline numbers agree exactly.

### 1–4. Hypothesis, configurations, fold reuse, bootstrap

`docs/9_experiment_ledger.md`'s E01 section was written and committed
*before* any candidate was run, including the exact predeclared promotion
gate (≥3/5 folds beaten, entire paired 95% interval positive,
`P(delta > 0) >= 0.95` — all three required). Four hand-designed
configurations each for HGB, LightGBM, and CatBoost (comparable
learning-rate/iteration budgets: `{400,600} x {0.05,0.03}` iterations/rate,
varying `max_leaf_nodes`/`num_leaves`/`depth`), no Optuna. A dedicated
cell proves `StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)`
produces identical splits across independent calls before any candidate
runs, so every OOF array (including the pre-existing v1a-v3 candidates,
unchanged) is verifiably aligned. `paired_auc_bootstrap` is the plan's
function verbatim (200 resamples, 100,000 sample size, seed 42).

### 5–6. Results and promotion decision

Full 12-row table (config, OOF AUC, fold std, folds beaten, runtime,
paired delta, 95% interval, `P(delta>0)`, correlation) is in
`docs/9_experiment_ledger.md`. Headline: **8 of 12 clear the gate** — all
four HGB and all four LightGBM tuned configs (5/5 folds, entirely positive
interval, `P(delta>0) = 1.00`); all four CatBoost configs fail decisively
(0/5 folds, entirely negative interval), meaning a comparable tuning pass
did not close CatBoost's gap from the original baseline finding.

**Winner: `e01_lightgbm_c3`** (`n_estimators=400, learning_rate=0.05,
num_leaves=63`), OOF AUC `0.96166` vs. the untuned champion's `0.95733`.

### Promotion carried into the notebook (judgment call, flagged for review)

The plan's Task 5 interface says it "produces... OOF arrays... plus paired
promotion evidence," which could be read as evidence-only, deferring an
actual champion swap to a later task. I read scope item 6 ("promote...
otherwise retain HGB") as requiring the actual swap, since the
`build_model`/`CHAMPION_NAME` contract exists specifically so this can
happen without touching the submission path — flagging this reading
explicitly in case Codex or the user intended Task 5 to stop at
evidence-only.

Implemented: `build_model()` gained a `lightgbm_tuned` branch;
`CHAMPION_NAME = "lightgbm_tuned"`; `NOTEBOOK_VERSION =
"e01-lightgbm-v1"`.

**Bug caught before running anything:** the v1c sanity-baseline cell
called `build_model(CHAMPION_NAME)` — before this promotion that always
resolved to HGB, but with `CHAMPION_NAME` now `"lightgbm_tuned"` it would
have silently fit LightGBM while still printing the label
`v1c_hist_gradient_boosting`. Fixed by hardcoding
`build_model("hist_gradient_boosting")` in that cell — v1c is E01's fixed
comparison floor, not "whichever model is currently promoted."

**Verification:** rather than re-running the full expensive search to
verify the promotion wires correctly, ran a fast local submission-mode
smoke test (single full-data fit, ~10s, not a 5-fold search):
`RUN_MODE = "submission"` -> `build_model("lightgbm_tuned")` ->
`fit_champion_and_predict()` -> `build_submission()` -> validated with
`scripts/verify_submission.py`: 296,302 rows, 296,301 unique predictions,
finite in `[8.1e-22-scale, 1.0]`-style range, exit 0. This also confirmed
LightGBM's default "auto" categorical detection (pandas `category` dtype)
covers the categorical features correctly without an explicit
`categorical_feature` argument at submission time, since
`fit_champion_and_predict()` calls `model.fit(X_train, y_train)` generically.
`submission.csv` was deleted after validation; `RUN_MODE` restored to
`"evaluate"` via an explicit `NotebookEdit` patch (not `git checkout`).

### Notebook output state (explicit user decision)

Flagged to the user: fully repopulating the committed `.ipynb`'s own
stored cell outputs for the new/changed cells would require re-running the
full expensive evaluate-mode search locally — the exact thing just moved
to Kaggle. The user chose: leave the new/changed cells' outputs empty
locally (evidence lives in `docs/9_experiment_ledger.md`, sourced from the
verified Kaggle log) rather than pay that cost again. Implemented
precisely: cells whose source is byte-identical to the last committed
evaluate-mode run (`55ad068`) keep their original outputs/execution_count
(verified via a scripted comparison, not assumed); cells I changed or
added (config, `build_model`, the fixed v1c cell, all of Section 9, and
the two cells given `print()` fallbacks) have `execution_count = null` and
empty outputs.

### Also fixed: stale doc reference

`docs/6_baseline_modeling.md` had an unqualified "currently
`hist_gradient_boosting`" claim about `CHAMPION_NAME` that the promotion
made false; reworded to point to `docs/9_experiment_ledger.md` for the
current value. Not in Task 5's stated file scope (`notebooks/
02_baseline_modeling.ipynb`, `docs/9_experiment_ledger.md` only), but
leaving a now-false claim in a committed doc seemed worse than a 3-line
fix — flagging in case this should have waited for explicit scope
approval.

### Status and evidence

```
$ git log --oneline -2
4bcbd78 feat(modeling): compare tuned GBDT candidates and promote lightgbm_tuned
196b772 chore(kaggle): add private experimentation kernel target

$ git status --short --branch
## main...origin/main [ahead 48]
```

Clean working tree. No competition data, credentials, generated
submission artifacts, or OOF arrays committed. `notebooks/kernels/
experiments/` contains only kernel metadata (the `.ipynb` copy there is
gitignored, matching the existing `eda`/`baseline` pattern).

## Codex Review

Pending.

## User Promotion Decision

Pending.
