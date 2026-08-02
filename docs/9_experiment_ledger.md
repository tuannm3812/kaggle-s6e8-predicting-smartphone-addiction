# Experiment Ledger

Every experiment's hypothesis and promotion criteria are recorded before its
results, per `docs/0_coding_standards.md`. Results and the promotion
decision are appended once the notebook run completes — never edited to fit
the outcome.

## E01 — Comparable GBDT Budget

**Hypothesis:** LightGBM or CatBoost can close the untuned HGB gap
(`docs/6_baseline_modeling.md` §2) when given comparable learning-rate and
iteration budgets to what the current champion (`v1c_hist_gradient_boosting`,
sklearn defaults) was never given a chance to use. The current champion is
also given its own tuned configurations in this search, so the comparison is
a genuine three-family search, not LightGBM/CatBoost chasing a frozen HGB
number.

**Search space:** up to four configurations per family (HGB, LightGBM,
CatBoost), comparable total boosting budget across families, no Optuna or
other automated search — every configuration is hand-designed and listed in
full below before it is run.

**Promotion evidence required (predeclared before running):** a candidate
replaces `v1c_hist_gradient_boosting` as champion only if, against that
exact champion's OOF predictions on the same folds:

1. it beats the champion's fold AUC on a majority of folds (at least 3 of
   the 5 seeded folds), **and**
2. the paired stratified bootstrap's 95% interval lower bound is strictly
   positive (the entire interval favors the candidate), **and**
3. the bootstrap's probability of a positive delta is at least 0.95.

All three conditions must hold. Any rejected configuration is recorded here
with its exact numbers — silently dropping a losing config is not permitted.
If no configuration clears the gate, `v1c_hist_gradient_boosting` remains
champion and every result is still recorded.

