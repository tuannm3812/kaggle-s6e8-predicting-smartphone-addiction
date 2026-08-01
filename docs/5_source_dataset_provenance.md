# Source Dataset Provenance

Investigates the candidate source dataset named in `docs/4_codex_claude_review_log.md`
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
This means the binary target is a **collapsed 4-level severity scale**, not
an independently-labeled binary outcome — the true decision boundary in
behavior-feature space is likely a genuine, not noisy, threshold. This is
context for modeling headroom (a strong, well-separated boundary may be
achievable), not a usable feature on its own, since `addiction_level` itself
is not in the competition data and cannot be reconstructed with certainty.

### 4. No missing values in the source; no exact row overlap with the competition

The source has **zero missing values** in any of the 12 shared feature
columns — the competition's missingness (present in every one of the 12
features, 4%–19% each, per `docs/1_instructions.md`) is not inherited from
the source. It was injected by the competition's generator, on top of a
source that was itself complete. This is a plausible causal mechanism for
`docs/3_eda_insights.md`'s finding that missingness carries ~no target
signal here (§4 of that doc, revised — see the OOF ablation still planned
per the review log's Q3/13.2.6): injected missingness of this kind is
commonly close to MCAR by construction, which would produce exactly the
weak marginal signal observed, though this is a plausible mechanism, not
proof — the OOF ablation is still the direct test.

Checked for literal row leakage: joining on the 12 shared feature columns,
**0 of the source's 7,500 rows exactly match any row in `train.csv` or
`test.csv`**. The competition data is a genuine re-synthesis, not a resample
or split of this source file.

## Implications For Modeling (Phase 2/3)

- No new usable feature: `addiction_level` isn't in the competition data and
  can't be safely reconstructed, so this doesn't change the feature set.
- Useful context for calibrating expectations: since the source's label is a
  clean threshold on an underlying severity scale, a well-tuned model may
  achieve a high AUC ceiling if the competition generator preserved that
  structure (plausible, not guaranteed — the generator both widened some
  feature ranges and injected missingness, either of which could blur the
  boundary).
- Supports (does not prove) the "missingness ~MCAR" reading in
  `docs/3_eda_insights.md` — treat as one more piece of evidence alongside
  the OOF ablation, not a replacement for it.

## Verification Commands

```bash
kaggle datasets metadata -p /tmp/candidate_src_meta jayjoshi37/smartphone-usage-and-addiction-prediction
kaggle datasets download -d jayjoshi37/smartphone-usage-and-addiction-prediction -p /tmp/candidate_src_data
```

Followed by a local pandas comparison of shape, dtypes, column names, value
domains, target prevalence, missingness, the `addiction_level` ↔
`addicted_label` cross-tab, and a row-hash join against `train.csv`/
`test.csv` on the 12 shared feature columns. Not committed: the downloaded
source CSV (`/tmp/candidate_src_data/`, outside the repo, not copied into
`data/`).
