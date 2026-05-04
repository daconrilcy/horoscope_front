# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `backend/docs/entitlements-canonical-platform.md`
- `backend/docs/ownership-index.md`
- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`
- `backend/app/tests/unit/test_backend_docs_ownership.py`
- `_condamad/stories/regression-guardrails.md`

## Required searches before editing

```bash
rg -n "entitlements-canonical-platform|Document status: historical-note" backend docs _condamad
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/docs docs/architecture backend/app/tests/unit/test_entitlement_docs_runtime_parity.py
```

## Likely modified files

- `docs/architecture/entitlements-canonical-platform.md`
- `backend/docs/ownership-index.md`
- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`

## Forbidden or high-risk files

- `backend/app/api/**`
- `backend/app/services/**`
- `backend/app/infra/db/**`
- `frontend/src/**`
- `backend/docs/entitlements-canonical-platform.md` after the move.
