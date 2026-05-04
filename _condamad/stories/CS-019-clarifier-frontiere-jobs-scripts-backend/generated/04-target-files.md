# Target Files — CS-019

## Lus avant modification

- `backend/app/jobs/__init__.py`
- `backend/app/jobs/compute_calibration_percentiles.py`
- `backend/app/jobs/generate_daily_calibration_dataset.py`
- `backend/app/jobs/refresh_user_baselines.py`
- `backend/app/jobs/calibration/*`
- `backend/app/jobs/qa/*`
- `backend/app/tests/unit/test_calibration_job.py`
- `backend/app/tests/unit/test_calibration_dataset.py`
- `backend/app/tests/unit/test_generate_review_grid.py`
- `backend/app/tests/unit/test_percentile_calculator.py`
- `backend/app/tests/unit/test_calibration_runtime.py`
- `backend/app/tests/integration/test_user_baseline_refresh_job.py`
- `_condamad/stories/regression-guardrails.md`

## Modifies

- `backend/app/jobs/__init__.py`
- `backend/app/jobs/compute_calibration_percentiles.py`
- `backend/app/jobs/generate_daily_calibration_dataset.py`
- `backend/app/services/calibration/*`
- `backend/scripts/generate_calibration_review_grid.py`
- `backend/scripts/generate_prediction_qa_cases.py`
- `backend/scripts/validate_calibration_dataset.py`
- `backend/app/tests/unit/test_backend_jobs_boundary.py`
- tests calibration ciblant les nouveaux owners
- artefacts CONDAMAD CS-019

## Supprimes

- `backend/app/jobs/calibration/*`
- `backend/app/jobs/qa/*`

## Scans requis

- `rg -n "from app\.jobs\.calibration\.(percentile_calculator|natal_profiles|runtime)" app tests`
- `rg -n "from app\.jobs\.qa\.generate_qa_cases" app tests`
- `rg -n "from app\.jobs\.calibration import (generate_review_grid|validate_dataset)" app tests`
- `rg --files app/prediction`
- `rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"`
