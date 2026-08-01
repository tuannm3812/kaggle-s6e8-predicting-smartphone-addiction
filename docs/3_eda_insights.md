# EDA Insights

From `notebooks/01_eda.ipynb`, revision 2, executed end-to-end 2026-08-01.
Findings first, evidence after, per `docs/0_coding_standards.md`. This
revision replaces the original version after the Codex review in
`docs/4_codex_claude_review_log.md` §13 found methodological gaps in
several of the original conclusions — see §11 below for what changed and
why.

## 1. Schema Confirmed

`train.csv`: 691,369 rows × 14 columns. `test.csv`: 296,302 rows × 13
columns. 12 features (9 numeric, 3 categorical), `id`, target
`addicted_label`.

## 2. Target Confirmed

Positive rate `490,474 / 691,369 = 0.7094`; negative `200,895 / 691,369 =
0.2906`. Matches the value already used to size the plan.

## 3. Numeric Feature Signal: Effect Size and Univariate AUC

Raw class-mean differences (used in the original revision of this doc) are
not comparable across features with different units/scales and are
sensitive to skew — `app_opens_per_day`'s raw gap looked like the largest in
the dataset purely as an artifact of that. Two scale-free diagnostics
instead:

| Feature | Cohen's *d* | Univariate AUC | n (non-missing) |
| --- | ---: | ---: | ---: |
| `daily_screen_time_hours` | 1.701 | **0.890** | 595,515 |
| `weekend_screen_time` | 1.609 | **0.881** | 579,306 |
| `social_media_hours` | 1.385 | **0.858** | 557,374 |
| `work_study_hours` | 0.572 | 0.655 | 639,851 |
| `gaming_hours` | 0.462 | 0.622 | 564,548 |
| `app_opens_per_day` | 0.140 | 0.541 | 610,659 |
| `sleep_hours` | 0.094 | 0.527 | 646,889 |
| `notifications_per_day` | −0.026 | 0.492 | 623,785 |
| `age` | 0.009 | 0.502 | 662,440 |

Both diagnostics agree closely with each other, and with the Pearson
ranking in §6 — `daily_screen_time_hours`, `weekend_screen_time`, and
`social_media_hours` are clearly the three strongest single-feature
predictors (univariate AUC 0.86–0.89 alone), with `work_study_hours` and
`gaming_hours` a clear second tier. `app_opens_per_day`'s univariate AUC
(0.541) confirms it is genuinely weak once measured correctly — the raw
mean-difference table in the original revision of this doc was the
misleading one, not the correlation ranking that replaced it.

## 4. Missingness

### 4.1 Train/Test Missingness Rate Differences

Per-column missingness *rates* differ between train and test by up to 3.4
points (`social_media_hours`: 19.4% train vs. 16.0% test; `gaming_hours`:
18.3% vs. 20.1%; full table unchanged from the original revision). At this
sample size the binomial standard error on a ~19% rate is ≈0.05 points, so a
3.4-point gap is roughly 60× that — a deliberate generator difference, not
sampling noise. This is a difference in missingness *rate*, separate from
whether the underlying *values* differ (checked in §8) or whether train and
test are jointly distinguishable (checked in §9).

### 4.2 Is Missingness Informative? — Marginal Analysis Only

Target rate for missing-vs-present rows differs by at most `0.0042` across
all 12 columns (unchanged from the original revision). **This is evidence
against a strong *marginal* signal, not proof there is no *conditional*
value** — a marginal comparison cannot detect missingness that matters only
combined with other features. Per the Codex review, `_is_missing` indicator
flags stay a **planned low-cost OOF ablation for Phase 2**, not something
this table rules out.

### 4.3 Missingness Co-Occurrence

Unchanged from the original revision: two moderate clusters (r = 0.21–0.28)
— a screen-time/engagement block (`social_media_hours`, `gaming_hours`,
`weekend_screen_time`, `daily_screen_time_hours`) and a notification/app-
usage pair (`notifications_per_day`, `app_opens_per_day`). Consistent with a
respondent skipping a whole question block rather than independent
per-field missingness.

## 5. Categorical Features: Target Rate

Unchanged from the original revision:

| Feature | Level | Addicted rate | Count |
| --- | --- | ---: | ---: |
| `gender` | Male | **0.7232** | 223,662 |
| `gender` | Female | 0.7038 | 221,595 |
| `gender` | Other | 0.7010 | 217,078 |
| `stress_level` | High | 0.7114 | 220,873 |
| `stress_level` | Low | 0.7112 | 207,783 |
| `stress_level` | **Medium** | **0.7057** | 207,565 |
| `academic_work_impact` | No | 0.7110 | 316,579 |
| `academic_work_impact` | Yes | 0.7079 | 330,566 |

