# Validation Plan

Toutes les commandes Python doivent etre lancees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

Commandes prevues:

- `cd backend; ruff format app/domain/astrology app/services/chart/json_builder.py app/tests/unit/domain/astrology app/tests/unit/test_chart_json_builder.py app/tests/unit/test_house_ruler_resolver.py`
- `cd backend; ruff check app/domain/astrology app/services/chart/json_builder.py app/tests/unit/domain/astrology app/tests/unit/test_chart_json_builder.py app/tests/unit/test_house_ruler_resolver.py`
- `cd backend; pytest -q app/tests/unit/domain/astrology app/tests/unit/test_chart_json_builder.py app/tests/unit/test_house_ruler_resolver.py`
- `rg -n "create_table|op.create_table|HouseRuntimeData|house_runtime" backend/migrations backend/app/infra backend/app/services`
