# CONDAMAD Validation Contract

## 1. Purpose

This contract defines how a CONDAMAD implementation must be validated before a story can be considered ready for review.

Validation is not a ceremonial final step. It is the evidence layer that proves that the story was implemented narrowly, safely, and in line with the repository architecture. A CONDAMAD story is complete only when every acceptance criterion has explicit implementation evidence, validation evidence, and final reviewer-facing proof.

The validation contract applies to the `condamad-dev-story` skill and to every generated story capsule under:

```text
_condamad/stories/<story-key>/
```

The contract is intentionally strict. It is optimized for Codex-style repository work: inspect the real code, protect the worktree, run targeted and broad checks, classify failures honestly, and produce a final evidence trail that a reviewer can trust.

## 2. Core Doctrine

CONDAMAD validation follows nine rules:

1. A story is not done because code changed.
2. A story is done only when every AC maps to code evidence and validation evidence.
3. A skipped command is never a pass.
4. A failing command is never hidden.
5. A legacy hit is never ignored.
6. A dirty worktree is never overwritten blindly.
7. A broad test suite does not replace targeted evidence.
8. Targeted checks do not replace regression evidence.
9. Final evidence must be written before the story is marked ready for review.

## 3. Validation Outcomes

Every CONDAMAD validation must end in one of four outcomes.

### 3.1 `PASS`

Use `PASS` only when:

- all acceptance criteria are satisfied;
- all required validations were run successfully;
- no unresolved regression exists;
- no unclassified legacy or DRY risk remains;
- final evidence is complete;
- the worktree only contains expected story changes.

### 3.2 `PASS_WITH_LIMITATIONS`

Use `PASS_WITH_LIMITATIONS` only when the implementation is believed correct, but one or more non-critical validations could not be run because of an environmental limitation.

This outcome requires explicit documentation of:

- the command that could not be run;
- the exact reason;
- the risk created;
- the compensating validation used;
- the reviewer focus required.

This outcome must not be used when a relevant test failed.

### 3.3 `FAIL`

Use `FAIL` when any required check ran and failed, or when an AC lacks implementation or validation evidence.

The story must not be marked ready for review.

### 3.4 `BLOCKED`

Use `BLOCKED` when implementation or validation cannot proceed without external input, missing credentials, missing dependencies, unavailable files, or clarification of a destructive or ambiguous change.

The final evidence must describe the blocker precisely.

## 4. Required Validation Files

A CONDAMAD capsule must contain or generate the following validation-related files:

```text
_condamad/stories/<story-key>/
  00-story.md
  generated/
    03-acceptance-traceability.md
    04-target-files.md
    06-validation-plan.md
    07-no-legacy-dry-guardrails.md
    10-final-evidence.md
```

Optional but recommended when the story is complex:

```text
  generated/
    05-implementation-plan.md
    09-dev-log.md
```

The validation files are not decorative. Codex must use them while implementing and must update the final evidence before completion.

## 5. Preflight Validation

Preflight validation happens before any code edit.

### 5.1 Required checks

The implementation agent must:

1. Locate the repository root.
2. Read the relevant `AGENTS.md` instructions in scope.
3. Run or inspect the equivalent of:

```bash
git status --short
```

4. Identify existing dirty files.
5. Confirm the source story or capsule is accessible.
6. Confirm the capsule structure is present or generate it.
7. Read the complete story before editing.
8. Read `generated/03-acceptance-traceability.md` before implementation.
9. Read `generated/06-validation-plan.md` before implementation.
10. Read `generated/07-no-legacy-dry-guardrails.md` before implementation.

### 5.2 Dirty worktree rule

If the worktree contains pre-existing user changes, Codex must not overwrite, revert, reformat, or stage them unless they are directly required by the story and clearly identified.

The final evidence must distinguish:

- pre-existing dirty files;
- files changed by the story;
- files intentionally left untouched.

### 5.3 Preflight evidence

Preflight evidence must be recorded in `generated/10-final-evidence.md` or `generated/09-dev-log.md`.

