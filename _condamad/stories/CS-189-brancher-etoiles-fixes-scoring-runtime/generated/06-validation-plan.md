# Validation Plan - CS-189

Toutes les commandes Python doivent etre lancees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Commands run

```powershell
cd backend
ruff format .
ruff check .
pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_prediction_reference_repository.py tests/unit/prediction/test_public_astro_daily_events.py
pytest -q app/tests/unit/test_domain_router.py app/tests/unit/test_contribution_calculator.py
pytest --long -q app/tests/integration/test_seed_31_prediction_v2.py
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py
rg -n "_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"
rg -n "dist.*1\.0" app/domain/prediction/enriched_astro_events_builder.py
rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
python -B -c "from app.main import app; print(app.title)"
```

Story validation:

```powershell
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md
```

## Note

`pytest -q app/tests/integration/test_seed_31_prediction_v2.py` est deselectionne
sans `--long`; la commande validee est donc `pytest --long -q ...`.