`stress_level` remains **non-monotonic** (High ≈ Low > Medium) — ordinal
encoding stays an explicit OOF experiment to validate, not a default
assumption, unlike `kaggle-s6e7`'s `stress_level`.

## 6. Feature Ranking: Pearson, Univariate AUC, and Mutual Information Disagree On Two Features

| Feature | Pearson \|r\| | Univariate AUC (§3) | Mutual info |
| --- | ---: | ---: | ---: |
| `daily_screen_time_hours` | 0.611 | 0.890 | 0.2230 |
| `weekend_screen_time` | 0.590 | 0.881 | 0.2040 |
| `social_media_hours` | 0.532 | 0.858 | 0.1576 |
| `notifications_per_day` | 0.012 | 0.492 | **0.0857** |
| `app_opens_per_day` | 0.063 | 0.541 | **0.0775** |
| `work_study_hours` | 0.251 | 0.655 | 0.0390 |
| `gaming_hours` | 0.205 | 0.622 | 0.0277 |
| `sleep_hours` | 0.043 | 0.527 | 0.0112 |
| `age` | 0.004 | 0.502 | 0.0035 |
| `gender` | n/a | n/a | 0.00023 |
| `stress_level` | n/a | n/a | 0.0000063 |
| `academic_work_impact` | n/a | n/a | 0.0000002 |

The top 3 numeric features agree across all three diagnostics — high
confidence these are genuinely the strongest predictors. **But
`notifications_per_day` and `app_opens_per_day` rank 4th and 5th by mutual
information despite being the two *weakest* features by Pearson correlation
and univariate AUC** (both near 0.5 AUC, i.e. almost uninformative on their
own). Mutual information captures nonlinear/non-monotonic dependence that
the other two diagnostics cannot — this is a genuine, not spurious,
disagreement worth testing directly rather than resolving by picking one
"authoritative" ranking (per `docs/4_codex_claude_review_log.md` §13.2.4).

Mutual information is computed on a deterministic stratified 150,000-row
sample. Per `docs/4_codex_claude_review_log.md` §15.3: `age`,
`notifications_per_day`, and `app_opens_per_day` are integer-valued (stored
as `float64` only due to missing values — confirmed `(values ==
values.round()).all()` on non-missing entries) with far fewer unique values
(18 / 231 / 166) than a genuinely continuous feature would have over 691k
rows, which biases `mutual_info_classif`'s continuous k-nearest-neighbor
estimator. These three are now marked discrete (integer-safe imputation:
rounded median), alongside the 3 categorical features, rather than treated
as continuous as in the prior revision. **The ranking and the
`notifications_per_day`/`app_opens_per_day` disagreement both persist under
the corrected discrete/continuous split** (values shifted by ≤0.002 each,
rank order unchanged) — the original finding was not an artifact of the
estimator misconfiguration. Treat these values as exploratory, not precise,
regardless.

Among categoricals, `gender`'s mutual information (0.00023) is over 30×
`stress_level`'s (0.0000063), consistent with §5's target-rate table
showing `gender` has the largest spread.

## 7. Duplicate Rows — Corrected Methodology

The original revision's duplicate count used `pd.concat([train, test]).duplicated()`,
which conflates true cross-split matches with test-internal duplicates (a
row matching an *earlier* row anywhere in the concatenated frame, whether
that earlier row is in train or test). Recomputed with three separate,
correctly-isolated numbers:

- **Train-internal duplicate rows** (excl. `id`/target): **0**
- **Test-internal duplicate rows** (excl. `id`): **0**
- **Distinct feature-rows appearing in both train and test** (explicit inner
  join on the 12 shared feature columns, robust to multiplicity): **2**

