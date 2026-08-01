# S6E8 Public-Notebook Competition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish reproducible EDA and modeling notebooks on Kaggle, establish a valid first submission, and improve it through evidence-gated tabular experiments within a 40-hour budget.

**Architecture:** Keep `01_eda.ipynb` and `02_baseline_modeling.ipynb` as the executable sources of truth. All comparable models use the same seeded five-fold split and aligned OOF probabilities; public Kaggle versions are promoted milestones rather than scratch runs. Claude implements each bounded task, Codex independently reviews its code and evidence, and the user authorizes promotion and submission decisions.

**Tech Stack:** Python 3, pandas, NumPy, scikit-learn, LightGBM, CatBoost, optional XGBoost, Jupyter, Kaggle CLI/API.

## Global Constraints

- Active-effort budget: approximately 10 hours/week and 40 hours total.
- Metric: ROC AUC on `addicted_label` probabilities.
- Comparable experiments: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`.
- Public kernels: `is_private: false`, `enable_internet: false`.
- Do not commit raw data, generated submissions, prediction arrays, credentials, or downloaded source data.
- Do not expose local account names, credential paths, tokens, or secrets in public artifacts.
- Public leaderboard score supports decisions but never selects an experiment by itself.
- Every task requires Claude implementation, Codex review, and a recorded user promotion decision before the next public milestone.
- Use Conventional Commits with one coherent change per commit.

---

## File Responsibility Map

| File | Responsibility |
| --- | --- |
| `notebooks/01_eda.ipynb` | Public, trusted data and drift analysis |
| `notebooks/02_baseline_modeling.ipynb` | OOF experiments, full-data fit, test inference, submission generation |
| `notebooks/kernels/eda/kernel-metadata.json` | Public EDA kernel configuration |
| `notebooks/kernels/baseline_modeling/kernel-metadata.json` | Public modeling kernel configuration |
| `scripts/push_kaggle_kernel.sh` | Stage and push the current source notebook to Kaggle |
| `scripts/verify_submission.py` | Validate a generated submission independently of notebook state |
| `docs/7_kaggle_run_manifest.md` | Kaggle URLs, versions, runtimes, package versions, execution status |
| `docs/8_submission_manifest.md` | Submission version, OOF score, public score, and decision |
| `docs/9_experiment_ledger.md` | Accepted and rejected Phase 3 hypotheses with paired evidence |
| `docs/10_final_lessons.md` | Final findings, limitations, and stop decision |
| `README.md` | Concise public narrative and current champion |

## Task 1: Publish And Verify The EDA Notebook

**Files:**
- Modify: `notebooks/01_eda.ipynb`
- Create: `docs/7_kaggle_run_manifest.md`
- Verify: `notebooks/kernels/eda/kernel-metadata.json`

**Interfaces:**
- Consumes: Kaggle competition input `playground-series-s6e8`.
- Produces: a successful public Kaggle notebook version and recorded runtime/environment evidence.

- [ ] **Step 1: Add a runtime-version output cell**

Add a final code cell whose output is compact and deterministic:

```python
from importlib.metadata import version

RUNTIME_PACKAGES = [
    "numpy",
    "pandas",
    "scikit-learn",
    "scipy",
    "matplotlib",
    "seaborn",
]
runtime_versions = {
    package: version(package) for package in RUNTIME_PACKAGES
}
runtime_versions
```

- [ ] **Step 2: Validate the notebook before publishing**

Run:

```bash
cd notebooks
python3 -m jupyter nbconvert --to notebook --execute --inplace 01_eda.ipynb
cd ..
python3 -c "import nbformat; nbformat.validate(nbformat.read('notebooks/01_eda.ipynb', 4))"
```

Expected: both commands exit `0`; the notebook contains no error output.

- [ ] **Step 3: Verify public offline-safe kernel metadata**

Run:

```bash
python3 -c "import json; p='notebooks/kernels/eda/kernel-metadata.json'; d=json.load(open(p)); assert d['is_private'] is False; assert d['enable_internet'] is False; assert d['competition_sources']==['playground-series-s6e8']"
```

Expected: exit `0` with no output.

- [ ] **Step 4: Push the EDA notebook**

Run:

```bash
scripts/push_kaggle_kernel.sh eda
```

Expected: Kaggle accepts a new public version of
`tuannm3812/smartphone-addiction-eda`.

- [ ] **Step 5: Wait for and inspect the Kaggle run**

Run periodically:

```bash
/Users/tuannm3812/Library/Python/3.9/bin/kaggle kernels status tuannm3812/smartphone-addiction-eda
```

Expected: final status `complete`. If status is `error`, inspect the kernel log,
make the smallest offline-safe fix, locally re-execute, and push a new version.

- [ ] **Step 6: Create the run manifest**

Create `docs/7_kaggle_run_manifest.md` using only evidence returned by the
successful run. It must contain these columns: notebook name, public URL,
Kaggle version, status, runtime, local comparison, and UTC execution date. Add
a second table containing every package and version emitted by the runtime
cell. Do not write provisional values.

The first heading is `# Kaggle Run Manifest`; the environment heading is
`## Trusted Kaggle Package Versions`.

