# Coding Standards

## Baseline

This project follows the shared `coding-standards/coding_standards.md` at the
GitHub root (`/Users/tuannm3812/Documents/GitHub/coding-standards`) as its
baseline. That file is the fallback for anything not overridden below —
commit message convention, pre-commit/pre-push workflow, feature-engineering
and leakage-prevention rules, and general documentation style all live there.
Everything in this doc is either a project-specific addition or an explicit
override of the shared baseline.

## Repository Scope

Notebook-first Kaggle workflow, matching the pattern used in
`kaggle-s6e6-predicting-stellar-class` and `kaggle-s6e7-predicting-student-health-risk`:

- `notebooks/` for EDA, baseline modeling, tuning, and ensembling, plus
  `notebooks/kernels/<name>/` holding each notebook's Kaggle
  `kernel-metadata.json` (see "Pushing Notebooks To Kaggle" below).
- `docs/` for durable findings and decisions.
- `assets/` for README images.
- `scripts/` for small CLI helpers (the Kaggle push script), not core logic.
- `data/` for local Kaggle files. Raw data is ignored.
- `predictions/` for OOF and test prediction matrices. Generated predictions
  are ignored.
- `scratch/` for temporary automation scripts. Generated helpers are ignored.

`data/`, `predictions/`, and `scratch/` are intentional additions on top of
the shared baseline's minimal root — this project needs local Kaggle CLI
downloads and OOF artifact review, so keep them, gitignored.

## Document Naming

- `0_coding_standards.md` — this file.
- `1_instructions.md` — official task, metric, files, deadline.
- `2_implementation_plan.md` — the day-1 phased plan (this competition's
  roadmap from EDA through final submission).
- Reserve further numbers for promoted, project-owned findings (EDA insights,
  baseline modeling results, submission manifest, leaderboard-improvement
  ledger) as the work actually produces them — don't pre-create empty docs.

Notebook naming: `01_eda.ipynb`, `02_baseline_modeling.ipynb`. Every
subsequent experiment (calibration, blends, HP search, multi-seed, CatBoost
diversity, stacking) should live as a config-flagged section inside
`02_baseline_modeling.ipynb` rather than a new notebook file, unless it
becomes too large or slow to run as a single public notebook — the same rule
`kaggle-s6e7` converged on after starting with a 4-notebook split.

## Python Style

- Follow PEP 8: 4-space indentation, group imports stdlib → third-party →
  local with a blank line between groups.
- Prefer small reusable functions with type hints; Google-style docstrings
  for anything reused across cells.
- Keep feature engineering fold-safe: target-derived transformations (target
  encoding, calibration, thresholding) must be fit inside each training fold
  only, never on the full training set before splitting.

## Notebook Style

Each notebook should include:

- Purpose statement.
- Configuration cell near the top, including explicit mode flags where
  behavior differs by run (one flag per experiment, not commented-out code).
- Deterministic seed.
- Markdown insight cells after every important plot or metric.
- Relative input-path handling for Kaggle and local execution.
- Numbered sections with clear reader-facing headers.
- A final "next moves" section that converts findings into experiments.
- Public-notebook polish: concise prose, no debug clutter, output tables
  readable without opening the source code.

**Outputs policy:** clear outputs before committing if the notebook code
changed and hasn't been rerun on Kaggle yet.
**Offline-safety:** the submitted notebook must not depend on internet
access beyond the Kaggle-provided input mount; gate any exploratory package
install behind a config flag, defaulting off.

## Feature Engineering & Leakage Prevention

- Only use fields available at inference time / present in both train and
  test.
- Never derive a feature from `addicted_label` outside cross-validation
  folds. Target encoding, calibration, and cross-fitted thresholds must be
  fit inside each fold and applied to that fold's held-out rows and to the
  test set.
- All twelve feature columns (`age`, `daily_screen_time_hours`,
  `social_media_hours`, `gaming_hours`, `work_study_hours`, `sleep_hours`,
  `notifications_per_day`, `app_opens_per_day`, `weekend_screen_time`,
  `gender`, `stress_level`, `academic_work_impact`) have missing values in
  both train and test (see `docs/1_instructions.md`) — missingness itself may
  carry signal, so prefer models/encodings that use it directly (native
  categorical NA handling in LightGBM/CatBoost, explicit `_is_missing`
  indicator flags) over blind imputation.

## Plot Style

Use `viridis` as the default color palette or colormap, matching the
previous episode repos.

## Documentation Style

- Findings and implications first, evidence after.
- Cite exact metrics, never vague claims.
- Timestamp any fact that can change: leaderboard scores, champion version,
  submission quota, deadlines.
- Keep the broad narrative in `README.md`; put the evidence trail in the
  numbered `docs/` files.

## Git Hygiene

Do not commit raw Kaggle data, model dumps, prediction arrays, local
credentials, temporary scripts, notebook checkpoints, or ad hoc experiment
dumps from `scratch/`.

## Kaggle Submission Method

Prefer submitting via Kaggle's **notebook submission** ("Submit to
Competition" from within the notebook) over uploading a `submission.csv`
generated elsewhere — Kaggle re-executes the notebook end-to-end, verifying
the leaderboard result matches the committed code. See the shared
`coding-standards/coding_standards.md` §11 for the general rule.

## Pushing Notebooks To Kaggle

Each notebook's Kaggle kernel has its own `kernel-metadata.json` under
`notebooks/kernels/<name>/`. `notebooks/01_eda.ipynb` and
`notebooks/02_baseline_modeling.ipynb` are the single source of truth; the
`.ipynb` copies inside `notebooks/kernels/*/` are gitignored and regenerated
on every push.

Push with `scripts/push_kaggle_kernel.sh <eda|baseline>` rather than running
`kaggle kernels push` directly against a hand-copied file.

## Kaggle Access Notes

The default `~/.kaggle/kaggle.json` (used by the Kaggle CLI without extra
flags) is configured and has accepted this competition's rules —
`kaggle competitions files playground-series-s6e8` and `kaggle competitions
download` both work as of 2026-08-01. Reusable diagnosis for CLI/API
friction, not specific to this competition:

- **Symptom: `kaggle competitions download` (or `kaggle datasets download`)
  returns `403 Forbidden`, but `kaggle competitions files`/`kaggle datasets
  files` works fine with the same credentials.** Cause: valid API
  credentials are not the same as competition/dataset access acceptance.
  Kaggle requires accepting the competition's rules (or, for some datasets,
  a terms click) through the web UI before the API serves data files, even
  though read-only metadata calls don't require that. Fix: open the page in
  a browser, accept, then retry — no credential change needed.
- **Symptom: `kaggle: command not found`.** Cause: a `pip install --user`
  Kaggle CLI install isn't always on the default `PATH`. Fix: locate it with
  `python3 -m pip show kaggle` / check the user site-packages `bin`
  directory, and either add it to `PATH` for the session or invoke it by
  full path.

**Kaggle competition and dataset Overview/description prose pages are not
fetchable by URL** (confirmed by `kaggle-s6e7`'s own troubleshooting notes,
and by `WebFetch` being unavailable for this purpose — both return only an
empty client-rendered shell). Structured facts (deadline, file list, team
count) come from `kaggle competitions list -s <slug>` / `kaggle competitions
files <slug>` / `kaggle datasets files <owner>/<slug>`; prose text needs to
be pasted in by the user or read after downloading the actual files.
