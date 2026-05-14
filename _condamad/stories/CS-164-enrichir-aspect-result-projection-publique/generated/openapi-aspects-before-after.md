# openapi-aspects-before-after.md

Story: CS-164-enrichir-aspect-result-projection-publique
Date: 2026-05-14

Before: no canonical owner existed for this exact story surface, or the previous surface was flat/untyped.
After: AspectResult porte le runtime et json_builder projette les champs publics enrichis en conservant les champs historiques.
Validation: pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py. Expanded targeted regression: 76 tests passed.
