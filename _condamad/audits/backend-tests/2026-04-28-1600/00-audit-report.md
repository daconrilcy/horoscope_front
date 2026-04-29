# CONDAMAD Domain Audit - backend-tests

## Scope

- Domain target: backend tests.
- Archetype: test-guard-coverage-audit with No Legacy / DRY dimensions.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/backend-tests/2026-04-28-1600/`.
- Regression guardrails consulted: `_condamad/stories/regression-guardrails.md`, RG-001 through RG-009.

## Current State

The backend test estate has 425 test files by static inventory and 3285 static test functions. A default pytest collection from `backend` succeeds after activating `.venv` and collects 3164 tests.

The suite is spread across multiple active roots:

- `backend/app/tests/unit`: 205 files.
- `backend/app/tests/integration`: 119 files.
- `backend/tests/llm_orchestration`: 39 files.
- `backend/tests/integration`: 25 files.
- `backend/tests/unit` and `backend/tests/unit/prediction`: 24 files combined.
- `backend/app/domain/llm/prompting/tests`: 1 embedded domain test file.

The configured pytest defaults in `backend/pyproject.toml` only include `app/tests`, `app/ai_engine/tests`, `tests/evaluation`, and `tests/integration`. The configured `app/ai_engine/tests` path is absent, while 64 existing test files with 304 static test functions are outside the configured roots.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 3 |
| Medium | 3 |
| Low | 1 |
| Info | 0 |

## Keep / Remove Guidance

Keep immediately:

- Tests collected by default that cover active API, auth, billing, entitlement, DB, LLM, and astrology behavior.
- No Legacy and architecture guard tests that map to RG-001 through RG-009.
- Operational script/docs tests until ownership is decided, because removing them would silently drop governance.

Rework before keeping long term:

- `test_story_*.py` files: keep their protected invariants, but rename or merge into canonical guard suites.
- DB-backed tests importing production `SessionLocal` or relying on global conftest monkeypatches.
- Test modules importing helpers from other executable test modules.

Remove or implement:

- `backend/app/tests/unit/test_seed_validation.py`, which is a no-op facade.

Needs user decision:

- Whether docs, PR template, backup/restore, secrets scan, and PowerShell pipeline checks belong in backend pytest or a separate quality/ops suite.

## Regression Guardrails

- Applicable invariants: RG-001, RG-002, RG-003, RG-004, RG-005, RG-006, RG-007, RG-008, RG-009.
- Required non-regression evidence for future cleanup: full pytest collection, static root inventory, No Legacy scans, and explicit mapping of story tests to durable guardrails.
- Allowed differences for future cleanup: only path/name movement with unchanged behavioral assertions, unless a story explicitly approves removal.

## Recommended Sequence

1. Fix default pytest discovery so every retained test is collected or explicitly opt-in.
2. Decide and document canonical backend test roots.
3. Converge DB fixtures and remove direct `SessionLocal` test dependencies.
4. Reclassify story-numbered files into durable guard suites.
5. Extract shared helpers from executable test modules.
6. Remove or implement the no-op seed validation test.

## Validation Notes

Python commands used for collection and validation were run after activating `.venv`, per repository rules. Full test execution was not run because this audit is read-only and the request was to audit organization and retention, not to validate the whole application behavior.
