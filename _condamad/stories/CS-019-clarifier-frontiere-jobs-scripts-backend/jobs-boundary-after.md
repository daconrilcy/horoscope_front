# Inventaire apres — CS-019

## Fichiers `app/scheduled_tasks`

```text
backend/app/scheduled_tasks/__init__.py
backend/app/scheduled_tasks/refresh_user_baselines.py
backend/app/scheduled_tasks/generate_daily_calibration_dataset.py
backend/app/scheduled_tasks/compute_calibration_percentiles.py
```

## Namespace `app/jobs`

```text
<absent>
```

## Owner canonique calibration

```text
backend/app/services/calibration/__init__.py
backend/app/services/calibration/natal_profiles.py
backend/app/services/calibration/generate_review_grid.py
backend/app/services/calibration/generate_qa_cases.py
backend/app/services/calibration/runtime.py
backend/app/services/calibration/percentile_calculator.py
backend/app/services/calibration/validate_dataset.py
```

## Wrappers CLI

```text
backend/scripts/generate_calibration_review_grid.py
backend/scripts/generate_prediction_qa_cases.py
backend/scripts/validate_calibration_dataset.py
```

## Imports actifs autorises

```text
backend/app/tests/unit/test_calibration_job.py -> app.scheduled_tasks.generate_daily_calibration_dataset
backend/app/tests/integration/test_user_baseline_refresh_job.py -> app.scheduled_tasks.refresh_user_baselines
backend/app/scheduled_tasks/compute_calibration_percentiles.py -> app.services.calibration.*
backend/app/scheduled_tasks/generate_daily_calibration_dataset.py -> app.services.calibration.*
backend/app/tests/unit/test_*calibration*.py -> app.services.calibration.*
backend/scripts/*.py -> app.services.calibration.*
```
