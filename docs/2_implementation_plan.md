# Implementation Plan

Day-1 phased plan for Playground Series S6E8 (Predicting Smartphone
Addiction), written 2026-08-01 against a **2026-08-31 23:59 UTC** deadline
(30 days), revised 2026-08-01 after the Codex review in
`docs/4_codex_claude_review_log.md`. Takes methodology (native categorical
handling, OOF-first validation, hypothesis-gated submissions, experiment
ledgers) from `kaggle-s6e6-predicting-stellar-class` and
`kaggle-s6e7-predicting-student-health-risk`, but **intentionally does not**
mirror their full model-proliferation scope (3 GBDT families × Optuna ×
multi-seed × blend × stacking) — that scope was sized before the user's
actual constraint was known: **a polished learning/portfolio project first,
still targeting a strong result, at ~10 active hours/week through
2026-08-31** (`docs/4_codex_claude_review_log.md` §1). Phase 3 below reflects
that constraint directly.

Competition shape: binary target `addicted_label` (70.9%/29.1% imbalance),
12 features, every feature column missing at 4%–19% in both train and test
(see `docs/1_instructions.md`).

**Metric confirmed 2026-08-01:** **ROC AUC**, exactly matching the
assumption this plan was built around (see `docs/1_instructions.md`).

## Phase 0 — Setup (done 2026-08-01)

- [x] Repo scaffold: `docs/`, `notebooks/`, `notebooks/kernels/{eda,baseline_modeling}/`,
  `scripts/`, `data/`, `predictions/`, `scratch/`, `.gitignore`,
  `requirements.txt`.
- [x] `data/` populated via `kaggle competitions download -c
  playground-series-s6e8`.
- [x] `docs/0_coding_standards.md`, `docs/1_instructions.md` written and
  corrected (12 features, not 13; credential/account details redacted to
  generic troubleshooting per the Codex review).
- [x] User pasted Overview/Evaluation prose → `docs/1_instructions.md`
  finalized, ROC AUC confirmed.
- [x] Kaggle kernel metadata set to `enable_internet: false` (offline-safety
  default per `docs/0_coding_standards.md` §4 / Codex review §8).
- [ ] First commit of the scaffold (pending user approval).

## Phase 1 — EDA (`notebooks/01_eda.ipynb`, target: by 2026-08-04) — done 2026-08-01, revised 2026-08-01

Executed end-to-end locally twice: an initial pass, then a revision after
the Codex review found several conclusions needed narrower wording or more
evidence (corrected duplicate-count methodology, standardized effect
size/univariate AUC/mutual information instead of raw class-mean gaps or
Pearson alone, categorical train/test comparison, 3-fold adversarial
validation with permutation-importance drill-down). Full findings and what
changed between revisions: `docs/3_eda_insights.md` §1–11.

Headline results feeding Phase 2 below:

- `daily_screen_time_hours`, `weekend_screen_time`, `social_media_hours` are
  the strongest predictors by every diagnostic tried (univariate AUC
  0.86–0.89, `docs/3_eda_insights.md` §3/§6).
- `notifications_per_day` and `app_opens_per_day` are near-uninformative by
  Pearson correlation and univariate AUC, but rank 4th/5th by mutual
  information — a genuine diagnostic disagreement, not resolved by picking
  one ranking; worth testing directly in a nonlinear model rather than
  dropped on linear/rank-based scores alone (`docs/3_eda_insights.md` §6).
- Missingness shows no strong *marginal* target signal, but that doesn't
  rule out conditional value — `_is_missing` flags stay a planned OOF
  ablation, not ruled out (`docs/3_eda_insights.md` §4.2).
- `stress_level` is non-monotonic (High ≈ Low > Medium) — ordinal encoding
  is an OOF experiment to validate, not a default assumption
  (`docs/3_eda_insights.md` §5).
- Adversarial validation (train vs. test) OOF AUC = 0.565 — mild, driven by
  raw feature values/combinations (not the known missingness-rate
  differences, which contribute almost nothing per permutation importance)
  — background context for interpreting any future local-CV-vs-leaderboard
  gap, not grounds for drift correction on its own
  (`docs/3_eda_insights.md` §9).

Also done: `docs/5_source_dataset_provenance.md` investigates the candidate
source dataset (`jayjoshi37/smartphone-usage-and-addiction-prediction`) —
strong circumstantial evidence it's the source named in
`docs/1_instructions.md`'s Dataset Description (identical 12 feature names,
identical target encoding, matching categorical vocabularies, 5/9 numeric
ranges match exactly, target prevalence within sampling noise), including a
recovered target-generation rule (the source's `addicted_label` is a
deterministic collapse of a 4-level severity scale) that sets modeling
expectations without adding a usable feature.

## Phase 2 — Baseline Modeling (`notebooks/02_baseline_modeling.ipynb`, by 2026-08-08) — done 2026-08-01

