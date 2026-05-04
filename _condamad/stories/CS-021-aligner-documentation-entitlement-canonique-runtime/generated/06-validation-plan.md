# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Doc/runtime parity | `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py` | `backend` | yes | pass |
| Ops entitlement API | `pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | `backend` | yes | pass |
| Public entitlement contract | `pytest -q app/tests/integration/test_entitlements_me_contract.py` | `backend` | yes | pass |
| Inverse API imports | `rg -n 'from app\\.api|import app\\.api' app/services app/domain app/infra app/core -g '*.py'` | `backend` | yes | zero hits |
| Full backend regression | `pytest -q` | `backend` | yes | pass |
