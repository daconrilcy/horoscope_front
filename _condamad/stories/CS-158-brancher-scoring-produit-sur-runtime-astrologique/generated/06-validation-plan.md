# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Product tests | `pytest -q app/tests/unit/test_domain_router.py app/tests/unit/test_natal_sensitivity.py app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_natal_structural_v3.py` | `backend` | yes | pass |
| Targeted regression | full targeted pytest bundle | `backend` | yes | pass |
| Recalc scan | `rg -n "sign_rulerships|get_sign_rulerships|HouseRulerResolver|cusp_sign.*ruler|app\\.infra" app/domain/prediction -g "*.py"` | `backend` | yes | zero hit |
