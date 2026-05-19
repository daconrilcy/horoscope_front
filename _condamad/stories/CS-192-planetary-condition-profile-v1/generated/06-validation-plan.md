<!-- Plan de validation CS-192. -->

# CS-192 Validation Plan

Toutes les commandes Python doivent etre executees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Tests cibles

```powershell
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/integration/test_reference_data_migrations.py
```

## Scans

```powershell
rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" backend/app/domain/astrology/condition -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/condition -g "*.py"
rg -n "VISIBILITY_WEIGHTS|CONDITION_SCORES|CONDITION_LEVELS|astral_chart_planet_condition_profiles" backend/app backend/migrations backend/tests -g "*.py"
```

## Qualite

```powershell
ruff format .
ruff check .
```
