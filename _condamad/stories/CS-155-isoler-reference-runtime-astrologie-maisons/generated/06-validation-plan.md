# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Runtime tests | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py` | `backend` | yes | pass |
| Targeted story tests | `pytest -q tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_domain_router.py app/tests/unit/test_natal_sensitivity.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_context_loader.py app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_intraday_activation_v3.py app/tests/unit/test_impulse_signal_v3.py app/tests/unit/test_natal_structural_v3.py app/tests/integration/test_intraday_refinement_integration.py` | `backend` | yes | pass |
| Lint ciblé | `ruff check <fichiers modifies>` | `backend` | yes | pass |
| Product scan | `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend` | yes | zero hit |