- [ ] **Step 7: Independent review gate**

Claude records the Kaggle version and comparison. Codex verifies the remote
status, public URL, saved outputs, and manifest. The user approves the EDA
milestone.

- [ ] **Step 8: Commit the trusted EDA milestone**

```bash
git add notebooks/01_eda.ipynb docs/7_kaggle_run_manifest.md
git commit -m "docs(eda): record trusted public Kaggle run"
```

## Task 2: Add A Tested Submission Contract

**Files:**
- Create: `scripts/verify_submission.py`
- Create: `tests/test_verify_submission.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: candidate submission path, `data/test.csv`, and `data/sample_submission.csv`.
- Produces: `validate_submission(path, test_path, sample_path) -> dict[str, int | float]` and a nonzero CLI exit on invalid artifacts.

- [ ] **Step 1: Write failing validator tests**

Create `tests/test_verify_submission.py`:

```python
from pathlib import Path

import pandas as pd
import pytest

from scripts.verify_submission import validate_submission


def write_contract_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    test = pd.DataFrame({"id": [10, 11, 12], "feature": [1, 2, 3]})
    sample = pd.DataFrame({"id": [10, 11, 12], "addicted_label": [0.5] * 3})
    submission = pd.DataFrame(
        {"id": [10, 11, 12], "addicted_label": [0.1, 0.7, 0.9]}
    )
    test_path = tmp_path / "test.csv"
    sample_path = tmp_path / "sample_submission.csv"
    submission_path = tmp_path / "submission.csv"
    test.to_csv(test_path, index=False)
    sample.to_csv(sample_path, index=False)
    submission.to_csv(submission_path, index=False)
    return submission_path, test_path, sample_path


def test_valid_submission_passes(tmp_path: Path) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    result = validate_submission(submission, test, sample)
    assert result["rows"] == 3
    assert result["unique_predictions"] == 3


@pytest.mark.parametrize("bad_value", [-0.1, 1.1, float("nan")])
def test_invalid_probability_fails(tmp_path: Path, bad_value: float) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    frame = pd.read_csv(submission)
    frame.loc[0, "addicted_label"] = bad_value
    frame.to_csv(submission, index=False)
    with pytest.raises(ValueError):
        validate_submission(submission, test, sample)


def test_id_order_mismatch_fails(tmp_path: Path) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    frame = pd.read_csv(submission).iloc[::-1]
    frame.to_csv(submission, index=False)
    with pytest.raises(ValueError):
        validate_submission(submission, test, sample)
