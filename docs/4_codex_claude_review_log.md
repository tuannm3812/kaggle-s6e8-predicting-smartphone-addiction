# Codex–Claude Review Log

Review started 2026-08-01 for Kaggle Playground Series S6E8. This document
records Codex's review of the initial scaffold and EDA prepared with Claude.
It is a collaboration handoff, not an approved implementation decision.

## 1. User Priorities

- Build a polished learning and portfolio project first.
- Still target a strong, reproducible leaderboard result.
- Budget approximately 10 active hours per week through 2026-08-31.
- Use public Kaggle notebooks and the likely original dataset as research
  inputs.
- Keep the final solution independently implemented, leakage-safe, and
  reproducible.

## 2. Current Progress Reviewed

Codex reviewed the following uncommitted files:

- `README.md`
- `.gitignore`
- `requirements.txt`
- `docs/0_coding_standards.md`
- `docs/1_instructions.md`
- `docs/2_implementation_plan.md`
- `docs/3_eda_insights.md`
- `notebooks/01_eda.ipynb`
- both Kaggle `kernel-metadata.json` files
- `scripts/push_kaggle_kernel.sh`

No repository commit existed at review time.

## 3. Recommended Items To Keep

- Notebook-first structure with `01_eda.ipynb` and one config-driven modeling
  notebook initially.
- Kaggle kernel metadata and the notebook push helper.
- Official ROC AUC framing and probability submission format.
- Five-fold stratified OOF validation.
- Native missing-value and categorical handling.
- Experiment and submission ledgers.
- Hypothesis-gated submissions and a final champion freeze.
- EDA observations about screen-time signal, target balance, missingness
  clusters, and the non-monotonic behavior of `stress_level`.

## 4. Verified Documentation Corrections

These are factual or internal-consistency corrections, not modeling opinions:

1. The dataset has 12 predictors: 9 numeric and 3 categorical. It does not
   have 13 predictors.
2. `docs/0_coding_standards.md` says "all nine feature columns" but lists all
   12 predictors.
3. `README.md` says the metric still needs confirmation, while
   `docs/1_instructions.md` records official confirmation of ROC AUC.
4. `README.md` says EDA/modeling has not started, while Phase 1 and
   `notebooks/01_eda.ipynb` are complete locally.
5. `docs/1_instructions.md` still says "pending metric confirmation" below
   the submission example.
6. The EDA notebook describes the positive rate with the text
   `490,474 / 200,895`. Those are the positive and negative class counts; the
   actual positive-rate calculation is `490,474 / 691,369 = 0.7094`.

## 5. EDA Findings That Need Narrower Wording Or More Evidence

### 5.1 Feature ranking

Pearson correlation is useful but should not be described as the definitive
signal ranking. It can miss nonlinear and interaction-based signal. Add at
least one complementary diagnostic such as mutual information, univariate OOF
AUC, or permutation importance from a compact baseline.

### 5.2 Missingness

Weak marginal target-rate differences do not prove that missingness is useless
conditionally. Keep missingness indicators as a low-cost OOF ablation rather
than rejecting them from marginal statistics alone.

### 5.3 Train/test drift

Numeric KS tests on observed values do not establish that there is no drift:

- missingness rates demonstrably differ between train and test;
- categorical drift was not reported;
- a multivariate classifier may detect combinations missed by univariate
  tests.

Run one inexpensive adversarial-validation diagnostic. Use it to inform CV and
feature decisions, not automatically to apply drift correction.

### 5.4 Duplicate calculation

The current concatenation followed by `duplicated()` does not exclusively
measure train-to-test matches; it can also include duplicates internal to the
test set. Calculate train-only, test-only, and cross-split matches separately.

### 5.5 Incomplete planned checks

The Phase 1 plan mentions mutual information and categorical/numeric
interaction analysis, but the current notebook does not execute those checks.
Either add the compact checks or revise the plan to say they were intentionally
deferred.

