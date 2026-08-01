# Competition Instructions

Kaggle operational troubleshooting (access errors, CLI PATH issues, why the
page can't be fetched by URL) lives in `docs/0_coding_standards.md` instead —
this doc stays limited to what the competition itself states.

## Competition

- Name: Predicting Smartphone Addiction
- Series: Kaggle Playground Series S6E8
- URL: https://www.kaggle.com/competitions/playground-series-s6e8
- Citation: Yao Yan, Walter Reade, Elizabeth Park. *Predicting Smartphone
  Addiction.* https://kaggle.com/competitions/playground-series-s6e8, 2026.
  Kaggle.

## Overview

> Welcome to the 2026 Kaggle Playground Series! We plan to continue in the
> spirit of previous playgrounds, providing interesting and approachable
> datasets for our community to practice their machine learning skills, and
> anticipate a competition each month.
>
> Your Goal: Predicting smartphone addiction.

## Evaluation

> Submissions are evaluated on **area under the ROC curve** between the
> predicted probability and the observed target.

**Confirmed 2026-08-01 (pasted by user)** — this matches the working
assumption the plan was already built around (inferred from
`sample_submission.csv`'s constant-probability baseline). Every
OOF/leaderboard decision in `docs/2_implementation_plan.md` was already
AUC-optimizing; no correction needed.

### Submission Format

> For each `id` in the test set, you must predict a probability for the
> `addicted_label` variable. The file should contain a header and have the
> following format:

```
id,addicted_label
691369,0.2
691370,0.3
691371,0.1
```

## Timeline

- Start Date: **August 1, 2026** (competition started the same day this
  project's scaffold was built — data files were staged 2026-06-25, ahead
  of the official start).
- Entry Deadline: same as Final Submission Deadline.
- Team Merger Deadline: same as Final Submission Deadline.
- **Final Submission Deadline: August 31, 2026**, 11:59 PM UTC — matches
  the `2026-08-31 23:59:00 UTC` already confirmed via `kaggle competitions
  list -s playground-series-s6e8`.
- All deadlines are 11:59 PM UTC on the stated day unless otherwise noted;
  organizers reserve the right to update the timeline.
- Daily submission quota: not stated on the competition page. Historically
  not a binding constraint for this line of projects (see `kaggle-s6e7`'s
  `6_submission_quota_strategy.md` — only 3 leaderboard submissions were
  ever used across that whole project); default to the same disciplined,
  hypothesis-gated submission rhythm rather than checking the quota.

## About The Tabular Playground Series

> The goal of the Tabular Playground Series is to provide the Kaggle
> community with a variety of fairly light-weight challenges that can be
> used to learn and sharpen skills in different aspects of machine learning
> and data science... The challenges will generally use fairly light-weight
> datasets that are synthetically generated from real-world data.

### Synthetically-Generated Datasets

> Using synthetic data for Playground competitions allows us to strike a
> balance between having real-world data (with named features) and
> ensuring test labels are not publicly available... the goal is to produce
> datasets that have far fewer artifacts.

This is consistent with `docs/3_eda_insights.md` §8: zero exact duplicates
within train, only 2 negligible cross train/test duplicates, and no
detectable train/test drift (KS test) on any numeric feature.

## Prizes

> 1st/2nd/3rd Place — choice of Kaggle merchandise, awarded once per person
> across the series.

## Dataset Description

> The dataset for this competition (both train and test) was inspired by
> the **Smartphone Addiction Prediction Dataset**.

Confirmed by downloading `data/` via `kaggle competitions download -c
playground-series-s6e8` and inspecting locally (2026-08-01):

### Files

- `train.csv` — 44.9 MB, 691,369 rows × 14 columns (12 features + `id` +
  target).
- `test.csv` — 18.7 MB, 296,302 rows × 13 columns (12 features + `id`, no
  target).
- `sample_submission.csv` — 7.7 MB, 296,302 rows × 2 columns (`id`,
  `addicted_label`).

### Target

- Column: `addicted_label`
- Type: binary, `{0, 1}`
- Class balance (train): `1` (addicted) = 490,474 (70.94%); `0` (not
  addicted) = 200,895 (29.06%) — moderately imbalanced toward the positive
  class.

### Features

| Column | Type | Train missing | Test missing | Notes |
| --- | --- | ---: | ---: | --- |
| `age` | numeric (float) | 28,929 (4.2%) | 17,138 (5.8%) | range 18–35 |
| `daily_screen_time_hours` | numeric (float) | 95,854 (13.9%) | 32,788 (11.1%) | |
| `social_media_hours` | numeric (float) | 133,995 (19.4%) | 47,397 (16.0%) | highest missingness of the numeric block |
| `gaming_hours` | numeric (float) | 126,821 (18.3%) | 59,420 (20.1%) | |
| `work_study_hours` | numeric (float) | 51,518 (7.5%) | 27,777 (9.4%) | |
| `sleep_hours` | numeric (float) | 44,480 (6.4%) | 22,455 (7.6%) | |
| `notifications_per_day` | numeric (float) | 67,584 (9.8%) | 34,221 (11.6%) | |
| `app_opens_per_day` | numeric (float) | 80,710 (11.7%) | 25,705 (8.7%) | |
| `weekend_screen_time` | numeric (float) | 112,063 (16.2%) | 50,697 (17.1%) | range 0.51–17.56 |
| `gender` | categorical | 29,034 (4.2%) | 14,212 (4.8%) | `{Male, Female, Other}` |
| `stress_level` | categorical | 55,148 (8.0%) | 19,626 (6.6%) | `{Low, Medium, High}` |
| `academic_work_impact` | categorical | 44,224 (6.4%) | 25,721 (8.7%) | `{No, Yes}` |

Every feature column has missingness in both train and test, at meaningfully
different rates per column (4%–19%) — this is a first-class modeling
consideration, not an edge case. Duplicate-row counts (train-internal,
test-internal, cross-split) are in `docs/3_eda_insights.md` — see that doc
for the corrected, split-out methodology; the submission format is already
covered under Evaluation above.

## Items Confirmed From Local Data

| Item | Status |
| --- | --- |
| Target column | `addicted_label`, binary `{0, 1}` |
| Submission column name | `addicted_label` (probability-shaped per sample submission) |
| Train file | `train.csv`, 44.9 MB, 691,369 rows |
| Test file | `test.csv`, 18.7 MB, 296,302 rows |
| Sample submission | `sample_submission.csv`, 7.7 MB |
| Target distribution | `1`: 490,474 (70.94%); `0`: 200,895 (29.06%) |
| Competition deadline | 2026-08-31 23:59:00 UTC (official, confirmed both via Kaggle CLI and pasted Overview text) |
| Evaluation metric | **ROC AUC** (official, confirmed 2026-08-01) |

## Expected Input Files

- `train.csv`
- `test.csv`
- `sample_submission.csv`