Minimum fields:

```md
## Preflight

- Repository root:
- Story source:
- Initial `git status --short`:
- Pre-existing dirty files:
- AGENTS.md files considered:
- Capsule generated: yes/no
```

## 6. Capsule Validation

If the capsule does not exist, Codex must generate it before implementation.

### 6.1 Required generated files

The capsule is valid only when these files exist:

```text
generated/01-execution-brief.md
generated/03-acceptance-traceability.md
generated/04-target-files.md
generated/06-validation-plan.md
generated/07-no-legacy-dry-guardrails.md
generated/10-final-evidence.md
```

### 6.2 Minimum quality checks

The capsule is invalid if:

- the execution brief does not identify the story objective;
- acceptance criteria are missing from the traceability matrix;
- target files are empty or generic when the story is code-specific;
- the validation plan has no executable checks;
- the No Legacy guardrails are absent for cleanup, refactor, migration, or canonicalization stories;
- final evidence has no AC validation table.

### 6.3 Capsule validation output

`generated/10-final-evidence.md` must include:

```md
## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes/no | PASS/FAIL | |
| `generated/01-execution-brief.md` | yes | yes/no | PASS/FAIL | |
| `generated/03-acceptance-traceability.md` | yes | yes/no | PASS/FAIL | |
| `generated/04-target-files.md` | yes | yes/no | PASS/FAIL | |
| `generated/06-validation-plan.md` | yes | yes/no | PASS/FAIL | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes/no | PASS/FAIL | |
| `generated/10-final-evidence.md` | yes | yes/no | PASS/FAIL | |
```

## 7. Acceptance Criteria Validation

Every acceptance criterion must be validated individually.

### 7.1 Required traceability matrix

`generated/03-acceptance-traceability.md` must contain a table with at least these columns:

```md
| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
```

Before final completion, `generated/10-final-evidence.md` must contain a completed evidence table:

```md
| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
```

### 7.2 Valid AC statuses

Use only these statuses:

- `PASS`
- `PASS_WITH_LIMITATIONS`
- `FAIL`
- `BLOCKED`
- `NOT_APPLICABLE`

`NOT_APPLICABLE` is allowed only when the AC is explicitly discovered to be irrelevant because the repository already satisfies it or because the story contains a scoped conditional requirement. It must include a justification.

### 7.3 AC completion rule

An AC cannot be marked `PASS` unless both are true:

- implementation evidence exists;
- validation evidence exists.

Implementation evidence may include:

- changed files;
- deleted files;
- unchanged files inspected and intentionally left as-is;
- configuration changes;
- migration changes;
- import rewiring;
- guardrail additions.

Validation evidence may include:

- unit tests;
- integration tests;
- architecture guard tests;
- import tests;
- regression tests;
- negative search evidence;
- lint/static checks;
- manual diff review evidence when automated validation is impossible.

### 7.4 Forbidden AC evidence

The following are not sufficient evidence:

- “implemented as requested”;
- “looks good”;
- “should work”;
- a changed file list without explaining which AC it satisfies;
- a test command that was not run;
- an unrelated full test suite with no targeted evidence;
- an unclassified search result.

## 8. Validation Plan Contract

`generated/06-validation-plan.md` defines how the story must be validated.

### 8.1 Required sections

The validation plan must include:

```md
# Validation Plan

## Environment assumptions

## Targeted checks

## Unit tests

## Integration tests

## Architecture / import guards

## DRY / No Legacy scans

## Quality checks

## Regression checks

## Diff review

## Commands that may be skipped only with justification
```

If a section does not apply, it must say why.

### 8.2 Command format

Each command must be represented as:

```md
| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
```

Example:

```md
| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted tests | `pytest backend/tests/test_example.py -q` | repo root | yes | all tests pass |
| Lint | `ruff check .` | `backend/` or repo root | yes | no lint errors |
```

### 8.3 Command selection rule

Codex must not invent commands blindly.

It must infer validation commands from:

