# Submission Manifest

Only completed leaderboard results are recorded here. Artifact identity and
validation evidence remain in `docs/7_kaggle_run_manifest.md`.

| UTC Date | Public Notebook | Kaggle Version | Candidate | OOF AUC | Public AUC | Decision |
| --- | --- | ---: | --- | ---: | ---: | --- |
| 2026-08-02 05:33:21.660 | [Baseline modeling](https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling) | 1 | `baseline-v1` — HGB (`hist_gradient_boosting`) | 0.95733 | 0.95865 | Establish as the first leaderboard baseline; proceed to comparable hand-designed tuning. |

The public score is `0.00132` above the local OOF score. This single result is
consistent with local CV being directionally useful, but it is not enough to
estimate leaderboard variance or justify selecting future experiments by
public score alone.

Submitted artifact SHA-256:
`f37f02ec21176f8e7b02bdc7122545edc4deb2b197ac37c970beaea62eb5e1ca`.

## Pending Champion Artifact (Task 7 — not yet submitted)

Public kernel version **2** produced a validated `lightgbm_tuned` /
`e01-lightgbm-v1` artifact (see `docs/7_kaggle_run_manifest.md` §"Champion
Submission-Mode Run"). It has **not** been submitted to the competition
leaderboard. No public AUC is recorded until the user authorizes that
exact file (SHA-256
`1986eedcf8f4adb7017494d5559e96fb50195c8bf32636a26927b3c2a6f859b3`).
