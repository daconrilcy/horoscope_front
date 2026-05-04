# Acceptance Traceability — CS-019

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | L'inventaire initial `app/jobs` a une classification par fichier et l'inventaire final cible `app/scheduled_tasks`. | Mettre a jour `jobs-boundary-classification.md`, `jobs-boundary-before.md`, `jobs-boundary-after.md`. | `pytest -q app/tests/unit/test_backend_jobs_boundary.py`; artefacts persistants. | PASS |
| AC2 | Le namespace `backend/app/jobs` est supprime, sans marker de compatibilite. | Supprimer `backend/app/jobs/**`; ajouter `backend/app/scheduled_tasks/__init__.py`. | `pytest -q app/tests/unit/test_backend_jobs_boundary.py`; `rg --files app/jobs` doit echouer chemin absent. | PASS |
| AC3 | Les services calibration/percentile ne sont plus sous `app.jobs`. | Deplacer percentile, runtime et profils vers `app.services.calibration`; mettre a jour tests. | `pytest -q app/tests/unit/test_percentile_calculator.py`; scans interdits. | PASS |
| AC4 | Les outils QA/revue manuels ne sont plus owners sous `app.jobs`. | Deplacer QA, validate_dataset et generate_review_grid vers `app.services.calibration`; ajouter wrappers `backend/scripts`. | `pytest -q app/tests/unit/test_generate_review_grid.py`; scans interdits. | PASS |
| AC5 | Les traitements planifiables gardent leur comportement observable sous `app.scheduled_tasks`. | Deplacer les trois entrypoints planifiables vers `app.scheduled_tasks`; mettre a jour imports/patchs tests. | `pytest -q app/tests/unit/test_calibration_job.py`; `pytest -q app/tests/integration/test_user_baseline_refresh_job.py`. | PASS |
| AC6 | Une garde bloque le retour de logique non planifiable et de `app.jobs`. | Mettre a jour `backend/app/tests/unit/test_backend_jobs_boundary.py`. | `pytest -q app/tests/unit/test_backend_jobs_boundary.py`. | PASS |
| AC7 | Les invariants transverses restent respectes. | `scheduled_tasks` est classe et `jobs` retire de la structure approuvee. | `pytest -q tests/unit/test_backend_structure_guard.py app/tests/unit/test_backend_jobs_boundary.py`; suite globale. | PASS |