1. `AGENTS.md`;
2. project configuration files;
3. existing scripts;
4. existing CI workflows;
5. existing test conventions;
6. story-specific instructions;
7. repository language/framework patterns.

When uncertain, Codex may choose the smallest safe validation command and must explain the choice.

## 9. Command Execution Contract

### 9.1 Required command evidence

Every command run must be logged in final evidence:

```md
| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
```

Use exact command text. Do not paraphrase.

### 9.2 Result values

Use only:

- `PASS`
- `FAIL`
- `SKIPPED`
- `BLOCKED`
- `NOT_APPLICABLE`

### 9.3 Exit status rule

If a command was run, record the exit status when available.

If the environment does not expose an exit status, record `unknown` and summarize the observed result honestly.

### 9.4 Failure rule

If a command fails:

1. stop treating validation as successful;
2. inspect the failure;
3. fix the implementation if the failure is story-related;
4. rerun the relevant command;
5. record both the failure and the successful rerun when useful for reviewer context.

Do not delete failure evidence if it explains a relevant implementation decision.

### 9.5 Skip rule

A skipped command must include:

- exact command;
- reason skipped;
- whether it is required;
- risk created;
- compensating evidence.

A required command skipped without justification makes validation `FAIL` or `BLOCKED`.

## 10. Recommended Validation Layers

CONDAMAD validation should be layered from narrow to broad.

### 10.1 Layer 1 — Static inspection

Before editing and before finalization:

```bash
git status --short
git diff --stat
git diff --check
```

Use `git diff --check` when available to detect whitespace and conflict marker issues.

### 10.2 Layer 2 — Targeted tests

Run the smallest tests that prove the changed behavior or structural rule.

Examples:

```bash
pytest backend/tests/test_specific_module.py -q
pytest backend/tests/domain/llm/test_gateway.py -q
pytest backend/tests/architecture/test_no_legacy_imports.py -q
```

Targeted tests are mandatory when relevant tests exist or can be added within scope.

### 10.3 Layer 3 — Architecture and import guards

For refactor, namespace, cleanup, DRY, or No Legacy stories, add or run architecture checks.

Examples:

```bash
pytest backend/tests/architecture -q
rg "from app\.services" backend/app backend/tests
rg "legacy|compat|shim|fallback|deprecated|alias" backend/app backend/tests docs scripts
```

Searches must be story-specific. Generic searches are useful but not enough when a specific symbol, module, registry key, or route was removed.

### 10.4 Layer 4 — Quality checks

Use repository-specific quality tooling.

Common Python examples:

```bash
ruff format .
ruff check .
pytest -q
```

When the project uses check-only formatting in CI, prefer the configured command, such as:

```bash
ruff format --check .
```

Do not run broad formatting over unrelated files if it would create noisy diffs outside the story scope unless the repository standard explicitly requires it.

### 10.5 Layer 5 — Regression suite

Run the broader regression suite required by the story and repository norms.

Examples:

```bash
pytest -q
./scripts/quality-gate.ps1
```

If the full suite is too expensive or impossible in the current environment, document the limitation and run the strongest targeted and intermediate checks available.

## 11. DRY / No Legacy Validation

When a story touches cleanup, refactor, canonicalization, namespace convergence, migration, fallback removal, or duplication removal, DRY / No Legacy validation is mandatory.

### 11.1 Required search evidence

The final evidence must include story-specific searches for:

- removed module names;
- removed class names;
- removed function names;
- old import paths;
- legacy registry keys;
- compatibility aliases;
- fallback branches;
- deprecated configuration keys;
- docs or tests that still present old paths as supported.

Example:

```bash
rg "<old_module>|<old_symbol>|<old_registry_key>" backend/app backend/tests docs scripts
rg "legacy|compat|shim|fallback|deprecated|alias" backend/app backend/tests docs scripts
```

### 11.2 Hit classification

Every search hit must be classified:

```md
| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
```

Allowed classifications:

