<!-- Revue CONDAMAD finale de CS-162. -->

# CONDAMAD Code Review

## Review target

- Story: `CS-162-heriter-regles-orbes-systemes-astrologiques`
- Capsule: `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques`
- Review date: 2026-05-14

## Inputs reviewed

- `00-story.md`
- Generated capsule files
- `_condamad/stories/regression-guardrails.md`, especially `RG-091` to `RG-097`
- `git diff --stat`, `git diff --check`, targeted diffs
- Subagent review layers: story conformance, technical risk, source objective closure
- Validation commands recorded in `generated/10-final-evidence.md`

## Diff summary

The implementation adds explicit `astral_systems.inherits_from_system_id`, removes active `copy_rules_from` usage, keeps `modern` and `traditional` as physical rule owners, makes `hellenistic` and `medieval` inherit `traditional`, updates resolver ordering, adds migration cleanup for databases already at the older `0104` state, and updates tests/docs/evidence.

## Review layers

- Story Conformance Reviewer: initial findings accepted and fixed.
- Technical Risk Reviewer: initial findings accepted and fixed; untracked migration note is resolved by keeping the migration in the change set.
- Source Finding Closure Reviewer: initial findings accepted and fixed.
- Iteration 2 reviewer: migration SQL portability and empty metadata edge case checked and fixed.

## Findings

No open findings.

Resolved findings:

- Existing DBs at old `0104` kept physical child copies: fixed by `20260514_0105` DELETE cleanup and migration regression test.
- Aspect docs described old 159-row copy model: fixed in `tables-aspects-et-roles.md`.
- Missing inheritance metadata could silently lose inherited orbs: fixed by explicit resolver error and unit test.
- Unknown `inherits_from` JSON parent was not rejected: fixed by seed validation and test.
- Capsule evidence/status were pending: fixed in generated evidence and story status.
- `20260514_0105` used column-to-column `IS` comparisons in DELETE cleanup: fixed with portable NULL-safe equality and migration regression coverage.
- Empty inheritance metadata list could still allow a child without local rules to fall back silently: fixed by requiring the requested system to appear in either local rules or inheritance metadata, with unit coverage.

## Acceptance audit

AC1-AC26 have implementation and validation evidence. The story is not audit-sourced and has no hidden in-domain residual work.

## Validation audit

Validation evidence is adequate:

- `ruff format .`
- `ruff check .`
- targeted resolver/repository tests
- reference payload and seed tests
- migration tests including old duplicate cleanup simulation
- No Legacy/documentation scans
- backend app startup smoke
- second-iteration combined validation: lint plus 64 targeted tests passed

Known warnings are existing SQLAlchemy reflection warnings for expression-based indexes in migration tests; they did not fail validation.

## DRY / No Legacy audit

- No compatibility shim, alias, re-export, fallback to `modern`, or duplicate resolver was introduced.
- `copy_rules_from` is absent from active JSON.
- Child systems do not store full inherited copies.
- Existing `astro_characteristics` hits are only migration guard references expected by `RG-091`.

## Commands run by reviewer

- `git diff --check`
- `git diff --stat`
- Targeted `rg` scans listed in final evidence.

## Residual risks

- None identified for the story scope.

## Verdict

CLEAN
