# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/api/route_exceptions.py`
- `backend/app/api/v1/routers/public/email.py`
- `backend/app/services/email/service.py`
- `backend/tests/integration/test_email_unsubscribe.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md`

## Must search

- `rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" backend frontend _condamad`
- `rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" backend/app`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/api backend/app/tests/unit/test_api_router_architecture.py backend/tests/integration/test_email_unsubscribe.py`

## Likely modified

- `backend/app/api/route_exceptions.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/decide-public-email-unsubscribe-canonicalization/route-consumption-audit.md`
- `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md`
- story generated evidence files

## Forbidden unless justified

- `backend/app/services/email/service.py`: only change if migration is explicitly approved.
- `backend/app/api/v1/routers/public/email.py`: only change if migration/deletion is explicitly approved.
- `frontend/**`: only change if a concrete consumer is found.
- `backend/migrations/**`: no schema change is in scope.
