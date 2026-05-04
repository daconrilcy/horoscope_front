# No Legacy / DRY Guardrails — CS-019

## Canonical ownership

| Responsibility | Canonical owner |
|---|---|
| Traitements applicatifs planifiables | `backend/app/scheduled_tasks/*.py` |
| Profils, runtime et calcul percentile calibration | `backend/app/services/calibration/*` |
| Outils QA/revue/validation manuels | `backend/scripts/*` wrappers vers `app.services.calibration` |

## Interdits

- Repertoire ou module `backend/app/jobs`.
- Import `app.jobs` sous quelque forme que ce soit.
- Repertoire ou module `backend/app/scheduled_tasks/calibration` ou `backend/app/scheduled_tasks/qa`.
- Re-export depuis `app.scheduled_tasks.__init__`.
- Nouveau fichier Python sous `app.scheduled_tasks` hors allowlist exacte de la garde.

## Guard executable

- `backend/app/tests/unit/test_backend_jobs_boundary.py`

## Classification des hits attendus

| Pattern | Classification | Action |
|---|---|---|
| `app.jobs` dans `test_backend_jobs_boundary.py` | test_guard_expected_hit | Chaine interdite volontairement testee par la garde. |
| `app.jobs` dans les artefacts CONDAMAD CS-019 | allowed_historical_reference | Preuve historique de la migration. |
