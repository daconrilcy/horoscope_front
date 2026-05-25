# Validation Plan

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B -m pytest -q backend\tests\unit\test_expert_technical_projection_contract.py --tb=short
python -B -m pytest -q backend\tests\unit\test_expert_technical_projection_contract.py backend\tests\architecture\test_api_contract_neutrality.py --tb=short
```

## Runtime neutrality

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -c "from app.main import app; payload=str(app.openapi()); paths={route.path for route in app.routes}; assert 'expert_technical_projection_v1' not in payload; assert not any('expert-technical-projection' in p for p in paths); print('PASS openapi/routes neutral')"
```

## Early guard scans

```powershell
rg -n "dignity|conditions|dominance|aspects|houses|structured_facts_v1|structured signals|evidence_refs|raw runtime traces|prompt internals|replay payloads|provider debug dumps|actor|role|projection id|action|decision|correlation_id" docs\architecture\expert-technical-projection-v1-contract.md

$row = rg -n "^\| `expert_technical_projection` \|" docs\architecture\official-product-primitives-public-projections.md
$row
if ($row -match "\| public \||futur contrat public expert|CS-255 API contract|CS-255 frontend client|CS-255 UI component|OpenAPI-ready") { exit 1 }
```

## Lint / static checks

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend\tests\unit\test_expert_technical_projection_contract.py
ruff check backend docs
git diff --check -- docs\architecture\expert-technical-projection-v1-contract.md docs\architecture\official-product-primitives-public-projections.md backend\tests\unit\test_expert_technical_projection_contract.py _condamad\stories\CS-273-expert-technical-projection-v1-internal-contract
```

## Evidence checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/validation.txt').exists()"
python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/app-surface-status.txt').exists()"
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-273-expert-technical-projection-v1-internal-contract
```

## Skipped checks

- Full repository pytest: skip allowed for this doc/contract story because targeted unit and architecture neutrality tests cover the changed surface, and the workspace has many unrelated dirty files.
- Frontend checks: skipped because no frontend file is touched and frontend is explicitly out of scope.
