# Validation Plan

## Targeted checks

```bash
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\unit\domain\astrology\test_client_interpretation_projection_v1_builder.py --tb=short
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
rg -n "from app\.(api|infra)|import app\.(api|infra)|chat\.completions|AsyncOpenAI|LLMNarrator" backend\app\domain\astrology\interpretation\client_interpretation_projection_v1_builder.py backend\tests\unit\domain\astrology\test_client_interpretation_projection_v1_builder.py
python -B -c "from app.main import app; from fastapi.testclient import TestClient; assert 'client_interpretation_projection_v1' not in str(app.openapi()); assert all('client_interpretation_projection_v1' not in getattr(r, 'path', '') for r in app.routes); assert TestClient(app).get('/health').status_code == 200"
git diff --check -- backend\app\domain\astrology\interpretation\client_interpretation_projection_v1_builder.py backend\tests\unit\domain\astrology\test_client_interpretation_projection_v1_builder.py _condamad\stories\CS-287-client-interpretation-projection-v1-builder-by-plan _condamad\stories\story-status.md
```

## Lint / static checks

```bash
ruff check app\domain\astrology\interpretation\client_interpretation_projection_v1_builder.py tests\unit\domain\astrology\test_client_interpretation_projection_v1_builder.py
ruff check .
```

## Full regression checks

```bash
python -B -m pytest -q --tb=short
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
