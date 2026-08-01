# S6E8 Competition Strategy Design

**Status:** Approved by the user on 2026-08-01.

**Competition:** Kaggle Playground Series S6E8 — Predicting Smartphone
Addiction

**Deadline:** 2026-08-31 23:59 UTC

## 1. Objective And Constraints

Build a polished learning and portfolio project first while still targeting a
strong, reproducible leaderboard result.

Project constraints:

- Approximately 10 active hours per week, or about 40 hours total.
- Public Kaggle notebooks are the trusted execution and publication surface.
- Public notebooks and the candidate source dataset may inform hypotheses,
  but the final solution must be independently implemented and leakage-safe.
- Local runs support fast iteration; only successful Kaggle runs can establish
  trusted public results.
- Every promoted result must be traceable to committed code and an exact
  public Kaggle notebook version.

## 2. Repository Architecture

Use a notebook-first repository:

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── assets/
├── docs/
│   ├── archive/
│   │   └── 4_codex_claude_review_log.md
│   ├── superpowers/
│   │   ├── specs/
│   │   │   └── 2026-08-01-s6e8-competition-strategy-design.md
│   │   └── plans/
│   ├── 0_coding_standards.md
│   ├── 1_instructions.md
│   ├── 2_implementation_plan.md
│   ├── 3_eda_insights.md
│   ├── 5_source_dataset_provenance.md
│   └── 6_baseline_modeling.md
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_baseline_modeling.ipynb
│   └── kernels/
├── scripts/
├── data/          # ignored
├── predictions/   # ignored
└── scratch/       # ignored
```

Keep two promoted notebooks initially. Small experiments remain controlled by
configuration flags inside `02_baseline_modeling.ipynb`. Add another notebook
only when a workflow has a genuinely separate purpose or incompatible runtime.

The archived Codex–Claude log is historical evidence, not an active source of
requirements. This design spec and the subsequent Superpowers implementation
plan are authoritative for future work.

## 3. Collaboration Model

Superpowers supplies the design, planning, review, and verification gates.
Claude and Codex collaborate through committed project artifacts instead of
depending on separate chat histories.

| Work | Primary | Independent review |
| --- | --- | --- |
| Strategy and experiment gates | Codex | User and Claude |
| Notebook implementation | Claude | Codex |
| Statistical and methodological review | Codex | Claude responds with evidence |
| Kaggle execution evidence | Implementing agent | Other agent verifies |
| Final promotion decision | User | Codex and Claude recommendations |

An agent must not both implement an experiment and provide its final approval.
Disagreements are recorded with evidence; the user decides when evidence does
not resolve the choice.

## 4. Data And Validation Design

The target is binary `addicted_label`, evaluated by ROC AUC. Use one fixed
five-fold `StratifiedKFold` split with shuffling and seed 42 for all comparable
experiments.

Every serious candidate produces:

- row-aligned OOF probabilities;
- overall and per-fold ROC AUC;
- fit runtime;
- finite/range/uniqueness checks;
- train/test prediction quantiles when test predictions exist;
- candidate-versus-champion paired differences;
- prediction correlation with other candidate families.

Feature families are evaluated as controlled ablations on identical folds:

1. Raw numeric and native categorical features.
2. Native missing-value handling, with explicit missing indicators tested once
   as an ablation.
3. A compact behavior-composition and residual feature pack.
4. Candidate-source-informed features that are available at inference time and
   independently justified.

Target-derived transformations must be fitted inside each training fold.
Target-free row transformations may be computed outside the CV loop when they
are identical for train and test.

Adversarial validation measures detectable train/test covariate shift only. It
does not prove whether OOF CV will track the leaderboard and does not, by
itself, justify drift correction.

## 5. Modeling Sequence

Use an evidence-gated sequence rather than a broad tournament:

1. Repair or retire the unstable logistic-regression sanity baseline.
2. Treat the existing HGB OOF AUC of `0.95733` as a local benchmark, not a
   champion.
3. Give HGB, LightGBM, and CatBoost small, comparable hand-designed searches.
4. Evaluate raw and engineered features on the same folds.
5. Add XGBoost only if leading models plateau or lack complementary rankings.
6. Use Optuna only when initial controlled searches demonstrate enough
   headroom to justify its time cost.
7. Use multi-seed averaging only when observed seed variance is material.
8. Blend only model families with complementary OOF errors.

Promotion does not use a fixed improvement threshold borrowed from another
competition. A candidate replaces the champion only when the evidence from
this dataset supports it:

- the paired OOF difference is positive and practically meaningful;
- improvement is not driven by a single fold;
- a memory-safe paired uncertainty estimate supports the improvement;
- prediction correlation demonstrates useful diversity for an ensemble;
- all probability and distribution sanity checks pass.

Public leaderboard score is supporting evidence, not the experiment selector.

## 6. Public Kaggle Notebook Design

Public Kaggle notebooks are intentional portfolio deliverables. Kernel
metadata uses `is_private: false` and offline-safe execution.

### 6.1 EDA publication

1. Push `01_eda.ipynb` through the repository helper.
2. Wait for a successful Kaggle execution.
3. Compare saved Kaggle outputs with documented local findings.
4. Record the public URL, Kaggle version, runtime, status, and important
   dependency versions.
5. Resolve material environment differences before publishing modeling
   claims based on the notebook.

### 6.2 Baseline publication

Before the baseline is submission-ready, add a submission mode that:

1. selects an explicitly configured candidate;
2. fits that configuration on all training rows;
3. predicts probabilities for the test set;
4. preserves sample-submission ID order;
5. validates row count, column order, finite values, probability range, and
   missing values;
6. writes `/kaggle/working/submission.csv`.

Push and execute the baseline publicly only after independent review. Inspect
its output artifact before submitting that exact notebook version to the
competition.

Do not expose credentials, local credential paths, secrets, or private data in
code, metadata, outputs, or documentation.

## 7. Phase Deliverables And Gates

### 7.1 EDA gate

- Public EDA notebook completes successfully.
- Kaggle outputs reproduce the documented conclusions within expected
  numerical tolerance.
- Runtime and dependency versions are recorded.
- Claude implementation receives Codex review.

### 7.2 Baseline gate

- Public modeling notebook performs the approved OOF evaluation.
- Submission mode fits the selected candidate and writes a valid artifact.
- The first submission establishes a reproducible leaderboard baseline.
- The submission manifest links the result to the exact notebook version.

### 7.3 Improvement gate

- Every experiment starts with a written hypothesis.
- Identical folds support paired candidate–champion comparison.
- Public versions are created for promoted milestones, not every parameter
  change.
- Rejected experiments remain in the evidence ledger with exact results.

### 7.4 Final gate

- Champion notebook reruns from scratch on Kaggle.
- Final submission is tied to that exact successful public version.
- Submission manifest records OOF AUC, public score, runtime, version, and
  decision.
- README and final lessons explain what worked, what failed, and why work
  stopped.

## 8. Failure Handling

- **Kaggle environment failure:** inspect logs, make the smallest offline-safe
  correction, and rerun.
- **Kaggle/local metric discrepancy:** stop promotion and investigate package
  versions, randomness, paths, and data handling.
- **Malformed submission:** do not submit; validate IDs, row count, column
  order, bounds, finite values, and missing values.
- **Claude/Codex disagreement:** record both technical positions and resolve
  through evidence or user decision.
- **Public score disagrees with OOF:** retain the known-good champion and avoid
  immediate leaderboard-driven tuning.
- **Runtime exceeds budget:** reduce search breadth before reducing validation
  quality.

## 9. Time Budget

Treat this as an initial allocation and revise it after measuring the first
trusted Kaggle modeling runtime:

| Workstream | Hours |
| --- | ---: |
| Correct scaffold, EDA validation, provenance research | 6 |
| Reproducible baselines and first submission | 12 |
| Source-informed features and missingness ablations | 10 |
| Model diversity, blending, and stability checks | 7 |
| Final Kaggle run and portfolio write-up | 5 |
| **Total** | **40** |

## 10. Completion Criteria

The project is complete when all of the following are true:

- a reproducible public champion notebook runs successfully on Kaggle;
- a valid final submission is tied to its exact notebook version;
- accepted and rejected experiments have a traceable evidence trail;
- the repository contains a polished portfolio narrative;
- the final decision explains why further experimentation was unlikely to be
  worth the remaining time.

Completion is not defined merely by exhausting the calendar or experiment
budget.
