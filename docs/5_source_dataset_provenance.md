# Source Dataset Provenance

Investigates the candidate source dataset named in `docs/archive/4_codex_claude_review_log.md`
§13.3: https://www.kaggle.com/datasets/jayjoshi37/smartphone-usage-and-addiction-prediction
("Smartphone Usage & Addiction Prediction", 7,500 rows, CC0-1.0, published
2026-02-19). Confirmed 2026-08-01 via `kaggle datasets metadata` /
`kaggle datasets download` and direct comparison against `data/train.csv`.

## Verdict

**Very likely the source** named in the official Dataset Description
("inspired by the Smartphone Addiction Prediction Dataset") — the evidence
below is strong and specific, but there is no explicit Kaggle-staff citation
confirming it, so this stays a **candidate source**, not a confirmed one,
per the review log's instruction.

## Evidence

### 1. Column-for-column schema match

All 12 competition feature names appear in the source dataset, spelled
identically, including distinctive names unlikely to coincide by chance
across independently-authored datasets: `academic_work_impact`,
`weekend_screen_time`, `daily_screen_time_hours`. The source has three
additional columns not present in the competition data: `transaction_id`,
`user_id` (row identifiers, correctly excluded from the competition's
feature set), and `addiction_level` (see §3 below).

The target column is spelled identically — `addicted_label` — with the same
`{0, 1}` encoding in both.

### 2. Matching value domains

| Check | Source | Competition train | Match? |
| --- | --- | --- | --- |
| `gender` levels | `{Female, Male, Other}` | `{Female, Male, Other}` | Exact |
| `stress_level` levels | `{High, Low, Medium}` | `{High, Low, Medium}` | Exact |
| `academic_work_impact` levels | `{No, Yes}` | `{No, Yes}` | Exact |
| `age` range | `[18, 35]` | `[18, 35]` | Exact |
| `sleep_hours` range | `[4.5, 9.0]` | `[4.5, 9.0]` | Exact |
| `notifications_per_day` range | `[20, 250]` | `[20, 250]` | Exact |
| `app_opens_per_day` range | `[15, 180]` | `[15, 180]` | Exact |
| `gaming_hours` range | `[0.0, 4.0]` | `[0.0, 4.0]` | Exact |
| `daily_screen_time_hours` range | `[3.0, 12.0]` | `[0.5, 15.0]` | Train is a wider superset |
| `social_media_hours` range | `[0.5, 6.0]` | `[0.0, 8.0]` | Train is a wider superset |
| `work_study_hours` range | `[0.5, 6.0]` | `[0.0, 6.0]` | Train is a wider superset |
| `weekend_screen_time` range | `[3.58, 14.88]` | `[0.51, 17.56]` | Train is a wider superset |
| Target positive rate | `0.7077` (5,308 / 7,500) | `0.7094` (490,474 / 691,369) | Within sampling noise for a 7.5k-row sample |

Five of nine numeric features have **exactly identical** min/max bounds
across a 7,500-row sample and a 691,369-row competition set — not the kind
of coincidence expected from an unrelated dataset. The four features where
the competition's range is a strict superset of the source's range are
consistent with a generator that widened those specific distributions (a
recognized synthetic-data technique, and consistent with Kaggle's own
"far fewer artifacts" framing in `docs/1_instructions.md`), not with an
unrelated data source.

### 3. Target-generation rule recovered from the source's extra column

The source's `addiction_level` column (`{NaN, Mild, Moderate, Severe}`, not
present in the competition data) is a **perfectly deterministic** function of
`addicted_label` in the source:

| `addiction_level` | count | `addicted_label` (min–max) |
| --- | ---: | --- |
| `Moderate` | 2,874 | `1`–`1` |
| `Severe` | 2,434 | `1`–`1` |
| `Mild` | 1,373 | `0`–`0` |
| `NaN` | 819 | `0`–`0` |

`addicted_label = 1` iff `addiction_level ∈ {Moderate, Severe}`; `= 0` iff
`addiction_level ∈ {Mild, NaN}` — zero exceptions across all 7,500 rows.

**Narrowed per `docs/archive/4_codex_claude_review_log.md` §15.5** (an earlier
version of this section over-claimed): this establishes only that
`addicted_label` is a **deterministic binary collapse of the recorded
`addiction_level` field** in the candidate source. It does **not** establish
that the decision boundary in *behavior-feature space* (the 12 predictors
actually available) is clean, threshold-like, or noise-free — `addiction_level`
and `addicted_label` may simply be two alternate representations of the same
underlying label, generated together, with no guarantee that the 12 recorded
predictors alone determine either one reliably. `addiction_level` is not in
the competition data and is not a usable feature. **Predictive headroom must
be measured through actual OOF results (`docs/6_baseline_modeling.md`
onward), not inferred from this label mapping.**

### 4. No missing values in the source; no exact row overlap with the competition

The source has **zero missing values** in any of the 12 shared feature
columns — the competition's missingness (present in every one of the 12
features, 4%–19% each, per `docs/1_instructions.md`) is not inherited from
the source; it was injected by the competition's generator on top of a
source that was itself complete. This says nothing about *why* the
generator injected missingness the way it did, or whether that missingness
carries target signal — `docs/3_eda_insights.md` §9's adversarial-validation
ablation found the value-vs-missingness attribution question genuinely
unresolved (not settled toward MCAR or toward informative missingness), and
`docs/6_baseline_modeling.md` §4's direct OOF ablation is the actual answer
on whether `_is_missing` flags help (they don't, on target AUC).

Checked for literal row leakage: joining on the 12 shared feature columns,
**0 of the source's 7,500 rows exactly match any row in `train.csv` or
`test.csv`**. The competition data is a genuine re-synthesis, not a resample
or split of this source file.

## Implications For Modeling (Phase 2/3)

Narrowed per `docs/archive/4_codex_claude_review_log.md` §15.5 — only what the
evidence in §3/§4 actually supports:

- No new usable feature: `addiction_level` isn't in the competition data and
  can't be safely reconstructed, so this doesn't change the feature set.
- `addicted_label` is a deterministic collapse of `addiction_level` *in the
  source*; this is a fact about the source's label construction, not a
  measurement of how predictable `addicted_label` is from the 12 competition
  features. Any claim about achievable AUC ceiling must come from actual OOF
  results, not from this label-mapping fact.
- Says nothing about missingness informativeness one way or the other — see
  `docs/3_eda_insights.md` §9 (adversarial validation, inconclusive
  attribution) and `docs/6_baseline_modeling.md` §4 (direct OOF ablation,
  the actual answer) instead.

## Verification

Reproducible comparison logic (metadata check, schema/value-domain
comparison, target-generation cross-tab, row-hash join against
`train.csv`/`test.csv`) lives in `scripts/verify_source_provenance.py`, not
in an unpreserved local session — run it against a fresh
`kaggle datasets download` if re-verification is needed. Per
`docs/archive/4_codex_claude_review_log.md` §15.6/15.7.3: the downloaded source CSV
itself is **not** committed and should stay outside the repository
(`/tmp/candidate_src_data/` or similar) — only the comparison logic and its
findings are preserved.
