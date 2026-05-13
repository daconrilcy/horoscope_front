# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Evaluator tests | `pytest -q tests/unit/domain/astrology/test_house_strength.py` | `backend` | yes | pass |
| Builder tests | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py` | `backend` | yes | pass |
| Lint ciblé | `ruff check <fichiers modifies>` | `backend` | yes | pass |
| Product scan | `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend` | yes | zero hit |
