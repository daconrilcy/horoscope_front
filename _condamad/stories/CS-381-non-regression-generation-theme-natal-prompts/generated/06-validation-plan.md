# Validation Plan

## Backend

- `.\.venv\Scripts\Activate.ps1; ruff format backend\tests\integration\astrology\test_natal_generation_regression.py backend\tests\integration\llm\test_theme_astral_provider_payload_handoff.py backend\tests\llm_orchestration\test_theme_astral_provider_payload_builder.py`
- `.\.venv\Scripts\Activate.ps1; ruff check backend`
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -m pytest -q backend\tests --tb=short -k "natal_chart or theme_astral or llm_astrology_input"`
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -m pytest -q backend\tests\architecture\test_llm_astrology_input_payload_boundaries.py --tb=short`
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert any('natal-chart' in r.path for r in app.routes)"`
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert '/v1/users/me/natal-chart' in app.openapi()['paths']"`

## Frontend

- `pnpm --dir frontend test -- NatalExpertPanel BirthProfilePage`
- `pnpm --dir frontend lint`
- `pnpm --dir frontend build`
- `$env:PLAYWRIGHT_PORT='4193'; $env:PLAYWRIGHT_SKIP_WEBSERVER='1'; pnpm --dir frontend test:e2e -- --grep "natal"` with explicit local Vite server.

## Guard scans

- `git diff --check`
- `rg -n "style=" frontend\e2e\natal-generation-regression.spec.ts frontend\src\tests\BirthProfilePage.test.tsx frontend\src\tests\NatalExpertPanel.test.tsx frontend\src\features\natal-chart\NatalExpertPanel.tsx frontend\src\pages\BirthProfilePage.tsx`
- `rg -n "chart_json|natal_data" backend\app\services\llm_generation\natal backend\app\domain\llm\runtime backend\tests\integration\astrology\test_natal_generation_regression.py backend\tests\integration\llm\test_theme_astral_provider_payload_handoff.py backend\tests\llm_orchestration\test_theme_astral_provider_payload_builder.py backend\tests\architecture\test_llm_astrology_input_payload_boundaries.py`
- `rg -n "provider_smoke|OPENAI_API_KEY|ANTHROPIC_API_KEY" backend\tests frontend\e2e`

## Rule for skipped commands

If a command cannot be run, record the exact command, reason, risk, and compensating evidence.
