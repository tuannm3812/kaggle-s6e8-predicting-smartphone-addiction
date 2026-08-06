# Submission Manifest

Only completed leaderboard results are recorded here. Artifact identity and
validation evidence remain in `docs/7_kaggle_run_manifest.md`.

| UTC Date | Public Notebook | Kaggle Version | Candidate | OOF AUC | Public AUC | Decision |
| --- | --- | ---: | --- | ---: | ---: | --- |
| 2026-08-06 01:53:26.370 | [Baseline modeling](https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling) | 2 | `e01-lightgbm-v1` — `lightgbm_tuned` | 0.96166 | **0.96286** | Final champion submit after Task 7 user authorization of the exact Kaggle v2 artifact. |
| 2026-08-02 05:33:21.660 | [Baseline modeling](https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling) | 1 | `baseline-v1` — HGB (`hist_gradient_boosting`) | 0.95733 | 0.95865 | Establish as the first leaderboard baseline; proceed to comparable hand-designed tuning. |

The HGB baseline public score was `0.00132` above its OOF. The champion
public score is `0.00120` above its OOF. Two points are still not enough to
estimate leaderboard variance or to select models by public score alone.

Submitted artifact SHA-256 values:

- HGB `baseline-v1`: `f37f02ec21176f8e7b02bdc7122545edc4deb2b197ac37c970beaea62eb5e1ca`
- `lightgbm_tuned` / `e01-lightgbm-v1`: `1986eedcf8f4adb7017494d5559e96fb50195c8bf32636a26927b3c2a6f859b3`

## Champion Artifact Submitted (Task 7)

User authorized submit of the exact public-kernel version **2** artifact on
2026-08-06. Public ROC AUC **0.96286** (OOF 0.96166; public − OOF =
`+0.00120`). Submitted file SHA-256
`1986eedcf8f4adb7017494d5559e96fb50195c8bf32636a26927b3c2a6f859b3` — same
bytes validated in `docs/7_kaggle_run_manifest.md` §"Champion Submission-Mode
Run (Task 7)".
