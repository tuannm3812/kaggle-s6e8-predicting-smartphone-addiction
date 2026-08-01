# Claude–Codex Active Task Log

This tracked file is the shared handoff and review channel for the current
task. Claude and Codex must read it before starting work. Only one agent
modifies the repository at a time.

## Workflow Rules

1. Work from the shared `main` checkout.
2. Before acting, read `git status`, recent `git log`, the implementation
   plan, and this file.
3. Claude implements and commits one coherent task; Codex reviews without
   editing the implementation.
4. Address review findings in separate commits. Do not amend reviewed
   commits.
5. Do not begin the next task while findings or the user's promotion decision
   remain unresolved.
6. Keep public notebooks and documentation reader-facing; internal agent,
   checklist, and review-log narration belongs only in this collaboration
   log.

## Previous Milestone

Task 1 and public EDA version 7 were approved by the user on 2026-08-02. The
full discussion is archived at
`docs/collaboration/archive/2026-08-02-task-1-eda.md`.

## Current Task

- Plan: `docs/superpowers/plans/2026-08-01-s6e8-implementation-plan.md`
- Task: Task 2 — Add A Tested Submission Contract
- Claude implementation commit: `fac512b` — `test(submission): add artifact contract validator`
- Status: implementation complete; awaiting Codex review
- Public promotion required: no; this task creates local validation tooling
- User decision required after Codex review: yes

## Scope

Create a reusable submission validator before generating or submitting model
predictions:

- Create `scripts/verify_submission.py`.
- Create `tests/test_verify_submission.py`.
- Modify `.gitignore` only if required by the implementation plan.
- Implement
  `validate_submission(submission_path, test_path, sample_path) -> dict`.
- Validate exact schema, row count, ID order, finite probabilities, and the
  inclusive probability range `[0, 1]`.
- Provide a CLI that exits nonzero for invalid submissions and prints a
  compact validation summary for valid submissions.
- Do not commit data, submissions, credentials, or generated prediction
  artifacts.

## Required Development Evidence

Claude must follow the plan's test-first sequence and report:

1. The initial failing test result before the implementation exists.
2. The smallest implementation that makes the tests pass.
3. Test coverage for valid input, out-of-range/NaN values, schema mismatch,
   row-count mismatch, and ID-order mismatch.
4. The final focused test command and result.
5. A CLI smoke test for both a valid and invalid temporary submission.
6. The implementation commit hash and clean `git status`.

Use temporary synthetic files for tests; do not depend on the competition
data files for the unit-test suite.

## Claude Implementation Report

**Status: complete, ready for Codex review.**
**Commit: `fac512b` — `test(submission): add artifact contract validator`**

Built test-first, per the plan's exact sequence.

### 1. Initial failing test result (RED)

```
$ python3 -m pytest tests/test_verify_submission.py -v
ERROR collecting tests/test_verify_submission.py
ImportError while importing test module '.../tests/test_verify_submission.py'.
tests/test_verify_submission.py:6: in <module>
    from scripts.verify_submission import validate_submission
E   ModuleNotFoundError: No module named 'scripts.verify_submission'
========================= 1 error in 0.53s =========================
```

Correct failure reason (module doesn't exist yet), not a typo or setup issue.

### 2. Smallest implementation that makes the tests pass

`scripts/verify_submission.py` — `validate_submission()` per the plan's
interface, plus one required fix: the plan's example used `dict[str, int |
float]` (PEP 604 union syntax), which raises `TypeError` at import time on
this environment's Python 3.9 (valid only on 3.10+). Fixed with `from
__future__ import annotations` so annotations are never evaluated at
runtime — no interface or behavior change, confirmed by re-running the
same tests unchanged.

### 3. Test coverage

`tests/test_verify_submission.py` covers all five categories the task
requires — **two more than the plan's own example test file included**:
the plan's illustrative code only had valid/out-of-range-NaN/ID-order; I
added `test_schema_mismatch_fails` and `test_row_count_mismatch_fails` to
actually satisfy "schema mismatch" and "row-count mismatch" from the
required-evidence checklist, using the same `write_contract_files` helper.

| Category | Test |
| --- | --- |
| Valid input | `test_valid_submission_passes` |
| Out-of-range/NaN | `test_invalid_probability_fails[-0.1, 1.1, nan]` (parametrized) |
| Schema mismatch | `test_schema_mismatch_fails` (added) |
| Row-count mismatch | `test_row_count_mismatch_fails` (added) |
| ID-order mismatch | `test_id_order_mismatch_fails` |

### 4. Final focused test command and result

```
$ python3 -m pytest tests/test_verify_submission.py -v
tests/test_verify_submission.py::test_valid_submission_passes PASSED
tests/test_verify_submission.py::test_invalid_probability_fails[-0.1] PASSED
tests/test_verify_submission.py::test_invalid_probability_fails[1.1] PASSED
tests/test_verify_submission.py::test_invalid_probability_fails[nan] PASSED
tests/test_verify_submission.py::test_id_order_mismatch_fails PASSED
tests/test_verify_submission.py::test_schema_mismatch_fails PASSED
tests/test_verify_submission.py::test_row_count_mismatch_fails PASSED
========================= 7 passed in 0.27s =========================
```

### 5. CLI smoke test

Using the real `data/test.csv`/`data/sample_submission.csv` and two
temporary submissions (not committed, scratch-only):

```
$ python3 scripts/verify_submission.py valid_submission.csv --test data/test.csv --sample data/sample_submission.csv
{'rows': 296302, 'unique_predictions': 1, 'minimum': 0.709424, 'maximum': 0.709424}
$ echo $?
0

$ python3 scripts/verify_submission.py invalid_submission.csv --test data/test.csv --sample data/sample_submission.csv
ValueError: Predictions must be within [0, 1]
$ echo $?
1
```

Valid case: exit 0, compact summary printed. Invalid case: exit 1 (nonzero),
as required.

### 6. Commit and status

Commit `fac512b`. `git status --short --branch`:

```
## main...origin/main [ahead 25]
```

Clean working tree. `.gitignore` already covered `submission.csv` and
`predictions/` — no change needed. No competition data, credentials, or
generated artifacts committed; test suite uses only `tmp_path` synthetic
files.

## Codex Review

Pending.

## Codex Review

Pending.

## User Promotion Decision

Pending.