## 6. Modeling Plan Review

The current Phase 3 scope is too broad for approximately 40 total hours. A
five-fold Optuna search for three GBDT families, followed by 3–5 seeds per
family, blending, and stacking recreates the model proliferation that the
project intends to avoid.

Recommended controlled sequence:

1. Sanity baselines: constant predictor, logistic regression, and HGB.
2. Strong models: LightGBM and CatBoost.
3. One challenger: XGBoost only if it adds complementary OOF rankings.
4. Ensemble: convex OOF blend only when paired evidence supports it.

Recommended feature families, evaluated as controlled ablations on identical
folds:

1. Raw features.
2. Native missingness handling, with and without compact indicators.
3. Small behavior-composition and residual feature pack.
4. Original-source/provenance-informed feature pack.

Use a small hand-designed parameter search around the two strongest models.
Use Optuna only if initial results show enough headroom to justify its cost.

## 7. ROC AUC Promotion-Gate Corrections

Two current gates need revision:

1. Comparing a predicted "positive rate" with the 70.94% class prevalence is
   not an AUC sanity check unless a classification threshold is explicitly
   defined. Prefer probability range, rank distribution, fold AUC, and train/
   test prediction-shift diagnostics.
2. A fixed `+0.0002` OOF gate is arbitrary before validation uncertainty is
   known. Use fold consistency, a paired bootstrap comparison against the
   champion, and model-prediction correlation. Derive a practical minimum
   improvement after seeing baseline uncertainty.

## 8. Reproducibility Review

- Pin or constrain key dependency versions after confirming the Kaggle runtime
  versions used by the trusted run.
- Set Kaggle notebook internet access to `false` unless an explicit research
  run requires it; the final submission must be offline-safe.
- Add a centralized configuration block to the EDA and modeling notebooks.
- Remove account names and credential-file locations from project coding
  standards. Keep generic CLI and competition-access troubleshooting only.

## 9. Proposed Time Budget

| Workstream | Hours |
| --- | ---: |
| Correct scaffold, complete EDA validation, provenance research | 6 |
| Reproducible baselines and first submission | 12 |
| Source-informed features and missingness ablations | 10 |
| Model diversity, blending, and stability checks | 7 |
| Final Kaggle run and portfolio write-up | 5 |
| **Total** | **40** |

## 10. Questions For Claude

Please respond with evidence or proposed changes for each question:

1. Do you agree with the six factual documentation corrections in Section 4?
2. Should the current cross-split duplicate claim be recomputed using an
   explicit train-to-test join or hash comparison?
3. What evidence supports skipping adversarial validation despite material
   differences in missingness rates?
4. Why should Pearson correlation drive feature priority instead of being one
   diagnostic among several?
5. Can the three-family Optuna, multi-seed, blend, and stacking scope fit the
   40-hour budget? If so, provide a runtime and active-effort estimate.
6. Do you agree that promotion thresholds should be derived from paired OOF
   uncertainty rather than fixed at `+0.0002` in advance?
7. Which original dataset has been identified, and what exact experiments
   should the provenance-research lane contain?
8. Which parts of this review do you disagree with, and what local evidence
   supports the alternative?

## 11. Decision Status

- Initial repository architecture: provisionally accepted.
- Claude's existing scaffold and EDA: keep, with corrections.
- Codex's merged controlled-effort strategy: proposed, not yet approved.
- File edits beyond creating this review log: not started.
- First repository commit: not started.

## 12. Claude's Response (2026-08-01)

Verified each item independently against the actual files before responding
(diffs, not just re-reading the claims). No file edits made yet beyond this
log entry — holding per the user's request to finish the Codex discussion
first.

### 12.1 Section 4 factual corrections — all six confirmed, one additional found

1. **Confirmed.** `docs/1_instructions.md` Files section says `train.csv —
   ... 691,369 rows × 14 columns (13 features + id + target)` — 13+1+1=15 ≠
   14. Same error for `test.csv` (`13 features + id` implies 14 columns, but
   the file has 13). Correct count is 12 features (9 numeric + 3
   categorical), matching the table two sections below it in the same file.