```

- [ ] **Step 2: Run the tests and confirm failure**

Run:

```bash
pytest tests/test_verify_submission.py -v
```

Expected: collection/import failure because `scripts.verify_submission` does
not exist.

- [ ] **Step 3: Implement the validator**

Create `scripts/verify_submission.py`:

```python
#!/usr/bin/env python3
"""Validate an S6E8 submission artifact."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def validate_submission(
    submission_path: Path,
    test_path: Path,
    sample_path: Path,
) -> dict[str, int | float]:
    """Validate schema, IDs, and probabilities for an S6E8 submission."""
    submission = pd.read_csv(submission_path)
    test = pd.read_csv(test_path, usecols=["id"])
    sample = pd.read_csv(sample_path)
    expected_columns = sample.columns.tolist()
    if submission.columns.tolist() != expected_columns:
        raise ValueError(f"Expected columns {expected_columns}")
    if len(submission) != len(test):
        raise ValueError("Submission row count does not match test")
    if not submission["id"].equals(test["id"]):
        raise ValueError("Submission IDs are not in test order")
    predictions = submission["addicted_label"].to_numpy(dtype=float)
    if not np.isfinite(predictions).all():
        raise ValueError("Predictions contain NaN or infinity")
    if not ((predictions >= 0.0) & (predictions <= 1.0)).all():
        raise ValueError("Predictions must be within [0, 1]")
    return {
        "rows": len(submission),
        "unique_predictions": int(np.unique(predictions).size),
        "minimum": float(predictions.min()),
        "maximum": float(predictions.max()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", type=Path)
    parser.add_argument("--test", type=Path, default=Path("data/test.csv"))
    parser.add_argument(
        "--sample",
        type=Path,
        default=Path("data/sample_submission.csv"),
    )
    args = parser.parse_args()
    print(validate_submission(args.submission, args.test, args.sample))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run validator tests**

```bash
pytest tests/test_verify_submission.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Ignore generated submissions**

Ensure `.gitignore` contains:

```gitignore
submission.csv
predictions/
```

- [ ] **Step 6: Review and commit**

Claude implements; Codex reviews error cases and test evidence.

```bash
git add .gitignore scripts/verify_submission.py tests/test_verify_submission.py
git commit -m "test(submission): add artifact contract validator"
```

## Task 3: Make The Baseline Notebook Submission-Ready

**Files:**
- Modify: `notebooks/02_baseline_modeling.ipynb`
- Modify: `docs/6_baseline_modeling.md`

**Interfaces:**
- Consumes: `RUN_MODE: Literal["evaluate", "submission"]`, `CHAMPION_NAME`, train/test/sample CSVs.
- Produces: OOF evidence in evaluation mode; `/kaggle/working/submission.csv` in submission mode.

- [ ] **Step 1: Add explicit configuration**

Add to the top configuration cell:

```python
RUN_MODE = "evaluate"  # "evaluate" or "submission"
CHAMPION_NAME = "hist_gradient_boosting"
NOTEBOOK_VERSION = "baseline-v1"
```

Reject invalid configuration immediately:

```python
if RUN_MODE not in {"evaluate", "submission"}:
    raise ValueError(f"Unsupported RUN_MODE: {RUN_MODE}")
```

- [ ] **Step 2: Stabilize or retire logistic regression**

Try a numerically stable sanity configuration:

```python
LogisticRegression(
    solver="saga",
    penalty="l2",
    C=0.1,
    max_iter=2_000,
    random_state=SEED,
    n_jobs=-1,
)
```

Run the logistic block alone on the fixed folds. If it emits numerical or
convergence warnings, set `RUN_LOGISTIC = False`, remove its AUC from the
trusted comparison table, and document it as retired rather than measured.

- [ ] **Step 3: Add a single model factory**

```python
def build_model(name: str):
    """Build a configured model without fitting it."""
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            random_state=SEED,
            max_iter=200,
            categorical_features="from_dtype",
        )
    raise ValueError(f"Unknown model: {name}")
```

The evaluation and submission paths must call this same factory.

- [ ] **Step 4: Add full-fit test inference**

```python
def fit_champion_and_predict(
    model_name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
) -> np.ndarray:
    """Fit the selected configuration on all training rows."""
    model = build_model(model_name)
    model.fit(X_train, y_train)
    return model.predict_proba(X_test)[:, 1]
```

- [ ] **Step 5: Add notebook-local artifact validation and writing**

```python
def build_submission(
    sample: pd.DataFrame,
    test_ids: pd.Series,
    predictions: np.ndarray,
) -> pd.DataFrame:
    """Create a schema-safe submission in test-row order."""
    submission = sample.copy()
    submission["id"] = test_ids.to_numpy()
    submission["addicted_label"] = predictions
    if submission.columns.tolist() != ["id", "addicted_label"]:
        raise ValueError("Unexpected submission columns")
    if not submission["id"].equals(test_ids.reset_index(drop=True)):
        raise ValueError("Submission ID order mismatch")
    if not np.isfinite(predictions).all():
        raise ValueError("Non-finite predictions")
    if not ((predictions >= 0.0) & (predictions <= 1.0)).all():
        raise ValueError("Predictions outside [0, 1]")
    return submission
```

In submission mode write:

```python
OUTPUT_PATH = (
    "/kaggle/working/submission.csv"
    if os.path.exists("/kaggle/working")
    else "../submission.csv"
)
submission.to_csv(OUTPUT_PATH, index=False)
print(f"Wrote {OUTPUT_PATH}: {submission.shape}")
```

- [ ] **Step 6: Run evaluation mode locally**

```bash
cd notebooks
python3 -m jupyter nbconvert --to notebook --execute --inplace 02_baseline_modeling.ipynb
cd ..
python3 -c "import nbformat; nbformat.validate(nbformat.read('notebooks/02_baseline_modeling.ipynb', 4))"
```

Expected: exit `0`, no error outputs, HGB OOF AUC remains within `0.0001` of
`0.95733` unless an explained dependency/version change occurred.

- [ ] **Step 7: Run submission mode locally**

Set `RUN_MODE = "submission"`, execute, then run:

```bash
python3 scripts/verify_submission.py submission.csv
```

Expected: 296,302 rows, correct ordered IDs, finite probabilities in `[0, 1]`.
Restore `RUN_MODE = "evaluate"` before committing; Kaggle submission versions
set it explicitly as part of their promoted configuration.

- [ ] **Step 8: Review and commit**

Claude implements. Codex checks that evaluation and submission use the same
factory and verifies both modes.

```bash
git add notebooks/02_baseline_modeling.ipynb docs/6_baseline_modeling.md
git commit -m "feat(modeling): add reproducible submission mode"
```

## Task 4: Publish Baseline And Establish The First Score

**Files:**
- Modify: `docs/7_kaggle_run_manifest.md`
- Create: `docs/8_submission_manifest.md`
- Verify: `notebooks/kernels/baseline_modeling/kernel-metadata.json`

**Interfaces:**
- Consumes: reviewed submission-ready baseline notebook.
- Produces: successful public Kaggle version, validated artifact, and first leaderboard score.

- [ ] **Step 1: Verify metadata and set submission configuration**

Confirm public/offline-safe metadata as in Task 1. Set the promoted notebook
copy to `RUN_MODE = "submission"`, `CHAMPION_NAME = "hist_gradient_boosting"`,
and the recorded `NOTEBOOK_VERSION`.

- [ ] **Step 2: Push the baseline notebook**

```bash
scripts/push_kaggle_kernel.sh baseline
```

Expected: Kaggle accepts a public version of
`tuannm3812/smartphone-addiction-baseline-modeling`.

- [ ] **Step 3: Wait for completion and download output**

```bash
/Users/tuannm3812/Library/Python/3.9/bin/kaggle kernels status tuannm3812/smartphone-addiction-baseline-modeling
/Users/tuannm3812/Library/Python/3.9/bin/kaggle kernels output tuannm3812/smartphone-addiction-baseline-modeling -p /private/tmp/s6e8-baseline-output
```

Expected: status `complete`; output contains `submission.csv`.

- [ ] **Step 4: Validate the Kaggle-generated artifact**

```bash
python3 scripts/verify_submission.py /private/tmp/s6e8-baseline-output/submission.csv
```

Expected: validator passes with 296,302 rows.

- [ ] **Step 5: Record the trusted run before submission**

Append the public URL, version, runtime, environment, OOF AUC, artifact checks,
and Codex review result to `docs/7_kaggle_run_manifest.md`.

- [ ] **Step 6: User promotion gate and leaderboard submission**

Only after the user approves the exact artifact, submit it through the Kaggle
notebook UI or approved competition-submission workflow. Do not submit an
unreviewed local CSV.

- [ ] **Step 7: Record the first score**

Create `docs/8_submission_manifest.md` only after the score is returned. Use
the heading `# Submission Manifest` and columns: UTC date, public notebook URL,
Kaggle version, candidate, OOF AUC, public AUC, and decision. The first row
records the actual HGB baseline evidence; do not write provisional score or
version values.

- [ ] **Step 8: Commit the public baseline evidence**

```bash
git add docs/7_kaggle_run_manifest.md docs/8_submission_manifest.md
git commit -m "docs(submission): record public baseline result"
```

## Task 5: Run Comparable Hand-Designed Tuning

**Files:**
- Modify: `notebooks/02_baseline_modeling.ipynb`
- Create: `docs/9_experiment_ledger.md`

**Interfaces:**
- Consumes: fixed folds and champion OOF probabilities.
- Produces: aligned OOF arrays for HGB, LightGBM, and CatBoost candidates plus paired promotion evidence.

- [ ] **Step 1: Write the experiment hypothesis**

Start `docs/9_experiment_ledger.md` with:

```markdown
## E01 — Comparable GBDT Budget

**Hypothesis:** LightGBM or CatBoost can close the untuned HGB gap when given
comparable learning-rate and iteration budgets.

**Promotion evidence required:** positive paired OOF delta, fold consistency,
and paired uncertainty supporting improvement over HGB.
```

- [ ] **Step 2: Add compact search configurations**

Use no more than four configurations per family. Keep exact dictionaries in
one configuration cell. Example LightGBM grid:

```python
LGBM_CONFIGS = [
    {"n_estimators": 400, "learning_rate": 0.05, "num_leaves": 31},
    {"n_estimators": 600, "learning_rate": 0.03, "num_leaves": 31},
    {"n_estimators": 400, "learning_rate": 0.05, "num_leaves": 63},
    {"n_estimators": 600, "learning_rate": 0.03, "num_leaves": 63},
]
```

Use comparable total boosting budgets for HGB and CatBoost. Do not enable
Optuna in this task.

- [ ] **Step 3: Add paired bootstrap comparison**

```python
def paired_auc_bootstrap(
    y_true: np.ndarray,
    champion_pred: np.ndarray,
    candidate_pred: np.ndarray,
    n_bootstrap: int = 200,
    bootstrap_size: int = 100_000,
    seed: int = 42,
) -> dict[str, float]:
    """Estimate paired AUC-difference uncertainty without storing samples."""
    rng = np.random.default_rng(seed)
    positive = np.flatnonzero(y_true == 1)
    negative = np.flatnonzero(y_true == 0)
    positive_size = round(bootstrap_size * len(positive) / len(y_true))
    negative_size = bootstrap_size - positive_size
    differences = np.empty(n_bootstrap)
    for index in range(n_bootstrap):
        sample = np.concatenate(
            [
                rng.choice(positive, positive_size, replace=True),
                rng.choice(negative, negative_size, replace=True),
            ]
        )
        differences[index] = (
            roc_auc_score(y_true[sample], candidate_pred[sample])
            - roc_auc_score(y_true[sample], champion_pred[sample])
        )
    return {
        "mean_delta": float(differences.mean()),
        "lower_95": float(np.quantile(differences, 0.025)),
        "upper_95": float(np.quantile(differences, 0.975)),
        "probability_positive": float((differences > 0).mean()),
    }
```

This is a deterministic, stratified approximation sized for the project
budget. Record `n_bootstrap`, `bootstrap_size`, and seed with every result.

- [ ] **Step 4: Execute the controlled search locally**

Run the notebook in evaluation mode. Expected: one table containing config,
overall AUC, fold AUCs, runtime, paired delta, interval, and correlation with
the HGB champion.

- [ ] **Step 5: Apply the promotion gate**

Promote only if improvement is positive across most folds and the paired
uncertainty is persuasive. Otherwise retain HGB and record every rejected
configuration with exact results.

- [ ] **Step 6: Independent review and commit**

Claude implements and documents E01. Codex reviews fold identity, OOF
alignment, bootstrap code, runtime, and conclusion.

```bash
git add notebooks/02_baseline_modeling.ipynb docs/9_experiment_ledger.md
git commit -m "feat(modeling): compare tuned GBDT candidates"
```

## Task 6: Conditional Diversity And Ensemble Pass

**Files:**
- Modify: `notebooks/02_baseline_modeling.ipynb`
- Modify: `docs/9_experiment_ledger.md`

**Interfaces:**
- Consumes: reviewed OOF predictions from Task 5.
- Produces: either a justified XGBoost/diverse candidate and blend or a documented stop decision.

- [ ] **Step 1: Check the entry condition**

Proceed only if either:

- no Task 5 candidate beats the current champion; or
- two strong candidates have prediction correlation below `0.995` and
  complementary residuals.

Otherwise record that this task was skipped to protect the time budget.

- [ ] **Step 2: Write the hypothesis before code**

```markdown
## E02 — Conditional Diversity

**Hypothesis:** A model with sufficiently different OOF rankings can improve a
convex blend even when its standalone AUC is slightly lower.
```

- [ ] **Step 3: Add at most one XGBoost configuration family**

Run no more than four hand-designed configurations on the fixed folds. Do not
run Optuna unless the user separately approves it from documented E02 evidence.

- [ ] **Step 4: Evaluate prediction diversity**

For each pair report Pearson and Spearman prediction correlation, standalone
AUC, and row-level disagreement on the top and bottom prediction deciles.

- [ ] **Step 5: Sweep a small convex blend grid**

```python
BLEND_WEIGHTS = np.linspace(0.0, 1.0, 21)
blend_rows = []
for weight in BLEND_WEIGHTS:
    blended = weight * champion_oof + (1.0 - weight) * challenger_oof
    blend_rows.append(
        {"champion_weight": weight, "oof_auc": roc_auc_score(y, blended)}
    )
```

Apply the paired bootstrap to the best blend versus the champion. A grid-best
score without paired support is rejected.

- [ ] **Step 6: Review, decide, and commit**

Claude implements. Codex checks leakage, OOF alignment, grid selection bias,
and paired evidence. The user promotes or stops.

```bash
git add notebooks/02_baseline_modeling.ipynb docs/9_experiment_ledger.md
git commit -m "feat(modeling): evaluate conditional model diversity"
```

## Task 7: Publish Champion And Close The Project

**Files:**
- Modify: `notebooks/02_baseline_modeling.ipynb`
- Modify: `docs/7_kaggle_run_manifest.md`
- Modify: `docs/8_submission_manifest.md`
- Create: `docs/10_final_lessons.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: final user-approved candidate configuration.
- Produces: rerun public champion, final valid submission, manifest entries, and portfolio narrative.

- [ ] **Step 1: Freeze the champion configuration**

Set `CHAMPION_NAME`, exact parameters, `RUN_MODE = "submission"`, seed, and
`NOTEBOOK_VERSION` in one configuration cell. Disable rejected experiment
blocks without deleting their documented results.

- [ ] **Step 2: Run locally and validate**

Execute the notebook, validate notebook JSON, and run
`scripts/verify_submission.py submission.csv`. Expected: all checks pass.

- [ ] **Step 3: Push and rerun publicly**

Push the baseline kernel, wait for completion, download its output, and run the
independent validator against the Kaggle-generated artifact.

- [ ] **Step 4: Submit the exact reviewed artifact**

User authorizes the final submission. Record its notebook URL/version and
public score in both manifests immediately.

- [ ] **Step 5: Write final lessons**

`docs/10_final_lessons.md` must contain:

- final OOF and public scores;
- accepted and rejected hypotheses;
- local/Kaggle reproducibility findings;
- limitations and private-leaderboard risks;
- explicit reason further experiments were stopped.

- [ ] **Step 6: Update README**

Add `Current Result`, `What Worked`, `Final Modeling Decision`, public notebook
links, and the documentation map. Use exact metrics and avoid unverified rank
claims.

- [ ] **Step 7: Final verification**

Run:

```bash
pytest tests/test_verify_submission.py -v
python3 -c "import nbformat; [nbformat.validate(nbformat.read(p, 4)) for p in ['notebooks/01_eda.ipynb', 'notebooks/02_baseline_modeling.ipynb']]"
git diff --check
git status --short
```

Expected: tests pass, notebooks validate, no whitespace errors, and only the
intended final documentation/notebook changes remain.

- [ ] **Step 8: Independent final review and commit**

Codex verifies the successful public run, exact artifact, manifests, tests,
and stop rationale. Claude addresses findings. The user approves completion.

```bash
git add README.md notebooks/02_baseline_modeling.ipynb docs/7_kaggle_run_manifest.md docs/8_submission_manifest.md docs/10_final_lessons.md
git commit -m "docs(project): freeze final S6E8 champion"
```
