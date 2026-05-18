# Validation Plan - CS-185

## Commandes backend

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py
pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py tests/unit/domain/astrology/test_chart_signature.py
pytest -q tests/unit/domain/astrology/test_chart_signature_runtime_data.py
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q app/tests/unit/test_astrology_prediction_boundary.py
```

## Scans

```powershell
cd backend
rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"
rg -n "seasonal_quadrant|fertility|humane|bestial|voice" app/domain/astrology app/services/natal -g "*.py"
rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
```

## Story validation

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
```
