# Kaggle Run Manifest

Evidence recorded from the actual successful public Kaggle run only — no
provisional values. Task 1 of
`.superpowers/sdd/2026-08-01-s6e8-implementation-plan/task-1-brief.md`.

| Notebook | Public URL | Kaggle Version | Status | Runtime | Local Comparison | UTC Execution Date |
| --- | --- | --- | --- | --- | --- | --- |
| `01_eda.ipynb` | https://www.kaggle.com/code/tuannm3812/smartphone-addiction-eda | 3 | `complete` | ~170s (8.8s–169.7s per kernel log timestamps) | Outputs match exactly — see below | 2026-08-01 10:22:23.823 UTC (`lastRunTime`, `kaggle kernels list -m`) |

## Version History

Three versions were pushed while resolving a real path-detection bug —
recorded per the brief's "record the failure and replacement version"
instruction, not silently overwritten:

| Version | Status | Outcome |
| --- | --- | --- |
| 1 | `error` | `FileNotFoundError: [Errno 2] No such file or directory: '../data/train.csv'`. Root cause: the notebook's Kaggle-path check used `/kaggle/input/playground-series-s6e8`, which does not exist on Kaggle's actual mount; the real competition input path is `/kaggle/input/competitions/playground-series-s6e8` (confirmed against the working pattern already used in the sibling `kaggle-s6e6`/`kaggle-s6e7` repos). The notebook silently fell through to the local-only `../data` fallback, which doesn't exist inside the Kaggle container. |
| 2 | `complete` | Smallest fix applied (corrected the path check to `/kaggle/input/competitions/playground-series-s6e8`). Ran successfully, but the runtime-versions cell's output (a bare dict expression, not `print()`) wasn't retrievable via `kaggle kernels output` — that command only returned the execution log for this kernel, not `__notebook__.ipynb`/`__results__.html`, and bare-expression `execute_result` outputs don't appear in the stdout/stderr log stream. |
| 3 | `complete` | Added `print(runtime_versions)` alongside the existing bare-expression display, so the required package-version evidence lands in the one output channel confirmed retrievable. No other content changed. This is the version recorded above and committed. |

## Local Vs. Kaggle Output Comparison

Every `print()`-based output in the notebook was diffed between the local
run (this worktree, `python3 -m jupyter nbconvert --to notebook --execute
--inplace`, default kernel) and the Kaggle v3 log — **all match exactly**:

- Target counts: `train: (691369, 14), test: (296302, 13)`, positive rate
  `0.7094` — identical.
- Categorical target-rate breakdown (`gender`, `stress_level`,
  `academic_work_impact`) — identical counts and means.
- Duplicate-row counts (train-internal: 0, test-internal: 0, cross-split: 2)
  — identical.
- Categorical train/test proportions — identical.
- Adversarial validation OOF AUCs (`A_raw_features_only`,
  `B_missingness_indicators_only`, `C_raw_plus_indicators`) — identical to
  4 decimal places (`0.5651` / `0.5654` / `0.5651`).

No error output on Kaggle (confirmed: no `error`/`traceback`/`exception`
string anywhere in the v3 kernel log).

Bare-expression (`execute_result`) outputs — DataFrames like
`numeric_signal`, `mutual_info_table`, `drift_table`, and the KDE/heatmap/
barplot figures — were not independently diffable this way, since they
don't appear in the log stream and `kaggle kernels output` did not return
`__notebook__.ipynb`/`__results__.html` for this kernel via this Kaggle CLI
version (1.7.4.5). This is a tooling limitation of this environment, not
evidence of any output difference — flagged as a concern in
`.superpowers/sdd/2026-08-01-s6e8-implementation-plan/task-1-report.md`
rather than silently assumed to match.

## Trusted Kaggle Package Versions

Printed by the notebook's own runtime-versions cell during the v3 Kaggle
run (`docs/7_kaggle_run_manifest.md` is the only place these are recorded
as trusted — do not copy stale numbers elsewhere):

| Package | Kaggle Version | Local Version (this worktree) |
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
pinned match to Kaggle's image. All outputs still matched exactly (see
above), so this drift did not affect results for this notebook. Per
`docs/2_implementation_plan.md` Phase 5 step 4 / the Codex review: these
are the first real trusted-runtime versions recorded for this project —
use them, not local versions, if/when `requirements.txt` is pinned.
