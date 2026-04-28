# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/api/v1/routers/public/email.py`
- `backend/app/services/email/service.py`
- `backend/app/services/email/public_email.py`
- `backend/tests/integration/test_email_unsubscribe.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`

## Must search

- `rg -n "app/api/v1/routers/public/email.py" _condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- `rg -n "unsubscribe|email_unsubscribed|marketing_types|get_db_session|db\\." backend/app backend/tests`
- `rg -n "mark.*unsub|unsubscribed|unsubscribe" backend/app/services backend/tests`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/api/v1/routers/public/email.py backend/app/services/email backend/tests/integration/test_email_unsubscribe.py`

## Likely modified

- `backend/app/api/v1/routers/public/email.py`
- `backend/app/services/email/service.py`
- `backend/tests/integration/test_email_unsubscribe.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- `_condamad/stories/reduce-api-sql-boundary-debt-public-email/**`

## Forbidden unless justified

- `backend/app/api/route_exceptions.py`
- `backend/migrations/**`
- `frontend/**`
- `backend/app/infra/db/models/**`
- `backend/pyproject.toml`

## Deletion candidates

- No file deletion expected.
