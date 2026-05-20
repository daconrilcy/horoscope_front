# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `dignities.sect` is the CS-197 object. | `_serialize_dignities()` unchanged for sect shape; tests assert CS-197 fields. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` passed in combined targeted command. | PASS |
| AC2 | New `sect_condition` entries use the CS-198 object. | `_serialize_planet_sect_condition()` still rejects missing/inconsistent fields. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` passed in combined targeted command. | PASS |
| AC3 | Advanced public blocks have tested present/empty serialization. | `planet_condition_profiles` serializes as a direct planet map, `planet_condition_signals` serializes as a direct planet map of signal lists, `advanced_conditions` and `dominant_planets` use the public field names from the initial brief, and empty computed maps are `{}`. Added `test_build_chart_json_serializes_empty_advanced_blocks`. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` passed in combined targeted command. | PASS |
| AC4 | Structural blocks serialize or neutralize only. | Added `_serialize_astral_points()` and `_serialize_signs_runtime()` from `NatalResult`; no-time neutralizes nested houses. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` passed in combined targeted command. | PASS |
| AC5 | `json_builder.py` has no forbidden engine imports. | No forbidden engine imports added. | Forbidden projection scan returned zero hits. | PASS |
| AC6 | Forbidden sect compatibility names are absent. | No sect legacy aliases added; scan hits are canonical runtime/reference fields, not public compatibility aliases. | Legacy alias scan classified in validation evidence. | PASS |
| AC7 | No-time modes preserve neutralization. | Existing no-time neutralization preserved; new point/sign house neutralization asserted. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` passed in combined targeted command. | PASS |
| AC8 | Old persisted payload gaps do not recalculate facts. | Added `test_get_audit_record_preserves_old_payload_gaps_without_backfill`. | `pytest -q backend/app/tests/unit/test_chart_result_service.py` passed in combined targeted command. | PASS |
| AC9 | Generated contract impact is checked or documented. | `public-json-validation.md` records dynamic chart JSON contract. | `python -c "from backend.app.main import app; app.openapi()"` passed. | PASS |
| AC10 | Required evidence artifacts mention all public blocks named by the contract. | Evidence files created under `evidence/`. | Evidence path checks and `rg` pattern scan passed. | PASS |
| AC11 | CS-200 golden cases still pass. | No domain calculation change. | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` passed in combined targeted command. | PASS |
| AC12 | No adjacent frontend/API/DB surface changes. | Diff touches backend chart projection/tests and CONDAMAD evidence/status only. | OpenAPI check passed; adjacent surface diff returned no files. | PASS |
| AC13 | Score values do not change. | Validation markdown records no-change score rows. | Evidence scan found `no-change score`. | PASS |
| AC14 | Astrology fact values do not change. | Validation markdown records no-change astrology rows. | Evidence scan found `no-change astrology`. | PASS |