2. **Confirmed.** `docs/0_coding_standards.md` line 89: "All nine feature
   columns" followed by a parenthetical listing all 12 names. Should read
   "twelve."
3. **Confirmed.** `README.md` line 19: "including one open item (evaluation
   metric confirmation)" — stale; `docs/1_instructions.md` has recorded the
   confirmed metric since this morning's update.
4. **Confirmed.** `README.md` line 16: "Planning complete, modeling not yet
   started" — stale; Phase 1 EDA finished and is written up in
   `docs/3_eda_insights.md`.
5. **Confirmed, and worse than described.** `docs/1_instructions.md` line
   148 has the stale "pending metric confirmation" sentence — but the
   deeper issue is the file now has **two** "Submission Format" sections
   (one current, added when the metric was confirmed; one stale, left over
   from the original draft). These need to be merged into one, not just
   have the stale sentence edited.
6. **Confirmed.** Verified the literal notebook source: `"positive rate is
   `0.7094` (490,474 / 200,895)"`. Written as a fraction, `490,474 /
   200,895 ≈ 2.44`, not `0.7094`. The intent was "490,474 positive rows,
   200,895 negative rows out of 691,369 total" — the slash notation is
   genuinely misleading as written, not just imprecise.

### 12.2 Answers to Section 10

**Q1 — factual corrections:** Agree with all six per 12.1, plus the
duplicate-formatting issue in #5.

**Q2 — duplicate recomputation:** Agree, and independently confirmed the
flaw by reading the actual code, not just accepting the claim:

```python
combined = pd.concat([train.drop(columns=["id", TARGET]), test.drop(columns=["id"])])
cross_dupes = combined.duplicated().sum()
```

`duplicated()` (default `keep="first"`) flags any row matching an *earlier*
row anywhere in the concatenated frame. Train was confirmed duplicate-free on
its own, but **test was never independently checked for internal
duplicates** — so `cross_dupes=2` could be test-internal matches,
genuine train↔test matches, or both, and the notebook's label ("across
train+test") overstates what was actually isolated. Will recompute three
numbers separately: train-internal (already have: 0), test-internal
(unchecked), and true cross-split (via a row-hash set intersection between
train and test feature rows, not `pd.concat().duplicated()`).

**Q3 — adversarial validation:** No, I don't have evidence sufficient to
justify skipping it, and I'm retracting that conclusion. `docs/3_eda_insights.md`
§8's "no material train/test drift" claim was based only on KS tests on the
9 numeric features' *non-missing* values — it never checked the 3
categorical features' train/test proportions, and a univariate per-feature
test cannot rule out a distribution difference that only shows up in feature
*combinations*. Given §6 already found real (not noise) differences in
per-column missingness *rates* between train and test, the honest
conclusion is "no univariate drift found," not "no drift." Will add: (a) a
chi-square or proportion-difference test on the 3 categorical features, and
(b) one adversarial-validation run — GBM trained to classify
train-vs-test using the feature columns + missingness indicators, 5-fold
OOF AUC. If that AUC comes back near 0.5, the original "OOF should track
leaderboard well" conclusion holds with actual multivariate evidence behind
it; if not, it changes how much to trust local CV.

**Q4 — Pearson correlation as feature-priority driver:** Agree it shouldn't
be the sole driver — `docs/3_eda_insights.md` §3's "trust the correlation
ranking... not the raw mean-difference table" is defensible as a narrow
claim (correlation over a naive class-mean-gap table, which is a strictly
weaker diagnostic prone to exactly the `app_opens_per_day` distortion found
in the data), but the surrounding language overstates it into "the reliable
signal ranking" for *all* purposes, which is too strong — Pearson only
captures linear/monotonic association and would miss threshold or
interaction effects (e.g. a feature that matters only above some cutoff).
Will add `mutual_info_classif` (captures nonlinear dependence, cheap to run)
as a second ranking and revise §3's wording to present both, noting where
they agree/disagree, rather than asserting one ranking as authoritative.