**Bootstrap parameters:** 200 resamples, sample size 100,000 (stratified to
the training set's class balance), seed 42, deterministic (`numpy.random.
default_rng(42)`), matching the plan's specification exactly.

## E01 — Results

Executed on a private Kaggle kernel (`tuannm3812/smartphone-addiction-
experiments-private`, version 2, `RUN_MODE = "evaluate"`), not locally —
see the Claude implementation report in `docs/collaboration/active_task.md`
for why. Zero error output; the fold-determinism check passed; every
number below is copied directly from the kernel's execution log
(`print()` output), not display()-rendered or re-derived.

Champion for comparison: `v1c_hist_gradient_boosting` (untuned HGB sanity
baseline), OOF AUC `0.95733`, fold std `0.00076`.

### All 12 configurations, ranked by paired mean delta vs. champion

| Rank | Candidate | Config | OOF AUC | Fold std | Folds beaten (of 5) | Runtime (s) | Paired mean delta | 95% interval | P(delta > 0) | Corr. with champion |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 1 | `e01_lightgbm_c3` | `n_estimators=400, learning_rate=0.05, num_leaves=63` | 0.96166 | 0.00062 | 5 | 80.7 | +0.004315 | [0.004068, 0.004599] | 1.00 | 0.99228 |
| 2 | `e01_lightgbm_c4` | `n_estimators=600, learning_rate=0.03, num_leaves=63` | 0.96142 | 0.00061 | 5 | 128.0 | +0.004072 | [0.003804, 0.004313] | 1.00 | 0.99324 |
| 3 | `e01_hgb_c3` | `max_iter=400, learning_rate=0.05, max_leaf_nodes=63` | 0.96139 | 0.00056 | 5 | 104.8 | +0.004048 | [0.003815, 0.004316] | 1.00 | 0.99364 |
| 4 | `e01_hgb_c4` | `max_iter=600, learning_rate=0.03, max_leaf_nodes=63` | 0.96118 | 0.00053 | 5 | 162.3 | +0.003828 | [0.003614, 0.004063] | 1.00 | 0.99439 |
| 5 | `e01_lightgbm_c1` | `n_estimators=400, learning_rate=0.05, num_leaves=31` | 0.95956 | 0.00066 | 5 | 68.2 | +0.002213 | [0.002045, 0.002379] | 1.00 | 0.99677 |
| 6 | `e01_hgb_c1` | `max_iter=400, learning_rate=0.05, max_leaf_nodes=31` | 0.95930 | 0.00051 | 5 | 90.1 | +0.001947 | [0.001788, 0.002087] | 1.00 | 0.99776 |
| 7 | `e01_lightgbm_c2` | `n_estimators=600, learning_rate=0.03, num_leaves=31` | 0.95891 | 0.00060 | 5 | 103.9 | +0.001563 | [0.001410, 0.001718] | 1.00 | 0.99738 |
| 8 | `e01_hgb_c2` | `max_iter=600, learning_rate=0.03, max_leaf_nodes=31` | 0.95874 | 0.00058 | 5 | 134.9 | +0.001394 | [0.001249, 0.001560] | 1.00 | 0.99823 |
| 9 | `e01_catboost_c3` | `iterations=400, learning_rate=0.05, depth=8` | 0.95296 | 0.00058 | 0 | 658.5 | -0.004375 | [-0.004663, -0.004085] | 0.00 | 0.98914 |
| 10 | `e01_catboost_c4` | `iterations=600, learning_rate=0.03, depth=8` | 0.95192 | 0.00060 | 0 | 998.8 | -0.005413 | [-0.005724, -0.005091] | 0.00 | 0.98804 |
| 11 | `e01_catboost_c1` | `iterations=400, learning_rate=0.05, depth=6` | 0.94917 | 0.00057 | 0 | 500.3 | -0.008163 | [-0.008570, -0.007793] | 0.00 | 0.98430 |
| 12 | `e01_catboost_c2` | `iterations=600, learning_rate=0.03, depth=6` | 0.94799 | 0.00069 | 0 | 738.2 | -0.009346 | [-0.009729, -0.008971] | 0.00 | 0.98233 |

All values are exactly as printed in the kernel log at
`https://www.kaggle.com/code/tuannm3812/smartphone-addiction-experiments-private`
(version 2) — none reconstructed or rounded beyond the log's own precision.

### Promotion gate applied

Per the predeclared rule above: **8 of 12 configurations clear the gate**
(all four HGB and all four LightGBM tuned configs — every one beats the
champion on all 5 folds, has an entirely positive 95% interval, and
`P(delta > 0) = 1.00`). All four CatBoost configurations fail decisively
(0 folds beaten, entirely negative intervals) — tuning depth and iteration
budget did not close CatBoost's gap from the original baseline comparison
(`docs/6_baseline_modeling.md` §2); it remains the weakest family even
after a comparable tuning pass.

**Winner (highest paired mean delta among gate-clearing candidates):
`e01_lightgbm_c3`** — `LGBMClassifier(n_estimators=400, learning_rate=0.05,
num_leaves=63, random_state=42)`.

### Decision

**Promoted.** `e01_lightgbm_c3`'s configuration replaces
`hist_gradient_boosting` as the notebook's champion:
`CHAMPION_NAME = "lightgbm_tuned"`, added to `build_model()` as a second
branch, `NOTEBOOK_VERSION = "e01-lightgbm-v1"`. The untuned HGB sanity
baseline (`v1c_hist_gradient_boosting`) remains in the notebook as a fixed
comparison point for E01 (hardcoded to
`build_model("hist_gradient_boosting")`, independent of `CHAMPION_NAME`) —
it is not deleted, since it is E01's own reference floor, not a discarded
result.

Post-promotion sanity check on `lightgbm_tuned`'s OOF predictions (same
check applied to the prior champion in Section 10): finite, within
`[0, 1]`, 691,367 of 691,369 predictions unique (not degenerate),
prediction range `(0.000596, 0.999996)`, overall OOF AUC `0.961664`
(matches the table above to the displayed precision).

### What this means for Task 6 and Task 7

- Task 7 ("Publish Champion") will publish `lightgbm_tuned`, not the
  original HGB baseline already public from Task 4.
- Task 6's entry condition ("no Task 5 candidate beats the current
  champion, or two strong candidates have prediction correlation below
  0.995 with complementary residuals") is not evaluated here — the
  relevant correlation is between the top *candidates* (e.g.
  `e01_lightgbm_c3` vs. `e01_hgb_c3`), not between a candidate and the
  original champion, and computing it is Task 6's own entry-condition
  check, not part of E01.
