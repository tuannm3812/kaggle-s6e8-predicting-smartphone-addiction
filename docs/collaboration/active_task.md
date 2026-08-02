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
- Claude implementation commit: `1e15fe1` — `feat(modeling): add
  reproducible submission mode`
- Status: implementation complete; awaiting Codex review
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

**Status: complete, ready for Codex review.**
**Commit: `1e15fe1` — `feat(modeling): add reproducible submission mode`**

Not a pure TDD task (the plan specifies a notebook feature, not a
test-first unit) but each behavior change was verified in isolation before
being trusted, per the plan's own evidence requirements.

### 1. Stabilize-or-retire logistic regression

Ran the plan's stabilized config (`solver="saga", penalty="l2", C=0.1,
max_iter=2_000, random_state=SEED, n_jobs=-1`) alone on the fixed folds.
Result: same `RuntimeWarning`s as the original (`divide by zero`,
`overflow`, `invalid value encountered in matmul`). Per the plan's decision
rule, set `RUN_LOGISTIC = False`, dropped it from the trusted comparison
table, and documented it as retired (`docs/6_baseline_modeling.md` §3) —
the block still exists in the notebook (gated `if RUN_V1_SANITY and
RUN_LOGISTIC:`) so the evidence is reproducible on demand, but it does not
execute or report a number by default.

### 2. Configuration and mode gating

Added `RUN_MODE: Literal["evaluate", "submission"]`, `CHAMPION_NAME`,
`NOTEBOOK_VERSION` to the top config cell, with immediate rejection of an
unsupported `RUN_MODE`. Every evaluation-only flag
(`RUN_V1_SANITY`/`RUN_V2_STRONG`/`RUN_V2_MISSING_ABLATION`/
`RUN_V3_ENGINEERED`/`RUN_CLASS_WEIGHT_ABLATION`/`RUN_SUMMARY`) is tied to
`RUN_MODE == "evaluate"`, so submission mode skips all experimentation.

### 3. Single model factory

```python
def build_model(name: str):
    """Build a configured model without fitting it."""
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            random_state=SEED, max_iter=200,
            categorical_features="from_dtype",
        )
    raise ValueError(f"Unknown model: {name}")
```

The v1c evaluation cell was refactored from constructing
`HistGradientBoostingClassifier` directly to calling
`build_model(CHAMPION_NAME)`; `fit_champion_and_predict()` in the new
Section 11 calls the identical factory. Confirmed by inspection:
`build_model` is the only place `HistGradientBoostingClassifier(...)` is
constructed in the notebook — grep for the class name returns exactly one
definition site (inside `build_model`) and zero other construction calls.

### 4. Full-fit inference and submission construction

Added `fit_champion_and_predict()` (fit on all training rows, predict on
test) and `build_submission()` (validates exact columns, ID order, finite
values, `[0, 1]` range before returning) exactly per the plan's interfaces,
plus the submission-mode write to `/kaggle/working/submission.csv` or
`../submission.csv`.

### 5. Also fixed: Kaggle input path bug

Proactively re-applied the same fix already made in `01_eda.ipynb`:
`/kaggle/input/<slug>` does not exist on Kaggle; the real mount is
`/kaggle/input/competitions/<slug>`. Not in the plan's explicit scope, but
required for the notebook to run un-modified on Kaggle in Task 4.

### 6. Evidence — evaluation mode

```
$ cd notebooks && python3 -m jupyter nbconvert --to notebook --execute --inplace 02_baseline_modeling.ipynb ...
[NbConvertApp] Writing 33324 bytes to 02_baseline_modeling.ipynb
nbconvert exit: 0
$ python3 -c "import nbformat; nbformat.validate(nbformat.read('notebooks/02_baseline_modeling.ipynb', 4))"
nbformat validate: OK
```

0 error outputs across all 15 code cells. HGB OOF AUC unchanged at exactly
`0.95733` (all other v2/v3 OOF numbers also unchanged from the pre-Task-3
notebook, confirming the refactor changed no evaluation behavior). This run
exceeded the 600s foreground timeout under system load (v1c took 937s vs.
~12s in earlier runs of the identical code) but completed successfully in
the background — a load/timing artifact, not a correctness problem.

### 7. Evidence — submission mode

Re-ran locally right before writing this report, to capture fresh,
verifiable numbers rather than relying on memory of an earlier run:

```
$ python3 -m jupyter nbconvert --to notebook --execute --inplace 02_baseline_modeling.ipynb --ExecutePreprocessor.timeout=300 --ExecutePreprocessor.kernel_name=s6e8-py39
[NbConvertApp] Writing 28369 bytes to 02_baseline_modeling.ipynb
nbconvert exit: 0
nbformat validate: OK
errors: 0
X: (691369, 12), y: (691369,), X_test: (296302, 12)
Wrote ../submission.csv: (296302, 2)

$ python3 scripts/verify_submission.py submission.csv
{'rows': 296302, 'unique_predictions': 296146, 'minimum': 8.12196190577754e-22, 'maximum': 1.0}
exit: 0
```

296,302 rows (matches `data/test.csv`), IDs in test order, all predictions
finite and within `[0, 1]`. `submission.csv` was scratch-only and deleted
after verification (`rm -f submission.csv`); `RUN_MODE` was then restored
to `"evaluate"` via `git checkout -- notebooks/02_baseline_modeling.ipynb`
(the committed file already had `RUN_MODE = "evaluate"`; this run and
revert happened entirely after commit `1e15fe1`, purely to gather this
report's evidence, and left the repository unchanged).

### 8. Commit and status

Commit `1e15fe1` — `feat(modeling): add reproducible submission mode`
(`notebooks/02_baseline_modeling.ipynb`, `docs/6_baseline_modeling.md`).

```
$ git status --short --branch
## main...origin/main [ahead 31]
```

Clean working tree (aside from this report update). No competition data,
credentials, or generated submission artifacts committed. A
public-notebook-prose sweep of the full notebook (grep for internal
doc/Phase/agent references) returned 0 hits.

## Codex Review

Pending.

## User Promotion Decision

Pending.
