# Validation Plan

All Python commands must run after `. .\.venv\Scripts\Activate.ps1`.

## Contract Checks

```powershell
python -B -c "from pathlib import Path; assert Path('docs/architecture/structured-facts-v1-contract.md').exists()"
rg -n "structured_facts_v1|stable|hashable|non narrative" docs\architecture\structured-facts-v1-contract.md
rg -n "positions|houses|major aspects|dominants|source metadata" docs\architecture\structured-facts-v1-contract.md
rg -n "stable ordering|deterministic serialization|hash input boundary|AI audit" docs\architecture\structured-facts-v1-contract.md
rg -n "AINarrativeInputContract|downstream|reference|calculation truth" docs\architecture\structured-facts-v1-contract.md
rg -n "ChartObjectRuntimeData|chart_objects|debug raw traces|internal payloads" docs\architecture\structured-facts-v1-contract.md
rg -n "B2C|optionnel|product projection" docs\architecture\structured-facts-v1-contract.md
```

## Application Surface Checks

```powershell
Set-Location backend
python -B -c "from app.main import app; assert 'structured_facts_v1' not in str(app.openapi())"
python -B -c "from app.main import app; assert all('structured_facts' not in getattr(r, 'path', '') for r in app.routes)"
Set-Location ..
git status --short -- backend\app frontend\src
```

## Story Evidence Checks

```powershell
python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-256-structured-facts-v1-contract/evidence/validation.txt').exists()"
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-256-structured-facts-v1-contract\00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-256-structured-facts-v1-contract\00-story.md
```

## Lint And Regression Checks

```powershell
Set-Location backend
ruff check .
python -B -m pytest -q --tb=short
```

## Skipped Commands

- `ruff format <python files>`: not applicable because CS-256 changes no Python source.
- Frontend and browser validations: not applicable because CS-256 changes no frontend source or route.
