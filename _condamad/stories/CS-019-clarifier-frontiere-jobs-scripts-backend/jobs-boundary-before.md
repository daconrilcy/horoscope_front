# Inventaire avant — CS-019

## Fichiers `app/jobs`

```text
backend/app/jobs/__init__.py
backend/app/jobs/refresh_user_baselines.py
backend/app/jobs/qa/__init__.py
backend/app/jobs/qa/generate_qa_cases.py
backend/app/jobs/generate_daily_calibration_dataset.py
backend/app/jobs/compute_calibration_percentiles.py
backend/app/jobs/calibration/__init__.py
backend/app/jobs/calibration/validate_dataset.py
backend/app/jobs/calibration/runtime.py
backend/app/jobs/calibration/percentile_calculator.py
backend/app/jobs/calibration/natal_profiles.py
backend/app/jobs/calibration/generate_review_grid.py
```

## Imports consommateurs constates avant migration

```text
backend/app/jobs/__init__.py -> app.jobs.calibration.natal_profiles
backend/app/jobs/qa/__init__.py -> app.jobs.calibration.natal_profiles
backend/app/jobs/qa/generate_qa_cases.py -> app.jobs.calibration.natal_profiles
backend/app/jobs/compute_calibration_percentiles.py -> app.jobs.calibration.*
backend/app/jobs/generate_daily_calibration_dataset.py -> app.jobs.calibration.*
backend/app/jobs/calibration/validate_dataset.py -> app.jobs.calibration.natal_profiles
backend/app/tests/unit/test_calibration_dataset.py -> app.jobs.calibration
backend/app/tests/unit/test_calibration_runtime.py -> app.jobs.calibration.runtime
backend/app/tests/unit/test_generate_review_grid.py -> app.jobs.calibration.generate_review_grid
backend/app/tests/unit/test_percentile_calculator.py -> app.jobs.calibration.percentile_calculator
```
