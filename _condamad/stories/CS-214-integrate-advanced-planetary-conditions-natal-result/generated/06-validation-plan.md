# CS-214 Validation Plan

Toutes les commandes Python sont executees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Tests cibles

```powershell
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py
```

## Qualite

```powershell
ruff format .
ruff check .
pytest -q
```

## Gardes

Scans RG-141 sur imports interdits, scoring, texte interpretatif, JSON
builder/frontend, symboles publics, logique detaillee dans `natal_calculation.py`,
presence de RG-141 et diff adjacent.
