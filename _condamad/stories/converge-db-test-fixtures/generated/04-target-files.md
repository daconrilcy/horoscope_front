# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/conftest.py`
- `backend/tests/conftest.py`
- `backend/app/tests/integration/conftest.py`
- `backend/tests/integration/app_db.py`
- `backend/tests/integration/test_backend_sqlite_alignment.py`
- `backend/tests/integration/test_llm_release.py`
- `backend/app/tests/integration/test_admin_content_api.py`

## Must search

- `rg -n "from app\.infra\.db\.session import .*\b(SessionLocal|engine)\b|db_session_module\.SessionLocal" backend/app/tests backend/tests -g "*.py"`
- `rg -n "Base\.metadata\.create_all" backend/app/tests backend/tests -g "*.py"`

## Likely modified

- `backend/tests/integration/app_db.py`
- `backend/app/tests/helpers/db_session.py`
- `backend/tests/integration/test_llm_release.py`
- `backend/app/tests/integration/test_admin_content_api.py`
- `backend/app/tests/unit/test_backend_db_test_harness.py`
- `_condamad/stories/converge-db-test-fixtures/*.md`
- `_condamad/stories/converge-db-test-fixtures/generated/*.md`

## Forbidden unless justified

- `backend/alembic/**`
- `backend/app/infra/db/models/**`
- `frontend/**`
- `requirements.txt`
