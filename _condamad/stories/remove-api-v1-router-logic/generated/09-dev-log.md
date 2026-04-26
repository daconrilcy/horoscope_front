# Dev Log

## Preflight

- Initial dirty files: `backend/horoscope.db`; `_condamad/stories/remove-api-v1-router-logic/` untracked.
- AGENTS considered: repository root `AGENTS.md`.
- Capsule generated with `condamad_prepare.py` after venv activation.

## Implementation Notes

- Audited 54 Python files under `backend/app/api/v1/router_logic/**`.
- Migrated former support modules into domain service packages under `backend/app/services/**`.
- Removed the rejected intermediate `backend/app/api/v1/handlers/**` placement.
- Replaced production imports and test monkeypatch strings to `app.services.*`.
- Deleted the legacy directory with no shim.
- Updated architecture guards to assert absence, negative import, no backend references, and no service mirror package.
- After code review, removed FastAPI adapter dependencies from migrated services: route/API modules now own `Request`, `Depends`, `StreamingResponse`, `HTTPException` translation, and CSV response construction.
- Added `backend/app/api/v1/response_exports.py` as the API v1 HTTP response factory for export CSV responses.
- Strengthened the architecture guard to reject any `fastapi` or `fastapi.*` import from `backend/app/services/**`.
- Updated `backend/docs/llm-db-cleanup-registry.json` allowlists for moved admin LLM files.
- Cleaned stale schema re-exports and fixed route `ErrorEnvelope` imports to use `app.api.v1.schemas.common`.

## Validation Notes

- First grouped targeted pytest command failed before collection because one story path used `app/tests/integration/test_admin_llm_catalog.py`; corrected to `tests/integration/test_admin_llm_catalog.py`.
- First full `pytest -q` failed on LLM DB cleanup allowlist still referencing the old path; allowlist migrated and the test passed.
- A later full suite exposed schema re-export assumptions after Ruff cleanup; route imports were corrected to the canonical common schema.
- Final `pytest -q`: 3112 passed, 12 skipped.
- Post-review remediation validation passed: `ruff format .`, `ruff check .`, architecture guard, targeted integration/unit suites, FastAPI leakage scan, legacy namespace scan, and `git diff --check`.
- User confirmed the full backend test suite passes after the remediation.