- `active_legacy_removed`
- `active_legacy_remaining_blocker`
- `allowed_historical_reference`
- `test_guard_expected_hit`
- `documentation_updated`
- `false_positive`
- `out_of_scope_with_justification`

Unclassified hits make validation incomplete.

### 11.3 Negative evidence rule

When the story removes a legacy path, at least one validation must prove that the old path is gone or fails explicitly.

Acceptable evidence:

- negative import test;
- architecture guard test;
- registry absence test;
- route absence test;
- configuration validation test;
- `rg` evidence with classified zero or allowed hits.

## 12. Diff Review Contract

Before finalizing, Codex must review the diff.

### 12.1 Required diff checks

Run or inspect equivalent output:

```bash
git diff --stat
git diff --check
git status --short
```

When practical, inspect the relevant hunks:

```bash
git diff -- <changed-file>
```

### 12.2 Diff review questions

Codex must verify:

- Are all changed files related to the story?
- Did any generated, lock, cache, binary, or unrelated file change unexpectedly?
- Did formatting touch files outside scope?
- Did any old import path remain active?
- Did any compatibility wrapper remain?
- Did any test assert legacy behavior as nominal behavior?
- Did any docs or comments contradict the implementation?
- Did story/capsule files change only in allowed ways?

### 12.3 Unexpected diff rule

If unexpected changes exist, Codex must either:

- revert only its own unrelated changes safely; or
- document the issue as a blocker or limitation.

Codex must not revert user-owned pre-existing changes.

## 13. Story File Validation

When the source story follows a BMAD-like format, Codex must preserve the story contract.

### 13.1 Allowed story updates

Unless the user explicitly asks otherwise, Codex may only update:

- task/subtask checkboxes;
- Dev Agent Record;
- File List;
- Change Log;
- Status.

### 13.2 Forbidden story updates

Codex must not rewrite:

- Story intent;
- Acceptance Criteria;
- Dev Notes;
- architecture context;
- business requirements;
- scope;
- non-goals.

If the story contains contradictions, Codex must document the issue and continue only when a safe interpretation exists.

### 13.3 Story status rule

The story may be marked `review` or equivalent only when:

- all ACs have evidence;
- required validations have passed or limitations are documented;
- final evidence is complete;
- no blocking issue remains.

## 14. Final Evidence Contract

`generated/10-final-evidence.md` is mandatory.

### 14.1 Required sections

It must include:

```md
# Final Evidence

## Story status

## Preflight

## Capsule validation

## AC validation

## Files changed

## Files deleted

## Tests added or updated

## Commands run

## Commands skipped or blocked

## DRY / No Legacy evidence

## Diff review

## Final worktree status

## Remaining risks

## Suggested reviewer focus
```

### 14.2 Story status block

Use this format:

```md
## Story status

- Validation outcome: PASS/PASS_WITH_LIMITATIONS/FAIL/BLOCKED
- Ready for review: yes/no
- Story key:
- Source story:
- Capsule path:
```

### 14.3 Files changed block

Use this format:

```md
## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
```

Change types:

- `added`
- `modified`
- `deleted`
- `moved`
- `renamed`
- `generated`

### 14.4 Commands run block

Use this format:

```md
## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
```

### 14.5 Commands skipped or blocked block

Use this format:

```md
## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
```

### 14.6 Final reviewer focus

Always include reviewer focus.

Examples:

- “Review namespace convergence and confirm no consumers should keep the old import path.”
- “Review architecture guard coverage for deleted compatibility wrapper.”
- “Review whether skipped full regression suite is acceptable given environment limitation.”

## 15. Validation Anti-Patterns

The following are forbidden:

- Marking ACs complete without test or check evidence.
- Claiming a command passed when it was not run.
- Omitting failed command output from the evidence trail.
- Treating a skipped full test suite as equivalent to a pass.
- Keeping compatibility wrappers to reduce implementation effort.
- Adding broad fallback behavior to make tests pass.
- Using only manual review where an automated test is practical.
- Running only broad tests and skipping targeted tests for the changed area.
- Running only targeted tests and skipping available regression checks without explanation.
- Reformatting unrelated files and hiding it in the diff.
- Failing to classify `rg` hits in No Legacy stories.
- Updating story acceptance criteria after implementation to match the code.
- Treating a generated capsule as a substitute for reading the actual repository.