All three are negligible relative to dataset size, consistent with Kaggle's
stated intent for newer Playground entries to have fewer generator
artifacts. The cross-split figure (2) is unchanged from the original
revision's number, but is now actually isolated to genuine cross-split
matches rather than possibly including test-internal duplicates (which are
independently confirmed to be zero anyway, so in this specific case the
correction doesn't change the number — only the confidence behind it).

## 8. Train/Test Distribution Checks

### 8.1 Numeric Features (Kolmogorov-Smirnov)

Unchanged: all 9 numeric features have `ks_stat` in `0.0009`–`0.0027` with
`p_value > 0.14` (most `> 0.4`) — no evidence of marginal distribution shift
on the observed (non-missing) values.

### 8.2 Categorical Features (chi-square) — Statistically Significant, Practically Small

| Feature | χ² | p-value | dof |
| --- | ---: | ---: | ---: |
| `gender` | 176.7 | 4.6×10⁻³⁸ | 3 |
| `stress_level` | 545.1 | 8.0×10⁻¹¹⁸ | 3 |
| `academic_work_impact` | 1646.8 | ≈0 | 2 |

All three are "significant" at any conventional threshold — expected at
n≈987k combined rows, where chi-square has enough power to detect even
trivial differences. The actual proportion gaps are small:

- `gender`: every observed-category gap ≤0.23pp; the missing-value bucket
  differs by 0.60pp (train 4.20% vs. test 4.80%).
- `stress_level`: observed-category gaps ≤0.58pp; missing-value bucket
  differs by 1.35pp (train 7.98% vs. test 6.62%).
- `academic_work_impact`: observed-category gaps ~1.0–1.3pp; missing-value
  bucket differs by 2.28pp (train 6.40% vs. test 8.68% — matches §4.1's
  missingness-rate table exactly, as it's the same underlying number).

**Conclusion:** the categorical chi-square "drift" is mostly the already-
known missingness-*rate* difference (§4.1) re-appearing as a proportion
gap, plus small (<1.3pp) differences in the observed-category splits — not
a new, separate distributional problem. Statistically significant at this
sample size is not the same as practically large.

## 9. Adversarial Validation

**Revised per `docs/4_codex_claude_review_log.md` §15.2**, which caught a
real methodological flaw in the original version of this section: a
`HistGradientBoostingClassifier` handles missing values natively, so a raw
column with NaN already encodes *both* the observed value *and* the
missing/not-missing pattern in one column. The original approach — permute
each raw column and read off permutation importance from one combined
model — cannot separate those two sources; a near-zero importance for the
explicit `_is_missing` indicator only shows the indicator is *redundant
once the NaN-aware raw column is present*, not that the raw column's
importance is really about values rather than missingness. The original
conclusion ("essentially all of the signal comes from the raw feature
values... not an artifact of the missingness-rate differences") did not
follow from that experiment and is retracted.

**Corrected design:** three separate 3-fold `HistGradientBoostingClassifier`
models trained to distinguish train rows from test rows, each on a
different feature set:

| Experiment | Features | OOF AUC |
| --- | --- | ---: |
| A — raw only | 12 features, native NaN handling, no indicators | 0.5651 |
| B — indicators only | 12 `_is_missing` columns, no raw values at all | **0.5654** |
| C — raw + indicators | All 24 columns (the original combined model) | 0.5651 |

**Finding:** all three are statistically indistinguishable from each other
(within a few 0.0001 of 0.565). **Missingness indicators *alone*, with zero
access to any raw feature value, achieve essentially the same
train/test-separating power as the raw features alone, or as both
combined.** This directly contradicts the previous revision's conclusion —
missingness pattern is not a negligible contributor; it is, on this
evidence, independently sufficient to explain nearly all of the detected
signal, exactly as much as the raw values are.

**What this does and doesn't establish:** A, B, and C landing on
essentially the same AUC means this experiment **cannot cleanly attribute**
the ~0.565 signal to "value drift" versus "missingness-pattern drift" as
separate causes — they carry highly overlapping/redundant information about
which rows are train vs. test. A plausible explanation is that both are
manifestations of the same underlying (unobserved) generation-process
difference between train and test — e.g. if some batch/segment factor
influenced both which values a row got and whether certain fields were
recorded, both channels would independently "see" the same rows differently.
This is speculation about mechanism, not established by this diagnostic —
what *is* established is the numeric result: neither value differences nor
missingness pattern differences alone or combined produce more than a mild
(~0.565) signal.

**Which raw columns matter within the combined model (Experiment C)** — for
knowing where to look, not for the values-vs-missingness question (that
question is answered by the A/B/C table above, not by this table):
permutation importance on Experiment C, held-out 20% split, 50,000-row
subsample, 5 repeats, scored on AUC drop:

| Feature | Importance (AUC drop) |
| --- | ---: |
| `app_opens_per_day` | 0.01566 |
| `social_media_hours` | 0.01123 |
| `daily_screen_time_hours` | 0.00740 |
| `notifications_per_day` | 0.00729 |
| `gaming_hours` | 0.00569 |
| `academic_work_impact` | 0.00547 |
| `work_study_hours` | 0.00520 |
| `age` | 0.00477 |
| `stress_level` | 0.00308 |
| `weekend_screen_time` | 0.00244 |

(Top 10 of 24 columns shown; numbers copied directly from this notebook's
own saved cell output, per §15.4 below — not from a separately-run script,
since `HistGradientBoostingClassifier` was observed to produce slightly
different importance values across separate process invocations even with
the same `random_state` set.)

**Interpretation, held to the review's strict framing:** an AUC of ~0.565 is
mild — well below the ~0.7–0.8+ range that would signal strong, exploitable
train/test separability. What drives it (values, missingness pattern, or
both reflecting a shared underlying cause) is **not resolved** by this
diagnostic, and this doc does not claim otherwise. This does **not** prove
OOF CV will diverge from the public leaderboard, and does **not** by itself
justify a drift-correction step; it's a data point to keep in mind if a
promoted Phase 2/3 candidate's local OOF score and public leaderboard score
disagree materially.

## 10. Next Moves (Phase 2 Priority Order)

1. Prioritize `daily_screen_time_hours`, `weekend_screen_time`,
   `social_media_hours` (agreement across all three diagnostics, §3/§6) for
   the baseline feature set and ratio/composition engineering.
2. Specifically test `notifications_per_day` and `app_opens_per_day` in a
   nonlinear model (not just via correlation screening) given the
   Pearson/AUC vs. mutual-information disagreement in §6 — don't drop them
   on the strength of their weak linear/rank-based scores alone.
3. Keep `gender` and `academic_work_impact` as native categorical;
   `stress_level` as unordered native-categorical by default, with ordinal
   encoding as an explicit OOF experiment (§5).
4. Run `_is_missing` indicator flags as a genuine OOF ablation in Phase 2 —
   §4.2's marginal analysis doesn't rule them out, and §9's revised
   adversarial finding (missingness pattern alone reaches the same
   train/test-separating power as raw values alone) is if anything a point
   *for* taking missingness seriously as a signal source, not against it —
   the actual answer still has to come from an OOF ablation on the target,
   not from either diagnostic. **Done in Phase 2:**
   `docs/6_baseline_modeling.md` §4 ran this exact ablation on the real
   target — `_is_missing` flags added `0.000004` OOF AUC on top of native
   NaN handling (noise), a clean negative result on the question this EDA
   pass could only raise, not resolve.
5. Treat the adversarial-validation result (§9, AUC ~0.565, value-vs-
   missingness attribution genuinely inconclusive) as background context
   for interpreting any future local-CV-vs-leaderboard gap — not as grounds
   for drift correction on its own.

## 11. What Changed From The Original Revision, And Why

Following the Codex review (`docs/4_codex_claude_review_log.md` §13),
retracted or narrowed:

- **"Trust the correlation ranking" (old §3) → replaced** with three
  agreeing diagnostics (§3/§6) instead of asserting one ranking as
  authoritative; also surfaced a genuine disagreement (notifications/app-
  opens) the single-ranking version couldn't have found.
- **"No material train/test drift... no adversarial validation needed" (old
  §8) → retracted.** That conclusion was based only on numeric KS tests. §8
  now includes categorical drift (statistically real, practically small)
  and §9 adds the adversarial-validation check the original conclusion
  should have had before making a "no drift" claim at all.
- **Duplicate count (old §8, "0 within train / 2 cross") → recomputed**
  with an explicit join instead of a concat-then-`duplicated()` call that
  could have conflated test-internal duplicates with true cross-split
  matches (§7). The final number is unchanged, but it's now backed by a
  methodology that couldn't have gotten it wrong by construction.
- **Missingness "not materially informative... don't prioritize" (old §4) →
  narrowed** to "no strong marginal signal found; still a planned OOF
  ablation" (§4.2) — the marginal evidence didn't support the stronger
  claim.

## 12. Revision 2: What Changed After Codex's Review Of The Completion Report

Following `docs/4_codex_claude_review_log.md` §15, a second, more
substantial round of corrections:

- **§9's causal claim ("the signal comes from raw values, not missingness")
  → retracted and replaced with a genuinely different finding.** The
  original permutation-importance experiment could not separate value
  signal from missingness-pattern signal (§15.2: `HistGradientBoostingClassifier`
  reads both from the same NaN-containing raw column). A corrected 3-way
  ablation (raw only / indicators only / raw+indicators) found all three
  land at ~0.565 — missingness indicators *alone* match the full model,
  meaning the attribution question is **genuinely unresolved**, not
  resolved in favor of "values." This is not a minor wording fix; it
  reverses the previous revision's headline conclusion for this section.
- **§6's mutual-information ranking → rerun with corrected discrete/
  continuous handling** (§15.3): `age`, `notifications_per_day`, and
  `app_opens_per_day` are integer-valued and were incorrectly treated as
  continuous, biasing the k-NN estimator. Rerunning with them marked
  discrete changed the values slightly but not the ranking or the
  `notifications_per_day`/`app_opens_per_day` disagreement — the original
  finding held up under the corrected methodology.
- **Permutation-importance numbers → corrected to match the actual saved
  notebook output** (§15.4). The previous revision of this doc had numbers
  from a separately-run standalone script, not the notebook's own executed
  cells — `HistGradientBoostingClassifier` was observed to produce slightly
  different importance values across separate process runs even with the
  same `random_state`, so a supplementary script's output is not
  interchangeable with the notebook's own trusted run. Every number in this
  revision was copied from `notebooks/01_eda.ipynb`'s actual final saved
  cell output, not retyped or reused from any other source.
