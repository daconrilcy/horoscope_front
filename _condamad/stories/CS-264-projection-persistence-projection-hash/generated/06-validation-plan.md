# Validation Plan

## Targeted Checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\unit\projections tests\integration\test_projection_persistence_schema.py tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py --tb=short
```

## Architecture Guard Checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q app\tests\unit\test_backend_db_test_harness.py::test_create_all_usage_stays_classified_outside_primary_horoscope_db app\tests\unit\test_backend_db_test_harness.py::test_sqlite_secondary_factories_stay_classified app\tests\unit\test_backend_services_structure_guard.py::test_services_root_matches_story_70_23_allowlist tests\unit\projections tests\integration\test_projection_persistence_schema.py tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py --tb=short
```

## Early Guard Scans

```powershell
rg -n "fake projection|synthetic projection|placeholder projection|fallback.*projection|shim|compat" backend\app\domain\astrology\projections backend\app\infra\db\models\projection_persistence.py backend\app\infra\db\repositories\projection_repository.py backend\app\services\projection_persistence_service.py backend\tests\unit\projections backend\tests\integration\test_projection_persistence_schema.py
rg -n "include_router\(.*projection|persisted_projections|projection_persistence" backend\app\api backend\app\main.py -g "*.py"
rg -n "projection_hash|narrative_answer_audit_v1|AINarrativePersistedProjectionIdentity" backend\app\domain\astrology\interpretation backend\tests\unit\domain\astrology\interpretation docs\architecture\narrative-answer-audit-v1-contract.md
git diff --check -- <story paths>
```

Expected:

- First scan returns exit code 1 with no matches for fake/synthetic/fallback patterns.
- Second scan returns exit code 1 with no public API route matches.
- Third scan returns matches proving narrative audit linkage.
- `git diff --check` returns exit code 0; line-ending warnings are acceptable.

## Lint / Static Checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format <changed python paths>
ruff check .
python -B -m alembic heads
python -B -c "from app.main import app; routes=[getattr(r,'path','') for r in app.routes]; assert not any('projection' in p for p in routes); spec=app.openapi(); assert 'persisted_projections' not in str(spec); assert 'projection_persistence' not in str(spec)"
```

## Full Regression Check

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q --tb=short
```

## Skipped Commands

- Frontend lint/tests/browser checks are skipped because the story has no frontend scope and no frontend files changed.
