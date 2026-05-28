# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Runtime birth data has a canonical contract. | `BirthContextInterpretationRuntimeData`, `BirthPlaceInterpretationRuntimeData`, `BirthPrecisionInterpretationRuntimeData`; `BirthPreparedData` now carries normalized source fields; `ChartInterpretationInputBuilder` projects from `prepared_input`. | `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_contracts.py --tb=short` -> PASS. | PASS |
| AC2 | Provider payload exposes structured birth date. | `_birth_context` emits `birth_date` and `birth_time_local`. | Provider payload test + `evidence/birth-context-after.json` -> PASS. | PASS |
| AC3 | Provider payload exposes structured birth place. | `_birth_context` emits `birth_place.city`, `country`, `timezone`, `latitude`, `longitude`. | Provider payload test + CS-371 examples scan -> PASS. | PASS |
| AC4 | Provider payload represents missing precision. | `_birth_context` emits `precision.birth_time_known` and `precision.coordinates_known`; `_limits` records missing birth context keys. | `test_birth_context_marks_missing_precision_without_reconstructing_values` -> PASS. | PASS |
| AC5 | Coordinates are emitted only from canonical data. | Coordinates come only from `prepared_input.birth_lat` / `birth_lon`; no `chart_id` parsing path. | AST guard test and `evidence/reintroduction-guard.txt` -> PASS. | PASS |
| AC6 | The versioned input schema covers birth context. | `THEME_ASTRAL_INPUT_SCHEMA` declares `input_data.birth_context` required shape. | `test_theme_astral_input_schema_declares_birth_context_shape`; `evidence/input-schema-after.json` -> PASS. | PASS |
| AC7 | Bigbang handoff preserves structured birth context. | Bigbang test asserts rendered canonical payload keeps date, time, place, timezone, coordinates, and precision. | `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short` via combined targeted suite -> PASS. | PASS |
| AC8 | CS-371 provider examples expose Paris birth fields. | Free/basic/premium provider payload JSON files now expose Paris birth fields in `input_data.birth_context`. | `rg` over scoped example directory -> PASS. | PASS |
| AC9 | JSON structure docs describe provider-visible birth fields. | README and JSON structure doc now state provider-visible birth fields and keep `chart_id` technical. | Docs legacy wording guard in `evidence/reintroduction-guard.txt` -> PASS. | PASS |
| AC10 | No unnecessary personal fields are added. | No first/last name, email, phone, address, or birth_name added to provider runtime/tests/examples. | Scoped personal field guard in `evidence/reintroduction-guard.txt` -> PASS. | PASS |
| AC11 | Story evidence artifacts are persisted. | `evidence/birth-context-before.json`, `birth-context-after.json`, `input-schema-after.json`, `reintroduction-guard.txt`, `validation.txt`. | `python -B -c "from pathlib import Path; assert ..."` -> PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
