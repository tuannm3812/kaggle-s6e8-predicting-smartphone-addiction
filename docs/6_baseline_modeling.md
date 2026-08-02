# Baseline Modeling

From `notebooks/02_baseline_modeling.ipynb`, executed end-to-end 2026-08-01
(0 errors, 5-fold `StratifiedKFold(shuffle=True, random_state=42)` OOF
throughout). Findings first, evidence after, per `docs/0_coding_standards.md`.

The notebook has two explicit run modes selected by a `RUN_MODE:
Literal["evaluate", "submission"]` configuration value (rejected immediately
if set to anything else): `evaluate` reproduces every result below;
`submission` fits the configured `CHAMPION_NAME` on all training rows via a
single `build_model(name)` factory and writes a schema-validated
`submission.csv`. Both modes share the same model-construction code path —
there is no separate submission-only model definition.

## 1. Progression Table

Fit times below are local reference timings from one run on this
checkout's hardware, not a controlled benchmark — they vary with system
load (a later run of identical code measured HGB at 937s under heavy
load vs. the 12s shown here) and should be read as rough relative
ordering, not exact wall-clock guarantees.

| Rank | Model | OOF AUC | Fold std | Fit Time (Reference, 5 Folds) |
| --- | --- | ---: | ---: | ---: |
| 1 | `v1c_hist_gradient_boosting` | **0.95733** | 0.00076 | 12s |
| 2 | `v3_lightgbm_plus_engineered` | 0.95533 | 0.00062 | 11s |
| 3 | `v2c_lightgbm_plus_missing_flags` | 0.95480 | 0.00068 | 13s |
| 3 | `v2a_lightgbm_native_cat` | 0.95480 | 0.00068 | 11s |
| 5 | `v2d_lightgbm_class_weight_balanced` | 0.95463 | 0.00058 | 11s |
| 6 | `v2b_catboost_native_cat` | 0.94190 | 0.00063 | 70s |
| 7 | `v1a_constant` | 0.50000 | 0.00000 | theoretical floor, not fit |
| — | `v1b_logistic_regression` | *(retired)* | — | — (numerically unstable, see §3; not in the trusted comparison) |

## 2. Headline Finding: The Sanity Baseline Beat The "Strong Models"

`HistGradientBoostingClassifier` with sklearn defaults (`max_iter=200`,
otherwise untouched) scored **0.9573**, ahead of every LightGBM/CatBoost
variant tried (best: 0.9553). This was not the expected outcome — v1c was
written as a sanity floor, not a candidate.

**This is not evidence that HGB is the better model family.** LightGBM was
run at `num_leaves=31, learning_rate=0.05, n_estimators=200` and CatBoost at
`depth=6, learning_rate=0.05, iterations=200` — reasonable defaults, not a
tuned configuration. HGB's sklearn defaults use `learning_rate=0.1` (double
what LightGBM/CatBoost were given here) at the same iteration budget, among
other differences. The honest reading: **none of these models have been
tuned yet**, and the comparison above is not a fair like-for-like model-family
verdict — it's a floor-setting result that directly justifies
`docs/2_implementation_plan.md` Phase 3 step 2's "small hand-designed
parameter search first" rather than skipping straight to picking a model
family. Do not treat v1c as the presumptive champion without giving
LightGBM/CatBoost a comparable tuning pass first.

## 3. Logistic Regression: Retired, Not Measured

`v1b_logistic_regression` triggered `RuntimeWarning`s (`divide by zero`,
`overflow`, `invalid value encountered in matmul`) during `lbfgs` solver
fitting, despite going through `SimpleImputer` + `StandardScaler` for
numeric features and `SimpleImputer` + `OneHotEncoder` for categoricals —
the pipeline that should prevent exactly this. A second, more conservative
configuration (`solver="saga", penalty="l2", C=0.1, max_iter=2_000,
random_state=SEED, n_jobs=-1`) was tried specifically to stabilize it and
produced the same warnings when run in isolation on the fixed folds. Per
the documented decision rule, logistic regression is now formally
**retired** (`RUN_LOGISTIC = False`) rather than reported as measured: its
OOF AUC is excluded from the trusted comparison table in §1, and the block
is skipped entirely rather than executed and caveated. Not investigated
further — logistic regression is a sanity floor, not a modeling candidate
for this problem, and time is better spent on the tuning pass in §2.
Flagged for anyone reusing this pipeline code elsewhere: the divergence
needs root-causing (likely solver/regularization related) before trusting a
logistic-regression OOF number from this exact setup again.

## 4. `_is_missing` Flags: Clean Answer — No Effect

`v2a_lightgbm_native_cat` (0.954800) vs. `v2c_lightgbm_plus_missing_flags`
(0.954804) — a difference of `0.000004`, far smaller than the fold std
(≈0.0007). This is the direct OOF-ablation test that
`docs/3_eda_insights.md` §4.2/§10 called for, and it resolves cleanly:
**explicit `_is_missing` indicator flags add nothing once native NaN
handling is already in the model.** Consistent with LightGBM's native
missing-value routing already capturing whatever information a redundant
indicator column would add. Do not carry `_is_missing` flags into Phase 3 —
this ablation, not the marginal EDA table, is the reason.

