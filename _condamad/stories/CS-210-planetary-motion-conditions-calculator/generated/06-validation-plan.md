# Validation Plan - CS-210

Toutes les commandes Python doivent etre executees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Tests calculateur | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py` | repo root | yes | pass |
| Tests contrats | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | yes | pass |
| Format | `ruff format .` | repo root | yes | pass |
| Lint | `ruff check .` | repo root | yes | pass |
| Regression Python | `pytest -q` | repo root | yes | pass |
| Imports interdits | `rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" $motion_paths` | repo root | yes | zero hit |
| Dependances interdites | `rg -n "sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" $motion_paths` | repo root | yes | zero hit |
| Scoring interdit | `rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $motion_paths` | repo root | yes | zero hit |
| Texte narratif interdit | `rg -n "interpretation|meaning|description|narrative|prompt" $motion_paths` | repo root | yes | zero hit |
| Symboles publics | `rg -n "PlanetaryMotionProfile|calculate_planetary_motion_condition|DEFAULT_PLANETARY_MOTION_PROFILES" backend/app/domain/astrology/planetary_conditions backend/tests/unit/domain/astrology/planetary_conditions` | repo root | yes | hits bornes aux surfaces autorisees |
| Diff adjacent | `git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | yes | vide |
