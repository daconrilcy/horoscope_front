# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| AST guard | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` | `backend` | yes | pass |
| Boundary scan | `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend` | yes | zero hit |
| Registry check | `rg -n "RG-095.*Frontiere domain astrology vers prediction" _condamad/stories/regression-guardrails.md` | repo root | yes | one hit |
