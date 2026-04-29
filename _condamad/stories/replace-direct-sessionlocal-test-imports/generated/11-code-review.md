# CONDAMAD Code Review

## Review Target

- Story: `_condamad/stories/replace-direct-sessionlocal-test-imports/00-story.md`
- Verdict: `CLEAN`
- Review date: 2026-04-29

## Inputs Reviewed

- Story acceptance criteria, non-goals, validation plan, and guardrails.
- `_condamad/stories/regression-guardrails.md`, especially `RG-010` and `RG-011`.
- Final evidence and after-snapshot artifacts for the DB session migration.
- Current worktree diff for the DB harness migration, `dev_seed`, startup/CLI/email session injection points, migrated tests, and review artifact.
- Fresh reviewer command output from the current worktree.

## Diff Summary

The implementation routes app-test DB ownership through
`backend/app/tests/helpers/db_session.py`, removes process-wide mutation of
`app.infra.db.session.SessionLocal` / `engine` from `backend/app/tests/conftest.py`,
keeps `backend/tests/integration/app_db.py` as the canonical `backend/tests`
helper, and hardens the DB harness guard against indirect `db_session_module`
access to both `SessionLocal` and `engine`.

The follow-up cleanup also removes backend-test string patch targets for
`app.infra.db.session.SessionLocal` and `app.infra.db.session.engine`.
Production code that opens sessions internally now exposes local private
injection points where needed, so tests patch the consumer module instead of the
global DB session module.

## Findings

No actionable findings.

The previous blocking finding against `backend/app/tests/integration/test_auth_api.py`
remains resolved. The later residual notes against `test_dev_seed.py`,
`test_canonical_llm_bootstrap.py`,
`test_check_canonical_entitlement_db_consistency_cli.py`, and
`test_email_idempotence.py` are also resolved: backend tests no longer contain
string references to `app.infra.db.session.SessionLocal` or
`app.infra.db.session.engine`.

## Acceptance Audit

- AC1: PASS. Before/after import snapshots exist, and the DB session allowlist has no active direct-import entries.
- AC2: PASS. App-test consumers route through `app.tests.helpers.db_session`; `backend/tests` consumers route through `tests.integration.app_db`.
- AC3: PASS. SQLite alignment still passes via `tests/integration/test_backend_sqlite_alignment.py`.
- AC4: PASS. No global `db_session_module.SessionLocal =` or `db_session_module.engine =` redirection remains.
- AC5: PASS. Batch evidence exists and full collection passes.

Applicable guardrails:

- `RG-010`: PASS via full pytest collection.
- `RG-011`: PASS via DB harness guard, zero-hit direct import scans, zero-hit global redirection scan, and zero-hit string patch target scan.

## Validation Audit

Reviewer commands run from `C:\dev\horoscope_front` with the venv activated before Python commands:

- `cd backend; ruff format --check .`: PASS, 1242 files already formatted.
- `cd backend; ruff check .`: PASS.
- `cd backend; pytest -q app/tests/unit/test_backend_db_test_harness.py tests/integration/test_backend_sqlite_alignment.py app/tests/integration/test_dev_seed.py app/tests/integration/test_auth_api.py tests/unit/test_canonical_llm_bootstrap.py app/tests/unit/test_check_canonical_entitlement_db_consistency_cli.py app/tests/unit/test_email_idempotence.py`: PASS, 35 passed.
- `cd backend; pytest -q tests/unit/prediction/test_llm_narrator.py -W error::DeprecationWarning`: PASS, 8 passed.
- `cd backend; pytest --collect-only -q --ignore=.tmp-pytest`: PASS, 3488 tests collected.
- `cd backend; pytest -q`: PASS, 3476 passed, 12 skipped.
- `cd backend; rg -n "from app\.infra\.db\.session import (SessionLocal|engine)" app/tests tests -g "*.py"`: PASS, zero hits.
- `cd backend; rg -n "db_session_module\.(SessionLocal|engine) =" app/tests tests -g "*.py"`: PASS, zero hits.
- `cd backend; rg -n "app\.infra\.db\.session\.(SessionLocal|engine)" app/tests tests -g "*.py"`: PASS, zero hits.
- `cd backend; python -c "from app.main import app; print(app.title)"`: PASS, `horoscope-backend`.
- `git diff --check`: PASS.

The previous `LLMNarrator` deprecation warnings are now captured as explicit
test expectations in `backend/tests/unit/prediction/test_llm_narrator.py`.

## DRY / No Legacy Audit

- No compatibility wrapper named `SessionLocal` was added.
- No direct test import of `SessionLocal` or `engine` from `app.infra.db.session` remains.
- No string patch target for `app.infra.db.session.SessionLocal` or `app.infra.db.session.engine` remains in backend tests.
- No global DB session redirection remains in `backend/app/tests/conftest.py`.
- `backend/app/tests/integration/test_dev_seed.py` uses the app-test DB helper through a private `dev_seed` injection point.
- `backend/tests/unit/test_canonical_llm_bootstrap.py` uses a private startup DB session injection point in `app.main`.
- `backend/app/tests/unit/test_check_canonical_entitlement_db_consistency_cli.py` patches the CLI's private session opener.
- `backend/app/tests/unit/test_email_idempotence.py` patches the email service module symbol instead of the global DB session module.
- The only active `db_session_module.SessionLocal()` / `engine` access found by broad scan is inside canonical helper `backend/tests/integration/app_db.py`.
- The DB harness guard now also detects forbidden string patch targets for the production DB session and engine.

## Residual Risks

- The migration is broad and mechanical, but the full backend suite and targeted DB harness checks pass.
- No warning summary remains in the full backend suite after the legacy narrator tests capture the expected deprecation warning.

## Verdict

`CLEAN`