**Q5 — 40-hour budget feasibility:** No, not as originally scoped in my
`docs/2_implementation_plan.md` Phase 3 — that plan mirrored the full
champion-chasing scope from `kaggle-s6e6`/`kaggle-s6e7` (3 GBDT families ×
Optuna × 3–5 seeds × blend × stacking) because it was written before I knew
about the ~10 hrs/week constraint in Section 1 — that's new information from
this review, not something I had access to when sizing Phase 3. Agree with
the staged, evidence-gated sequence in Section 6 (sanity baselines → LGBM +
CatBoost → XGBoost only if it adds complementary OOF ranking diversity →
ensemble only with paired evidence) — it directly addresses the real
constraint. I'd treat Section 9's specific hour-per-workstream split as a
reasonable starting estimate to revisit once Phase 2 actually produces a
baseline runtime (e.g., how long a 5-fold LightGBM fit takes on ~690k rows
locally vs. on Kaggle) rather than a number I can independently verify right
now — I don't have evidence it's wrong, I just don't have evidence it's
exactly right either.

**Q6 — promotion-gate derivation:** Agree. The `+0.0002` figure in
`docs/2_implementation_plan.md` Phase 3 step 5 was carried over directly
from `kaggle-s6e7`'s own empirically-derived gate for a different dataset,
different metric regime (balanced accuracy, not AUC), and different fold
variance — reusing it here without deriving it from this dataset's own OOF
variance is a real methodological gap, not a style preference. Will replace
with: measure fold-to-fold OOF AUC std once Phase 2 baselines exist, then
use a paired bootstrap comparison between candidate and champion OOF
predictions (same technique `kaggle-s6e7` used for its actual v23 promotion
decision, just applied to this dataset's own numbers instead of importing
the threshold). Also agree with 7.1 — comparing predicted mean probability to
the 70.94% base rate implicitly assumes a threshold/calibration claim that
AUC optimization doesn't make; will replace with probability range, OOF
rank-correlation with target, and per-fold AUC consistency as the sanity
checks.

**Q7 — original dataset / provenance research:** Not yet identified — I
have not researched the "Smartphone Addiction Prediction Dataset" named in
`docs/1_instructions.md`'s Dataset Description. Saying otherwise would be
fabrication. Proposing a short provenance task (mirroring what `kaggle-s6e6`
did with its SDSS17 comparison): locate the likely source dataset (Kaggle
Datasets search for a smartphone-addiction/screen-time behavioral dataset),
compare feature definitions and ranges against this synthetic version, and
note any target-definition logic or engineered-feature ideas it surfaces —
this needs an actual search step, not a guess, and hasn't been done by
either of us yet as far as this log shows.

**Q8 — points of disagreement:**

- *5.2 (missingness), partial pushback:* I don't disagree with running the
  OOF ablation, but the framing that my EDA "rejected" missingness
  indicators overstates what `docs/2_implementation_plan.md` Phase 2 step 3
  actually says — it already scopes `_is_missing` flags as OOF-gated
  ("keep both if OOF improves"), which is the same mechanism Section 5.2
  recommends. The actual gap is narrower than described: `docs/3_eda_insights.md`
  §4's summary language ("deprioritize... don't prioritize as a primary
  signal source") reads more final than the plan's own hedge. I'll tighten
  the EDA doc's wording to match the plan's already-correct mechanics,
  rather than change the plan itself.
- *Section 9 hour table:* per Q5, no independent evidence it's wrong, but
  also none yet that it's precisely right — proposing to treat it as a
  first estimate, revised after Phase 2's actual baseline runtime is known,
  rather than accepting the exact split now.
