# Execution Brief — CS-019

## Objectif

Clarifier puis durcir la frontiere entre traitements planifiables et scripts backend: `backend/app/scheduled_tasks` devient l'unique owner des traitements applicatifs planifiables, `backend/scripts` reste le point d'entree CLI manuel, et `app.jobs` est supprime.

## Bornes

- Modifier uniquement la surface traitements planifiables/calibration, ses tests directs, les wrappers scripts et les preuves CONDAMAD.
- Ne pas modifier API, frontend, schema DB, migrations ou contrats OpenAPI.
- Ne pas conserver de shim, alias, re-export ou fallback `app.jobs`.

## Definition de termine

- `app.scheduled_tasks` contient uniquement `compute_calibration_percentiles.py`, `generate_daily_calibration_dataset.py`, `refresh_user_baselines.py` et un `__init__.py` neutre.
- `app.jobs` est absent physiquement et aucun import actif ne le cible.
- Les imports non-job ciblent `app.services.calibration`.
- `test_backend_jobs_boundary.py` bloque la reintroduction de `app.jobs` et de helpers non planifiables sous `app.scheduled_tasks`.
