# CS-224 Implementation Review

## Iteration 1

Status: issues found and fixed.

Findings:

- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` ne detectait les lectures legacy que lorsque la variable locale s'appelait exactement `natal_result`. Un nouveau consommateur pouvait contourner le guardrail avec `result: NatalResult` ou une variable issue de `build_natal_result`.
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` verifiait la presence de la route et OpenAPI, mais ne prouvait pas par `TestClient` que `/v1/astrology-engine/natal/calculate` conserve les projections publiques sans exposer `chart_objects`.

Fixes:

- Le guardrail AST identifie maintenant les variables annotees `NatalResult` et les variables assignees depuis `build_natal_result`, independamment du nom local.
- Le test d'integration public appelle maintenant `/v1/astrology-engine/natal/calculate` avec un `TestClient`, un calcul natal fake, puis verifie `planet_positions`, `houses`, `astral_points`, `dignities`, `advanced_conditions`, `aspects` et l'absence de `chart_objects`.

Validation:

- `.\.venv\Scripts\Activate.ps1; ruff format backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; ruff check backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS, `4 passed, 3 deselected`.

## Iteration 2

Status: clean.

Review result:

- AC1-AC3: documentation runtime surface presente et couverte.
- AC4-AC8: guardrails legacy, `object_type`, builders specialises et seuils magiques couverts.
- AC9-AC11: projections historiques coherentes avec `chart_objects`.
- AC12-AC13: `NatalResult`, OpenAPI et route publique conservent la compatibilite sans exposer `chart_objects`.
- AC14: aucune suppression sans preuve; audit de retrait present.
- AC15: aucun changement de doctrine identifie.
- AC16: evidence finale presente.

Validation:

- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_chart_runtime_surface_documentation.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\unit\domain\astrology\test_chart_runtime_surface_projections.py backend\tests\unit\domain\astrology\test_natal_result_contract.py backend\tests\unit\domain\astrology\test_chart_object_runtime_architecture.py backend\tests\integration\astrology\test_natal_public_contract_compatibility.py`: PASS, `23 passed, 3 deselected`.

No remaining actionable implementation issue found in the fresh review.
