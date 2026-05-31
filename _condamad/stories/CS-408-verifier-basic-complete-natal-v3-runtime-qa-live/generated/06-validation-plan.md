# Validation Plan

## Backend

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff check tests\integration\test_natal_basic_complete_v3_runtime.py tests\unit\test_natal_interpretation_service_v3_schema_guard.py tests\unit\test_natal_chart_long_quota_on_acceptance.py tests\integration\test_natal_interpretation_rejected_public_boundary.py
python -B -m pytest --long -q tests\integration\test_natal_basic_complete_v3_runtime.py tests\unit\test_natal_interpretation_service_v3_schema_guard.py tests\unit\test_natal_chart_long_quota_on_acceptance.py tests\integration\test_natal_interpretation_rejected_public_boundary.py --tb=short
python -B -c "from app.main import app; assert app.routes; assert app.openapi(); print('routes_openapi_ok')"
rg -n "natal_interpretation_short|natal/interpretation/free|schema_version.*v2" app tests
Pop-Location
```

Expected: lint and pytest pass; scans may return classified legacy/test/catalog hits only.

## Frontend

```powershell
pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard
pnpm --dir frontend lint
pnpm --dir frontend build
rg -n "visibility_expression|audit_input|interpretive_signal_ids|projection_version|ni-evidence-tags|ni-projections" frontend\src
```

Expected: tests, lint and build pass; scans may return classified API/CSS/test guard hits only.

## Story evidence

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-408-verifier-basic-complete-natal-v3-runtime-qa-live\00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-408-verifier-basic-complete-natal-v3-runtime-qa-live\00-story.md
python -B -c "from pathlib import Path; assert Path('_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md').exists(); assert Path('_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/qa-live-report.md').exists()"
```
