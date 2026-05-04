# Validation Plan — CS-019

## Environment assumptions

- Toutes les commandes Python sont lancees apres `.\.venv\Scripts\Activate.ps1`.
- Les commandes backend sont lancees depuis `backend/` apres `Push-Location backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Garde frontiere jobs | `pytest -q app/tests/unit/test_backend_jobs_boundary.py` | `backend/` | yes | passe |
| Jobs calibration | `pytest -q app/tests/unit/test_calibration_job.py app/tests/unit/test_calibration_dataset.py` | `backend/` | yes | passe |
| Outils review/percentile | `pytest -q app/tests/unit/test_generate_review_grid.py app/tests/unit/test_percentile_calculator.py` | `backend/` | yes | passe |
| Runtime calibration | `pytest -q app/tests/unit/test_calibration_runtime.py` | `backend/` | yes | passe |
| Job baseline integration | `pytest -q app/tests/integration/test_user_baseline_refresh_job.py` | `backend/` | yes | passe |
| Guardrails transverses | `pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py` | `backend/` | yes | passe |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Namespace jobs absent | `rg --files app/jobs` | `backend/` | yes | chemin absent |
| Imports jobs interdits | `rg -n "from app\.jobs|import app\.jobs" app tests scripts -g "*.py"` | `backend/` | yes | zero hit |
| Imports scheduled_tasks bornes | `rg -n "from app\.scheduled_tasks|import app\.scheduled_tasks" app tests scripts -g "*.py"` | `backend/` | yes | hits uniquement pour entrypoints planifiables et tests directs |
| Namespace prediction absent | `rg --files app/prediction` | `backend/` | yes | chemin absent |
| Imports prediction absents | `rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"` | `backend/` | yes | zero hit |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | pas de diff inattendu |
| Lint | `ruff check .` | `backend/` | yes | passe |
| Tests backend | `pytest -q` | `backend/` | yes | passe ou limitation documentee |
| Diff check | `git diff --check` | repo root | yes | aucune erreur |

## Story validators

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md` | repo root | yes | passe |
| Story validate explain | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md` | repo root | yes | passe |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md` | repo root | yes | passe |
| Story lint strict | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md` | repo root | yes | passe |
