# Acceptance Traceability CS-191

| AC | Evidence | Validation | Status |
|---|---|---|---|
| AC1 runtime expose `dignity_reference` | `runtime_reference.py`, repository runtime, inventaires types/systemes et `evidence/dignity-runtime-reference.md` | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | PASS |
| AC2 contrats sans dict libre | `backend/app/domain/astrology/dignities/contracts.py`; breakdowns avec `reason` explicite | `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py` | PASS |
| AC3 secte explicite | `sect_calculator.py` | `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | PASS |
| AC4 dignites essentielles runtime | `essential_dignity_calculator.py`; domicile, exaltation, detriment, fall, triplicity, term, face et peregrine sans dignite positive | `pytest -q backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py` | PASS |
| AC5 dignites accidentelles | `accidental_dignity_calculator.py`; tests maisons, mouvement, joie, priorite solaire et exclusion du Soleil | `pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py` | PASS |
| AC6 orchestration sans LLM | `planet_dignity_scoring_service.py` | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` + scans RG-118 | PASS |
| AC7 `NatalResult.dignities` sans casser l'existant | `natal_calculation.py`, `json_builder.py`, snapshots evidence | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | PASS |
| AC8 calculateurs sans DB directe | `test_astrology_runtime_reference_guard.py`; scans RG-118 zero-hit | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py` + scans RG-118 | PASS |
