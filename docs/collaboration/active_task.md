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
- Status: ready for Claude implementation
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

Pending.

## Codex Review

Pending.

## User Promotion Decision

Pending.
