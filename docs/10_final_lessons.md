# Final Lessons — Playground Series S6E8

Closed under Task 7 after Tasks 1–6 (EDA → validator → baseline → public HGB
score → GBDT tuning → diversity SKIP). Authoritative collaboration history:
`docs/collaboration/archive/`.

## Final Scores

| Metric | Value | Venue / evidence |
| --- | ---: | --- |
| Champion OOF AUC | **0.96166** | Private experiments kernel (E01/E02); `docs/9_experiment_ledger.md` |
| Champion config | `lightgbm_tuned` = LGBM c3 (`n_estimators=400`, `learning_rate=0.05`, `num_leaves=63`, `random_state=42`) | `build_model("lightgbm_tuned")` / `LGBM_CONFIGS[2]` |
| Prior public HGB baseline | OOF 0.95733 → public **0.95865** | Public baseline kernel v1; `docs/8_submission_manifest.md` |
| Champion public AUC | **pending** | Public baseline kernel **v2** artifact validated; not submitted pending user authorization (`docs/7_kaggle_run_manifest.md`) |

## Accepted Hypotheses

- Untuned sklearn HGB is a strong, cheap floor (OOF 0.95733; first public
  score 0.95865).
- Hand-designed, budget-aligned LightGBM beats that floor with paired
  bootstrap support (`e01_lightgbm_c3`, OOF 0.96166, gate cleared vs HGB).
- Shared `build_model` / `fit_model` factory keeps evaluate and submission
  paths aligned.
- Private Kaggle for search + public kernel only for milestone artifacts is
  a workable provenance pattern when logs are `print()`-based and fingerprinted.

## Rejected Hypotheses / Stops

- Logistic regression as a usable baseline (numerically unstable here).
- `_is_missing` indicator flags (Δ ≈ 0).
- `class_weight="balanced"` on LightGBM (slightly worse).
- Treating early untuned LGBM/CatBoost vs HGB as a family verdict (mismatched
  budgets; fixed in E01).
- **Task 6 conditional diversity / ensemble:** Pearson correlation between
  `lightgbm_tuned` and tuned HGB c3 was `0.997563` (fails predeclared
  `< 0.995`), despite complementary error-set Jaccard `0.8772` (passes
  `<= 0.90`). AND-gate → **SKIP**. No XGBoost family and no blend sweep.

## Why Further Experiments Stopped

Task 6’s predeclared entry gate failed on correlation. Spending more budget
on a near-collinear second tree model (or a blend of the same pair) was not
justified under the plan. The working champion remains the E01 LightGBM
configuration. Optuna / broader search were never opened on this line of
work after the diversity SKIP.

## Local / Kaggle Reproducibility

- EDA public kernel: printed findings match local aside from a documented
  0.0001 adversarial-AUC difference and package-version drift
  (`docs/7_kaggle_run_manifest.md`).
- HGB submission-mode public v1: validator stats matched local exactly;
  artifact SHA recorded and submitted.
- LightGBM champion public v2: validator summary fields match local
  (`rows=296302`, `unique_predictions=296301`, same min/max); predictions
  agree within ~1e-12 abs; CSV SHA differs across environments (float
  formatting / library builds). Evidence of record for submit is the
  **Kaggle-downloaded** file SHA
  `1986eedcf8f4adb7017494d5559e96fb50195c8bf32636a26927b3c2a6f859b3`.
- Trusted OOF for the champion comes from the private experiments kernel,
  not from public submission-mode runs (which skip CV by design).

## Limitations And Private-Leaderboard Risks

- OOF and public scores are single-split / single-submission snapshots;
  they do not estimate leaderboard variance.
- E01/E02 paired bootstraps condition on fixed OOF fits and are not
  multiplicity-corrected independent confirmations.
- Package versions differ between this Mac and Kaggle; tiny prediction
  float differences are expected.
- Private LB overfitting risk remains if future work chased public scores;
  this project stopped when the diversity gate failed, not when public
  score plateaus were measured for the champion (champion not yet submitted).

## Public Notebooks

- EDA: https://www.kaggle.com/code/tuannm3812/smartphone-addiction-eda
- Baseline / champion modeling:
  https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling
  (v1 = HGB baseline submit; v2 = `lightgbm_tuned` artifact, awaiting submit
  authorization)
