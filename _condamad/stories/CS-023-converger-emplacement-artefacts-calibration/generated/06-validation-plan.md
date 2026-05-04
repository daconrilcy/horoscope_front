# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Artifact location guard | `pytest -q app/tests/unit/test_calibration_artifact_locations.py` | `backend` | yes | pass |
| Calibration regressions | `pytest -q app/tests/unit/test_calibration_job.py app/tests/unit/test_calibration_runtime.py app/tests/unit/test_v3_calibration.py` | `backend` | yes | pass |
| Path scan | `rg -n 'backend/docs/calibration|docs/calibration|percentile_report|review-grid' app tests scripts ..\\docs` | `backend` | yes | only canonical/guard hits |
| Full backend regression | `pytest -q` | `backend` | yes | pass |
