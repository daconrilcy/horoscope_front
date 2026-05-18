# Acceptance Traceability

| AC | Evidence code | Evidence validation | Status |
|---|---|---|---|
| 1 | `planet_interpretation_seed_service.py`, `reference_data_service.py`, `reference_seed_service.py` | `pytest app/tests/unit/test_reference_data_service.py -q` | PASS |
| 2 | `aspect_reference.py`, `event_detector.py`, `aspects.py`, `aspect_calculation_contracts.py` | `pytest app/tests/unit/test_astrology_reference_catalog_guard.py -q` | PASS |
| 3 | `prediction_schemas.py`, `prediction_reference_repository.py`, `context_loader.py` | targeted unit tests + daily API long tests | PASS |
| 4 | `test_astrology_reference_catalog_guard.py` | included in targeted pytest run | PASS |
| 5 | daily API and seed v2 tests | commands recorded in final evidence | PASS |
