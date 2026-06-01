# Validation Plan

Commentaire global: ce plan garde les validations CS-426 limitees a l'inventaire et a la preuve d'absence de delta runtime.

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format tests\architecture\test_legacy_natal_generation_inventory_guard.py
ruff check tests\architecture\test_legacy_natal_generation_inventory_guard.py
python -B -m pytest -q tests\architecture\test_legacy_natal_generation_inventory_guard.py --tb=short
```

## Required scans

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation|basic_natal_prompt_payload" backend frontend _story_briefs _condamad
rg -n "use_case_level|variant_code|forceRefresh|shouldRefreshShortAfterBasicUpgrade" frontend/src backend/app
rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|AstroResponse_v3|EXIGENCE PREMIUM" backend/app backend/scripts
rg -n "UserNatalInterpretationModel|chart_id|variant_code|answer_type|was_fallback" backend/app/services/llm_generation/natal backend/app/infra/db/models
git status --short -- _condamad _story_briefs backend frontend
git status --short -- _condamad/run-state.json
```

## Static checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
cd ..
git diff --check
python -B -c "<runtime delta check over backend/app, frontend/src, backend/scripts, backend/app/ops/llm/bootstrap, backend/app/infra/db/models>"
```

## Skipped checks

Full backend/frontend regression suites and local app startup are not required for this inventory-only story because functional runtime code is unchanged. The compensating evidence is the targeted architecture guard, required scans, lint, `git diff --check`, and runtime delta check.
