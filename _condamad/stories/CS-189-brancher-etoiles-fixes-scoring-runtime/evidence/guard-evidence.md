# Guard Evidence - CS-189

## RG-117

Commands run from `backend` after activating `.venv`:

```powershell
pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_prediction_reference_repository.py tests/unit/prediction/test_public_astro_daily_events.py
```

Result: PASS, 44 passed.

```powershell
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py
```

Result: PASS, 11 passed.

```powershell
pytest --long -q app/tests/integration/test_seed_31_prediction_v2.py
```

Result: PASS, 7 passed. This covers the fixed-star ruleset parameter seed and
the repair of an existing locked V2 ruleset missing those parameters.

```powershell
rg -n "_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"
```

Result: zero hit.

```powershell
rg -n "dist.*1\.0" app/domain/prediction/enriched_astro_events_builder.py
```

Result: zero hit.

```powershell
rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
```

Result: zero hit.

## Lint and startup

```powershell
ruff format .
ruff check .
python -B -c "from app.main import app; print(app.title)"
```

Results: PASS; app import prints `horoscope-backend`.
