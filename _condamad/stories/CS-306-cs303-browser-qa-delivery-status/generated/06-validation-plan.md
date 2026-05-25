# Validation Plan

## Frontend checks

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation
node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

## Browser QA

```powershell
node _condamad\stories\CS-306-cs303-browser-qa-delivery-status\evidence\cs306-browser-qa.mjs
node --check _condamad\stories\CS-306-cs303-browser-qa-delivery-status\evidence\cs306-browser-qa.mjs
```

The browser QA script must start the Vite server on the exact logged `base_url`, open `/natal` in Chromium on desktop
and mobile, verify both CS-303 projection cards, and persist screenshots plus `browser-qa-ledger.json`.

## Backend contract checks

Run only after activating `.\.venv\Scripts\Activate.ps1`.

```powershell
cd backend
python -B -m pytest -q tests\api\test_projection_openapi.py tests\api\test_projection_endpoint.py tests\api\test_projection_authorization.py --tb=short
python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi().get('paths', {}); assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"
ruff check .
```

## Static guards

```powershell
cd frontend
rg -n "fetch\\(.*/v1/astrology/projections" src
rg -n "style=" src -g "*.tsx"
rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src
```

## Story validation

Run only after activating `.\.venv\Scripts\Activate.ps1`.

```powershell
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-306-cs303-browser-qa-delivery-status
python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-306-cs303-browser-qa-delivery-status\00-story.md
python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-306-cs303-browser-qa-delivery-status\00-story.md
```

## Rule for skipped commands

If a command cannot be run, record the exact command, reason, risk, and compensating evidence.