Executed end-to-end (0 errors); full results in `docs/6_baseline_modeling.md`.
Headline finding: the untuned sklearn `HistGradientBoostingClassifier`
sanity baseline (OOF AUC 0.9573) currently beats the untuned LightGBM/
CatBoost "strong models" (best 0.9553) — **not** a model-family verdict,
since none were tuned to comparable settings; it directly motivates Phase
3's hand-designed search rather than skipping to a model choice. Two
ablations resolved cleanly: `_is_missing` flags add nothing on top of
native NaN handling (drop them), and class-weight balancing shows no AUC
benefit (default to unweighted). Engineered features show a small positive
delta smaller than fold-to-fold noise — carried into Phase 3 as an open
candidate, not yet a confirmed win. Logistic regression hit solver
numerical instability — noted, not blocking, not investigated further
(sanity floor, not a candidate).

Original plan (kept for reference; the steps below were followed as
written):

1. **Validation:** `StratifiedKFold(n_splits=5, shuffle=True,
   random_state=<seed>)` on `addicted_label`. Report OOF AUC per fold and
   mean ± std — the fold-to-fold std here is also what Phase 3's promotion
   gate will be derived from, so record it precisely.
2. **v1 — sanity baselines:** constant predictor (base-rate probability),
   regularized logistic regression, and `HistGradientBoostingClassifier`
   (native NaN handling). Establishes a floor and confirms the eval
   pipeline before any tuning.
3. **v2 — strong models:** LightGBM and CatBoost with native categorical
   support (`gender`, `stress_level`, `academic_work_impact`) and native
   missing-value handling (no imputation).
   - `_is_missing` indicator flags: run as an explicit OOF ablation
     (with vs. without) per `docs/3_eda_insights.md` §4.2/§10 — not skipped.
