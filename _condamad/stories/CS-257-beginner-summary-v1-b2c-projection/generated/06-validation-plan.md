# Validation Plan

## Scope

CS-257 is documentation-only. Validation must prove the `beginner_summary_v1`
contract exists, covers every source brief requirement, keeps application
surfaces unchanged and persists CONDAMAD evidence.

## Story and capsule checks

```powershell
. .\.venv\Scripts\Activate.ps1
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-257-beginner-summary-v1-b2c-projection
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-257-beginner-summary-v1-b2c-projection\00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-257-beginner-summary-v1-b2c-projection\00-story.md
```

## Contract shape scans

```powershell
rg -n "beginner_summary_v1|B2C|free|basic" docs\architecture\beginner-summary-v1-contract.md
rg -n "signes principaux|ascendant|maison dominante|thèmes dominants" docs\architecture\beginner-summary-v1-contract.md
rg -n "loading|empty|degraded|unavailable|trigger" docs\architecture\beginner-summary-v1-contract.md
rg -n "heure de naissance|ascendant|house-dependent|degraded_reason" docs\architecture\beginner-summary-v1-contract.md
rg -n "structured_facts_v1|upstream factual source|direct public payload" docs\architecture\beginner-summary-v1-contract.md
rg -n "controlled error|raw runtime|debug|audit|premium" docs\architecture\beginner-summary-v1-contract.md
rg -n "beginner_summary_v1|CS-257|future API contract, not CS-257|fixed_star_contacts" docs\architecture\official-product-primitives-public-projections.md
```

## Application surface guards

```powershell
. .\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -c "from app.main import app; assert 'beginner_summary_v1' not in str(app.openapi())"
python -B -c "from app.main import app; assert all('beginner_summary' not in getattr(r, 'path', '') for r in app.routes)"
git status --short -- backend/app frontend/src backend/tests backend/migrations
```

## Quality gates

```powershell
. .\.venv\Scripts\Activate.ps1
ruff format --check .
ruff check .
Set-Location backend
python -B -m pytest -q --tb=short
Set-Location ..
git diff --check
```

## Rule for skipped commands

Skipped commands must be recorded with the exact command, reason, risk and any
compensating evidence.
