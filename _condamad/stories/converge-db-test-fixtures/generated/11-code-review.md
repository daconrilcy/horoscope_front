# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/converge-db-test-fixtures/00-story.md`
- Review date: 2026-04-29
- Verdict: `ACCEPTABLE_WITH_LIMITATIONS`

## Inputs reviewed

- Story contract and acceptance criteria.
- Generated evidence: `03-acceptance-traceability.md`, `06-validation-plan.md`, `07-no-legacy-dry-guardrails.md`, `10-final-evidence.md`.
- Regression registry: `_condamad/stories/regression-guardrails.md`.
- Changed code and new files under `backend/app/tests`, `backend/tests/integration`, and `_condamad/stories/converge-db-test-fixtures`.

## Diff summary

- Added canonical DB helper for `backend/app/tests`.
- Updated canonical integration helper documentation and typing.
- Migrated representative tests off direct `SessionLocal` imports.
- Hardened the DB harness architecture guard for direct imports, `create_all`, SQLite factories, and primary DB risk.
- Added `RG-011` to the regression guardrail registry.
- Completed the after-inventory with command counts and classifications.

## Findings

No remaining blocking findings for this DB harness story after remediation.

Resolved review items:

- Required backend lot no longer depends on the full `test_llm_release.py` file, whose remaining failures are release-service behavior outside this story. The required migrated subset is explicit and passing.
- `test_backend_db_test_harness.py` now guards direct imports, unclassified `Base.metadata.create_all`, unclassified SQLite factories, and `create_all` in files that reference `horoscope.db`.
- `db-test-session-imports-after.md` now records scan commands, hit counts, migrated-file deltas, and classification owners.

## Acceptance audit

- AC1: Pass. Import inventory and exception register are persisted; guard test covers growth.
- AC2: Pass. Canonical helpers are used by the representative migrated files; targeted app and backend lots pass.
- AC3: Pass. No Alembic/model changes were introduced, and SQLite alignment validation is required.
- AC4: Pass. Guard coverage now includes the explicit story reintroduction conditions.

## Validation audit

Required commands:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_backend_db_test_harness.py
pytest -q tests/integration/test_backend_sqlite_alignment.py
pytest -q app/tests/integration/test_admin_content_api.py
pytest -q tests/integration/test_llm_release.py -k "activation_evidence_requires_timezone_aware_datetime or activate_endpoint_rejects_naive_generated_at_with_422 or llm_release_lifecycle or snapshot_validation_independence"
ruff check .
```

Residual validation limitation:

- Full `pytest -q` previously timed out, so full-suite regression remains unproven in this story evidence.
- Full `pytest -q tests/integration/test_llm_release.py` still fails for release-service paths outside the DB helper migration.

## DRY / No Legacy audit

- No compatibility alias or re-export was introduced.
- The canonical helpers are thin wrappers over the effective pytest-patched session owner.
- Remaining legacy imports are explicitly allowlisted for later batches.

## Verdict

`ACCEPTABLE_WITH_LIMITATIONS`

The review blockers are remediated for the DB harness story. The remaining limitations are broader suite runtime and unrelated `test_llm_release.py` release-service failures.