4. **v3 — engineered features** (from `docs/3_eda_insights.md`'s findings,
   not just the original EDA plan's a-priori guesses):
   - Screen-time composition ratios among the top-3 predictors, e.g.
     `social_media_hours / daily_screen_time_hours`, `gaming_hours /
     daily_screen_time_hours` (guard divide-by-zero/NaN).
   - A 24-hour time-budget residual: `24 - (sleep_hours + work_study_hours +
     daily_screen_time_hours)`.
   - `weekend_screen_time - daily_screen_time_hours` (weekend escalation).
   - `notifications_per_day` and `app_opens_per_day`: include as raw
     inputs and test in the nonlinear models directly (LightGBM/CatBoost
     already handle nonlinear splits) rather than engineering a derived
     ratio speculatively — the mutual-information disagreement
     (`docs/3_eda_insights.md` §6) means the right test is "does a
     nonlinear model use them," not a hand-designed transform.
   - Source-informed feature pack: re-check `docs/5_source_dataset_provenance.md`
     once v1–v3 OOF results exist — if headroom looks limited, revisit
     whether the source's exact numeric ranges (e.g. the narrower
     `daily_screen_time_hours [3,12]` vs. competition's `[0.5,15]`) suggest
     a useful clipping/binning transform; not assumed necessary up front.
   - All engineered features target-free and computable identically on
     train and test — no fold-only stats at this stage
     (`docs/0_coding_standards.md`'s leakage rule).
5. **Class imbalance handling:** AUC is rank-based, so `class_weight`/
   `scale_pos_weight` mainly affects optimizer dynamics, not the ranking
   itself — still worth one OOF A/B (balanced vs. unweighted), logged either
   way, not assumed.
6. **Candidate sanity checks** (replaces the old "predicted positive rate
   vs. 70.94%" check, which implicitly assumed a classification threshold
   that AUC optimization doesn't make — Codex review §7.1/13.4): finite,
   non-missing predictions within `[0, 1]`; sufficient prediction
   uniqueness (not a near-constant output); per-fold and overall OOF AUC;
   train/test prediction quantile comparison.
7. Record every v1–v3 variant's OOF score in `docs/6_baseline_modeling.md`.

## Phase 3 — Model Optimization & Ensemble (by 2026-08-18) — evidence-gated sequence

**Status 2026-08-04:** hand-designed search + promotion-gate **code** landed on
`cursor/phase3-tuning-16f2` (`docs/7_model_optimization_and_ensemble.md`).
Competition OOF numbers still pending a desktop re-run with real
`playground-series-s6e8` data (cloud agent lacked Mac-local Kaggle
credentials). Deliberately staged and gated — each step only proceeds if the
previous one's evidence justifies its cost, per
`docs/4_codex_claude_review_log.md` §13.4:

1. **Sanity baselines** — already covered in Phase 2 step 2 (constant
   predictor, logistic regression, HGB); referenced here as the floor
   everything else must beat.
2. **Strong models:** LightGBM and CatBoost (from Phase 2 step 3), tuned
   with a **small hand-designed parameter search first** (a handful of
   manually-chosen configurations, not a full sweep).
3. **Conditional challenger — XGBoost:** add only if it produces
   complementary OOF rankings or residual behavior versus LightGBM/CatBoost
   (i.e. it's wrong on different rows, not just a slightly different score)
   — not added by default to "have three models."
4. **Optuna — conditional, not default:** only if the hand-designed search
   in step 2 shows enough headroom (a real, evidenced gap between tried
   configurations) to justify the extra tuning time. If the hand-designed
   search already plateaus, skip it and say so in the ledger.
5. **Multi-seed averaging:** only if single-seed OOF variance (from Phase
   2 step 1's fold std) is non-trivial relative to the gap between
   candidates — not run by default as a fixed 3–5-seed step.
6. **Ensemble:** a convex OOF-weighted probability blend across model
   families, **only when paired evidence and prediction diversity justify
   it** (see promotion gate below) — not attempted just because multiple
   models exist. Stacking is out of scope unless the blend's paired
   evidence is unusually strong and time remains.
7. **Promotion gate — derived from this dataset's own uncertainty, not a
   borrowed number:** the original `+0.0002` figure was copied from
   `kaggle-s6e7`'s own empirically-derived gate for a different dataset and
   metric regime (balanced accuracy, not AUC) — reusing it here without
   deriving it from this dataset's OOF variance was a methodological gap
   (Codex review §7.2/§13.4). Instead:
   - Measure fold-to-fold OOF AUC std from Phase 2 step 1 first.
   - Use a paired bootstrap comparison between candidate and champion OOF
     predictions (same technique `kaggle-s6e7` used for its actual v23
     promotion decision — applied to this dataset's own numbers, not an
     imported threshold).
   - Check fold consistency (no single fold driving the whole gain) and
     inter-model prediction correlation/diversity when evaluating an
     ensemble candidate specifically.
8. Record every experiment (accepted and rejected) in a running ledger:
   `docs/10_leaderboard_improvement_insights.md`, accepted/rejected with
   exact numbers.

Time budget: treat `docs/4_codex_claude_review_log.md` §9's ~40-hour,
5-workstream estimate as an initial allocation, to be revisited once Phase 2
produces a measured baseline runtime (fold-fit time on ~690k rows locally
vs. on Kaggle) — not committed to precisely as written.

## Phase 4 — Submission Strategy (ongoing from first candidate, ~2026-08-08 onward)

Full detail in `docs/9_submission_quota_strategy.md` (to be written once the
first candidate is ready); the core rules, adapted from S6E7's discipline
(which used only 3 leaderboard submissions total):

- Submit only a reproducible, notebook-generated candidate with a clear
  hypothesis and OOF support — never a blind threshold/weight sweep.
- One submission per accepted hypothesis, not per parameter tweak.
- Log every submission immediately: notebook version, OOF score, public
  score, prediction-mix sanity check (Phase 2 step 6's checks), in
  `docs/8_submission_manifest.md`.
- Always submit via Kaggle's "Submit to Competition" from a pushed public
  notebook (`scripts/push_kaggle_kernel.sh baseline`), never a
  detached local CSV upload, so the leaderboard score is tied to
  reproducible, committed code (`docs/0_coding_standards.md`).
- Keep the current champion as a known-good fallback at every step.

## Phase 5 — Final Week (2026-08-25 to 2026-08-31)

1. Freeze feature engineering; spend remaining time on ensembling stability
   and final promotion-gate checks only.
2. Re-run the champion notebook end-to-end on Kaggle once more to confirm
   reproducibility.
3. Submit the final champion with enough buffer before 2026-08-31 23:59 UTC
   to recover from a failed Kaggle run (aim to have the final submission
   locked in by 2026-08-30).
4. Confirm dependency versions actually used in the trusted Kaggle run are
   recorded/pinned in `requirements.txt` — don't claim exact reproducibility
   before that's verified (Codex review §8).
5. Write the closing README update (`## Current Result` table, `## What
   Worked`, `## Final Modeling Decision`) — findings first, exact metrics,
   explicit stop-condition reasoning, and (per the portfolio-project
   priority in `docs/4_codex_claude_review_log.md` §1) a clear write-up of
   what was learned, not just the final score.

## Planned Docs (created as each phase produces results)

| Doc | Phase | Content |
| --- | --- | --- |
| `3_eda_insights.md` | 1 | Class balance, missingness, feature signal, drift — done, revised |
| `4_codex_claude_review_log.md` | — | Codex/Claude collaborative review, ongoing |
| `5_source_dataset_provenance.md` | 1 | Candidate source dataset investigation — done |
| `6_baseline_modeling.md` | 2 | v1→v3 baseline progression table |
| `7_model_optimization_and_ensemble.md` | 3 | Tuning + ensemble strategy and results |
| `8_submission_manifest.md` | 4 | Every leaderboard submission, score, decision |
| `9_submission_quota_strategy.md` | 4 | Submission discipline, rhythm, final-gate rules |
| `10_leaderboard_improvement_insights.md` | 3–5 | Full experiment ledger, accepted + rejected |

Reserve a new number only for a promoted, project-owned finding — not every
parameter tweak — per `docs/0_coding_standards.md`.
