# Code Review - CS-166-calculer-aspects-dominants-et-socle-synastrie

Verdict: CLEAN

## Review/fix iteration summary

- Iteration 1 accepted findings: broken public exports, inter-chart orb rule matching, CS-164 silent non-runtime fallback, incomplete evidence.
- Fixes applied and validated with targeted tests and ruff.
- Iteration 2 accepted findings: internal `aspect_runtime` payload exposure risk, AspectSchoolType enum normalization bug, and daily prediction QA FK cleanup gap.
- Iteration 3 accepted findings: permissive provenance/modifier/strength/dominant/pattern runtime contracts and missing French module docstring on modified calculator exports.
- Iteration 3 result: no remaining blocking finding identified in main session.

## Validation evidence

- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py tests/unit/domain/astrology/test_aspect_modifiers.py tests/unit/domain/astrology/test_aspect_interpretation_facts.py tests/unit/domain/astrology/test_aspect_semantic_provenance.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py tests/unit/domain/astrology/test_pattern_runtime_contract.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_prediction_boundary.py : PASS, 34 tests.
- .\.venv\Scripts\Activate.ps1; cd backend; ruff format . : PASS.
- .\.venv\Scripts\Activate.ps1; cd backend; ruff check . --fix; ruff check . : PASS.
- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology/test_astrology_public_exports.py tests/unit/domain/astrology/test_interchart_aspects.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py : PASS, 22 tests.
- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py tests/unit/domain/astrology/test_aspect_modifiers.py tests/unit/domain/astrology/test_aspect_interpretation_facts.py tests/unit/domain/astrology/test_aspect_semantic_provenance.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py tests/unit/domain/astrology/test_pattern_runtime_contract.py tests/unit/domain/astrology/test_astrology_public_exports.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspect_interpretation_seed_service.py : PASS, 76 tests.
- .\.venv\Scripts\Activate.ps1; cd backend; ruff check app/domain/astrology tests/unit/domain/astrology app/tests/unit/test_aspects_calculator.py app/tests/unit/test_chart_json_builder.py app/tests/integration/test_daily_prediction_qa.py : PASS.
- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology app/tests/unit/test_aspects_calculator.py app/tests/unit/test_natal_calculation_service.py::test_calculate_natal_returns_major_aspects_with_extended_reference_planets app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py app/tests/integration/test_daily_prediction_qa.py::test_legacy_ruleset_1_0_0_still_supported : PASS, 70 tests.
## Residual classification

- app/domain/prediction/public_projection.py contains a pre-existing product field dominant_aspects. It is not a DominantAspect runtime owner and was not changed.
- PatternType enum intentionally contains t_square, grand_trine, yod, kite, mystic_rectangle under the canonical runtime owner.
