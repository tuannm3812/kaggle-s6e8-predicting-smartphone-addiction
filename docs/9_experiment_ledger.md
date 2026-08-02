# Experiment Ledger

Every experiment's hypothesis and promotion criteria are documented in this
file before its results, per `docs/0_coding_standards.md`. The hypothesis
section below was written during the working session before any candidate
was run, and results are not edited to fit the outcome — but this is not
independently provable from repository history: the criteria and the first
results both entered Git in the same commit (`4bcbd78`), so commit history
alone cannot establish that ordering.

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

**Recommendation criteria (predeclared before running):** a candidate is
recommended for promotion over `v1c_hist_gradient_boosting` only if,
against that exact champion's OOF predictions on the same folds:

1. it beats the champion's fold AUC on a majority of folds (at least 3 of
   the 5 seeded folds), **and**
2. the paired stratified bootstrap's 95% interval lower bound is strictly
   positive (the entire interval favors the candidate), **and**
3. the bootstrap's probability of a positive delta is at least 0.95.

All three conditions must hold. Any rejected configuration is recorded here
with its exact numbers — silently dropping a losing config is not permitted.
Clearing this gate produces a recommendation for the user's promotion
decision; it does not by itself change which model the notebook's
`CHAMPION_NAME` builds. If no configuration clears the gate,
`v1c_hist_gradient_boosting` remains the recommendation and every result is
still recorded.

