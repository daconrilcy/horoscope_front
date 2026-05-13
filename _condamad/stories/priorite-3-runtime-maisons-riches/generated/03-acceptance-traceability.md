# Acceptance Traceability

| AC | Evidence code | Evidence validation | Status |
|---|---|---|---|
| Runtime houses enrichies | `HouseRuntimeData`, `build_house_runtime_data`, `build_natal_result` | `pytest -q tests/unit/domain/astrology ...` | PASS |
| Whole Sign sans interception | `_normalize_house_system`, `house_system=HouseSystemType.WHOLE_SIGN` test | `test_runtime_builder_whole_sign_enum_without_interception` | PASS |
| Quadrant avec interceptions | `resolve_contained_signs`, `resolve_intercepted_signs`, builder Placidus golden | `test_runtime_builder_golden_placidus_with_interception_and_three_signs` | PASS |
| JSON houses enrichi + `sign` legacy | `json_builder._serialize_house_runtime`, `HouseRuntimeData.sign` serialise | `test_build_chart_json_projects_rich_runtime_house`, `test_persist_and_get_audit_record` | PASS |
| Rulers source canonique | `HouseRulerResolver(sign_rulerships)` puis injection runtime sans recalcul | `test_house_ruler_resolver.py`, runtime builder tests | PASS |
| Pas de SQL runtime | Aucun fichier migration/infra touche; scan runtime SQL zero-hit | `rg -n "house_runtime\|HouseRuntimeData\|contained_signs\|intercepted_signs\|HouseStrengthRuntimeData" backend\migrations backend\app\infra` | PASS |
| Tests et golden | Tests contained/intercepted/strength/runtime builder/golden + tests service | 101 tests cibles PASS; `ruff check .` PASS | PASS_WITH_LIMITATION |
