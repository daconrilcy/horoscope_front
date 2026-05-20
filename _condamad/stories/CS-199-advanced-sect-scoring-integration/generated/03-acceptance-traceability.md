# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `out_of_sect` uses `PlanetSectCondition.is_out_of_sect`. | `HayzCalculator` emits `out_of_sect` from `sect_condition.is_out_of_sect`. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`; `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py`; evidence snapshots. | PASS |
| AC2 | Hayz sect prerequisite uses `PlanetSectCondition.is_in_sect`. | `HayzCalculator` requires `sect_condition.is_in_sect` before emitting `hayz`. | `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py`. | PASS |
| AC3 | Hayz still requires non-sect hayz factors and is not reduced to `in_sect`. | `HayzCalculator` evaluates runtime-backed horizon and sign-gender hayz factors inside `advanced_conditions`. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. | PASS |
| AC4 | Missing `PlanetSectCondition` fails explicitly. | `HayzCalculator` raises `ValueError` for missing sect condition on sect-dependent advanced conditions. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. | PASS |
| AC5 | Profiles consume runtime-weighted advanced facts only and do not recalculate sect. | No service code change; guard test added for forbidden sect calculator imports. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`; forbidden scans. | PASS |
| AC6 | Dominance consumes condition/profile factors without sect recomputation. | No engine code change; guard test added for forbidden sect calculator imports. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`; forbidden scans. | PASS |
| AC7 | Interpretation adapter consumes facts only. | No adapter code change; guard test added for forbidden sect calculator imports. | `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`; forbidden scans. | PASS |
| AC8 | Day/night score outputs stay stable where prior logic was equivalent. | Equivalent outputs kept; source-of-truth changed to `PlanetSectCondition`. | Targeted tests; `python -m json.tool` on before/after snapshots. | PASS |
| AC9 | Score deltas are documented. | Validation evidence records `score delta` as zero for equivalent cases. | `rg -n "score delta" _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-validation.md`. | PASS |
| AC10 | Forbidden sect patterns remain absent. | No local sect constants, downstream calculators or legacy aliases introduced. | `rg` scans recorded in `advanced-sect-validation.md`. | PASS |
| AC11 | Public JSON shape remains CS-197/CS-198-compatible. | `json_builder.py` unchanged; projection tests kept passing. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`; snapshots mark public shape unchanged. | PASS |
| AC12 | Persistent evidence files are complete. | Evidence directory contains before/audit/after/validation artifacts. | `python -m json.tool` on snapshots; `rg` evidence scan. | PASS |

Status values used for CS-199 closure: `PENDING`, `PASS`, `FAIL`, `BLOCKED`.