**Bootstrap parameters:** 200 resamples, sample size 100,000 (stratified to
the training set's class balance), seed 42, deterministic (`numpy.random.
default_rng(42)`), matching the plan's specification exactly.

## E01 — Results

Executed on a private, GPU-enabled Kaggle kernel dedicated to
experimentation, kept separate from the public baseline notebook. Version 3
is the evidence of record. Version 1 ran the same search but surfaced the
results table only through the notebook's rendered display, not the run
log. Version 2 added `print()` output for the full 12-row statistical
table but still omitted each candidate's individual fold AUCs. Version 3
added those fold-AUC prints and the fail-loud gate-recommendation
assertion, and is the version this section's numbers are taken from.

- Kaggle kernel status: `complete`.
- Run completion observed: `2026-08-02 10:39:12 UTC` (directly observed via
  repeated status polling; the Kaggle API's `lastRunTime` field returned a
  stale earlier timestamp for this kernel and is not used here).
- Downloaded log: 13,368 bytes, SHA-256
  `16d9a8b9afb58058895b770528f265a0c234a973898f1152218accdfe8b0fd01`.
- Zero `error`/`traceback` output. The fold-determinism check
  (`StratifiedKFold` produces identical splits across independent calls)
  passed. The notebook's fail-loud assertion tying the gate's computed
  winner to the documented recommendation (`E01_WINNER ==
  E01_RECOMMENDED_CANDIDATE`) passed silently — no `AssertionError` in the
  log.
- Every number below is copied directly from the kernel's `print()` output,
  not reconstructed, rounded beyond the log's own precision, or taken from
  a rendered table.

Champion for comparison: `v1c_hist_gradient_boosting` (untuned HGB sanity
baseline), OOF AUC `0.95733`, fold std `0.00076`.

### All 12 configurations, ranked by paired mean delta vs. champion

| Rank | Candidate | Config | OOF AUC | Fold std | Folds beaten (of 5) | Runtime (s) | Paired mean delta | 95% interval | Resamples positive | Corr. with champion |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 1 | `e01_lightgbm_c3` | `n_estimators=400, learning_rate=0.05, num_leaves=63` | 0.96166 | 0.00062 | 5 | 76.8 | +0.004315 | [0.004068, 0.004599] | 200/200 | 0.99228 |
| 2 | `e01_lightgbm_c4` | `n_estimators=600, learning_rate=0.03, num_leaves=63` | 0.96142 | 0.00061 | 5 | 122.8 | +0.004072 | [0.003804, 0.004313] | 200/200 | 0.99324 |
| 3 | `e01_hgb_c3` | `max_iter=400, learning_rate=0.05, max_leaf_nodes=63` | 0.96139 | 0.00056 | 5 | 112.4 | +0.004048 | [0.003815, 0.004316] | 200/200 | 0.99364 |
| 4 | `e01_hgb_c4` | `max_iter=600, learning_rate=0.03, max_leaf_nodes=63` | 0.96118 | 0.00053 | 5 | 170.9 | +0.003828 | [0.003614, 0.004063] | 200/200 | 0.99439 |
| 5 | `e01_lightgbm_c1` | `n_estimators=400, learning_rate=0.05, num_leaves=31` | 0.95956 | 0.00066 | 5 | 67.9 | +0.002213 | [0.002045, 0.002379] | 200/200 | 0.99677 |
| 6 | `e01_hgb_c1` | `max_iter=400, learning_rate=0.05, max_leaf_nodes=31` | 0.95930 | 0.00051 | 5 | 96.0 | +0.001947 | [0.001788, 0.002087] | 200/200 | 0.99776 |
| 7 | `e01_lightgbm_c2` | `n_estimators=600, learning_rate=0.03, num_leaves=31` | 0.95891 | 0.00060 | 5 | 102.4 | +0.001563 | [0.001410, 0.001718] | 200/200 | 0.99738 |
| 8 | `e01_hgb_c2` | `max_iter=600, learning_rate=0.03, max_leaf_nodes=31` | 0.95874 | 0.00058 | 5 | 145.6 | +0.001394 | [0.001249, 0.001560] | 200/200 | 0.99823 |
| 9 | `e01_catboost_c3` | `iterations=400, learning_rate=0.05, depth=8` | 0.95296 | 0.00058 | 0 | 653.8 | -0.004375 | [-0.004663, -0.004085] | 0/200 | 0.98914 |
| 10 | `e01_catboost_c4` | `iterations=600, learning_rate=0.03, depth=8` | 0.95192 | 0.00060 | 0 | 976.3 | -0.005413 | [-0.005724, -0.005091] | 0/200 | 0.98804 |
| 11 | `e01_catboost_c1` | `iterations=400, learning_rate=0.05, depth=6` | 0.94917 | 0.00057 | 0 | 493.2 | -0.008163 | [-0.008570, -0.007793] | 0/200 | 0.98430 |
| 12 | `e01_catboost_c2` | `iterations=600, learning_rate=0.03, depth=6` | 0.94799 | 0.00069 | 0 | 736.0 | -0.009346 | [-0.009729, -0.008971] | 0/200 | 0.98233 |

"Resamples positive" is `probability_positive * 200` — the count of the 200
bootstrap resamples (not an independent statistical guarantee) in which the
candidate's AUC exceeded the champion's.

### Individual fold AUCs (all 12 candidates, 5 seeded folds each)

| Candidate | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `e01_hgb_c1` | 0.95865 | 0.95894 | 0.95969 | 0.96005 | 0.95915 |
| `e01_hgb_c2` | 0.95803 | 0.95815 | 0.95910 | 0.95957 | 0.95886 |
| `e01_hgb_c3` | 0.96071 | 0.96100 | 0.96196 | 0.96215 | 0.96115 |
| `e01_hgb_c4` | 0.96052 | 0.96086 | 0.96164 | 0.96195 | 0.96092 |
| `e01_lightgbm_c1` | 0.95863 | 0.95933 | 0.95986 | 0.96063 | 0.95935 |
| `e01_lightgbm_c2` | 0.95804 | 0.95863 | 0.95916 | 0.95987 | 0.95885 |
| `e01_lightgbm_c3` | 0.96069 | 0.96151 | 0.96203 | 0.96257 | 0.96153 |
| `e01_lightgbm_c4` | 0.96051 | 0.96114 | 0.96184 | 0.96231 | 0.96131 |
| `e01_catboost_c1` | 0.94820 | 0.94900 | 0.94951 | 0.94990 | 0.94925 |
| `e01_catboost_c2` | 0.94696 | 0.94749 | 0.94841 | 0.94891 | 0.94818 |
| `e01_catboost_c3` | 0.95207 | 0.95295 | 0.95310 | 0.95388 | 0.95277 |
| `e01_catboost_c4` | 0.95099 | 0.95178 | 0.95198 | 0.95287 | 0.95200 |

### Gate applied

Per the predeclared rule above: **8 of 12 configurations clear the gate**
(all four HGB and all four LightGBM tuned configs — every one beats the
champion on all 5 folds, has an entirely positive 95% interval, and 200 of
200 bootstrap resamples positive). All four CatBoost configurations fail
decisively (0 folds beaten, entirely negative intervals, 0 of 200 resamples
positive). Within this specific bounded search (these four hand-designed
configurations, this iteration/learning-rate range), CatBoost was the
weakest family — tree structure, capacity, and per-iteration compute cost
were not held equal across families, only the iteration count and learning
rate were, so this is not a general claim about CatBoost's ceiling.

**Highest paired mean delta among gate-clearing candidates:
`e01_lightgbm_c3`** — `LGBMClassifier(n_estimators=400, learning_rate=0.05,
num_leaves=63, random_state=42)`.

### What the gate result does and does not support

`e01_lightgbm_c3` is the best-performing configuration found in this
12-candidate bounded search — a **provisional, working recommendation**,
not proof that it is the best possible configuration or that LightGBM is
provably the best family:

- It was selected as the arg-max of paired delta across all 12 candidates
  evaluated on the same OOF predictions used to compute that delta —
  the same data used for both selection and inference. This is a form of
  selection bias (sometimes called the "winner's curse"): the reported
  advantage of the selected candidate is expected to be optimistic relative
  to its advantage on genuinely new data.
- Its margin over the next-best HGB configuration (`e01_hgb_c3`,
  OOF AUC `0.96139`) is only `0.00027` — small relative to the fold-to-fold
  variation already observed elsewhere in this notebook (`docs/
  6_baseline_modeling.md`'s fold stds are of similar magnitude). LightGBM
  and HGB are close, not clearly separated, at the top of this search.
- The paired bootstrap resamples rows from the already-computed,
  already-fitted fold predictions. It quantifies uncertainty from row
  sampling only — it does not include uncertainty from refitting with
  different data splits or random seeds, from the fact that 12
  configurations were compared and the best one reported (a
  multiple-comparisons effect that is not corrected for here), or from
  model/hyperparameter selection itself. Treat the reported interval as a
  lower bound on true uncertainty, not the full picture.

### Recommendation (not a promotion)

`e01_lightgbm_c3`'s configuration is recorded as the E01 recommendation and
wired into `build_model("lightgbm_tuned")` (referencing the same
`LGBM_CONFIGS[2]` dictionary the search used, not a duplicated literal), so
it is available to fit and submit without further code changes. It is
**not** the active champion: `CHAMPION_NAME` remains
`"hist_gradient_boosting"`, and `v1c_hist_gradient_boosting` remains the
notebook's fixed comparison baseline (`build_model("hist_gradient_boosting")`
directly, independent of `CHAMPION_NAME`) — it is not deleted, since it is
E01's own reference floor, not a discarded result. Switching `CHAMPION_NAME`
to `"lightgbm_tuned"` is a separate, explicit, post-approval action once the
user makes a promotion decision.

Sanity check on `lightgbm_tuned`'s OOF predictions (same check the notebook
applies to the current champion): finite, within `[0, 1]`, 691,367 of
691,369 predictions unique (not degenerate), prediction range `(0.000596,
0.999996)`, overall OOF AUC `0.961664` (matches the table above to the
displayed precision).

### Open questions for Task 6 and Task 7

- If `lightgbm_tuned` is promoted, Task 7 ("Publish Champion") would publish
  it in place of the HGB baseline already public from Task 4.
- Task 6's entry condition ("no Task 5 candidate beats the current champion,
  or two strong candidates have prediction correlation below 0.995 with
  complementary residuals") is not evaluated here — the relevant
  correlation is between top *candidates* (e.g. `e01_lightgbm_c3` vs.
  `e01_hgb_c3`), not between a candidate and the original champion, and
  computing it is Task 6's own entry-condition check.
