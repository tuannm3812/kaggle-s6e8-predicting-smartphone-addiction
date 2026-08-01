# Kaggle Run Manifest

Evidence recorded from the actual successful public Kaggle run only — no
provisional values.

| Notebook | Public URL | Kaggle Version | Status | Runtime | Local Comparison | UTC Execution Date |
| --- | --- | --- | --- | --- | --- | --- |
| `01_eda.ipynb` | https://www.kaggle.com/code/tuannm3812/smartphone-addiction-eda | 6 | `complete` | ~160s (8.7s–168.3s per kernel log timestamps) | All retrievable printed outputs were compared. Computed findings match except for the documented 0.0001 A/C differences; runtime package versions differ as documented below. | 2026-08-01 13:44:06.067 UTC (`lastRunTime`, `kaggle kernels list -m`) |

## Version History

Six versions were pushed while resolving a real path-detection bug,
closing a verification gap, rewriting the notebook's prose for a public
audience, and improving structure/readability. Each is recorded below,
not silently overwritten:

| Version | Status | Outcome |
| --- | --- | --- |
| 1 | `error` | `FileNotFoundError: [Errno 2] No such file or directory: '../data/train.csv'`. Root cause: the notebook's Kaggle-path check used `/kaggle/input/playground-series-s6e8`, which does not exist on Kaggle's actual mount; the real competition input path is `/kaggle/input/competitions/playground-series-s6e8` (confirmed against the working pattern already used in the sibling `kaggle-s6e6`/`kaggle-s6e7` repos). The notebook silently fell through to the local-only `../data` fallback, which doesn't exist inside the Kaggle container. |
| 2 | `complete` | Fix applied (corrected the path check to `/kaggle/input/competitions/playground-series-s6e8`). Ran successfully, but the runtime-versions cell's output (a bare dict expression, not `print()`) wasn't retrievable via `kaggle kernels output` — that command only returned the execution log for this kernel, not `__notebook__.ipynb`/`__results__.html`, and bare-expression `execute_result` outputs don't appear in the stdout/stderr log stream. |
| 3 | `complete` | Added `print(runtime_versions)` so the package-version evidence lands in the log. Several load-bearing numeric findings (feature-signal ranking, mutual information, drift statistics) were still only bare-expression DataFrames, unverifiable against Kaggle the same way. |
| 4 | `complete` | Added a single `print()`ed JSON verification summary (former Section 11 of the notebook) covering numeric signal ranking, mutual information, numeric and categorical drift statistics, adversarial-validation AUCs, and duplicate counts — closing the verification gap for everything except plots. Some notebook markdown was not yet self-contained for a public reader. |
| 5 | `complete` | Rewrote every markdown cell to be self-contained and reader-facing — methodology and cautions preserved, internal references removed. No computed cell changed; re-verified identical results (except the already-documented 0.0001 A/C difference) and identical contiguous execution counts (1–22) after the rewrite. |
| 6 | `complete` | Structural cleanup: removed the JSON verification-summary section (it only existed to work around the `kaggle kernels output` limitation noted above, and duplicated numbers already shown in the tables earlier in the notebook — no value for a reader). Moved the package-version cell from the end to a new "Environment" section right after setup, reformatted as a readable bullet list instead of a raw dict print. Converted four dense insight cells to bulleted lists for scanability. No computed cell changed. This is the version recorded above and committed. |

## Local Vs. Kaggle Output Comparison

**All retrievable printed outputs were compared. Computed findings match
except for the documented 0.0001 A/C differences; runtime package versions
differ as documented below.** Every `print()`-based output — including the
environment section moved to the top of the notebook in version 6 — was
diffed line-by-line between the local run (this checkout, `python3 -m
jupyter nbconvert --to notebook --execute --inplace`, default kernel) and
the Kaggle v6 log:

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
string anywhere in the v6 kernel log). Execution counts remain contiguous
1–21 across all 21 code cells, confirming a genuine top-to-bottom run with
no stale/out-of-order cell state.

**Not independently verified:** the KDE/heatmap/barplot figures. These
remain bare-expression outputs with no text representation to diff, and
`kaggle kernels output` did not return `__notebook__.ipynb`/
`__results__.html` for this kernel via this Kaggle CLI version (1.7.4.5),
despite the log confirming both files were written server-side.
Pixel-level figure comparison is out of scope for this milestone rather
than a blocking gap.

## Trusted Kaggle Package Versions

Printed by the notebook's own Environment section during the v6 Kaggle run
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