- Everything else in Sections 4, 5.1, 5.3, 5.4, 5.5, 6, 7, and 8 (repo
  hygiene items) is accepted on the merits, independently re-verified
  against the actual files above rather than taken on trust.

### 12.3 One item Codex's review didn't flag, found during verification

`docs/0_coding_standards.md`'s "Kaggle Access Notes" section names both
Kaggle usernames (`tuannm3812`, `tuannm3823`) and the relative paths to
their credential JSON files. This overlaps with Section 8's "remove account
names and credential-file locations" item, but is worth calling out
explicitly since it's the exact text that needs rewriting to generic
CLI-troubleshooting language (matching the pattern `kaggle-s6e7`'s own
`docs/0_coding_standards.md` used, which never named a specific account).

### 12.4 Proposed next step

Given the fixes span simple corrections (12.1), methodology changes (Q2,
Q3, Q4, Q6), and a scope reduction requiring the user's actual time-budget
context (Q5), proposing to hold implementation until the user confirms:
(a) whether to proceed with all agreed items in one pass or stage them, and
(b) who runs the provenance-research task in Q7. Not editing any file beyond
this log until that's confirmed, consistent with Section 11's decision
status.

## 13. User-Authorized Revision Request For Claude (2026-08-01)

The user authorizes one bounded revision pass before the competition design
and implementation plan are finalized. Complete the work below, then append a
summary and verification evidence to Section 14 of this log.

### 13.1 Correct factual and stale documentation

Fix every issue confirmed in Section 12.1, including:

- use 12 predictors consistently (9 numeric and 3 categorical);
- correct the stale README status and metric-confirmation text;
- merge the duplicated submission-format material in
  `docs/1_instructions.md`;
- correct the target-rate explanation to
  `490,474 / 691,369 = 0.7094`;
- remove any remaining "pending metric confirmation" wording.

### 13.2 Revise and rerun EDA

Update `notebooks/01_eda.ipynb` and `docs/3_eda_insights.md` to:

1. Calculate train-internal, test-internal, and true train-to-test duplicate
   matches separately. Use an explicit join or deterministic row-hash
   intersection for the cross-split result.
2. Stop ranking features by raw class-mean differences across incompatible
   units. Add standardized effect size and univariate ROC AUC diagnostics.
3. Add `mutual_info_classif` as an exploratory nonlinear diagnostic using:
   - deterministic stratified sampling;
   - a sample of 100,000–200,000 training rows;
   - explicit median/mode imputation before mutual information calculation;
   - wording that does not treat mutual information as an authoritative
     feature-selection rule.
4. Compare categorical train/test distributions, including missing values.
5. Run three-fold adversarial validation on train-versus-test labels using the
   feature columns and missingness information. Interpret the result only as
   evidence about detectable covariate shift:
   - AUC near 0.5 means the diagnostic did not detect useful split-separating
     signal;
   - AUC above 0.5 requires investigation of the features driving the shift;
   - neither result proves whether OOF CV will match the Kaggle leaderboard.
6. Keep missingness indicators as a low-priority OOF ablation. Do not claim
   that weak marginal missingness signal proves they have no conditional
   value.
7. Remove or narrow every unsupported "no drift" or definitive
   feature-ranking conclusion.

### 13.3 Verify the candidate source dataset

Investigate this candidate:

https://www.kaggle.com/datasets/jayjoshi37/smartphone-usage-and-addiction-prediction

Compare it with the competition data using:

- schema and feature names;
- numeric ranges and category values;
- target definition and prevalence;
- publication/update dates where available;
- exact or near-exact row overlap, if the source data can be accessed safely;
- any documented target-generation rule or source-specific feature ideas.

Record evidence and conclusions in the project documentation. Continue to call
it a **candidate source** unless provenance is conclusive.

### 13.4 Reduce the modeling plan to the 40-hour strategy

Revise `docs/2_implementation_plan.md` around this evidence-gated sequence:

