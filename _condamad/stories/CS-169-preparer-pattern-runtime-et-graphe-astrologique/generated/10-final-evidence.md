# Final Evidence - CS-169-preparer-pattern-runtime-et-graphe-astrologique

## Story status

- Final status: done
- Last update: 2026-05-14
- Subagents used: yes, three read-only CONDAMAD review layers.
- Review/fix iterations: 3. Iteration 1 fixed public exports, inter-chart orb rule matching, chart runtime fallback, and evidence placeholders. Iteration 2 fixed internal payload and QA cleanup issues. Iteration 3 hardened runtime/provenance contracts and re-reviewed clean.

## Implementation summary

PatternRuntimeData, PatternType et contrats de readiness graphe ajoutes.

## Story-specific AC evidence

- Implementation evidence: backend astrology runtime, interpretation, calculators, chart serializer, and tests changed for this story sequence.
- Validation evidence: pytest -q tests/unit/domain/astrology/test_pattern_runtime_contract.py.
- Expanded regression evidence: 76 targeted tests passed, including public exports, chart_result_service, orb override regression, astrology/prediction boundary, seed profile shape.
- Status: PASS.

## Files changed

- backend/app/domain/astrology/builders/aspect_runtime_builder.py
- backend/app/domain/astrology/calculators/aspects.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/domain/astrology/runtime/aspect_runtime_data.py
- backend/app/domain/astrology/runtime/aspect_modifiers.py
- backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py
- backend/app/domain/astrology/runtime/pattern_runtime_data.py
- backend/app/domain/astrology/runtime/astrological_graph_contracts.py
- backend/app/domain/astrology/runtime/__init__.py
- backend/app/domain/astrology/interpretation/aspect_strength_contracts.py
- backend/app/domain/astrology/interpretation/aspect_strength.py
- backend/app/domain/astrology/interpretation/aspect_semantic_provenance.py
- backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py
- backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py
- backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py
- backend/app/domain/astrology/interpretation/dominant_aspects.py
- backend/app/domain/astrology/interpretation/__init__.py
- backend/app/services/chart/json_builder.py
- backend tests under backend/tests/unit/domain/astrology and backend/app/tests/unit/test_chart_json_builder.py.

## Commands run

- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py tests/unit/domain/astrology/test_aspect_modifiers.py tests/unit/domain/astrology/test_aspect_interpretation_facts.py tests/unit/domain/astrology/test_aspect_semantic_provenance.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py tests/unit/domain/astrology/test_pattern_runtime_contract.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_prediction_boundary.py : PASS, 34 tests.
- .\.venv\Scripts\Activate.ps1; cd backend; ruff format . : PASS.
- .\.venv\Scripts\Activate.ps1; cd backend; ruff check . --fix; ruff check . : PASS.
- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology/test_astrology_public_exports.py tests/unit/domain/astrology/test_interchart_aspects.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py : PASS, 22 tests.
- .\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py tests/unit/domain/astrology/test_aspect_modifiers.py tests/unit/domain/astrology/test_aspect_interpretation_facts.py tests/unit/domain/astrology/test_aspect_semantic_provenance.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py tests/unit/domain/astrology/test_pattern_runtime_contract.py tests/unit/domain/astrology/test_astrology_public_exports.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspect_interpretation_seed_service.py : PASS, 76 tests.
## Guardrail scans

- rg -n "reasons\.append\(\"|AspectStrengthRuntimeData\(.*reasons=\[" app/domain/astrology -g "*.py" : PASS, zero hit.
- rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py" : PASS, zero hit.
- rg -n "OpenAI|AIEngineAdapter|chat\.completions|llm" app/domain/astrology -g "*.py" : PASS, zero hit.
- rg -n "AspectSemanticCandidate|SemanticProvenance|semantic_candidate" app/domain/prediction -g "*.py" : PASS, zero hit.
- rg -n "source_authority\s*=\s*['\"]unknown|semantic_axes.*without" app/domain/astrology -g "*.py" : PASS, zero hit.
- rg -n "\bweight\b|prediction_weight" app/domain/astrology -g "*.py" : PASS, zero hit for ambiguous weight and prediction_weight.
- rg -n "synastry.*aspect|aspect.*synastry" app docs -g "*.py" -g "*.md" : PASS, zero hit.
- rg -n "graph_nodes|graph_edges" app/domain/prediction -g "*.py" : PASS, zero hit.
- rg -n "t_square|grand_trine|yod|kite|mystic_rectangle" app -g "*.py" : expected hits only in app/domain/astrology/runtime/pattern_runtime_data.py PatternType enum.
- rg -n "DominantAspect|dominant_aspect" app/domain/prediction -g "*.py" : known pre-existing product field dominant_aspects in app/domain/prediction/public_projection.py, not a new runtime owner.

## Review findings fixed

- Public package exports now use lazy canonical exports and are covered by test_astrology_public_exports.py.
- Inter-chart aspects preserve original body codes for resolver matching and carry chart_a/chart_b separately; orb_rules targeted to sun/moon are tested.
- Chart aspect serialization builds AspectRuntimeData when missing instead of silently returning an unenriched payload.
- AspectResult excludes internal aspect_runtime from model_dump while still building runtime data for calculations.
- AspectSchoolType is normalized to its code before orb resolution, restoring natal aspects under enum inputs.
- Daily prediction QA cleanup now deletes aspect definitions and orb rules before astral_aspects, removing FK setup errors.
- Runtime contract validation now rejects blank semantic axes, non-canonical graph values, invalid modifier intensity, invalid strength scores and invalid dominant ranks.
- Evidence placeholders and open traceability markers were replaced.

## Remaining risks

- Targeted story validation passed: ruff format/check, 70 focused tests, and backend /health smoke.
- Full backend pytest still has unrelated prediction QA/regression budget failures: active_day produces 12 decision windows versus the expected max 6, and prediction non-regression snapshots are out of date.