## 16. Validation Strategy by Story Type

### 16.1 Behavior story

Required evidence:

- targeted unit or integration tests;
- edge case tests;
- regression suite or relevant subset;
- lint/static checks.

### 16.2 Refactor story

Required evidence:

- characterization or regression tests;
- import/path checks;
- diff review;
- no unrelated behavior changes;
- no duplicate implementation path.

### 16.3 No Legacy / cleanup story

Required evidence:

- negative search evidence;
- deleted or migrated old paths;
- updated consumers;
- architecture guards when useful;
- explicit classification of remaining hits.

### 16.4 Namespace convergence story

Required evidence:

- canonical imports used by all nominal consumers;
- old namespace no longer active;
- tests updated to canonical path;
- no re-export modules preserving the old namespace;
- import regression or architecture guard.

### 16.5 Configuration / registry story

Required evidence:

- canonical config or registry tests;
- missing canonical config fails explicitly;
- no fallback to legacy keys;
- updated seeds/fixtures/docs when relevant.

### 16.6 Documentation-only story

Required evidence:

- changed docs listed;
- no code changes unless justified;
- links, paths, commands, and examples checked where possible;
- reviewer focus on accuracy and drift risk.

## 17. Minimal Validation Templates

### 17.1 Minimal `06-validation-plan.md`

```md
# Validation Plan

## Environment assumptions

- Repository root: TBD
- Main language/framework: TBD
- Test framework: TBD
- Lint/static tools: TBD

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted story tests | `TBD` | repo root | yes | all pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Removed symbols scan | `rg "TBD" backend/app backend/tests docs scripts` | repo root | yes | no active legacy hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint/static check | `TBD` | repo root | yes | no errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Regression suite | `TBD` | repo root | yes | all pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Worktree status | `git status --short` | repo root | yes | expected files only |
```

### 17.2 Minimal command evidence table

```md
| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest backend/tests/example_test.py -q` | repo root | PASS | 0 | 3 tests passed |
| `ruff check .` | repo root | PASS | 0 | no lint errors |
```

### 17.3 Minimal AC validation table

```md
| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/...` updated | `pytest ... -q` passed | PASS | |
```

## 18. Completion Gate

The story may be marked ready for review only when all gates pass:

```md
| Gate | Status |
|---|---|
| Capsule exists and is valid | PASS/FAIL |
| All ACs have evidence | PASS/FAIL |
| Targeted tests/checks passed | PASS/FAIL |
| Required quality checks passed | PASS/FAIL |
| Regression checks passed or limitations documented | PASS/FAIL |
| DRY / No Legacy evidence complete | PASS/FAIL |
| Diff reviewed | PASS/FAIL |
| Story file updated only in allowed sections | PASS/FAIL |
| Final evidence complete | PASS/FAIL |
| Final worktree status recorded | PASS/FAIL |
```

If any gate is `FAIL`, the story is not ready for review.

If any gate is `BLOCKED`, the story is not ready for review unless the user explicitly accepts the limitation and asks to proceed.

## 19. Final Response Contract

After completing validation, Codex must return a concise user-facing summary.

Required content:

- story key;
- validation outcome;
- ready-for-review status;
- files changed;
- tests/checks run;
- skipped or blocked checks, if any;
- remaining risks;
- capsule path.

Do not paste the entire final evidence file into the chat unless the user asks for it.

## 20. Reviewer Mindset

The final validation must make review easier, not harder.

A reviewer should be able to answer these questions quickly:

- What changed?
- Why did it change?
- Which AC does each change satisfy?
- What proves it works?
- What proves no legacy path remains?
- What was not validated?
- Where should review attention focus?

If the final evidence cannot answer those questions, validation is incomplete.