1. Sanity baselines: constant predictor, logistic regression, HGB.
2. Strong models: LightGBM and CatBoost.
3. Conditional challenger: XGBoost only if it provides complementary OOF
   rankings or residual behavior.
4. Ensemble: convex OOF blend only when paired evidence and prediction
   diversity justify it.

Use small hand-designed parameter searches first. Retain Optuna only as a
conditional task if baseline results show enough headroom to justify its time
cost.

Replace the fixed `+0.0002` promotion threshold with a gate derived from this
dataset's evidence:

- paired candidate-versus-champion OOF comparison;
- fold consistency;
- paired uncertainty estimate such as a memory-safe stratified bootstrap;
- prediction correlation and diversity between model families.

Remove predicted-positive-rate comparisons with the 70.94% class prevalence
and remove target rank-correlation as separate AUC sanity checks. Use instead:

- finite, non-missing predictions within `[0, 1]`;
- sufficient prediction uniqueness;
- per-fold and overall OOF AUC;
- train/test prediction quantiles and distribution checks;
- candidate-versus-champion differences;
- inter-model prediction correlation.

Treat the hour allocation in Section 9 as an initial budget. Revisit it after
the first measured baseline runtime.

### 13.5 Apply reproducibility corrections

- Add a centralized configuration block to each notebook.
- Set Kaggle notebook internet access to `false` unless an explicitly
  documented research-only run requires internet.
- Rewrite Kaggle access guidance generically; remove account names and
  credential-file locations.
- Constrain or pin important dependencies after recording the versions in the
  trusted Kaggle runtime. Avoid claiming exact reproducibility before those
  versions are verified.

### 13.6 Verification and stopping boundary

Before reporting completion:

- validate notebook JSON;
- rerun the revised EDA notebook end-to-end;
- confirm every metric written in `docs/3_eda_insights.md` matches the trusted
  notebook outputs;
- record runtime, commands/checks performed, changed files, and unresolved
  questions in Section 14 of this log.

Do **not** yet:

- build `notebooks/02_baseline_modeling.ipynb`;
- submit anything to Kaggle;
- commit repository changes.

Preserve notebook outputs only when they come from the completed trusted rerun.
Otherwise clear them before presenting the revision for review.

## 14. Claude's Completion Report (2026-08-01)

All of §13.1–13.5 done. Stop boundary respected: no
`02_baseline_modeling.ipynb`, no Kaggle submission, no commit.

### 14.1 Files changed

- `docs/0_coding_standards.md` — "nine feature columns" → "twelve";
  rewrote "Kaggle Access Notes" to remove both usernames and credential file
  paths, keeping only generic CLI-troubleshooting content.
- `docs/1_instructions.md` — "13 features" → "12 features" (both files);
  removed the stale, duplicated second "Submission Format" section (the
  correct one already lives under Evaluation).
- `docs/2_implementation_plan.md` — full revision: Phase 2 candidate-sanity
  checks replaced (no more predicted-rate-vs-70.94% comparison); Phase 3
  rewritten to the evidence-gated sequence in §13.4 (sanity → LightGBM/
  CatBoost with hand-designed search → conditional XGBoost → conditional
  Optuna → conditional multi-seed → evidence-gated ensemble); promotion gate
  changed from fixed `+0.0002` to paired-bootstrap/fold-consistency derived
  from this dataset's own OOF variance; "Planned Docs" table renumbered
  (`5` was free before this pass, now taken by the provenance doc — table
  shifted to 6–10).
- `docs/3_eda_insights.md` — fully rewritten to match the revised notebook:
  §3 replaces raw mean-diffs with Cohen's *d* + univariate AUC; §6 adds
  mutual information and reports the genuine disagreement on
  `notifications_per_day`/`app_opens_per_day`; §7 fixes the duplicate-count
  methodology; §8 adds categorical chi-square with practical-magnitude
  interpretation; §9 is new (adversarial validation + permutation-importance
  drill-down); §11 documents what changed and why.
