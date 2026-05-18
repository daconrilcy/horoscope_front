# Acceptance Traceability

| AC | Evidence code | Evidence validation | Status |
|---|---|---|---|
| 1 | `aspect_reference.py`, `event_detector.py`, `aspect_runtime_builder.py` | `pytest app/tests/regression/test_engine_non_regression.py -q --long` | PASS |
| 2 | `public_projection.py`, `public_predictions.py`, `predictions.py`, `qa.py` | `pytest app/tests/integration/test_daily_prediction_api.py -q --long` et `pytest app/tests/integration/test_daily_prediction_qa.py -q --long` | PASS |
| 3 | `public_projection.py` | Tests API quotidiennes/QA avec doubles sans `reference_version_id` inclus dans les validations ciblées | PASS |
| 4 | `test_natal_structural_v3.py` | `pytest app/tests/unit/test_natal_structural_v3.py -q` | PASS |
| 5 | Suite longue ciblée et complète | `ruff check .` et `pytest -q --long` | PASS |
