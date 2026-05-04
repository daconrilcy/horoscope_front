# Final Evidence — CS-019

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Review verdict: CLEAN
- Story key: CS-019-clarifier-frontiere-jobs-scripts-backend
- Source story: `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md`
- Capsule path: `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: CS-019 et registres CONDAMAD deja modifies/non suivis.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Mis a jour pour la cible stricte `app.scheduled_tasks`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Mis a jour. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC7 couverts. |
| `generated/04-target-files.md` | yes | yes | PASS | Surface inspectee et modifiee. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Scans `app jobs` et `scheduled_tasks` ajoutes. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | `app.jobs` interdit. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Evidence complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `jobs-boundary-classification.md`, `jobs-boundary-before.md`, `jobs-boundary-after.md`. | `pytest -q app/tests/unit/test_backend_jobs_boundary.py` PASS. | PASS | Classification initiale et cible finale persistantes. |
| AC2 | `backend/app/jobs/**` supprime; `backend/app/scheduled_tasks/__init__.py` ajoute. | `pytest -q app/tests/unit/test_backend_jobs_boundary.py` PASS; `rg --files app/jobs` chemin absent. | PASS | Aucun marker de compatibilite `app.jobs`. |
| AC3 | Modules percentile/runtime/profils sous `backend/app/services/calibration`. | `pytest -q app/tests/unit/test_percentile_calculator.py` PASS; scans anciens imports zero hit actif. | PASS | Ancien package supprime. |
| AC4 | QA, validate dataset et review grid sous `app.services.calibration`, wrappers `backend/scripts`. | `pytest -q app/tests/unit/test_generate_review_grid.py` PASS; scans anciens imports zero hit actif. | PASS | Aucun owner manuel sous `scheduled_tasks`. |
| AC5 | Entry points planifiables sous `backend/app/scheduled_tasks`. | `pytest -q app/tests/unit/test_calibration_job.py`; `pytest -q app/tests/integration/test_user_baseline_refresh_job.py` PASS. | PASS | Comportement observable preserve par tests existants. |
| AC6 | `backend/app/tests/unit/test_backend_jobs_boundary.py` bloque `app.jobs` et les imports non bornes. | Test garde PASS. | PASS | Garde paths/imports incluant `backend/scripts`. |
| AC7 | Aucun `app.prediction` recree; guardrails topology/DB/helper passes. | `pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py` PASS; scans prediction zero/absent. | PASS | RG-010, RG-011, RG-013, RG-038 respectes. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/scheduled_tasks/__init__.py` | added | Marker neutre des traitements planifiables. | AC2, AC6 |
| `backend/app/scheduled_tasks/compute_calibration_percentiles.py` | moved | Entry point planifiable percentile. | AC5 |
| `backend/app/scheduled_tasks/generate_daily_calibration_dataset.py` | moved | Entry point planifiable dataset. | AC5 |
| `backend/app/scheduled_tasks/refresh_user_baselines.py` | moved | Entry point planifiable baseline. | AC5 |
| `backend/app/services/calibration/*` | added/moved | Owner canonique calibration/QA/revue. | AC3, AC4 |
| `backend/scripts/generate_calibration_review_grid.py` | added | Wrapper CLI grille revue. | AC4 |
| `backend/scripts/generate_prediction_qa_cases.py` | added | Wrapper CLI cas QA. | AC4 |
| `backend/scripts/validate_calibration_dataset.py` | added | Wrapper CLI validation dataset. | AC4 |
| `backend/app/tests/unit/test_backend_jobs_boundary.py` | added/modified | Garde anti-reintroduction `app.jobs`. | AC1, AC2, AC6 |
| Tests calibration/baseline | modified | Imports owners canoniques. | AC3, AC4, AC5 |
| Artefacts CONDAMAD CS-019 | added/modified | Evidence, classification, snapshots. | AC1-AC7 |

## Files deleted

- `backend/app/jobs/__init__.py`
- `backend/app/jobs/compute_calibration_percentiles.py`
- `backend/app/jobs/generate_daily_calibration_dataset.py`
- `backend/app/jobs/refresh_user_baselines.py`
- `backend/app/jobs/calibration/__init__.py`
- `backend/app/jobs/calibration/generate_review_grid.py`
- `backend/app/jobs/calibration/natal_profiles.py`
- `backend/app/jobs/calibration/percentile_calculator.py`
- `backend/app/jobs/calibration/runtime.py`
- `backend/app/jobs/calibration/validate_dataset.py`
- `backend/app/jobs/qa/__init__.py`
- `backend/app/jobs/qa/generate_qa_cases.py`

## Tests added or updated

- Added/updated: `backend/app/tests/unit/test_backend_jobs_boundary.py`.
- Updated: `test_calibration_job.py`, `test_calibration_dataset.py`, `test_calibration_runtime.py`, `test_generate_review_grid.py`, `test_percentile_calculator.py`, `test_user_baseline_refresh_job.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `ruff format .` | `backend/` | PASS | 0 | Format global applique/verifie. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_backend_jobs_boundary.py` | `backend/` | PASS | 0 | Garde frontiere stricte. |
| `pytest -q app/tests/unit/test_calibration_job.py app/tests/unit/test_calibration_dataset.py` | `backend/` | PASS | 0 | Jobs calibration et dataset. |
| `pytest -q app/tests/unit/test_generate_review_grid.py app/tests/unit/test_percentile_calculator.py` | `backend/` | PASS | 0 | Outils review et service percentile. |
| `pytest -q app/tests/unit/test_calibration_runtime.py` | `backend/` | PASS | 0 | Runtime calibration. |
| `pytest -q app/tests/integration/test_user_baseline_refresh_job.py` | `backend/` | PASS | 0 | Traitement baseline. |
| `pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py` | `backend/` | PASS | 0 | Guardrails transverses. |
| `pytest -q tests/unit/test_backend_structure_guard.py app/tests/unit/test_backend_jobs_boundary.py` | `backend/` | PASS | 0 | 6 passed; `scheduled_tasks` classe et `jobs` retire des dossiers approuves. |
| `rg --files app/jobs` | `backend/` | PASS | 2 | Chemin absent. |
| `rg -n "from app\.jobs\|import app\.jobs" app tests scripts -g "*.py"` | `backend/` | PASS | 1 | Zero hit actif. |
| `rg -n "from app\.scheduled_tasks\|import app\.scheduled_tasks" app tests scripts -g "*.py"` | `backend/` | PASS | 0 | Hits bornes aux tests directs des entrypoints planifiables. |
| `rg --files app/prediction` | `backend/` | PASS | 2 | Chemin absent, conforme a RG-038. |
| `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend/` | PASS | 1 | Zero hit. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-019-clarifier-frontiere-jobs-scripts-backend\00-story.md` | repo root | PASS | 0 | Story validation PASS. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-019-clarifier-frontiere-jobs-scripts-backend\00-story.md` | repo root | PASS | 0 | Story lint PASS. |
| `pytest -q` | `backend/` | PASS | 0 | 3598 passed, 12 skipped in 625.29s apres rename strict. |
| `git diff --check` | repo root | PASS | 0 | Aucun whitespace/conflict marker; warnings CRLF seulement. |

## Commands skipped or blocked

- Aucun.

## DRY / No Legacy evidence

- `backend/app/jobs` supprime physiquement.
- Aucun re-export, alias, wrapper ou fallback ne conserve `app.jobs`.
- Les traitements planifiables ont un owner explicite: `app.scheduled_tasks`.
- Les helpers reutilisables restent sous `app.services.calibration`.

## Diff review

- `git diff --stat`: scope limite a CS-019, scheduled tasks/services calibration, tests directs, wrappers scripts et artefacts CONDAMAD.
- `git diff --check`: PASS, warnings CRLF non bloquants.

## Final worktree status

- `git status --short`: modifications attendues CS-019, suppressions `app/jobs`, nouveaux fichiers `app/scheduled_tasks`, `app/services/calibration`, wrappers `backend/scripts`, garde `test_backend_jobs_boundary.py`, capsule CS-019 et registres CONDAMAD.

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Verifier que `app.scheduled_tasks` est le bon nom durable pour les traitements planifiables.
- Verifier que l'absence totale de `app.jobs` reste l'invariant souhaite.