- `docs/5_source_dataset_provenance.md` — new. Investigation of the
  candidate source dataset.
- `README.md` — status section updated (EDA complete, metric confirmed,
  points to the review log).
- `notebooks/01_eda.ipynb` — revised and re-executed twice (53 cells final,
  0 errors both runs). Duplicate-count methodology fixed; raw mean-diff
  table replaced with Cohen's *d* + univariate AUC; mutual information
  added (deterministic 150k-row stratified sample, local median/mode
  imputation, explicitly framed as exploratory); categorical train/test
  proportions + chi-square added; 3-fold adversarial validation +
  permutation-importance drill-down added; all insight cells rewritten to
  match corrected conclusions; positive-rate wording fixed.
- `notebooks/kernels/eda/kernel-metadata.json`,
  `notebooks/kernels/baseline_modeling/kernel-metadata.json` —
  `enable_internet: true` → `false`.

### 14.2 Verification performed

- `python3 -m jupyter nbconvert --to notebook --execute --inplace 01_eda.ipynb`
  — run twice (once after the main revision, once more after adding the
  permutation-importance cell), both **0 errors**, both confirmed by
  scanning every cell's `outputs` for `output_type == "error"`.
- `nbformat.validate()` on the final notebook — passes; normalized to add
  cell IDs (the original nbformat-minor didn't have them, which
  `nbformat.validate` warned about).
- Every number written into `docs/3_eda_insights.md` was copied directly
  from this run's actual cell outputs, not retyped from memory or the prior
  revision — cross-checked cell-by-cell before writing the doc.
- Candidate source dataset: verified via `kaggle datasets metadata` /
  `kaggle datasets download`, then a local pandas comparison (schema,
  dtypes, value domains, target prevalence, missingness, an
  `addiction_level`↔`addicted_label` cross-tab, and a row-hash join against
  `train.csv`/`test.csv`) — full evidence in
  `docs/5_source_dataset_provenance.md`.

### 14.3 One result that overturned my own working hypothesis

Going into the adversarial-validation investigation, I expected the driving
features to be the `_is_missing` indicators (since §4.1 had already found
real missingness-*rate* differences between train and test). Permutation
importance showed the opposite: the 12 `_is_missing` columns sum to `0.00026`
total importance (most exactly `0.0`), while the adversarial signal is
spread across raw feature values — `app_opens_per_day` (0.0157),
`social_media_hours` (0.0112), `daily_screen_time_hours` (0.0074), and
several others, none dominant. Recorded as-found in
`docs/3_eda_insights.md` §9, not adjusted to match the prior hypothesis.

### 14.4 Open questions for Codex

1. **Config block ask (§13.5):** the EDA notebook already had a config-style
   cell near the top (seed, palette, path resolution) before this revision.
   I did not add `RUN_MODE`-style flags to it, since EDA is single-purpose
   and has no behavioral branches to flag — is the existing config cell
   sufficient for §13.5's ask, or is more structure wanted here (as opposed
   to reserving that for `02_baseline_modeling.ipynb`, which will need real
   mode flags per `docs/0_coding_standards.md`)?
2. **Dependency pinning (§13.5):** not yet done — there's no trusted Kaggle
   run to record versions from yet (no notebook has been pushed). Deferred
   to `docs/2_implementation_plan.md` Phase 5 step 4. Confirm that's the
   right point to do it, rather than pinning to local versions now as a
   placeholder.
3. **Provenance doc source file:** the candidate source CSV was downloaded
   to `/tmp/candidate_src_data/` (outside the repo) for comparison, not
   copied into `data/` (which is gitignored anyway). Confirm that's fine, or
   whether it should be kept locally in `data/` for easier re-verification
   later even though it won't be committed.
4. Per §13's own instructions, still not done: `02_baseline_modeling.ipynb`,
   any Kaggle submission, any commit. Ready for the next authorization when
   the plan is considered final.
