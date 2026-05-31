# Story Writer Failure Modes

<!-- Patterns extracted from failed CS story drafts. Keep examples here so SKILL.md stays concise. -->

## Brief Primitive Loss

Failure pattern: the source brief names concrete primitives, but the story
collapses them into a broad layer name.

Correction:

- create a Brief Primitive Ledger before drafting;
- classify each named primitive as in scope, out of scope, dependency, or
  blocker;
- map each in-scope primitive to an AC, task, validation command, guardrail, or
  expected file;
- map each out-of-scope primitive to an explicit non-goal.

## Mutating Audit Validation

Failure pattern: an audit-only story asks the dev agent to run a mutating
formatter or fixer, creating implementation work inside an audit contract.

Correction:

- use check-only commands such as `ruff format --check`;
- reserve mutating commands such as `ruff format .` for implementation stories;
- preserve named source validations textually unless they are out of scope, and
  justify every omission.

## Wrong Working Directory Paths

Failure pattern: validation commands use both `cd backend` and `backend/...`
paths, or both `cd frontend` and `frontend/...` paths.

Correction:

- after `cd backend`, use paths relative to `backend`;
- after `cd frontend`, use paths relative to `frontend`;
- when the command runs from repository root, keep full repository-relative
  paths.

## Overbroad Negative Scan

Failure pattern: a forbidden symbol scan rejects legitimate fixtures,
snapshots, or adjacent surfaces. CS-321-style examples include banning a symbol
such as `trackEvent` across roots where allowed test fixtures or unrelated
domains still own that token.

Correction:

- state `forbidden_pattern`;
- state `allowed_fixture_pattern`;
- state exact scan `roots`;
- state expected false positives and how to classify them;
- prefer domain-local ownership or route patterns over repo-wide symbol bans.

## Adjacent Guardrails In Applicable Table

Failure pattern: guardrails from nearby frontend, auth, database, style, build,
or migration domains are listed as applicable because the registry contains
them, not because the story touches that surface.

Correction:

- use only exact path, operation, contract, domain, or universal local matches;
- justify each selected guardrail as `scope -> invariant -> evidence`;
- move `Needs-investigation`, registry gaps, and adjacent guardrails into notes;
- reject guardrail IDs with no local domain connection.

## Compound Acceptance Criteria

Failure pattern: one AC combines several obligations with `and`, comma lists,
or mixes behavior and validation in the same Requirement cell.

Correction:

- split one row per invariant;
- move command details to the evidence cell or Validation Plan;
- keep long enumerations in tasks or contract sections unless each item is a
  separate acceptance invariant.

## Incomplete Audit Or Report Story

Failure pattern: an audit/report story preserves a title and generic output but
drops mandatory source questions, upstream sources, deliverable formats, or
blocker conditions.

Correction:

- copy mandatory questions into ACs or deliverable requirements;
- name upstream sources and missing-source blockers;
- specify artifact paths and output format;
- map closure or reclassification expectations in Source Finding Closure.