## 5. Engineered Features: Small Positive Signal, Not Yet Distinguishable From Noise

`v3_lightgbm_plus_engineered` (0.955329) vs. `v2a_lightgbm_native_cat`
(0.954800) — a `+0.000529` gain, smaller than one fold standard deviation
(≈0.0006–0.0007). Directionally positive, consistent with
`docs/3_eda_insights.md`'s top-3-feature ratios carrying real signal, but
**this delta alone does not clear the bar** `docs/2_implementation_plan.md`
Phase 3 sets for promotion (paired-bootstrap evidence, not just a raw OOF
gap smaller than fold-to-fold noise). Keep the engineered features as a
live candidate into the Phase 3 tuning pass rather than either committing to
them or discarding them on this result alone.

## 6. Class-Imbalance Weighting: Confirms The EDA-Time Prediction

`v2d_lightgbm_class_weight_balanced` (0.954631) vs. unweighted
`v2a_lightgbm_native_cat` (0.954800) — balanced weighting is very slightly
*lower*, by `0.000169`, again within fold-std noise. Confirms
`docs/2_implementation_plan.md` Phase 2 step 5's prediction: since AUC is
rank-based, `class_weight` mainly perturbs optimizer dynamics rather than
the final ranking, and shows no measurable benefit here. Default to
unweighted going forward; balanced weighting is not worth carrying as a
config dimension into Phase 3 tuning.

## 7. Candidate Sanity Checks (Current Leader: `v1c_hist_gradient_boosting`)

Per `docs/2_implementation_plan.md` Phase 2 step 6 (replacing the old
predicted-rate-vs-70.94%-base-rate check, which implicitly assumed a
threshold AUC optimization doesn't make):

| Check | Result |
| --- | --- |
| Finite, within `[0, 1]` | Pass |
| Unique predictions | 686,565 / 691,369 (99.3%) — not degenerate |
| Prediction range | `(1.7×10⁻⁷⁹, 1.0)` — both ends are legitimate confident probabilities, not out-of-bounds |
| Overall OOF AUC | 0.95733 |

All pass. This is a sanity gate, not a promotion decision — Phase 3 still
needs the fold-consistency and paired-bootstrap checks before anything is
declared champion.

## 8. Reproducibility: Evaluate And Submission Modes

The notebook's `RUN_MODE` flag makes the two things it's used for —
generating OOF evidence and generating a Kaggle submission — explicit and
mutually exclusive, sharing one model factory instead of drifting apart:

- `RUN_MODE = "evaluate"` (the committed default) runs every OOF experiment
  above and reproduces the `0.95733` HGB result exactly.
- `RUN_MODE = "submission"` skips all evaluation-only work, fits
  `CHAMPION_NAME` (currently `hist_gradient_boosting`) on all training rows
  through `build_model()`, and writes a schema-validated CSV to
  `/kaggle/working/submission.csv` (or `../submission.csv` outside Kaggle).
  `build_submission()` checks exact columns, ID order, finite values, and
  the `[0, 1]` probability range before writing.
- Both paths call the same `build_model(name)` factory, so the fitted
  submission model's estimator configuration (class and hyperparameters)
  is guaranteed identical to the one the OOF score was measured on. This
  covers estimator-configuration parity; feature selection and categorical
  conversion are shared through the same data-loading cell rather than the
  factory itself, and were separately verified to match between the two
  modes.

## 9. What Feeds Phase 3

1. **Tune before comparing model families.** §2's gap is a floor-setting
   artifact of mismatched hyperparameters, not a verdict on HGB vs.
   LightGBM vs. CatBoost. Phase 3's hand-designed search should tune all
   three (at minimum matching learning rates/iteration budgets) before any
   model-family conclusion is drawn.
2. **Drop `_is_missing` flags** (§4) — resolved, don't carry forward.
3. **Keep engineered features as an open candidate** (§5) — resolved
   direction (positive), not resolved magnitude (needs the paired-bootstrap
   check once a tuned champion exists).
4. **Default to unweighted** (§6) — resolved, don't carry `class_weight`
   forward as a tuning dimension.
5. **Logistic regression is retired, not fixed** (§3) — a stabilization
   attempt was tried and still failed; root-causing the solver divergence is
   not blocking, since it's a sanity floor rather than a candidate.
6. CatBoost's reference per-fold fit time (70s) is roughly 6x LightGBM's
   (11s) at comparable settings in this same run — a real relative cost to
   weigh against any accuracy gain CatBoost shows once properly tuned,
   given the ~10 hrs/week budget in
   `docs/archive/4_codex_claude_review_log.md` §1, even though the
   absolute seconds are reference timings that vary with system load (§1).
