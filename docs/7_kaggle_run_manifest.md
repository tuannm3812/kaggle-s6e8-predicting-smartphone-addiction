# Kaggle Run Manifest

Evidence recorded from the actual successful public Kaggle run only — no
provisional values.

| Notebook | Public URL | Kaggle Version | Status | Runtime | Local Comparison | UTC Execution Date |
| --- | --- | --- | --- | --- | --- | --- |
| `01_eda.ipynb` | https://www.kaggle.com/code/tuannm3812/smartphone-addiction-eda | 7 | `complete` | ~166s (11.0s–176.6s per kernel log timestamps) | All retrievable printed outputs were compared. Computed findings match except for the documented 0.0001 A/C differences; runtime package versions differ as documented below. | 2026-08-01 14:01:19.273 UTC (`lastRunTime`, `kaggle kernels list -m`) |
| `02_baseline_modeling.ipynb` (`RUN_MODE = "submission"`, HGB `baseline-v1`) | https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling | 1 | `complete` | ~31s total (data load 18.9s; fit + predict + write 12.5s, per kernel log timestamps) | Downloaded artifact validated with `scripts/verify_submission.py`; see §"Baseline Submission-Mode Run" below. | 2026-08-02 04:10:56.897 UTC (`lastRunTime`, `kaggle kernels list -m`) |
| `02_baseline_modeling.ipynb` (`RUN_MODE = "submission"`, `lightgbm_tuned` / `e01-lightgbm-v1`) | https://www.kaggle.com/code/tuannm3812/smartphone-addiction-baseline-modeling | 2 | `complete` | ~44s to write (data load ~20s; fit+predict+write ~23s, per kernel log timestamps) | Downloaded artifact validated with `scripts/verify_submission.py`; see §"Champion Submission-Mode Run (Task 7)" below. | 2026-08-05 14:06:21.933 UTC (`lastRunTime`, `kaggle kernels list -m`) |

## Version History

Seven versions were pushed while resolving a real path-detection bug,
closing a verification gap, rewriting the notebook's prose for a public
audience, improving structure/readability, and correcting an evidence
regression that readability pass introduced. Each is recorded below, not
silently overwritten:

| Version | Status | Outcome |
| --- | --- | --- |
| 1 | `error` | `FileNotFoundError: [Errno 2] No such file or directory: '../data/train.csv'`. Root cause: the notebook's Kaggle-path check used `/kaggle/input/playground-series-s6e8`, which does not exist on Kaggle's actual mount; the real competition input path is `/kaggle/input/competitions/playground-series-s6e8` (confirmed against the working pattern already used in the sibling `kaggle-s6e6`/`kaggle-s6e7` repos). The notebook silently fell through to the local-only `../data` fallback, which doesn't exist inside the Kaggle container. |
| 2 | `complete` | Fix applied (corrected the path check to `/kaggle/input/competitions/playground-series-s6e8`). Ran successfully, but the runtime-versions cell's output (a bare dict expression, not `print()`) wasn't retrievable via `kaggle kernels output` — that command only returned the execution log for this kernel, not `__notebook__.ipynb`/`__results__.html`, and bare-expression `execute_result` outputs don't appear in the stdout/stderr log stream. |
| 3 | `complete` | Added `print(runtime_versions)` so the package-version evidence lands in the log. Several load-bearing numeric findings (feature-signal ranking, mutual information, drift statistics) were still only bare-expression DataFrames, unverifiable against Kaggle the same way. |
| 4 | `complete` | Added a single `print()`ed JSON verification summary (former Section 11 of the notebook) covering numeric signal ranking, mutual information, numeric and categorical drift statistics, adversarial-validation AUCs, and duplicate counts — closing the verification gap for everything except plots. Some notebook markdown was not yet self-contained for a public reader. |
| 5 | `complete` | Rewrote every markdown cell to be self-contained and reader-facing — methodology and cautions preserved, internal references removed. No computed cell changed; re-verified identical results (except the already-documented 0.0001 A/C difference) and identical contiguous execution counts (1–22) after the rewrite. |
| 6 | `complete` | Removed the JSON verification-summary section for readability — it duplicated numbers already shown in the tables earlier in the notebook, but (this was under-weighted at the time) it was also the only channel making the numeric-signal, mutual-information, and drift DataFrame findings independently verifiable against Kaggle, since `kaggle kernels output` cannot retrieve bare-`execute_result` values. Removing it reopened that verification gap while the manifest's comparison claims were not narrowed to match — an evidence regression, caught on review. Moved the package-version cell to a new "Environment" section at the top, reformatted as a bullet list; kept in version 7. |
| 7 | `complete` | Restored a compact, clearly-labeled "Reproducibility Snapshot" appendix (deterministic `print()`ed JSON, same content as version 4's, reusing already-computed values with no recomputation) at the end of the notebook — closing the verification gap again while keeping every version 6 readability improvement (environment section at the top, bulleted insight cells). No computed cell changed. This is the version recorded above and committed. |

## Local Vs. Kaggle Output Comparison

**All retrievable printed outputs were compared. Computed findings match
except for the documented 0.0001 A/C differences; runtime package versions
differ as documented below.** Every `print()`-based output — including the
Environment section at the top and the Reproducibility Snapshot at the
end — was diffed line-by-line between the local run (this checkout,
`python3 -m jupyter nbconvert --to notebook --execute --inplace`, default
kernel) and the Kaggle v7 log:

**Match exactly:**
- Target counts (`train: (691369, 14), test: (296302, 13)`), positive rate `0.7094`.
- Categorical target-rate breakdown and train/test proportions (`gender`, `stress_level`, `academic_work_impact`).
- Duplicate-row counts (train-internal: 0, test-internal: 0, cross-split: 2).
- Numeric signal ranking (Cohen's-*d*-consistent univariate AUC, all 9 features).
- Mutual information (all 12 features).
- Numeric drift KS statistics (all 9 features).
- Categorical drift chi-square statistics (all 3 features).
- Adversarial validation AUC, experiment B (missingness indicators only): `0.5654` both.

**One real, documented difference in computed findings:** adversarial
validation AUC for experiments A (raw features only) and C (raw +
indicators) — local `0.5650`, Kaggle `0.5651`, a `0.0001` difference. This
is not a new concern for this project: `HistGradientBoostingClassifier`
has previously been observed producing slightly different values across
separate process runs with the same `random_state` set (previously
between two local runs; here between local and Kaggle, same underlying
cause — likely multi-threaded histogram-building floating-point
non-associativity). Reported exactly rather than rounded away or described
as a match. Runtime package versions also differ, as expected — see the
table below.

No error output on Kaggle (confirmed: no `error`/`traceback`/`exception`
string anywhere in the v7 kernel log). Execution counts remain contiguous
1–22 across all 22 code cells, confirming a genuine top-to-bottom run with
no stale/out-of-order cell state.

**On version 6, corrected:** the version 6 manifest listed numeric-signal
ranking, mutual information, and drift statistics under "Match exactly"
without independently verifying them for that specific version — the
verification channel for those DataFrame findings (the printed summary)
had just been removed in that same version, and the claim was carried
forward from version 5 rather than re-checked. Version 5's own comparison
for those items remains valid (they were genuinely diffed then), and the
producing source cells were byte-identical from version 5 through version
7, but version 6 itself was never independently re-verified for those
specific findings. Version 7 closes that gap directly.

**Not independently verified:** the KDE/heatmap/barplot figures. These
remain bare-expression outputs with no text representation to diff, and
`kaggle kernels output` did not return `__notebook__.ipynb`/
`__results__.html` for this kernel via this Kaggle CLI version (1.7.4.5),
despite the log confirming both files were written server-side.
Pixel-level figure comparison is out of scope for this milestone rather
than a blocking gap.

## Trusted Kaggle Package Versions

Printed by the notebook's own Environment section during the v7 Kaggle run
(this table is the only place these are recorded as trusted — do not copy
stale numbers elsewhere):

| Package | Kaggle Version | Local Version (this checkout) |
| --- | --- | --- |
| numpy | 2.0.2 | 2.4.6 |
| pandas | 2.3.3 | 2.3.3 |
| scikit-learn | 1.6.1 | 1.9.0 |
| scipy | 1.16.3 | 1.17.1 |
| matplotlib | 3.10.0 | 3.11.1 |
| seaborn | 0.13.2 | 0.13.2 |

Local versions differ from Kaggle's for 4 of 6 packages (numpy,
scikit-learn, scipy, matplotlib) — expected, since local execution used
whatever this machine's default Python environment has installed, not a
pinned match to Kaggle's image. These are the first real trusted-runtime
versions recorded for this project — use them, not local versions, if/when
`requirements.txt` is pinned.

## Baseline Submission-Mode Run

The trusted OOF evidence for `02_baseline_modeling.ipynb` (HGB OOF AUC
`0.95733`) was established locally and recorded in
`docs/6_baseline_modeling.md`; `RUN_MODE = "submission"` skips all
evaluation work by design, so this Kaggle run is not expected to reproduce
that number — it exists to prove the champion configuration fits and
predicts cleanly inside Kaggle's own execution environment and produces a
valid competition artifact.

**Push.** The public notebook was pushed with `RUN_MODE = "submission"`,
`CHAMPION_NAME = "hist_gradient_boosting"`; the repository's committed
copy uses `RUN_MODE = "evaluate"`, matching the source used for the
trusted OOF evidence above.

**Execution log.** No `error`/`traceback` string anywhere in the version-1
kernel log. Full stdout:

```
X: (691369, 12), y: (691369,), X_test: (296302, 12)
Wrote /kaggle/working/submission.csv: (296302, 2)
```

Timestamps in the log: data load completed at 18.9s, the write completed
at 31.4s (so fit + predict + write took ~12.5s), on the notebook's
GPU-enabled Kaggle runtime — not comparable to the CPU-only local reference
timings in `docs/6_baseline_modeling.md` §1.

**Environment.** This run's kernel log shows Kaggle's Python 3.12
environment (`/usr/local/lib/python3.12/dist-packages/...` in the
nbconvert/HTML-export stack trace lines) and confirms the kernel ran on
the public, internet-disabled, GPU-enabled configuration declared in
`notebooks/kernels/baseline_modeling/kernel-metadata.json`. Submission
mode does not print a package-version summary, so exact library versions
for this run are not recorded here; do not assume they match the EDA
notebook's trusted-version table above.

**Artifact validation.** Downloaded via `kaggle kernels output` to
`/private/tmp/s6e8-baseline-output/submission.csv` (temporary directory,
not committed), then validated:

```
$ python3 scripts/verify_submission.py /private/tmp/s6e8-baseline-output/submission.csv
{'rows': 296302, 'unique_predictions': 296146, 'minimum': 8.12196190577754e-22, 'maximum': 1.0}
exit: 0
```

296,302 rows (matches `data/test.csv`), IDs in test order, all predictions
finite and within `[0, 1]`. `unique_predictions`, `minimum`, and `maximum`
match exactly what an independent local `RUN_MODE = "submission"` run
produced for the same committed champion configuration.

File identity, for the user-approval and submission gates:

| Property | Value |
| --- | --- |
| Bytes | 7,743,772 |
| SHA-256 | `f37f02ec21176f8e7b02bdc7122545edc4deb2b197ac37c970beaea62eb5e1ca` |

**Champion factory confirmation.** The published notebook's submission
path (`fit_champion_and_predict(CHAMPION_NAME, ...)` calling
`build_model(CHAMPION_NAME)`) is the same factory call the evaluation path
uses — no separate Kaggle-only model-construction code exists.

The exact artifact above was submitted after explicit approval. Kaggle
completed scoring with public ROC AUC `0.95865`; the submission and decision
are recorded in `docs/8_submission_manifest.md`.
