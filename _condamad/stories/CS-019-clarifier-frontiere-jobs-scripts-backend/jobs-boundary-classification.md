# Classification frontiere traitements planifiables — CS-019

| Fichier initial | Classification | Owner final | Decision |
|---|---|---|---|
| `backend/app/jobs/__init__.py` | package marker ambigu | supprime | Le package `app.jobs` disparait pour eviter un owner generique a 3 fichiers. |
| `backend/app/jobs/refresh_user_baselines.py` | traitement planifiable | `backend/app/scheduled_tasks/refresh_user_baselines.py` | Deplace vers l'owner explicite des taches planifiables. |
| `backend/app/jobs/generate_daily_calibration_dataset.py` | traitement planifiable | `backend/app/scheduled_tasks/generate_daily_calibration_dataset.py` | Deplace vers l'owner explicite des taches planifiables. |
| `backend/app/jobs/compute_calibration_percentiles.py` | traitement planifiable | `backend/app/scheduled_tasks/compute_calibration_percentiles.py` | Deplace vers l'owner explicite des taches planifiables. |
| `backend/app/jobs/calibration/percentile_calculator.py` | service reusable | `backend/app/services/calibration/percentile_calculator.py` | Deplace, ancien chemin supprime. |
| `backend/app/jobs/calibration/natal_profiles.py` | donnees/runtime calibration reutilisables | `backend/app/services/calibration/natal_profiles.py` | Deplace, ancien chemin supprime. |
| `backend/app/jobs/calibration/runtime.py` | service runtime reutilisable | `backend/app/services/calibration/runtime.py` | Deplace, ancien chemin supprime. |
| `backend/app/jobs/calibration/validate_dataset.py` | outil manuel de validation | `backend/app/services/calibration/validate_dataset.py` + `backend/scripts/validate_calibration_dataset.py` | Deplace, wrapper CLI ajoute. |
| `backend/app/jobs/calibration/generate_review_grid.py` | outil manuel de revue | `backend/app/services/calibration/generate_review_grid.py` + `backend/scripts/generate_calibration_review_grid.py` | Deplace, wrapper CLI ajoute. |
| `backend/app/jobs/qa/generate_qa_cases.py` | outil manuel QA | `backend/app/services/calibration/generate_qa_cases.py` + `backend/scripts/generate_prediction_qa_cases.py` | Deplace, wrapper CLI ajoute. |
| `backend/app/jobs/calibration/__init__.py` | package legacy | supprime | Supprime sans re-export. |
| `backend/app/jobs/qa/__init__.py` | package legacy | supprime | Supprime sans re-export. |
