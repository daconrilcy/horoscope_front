# Provider Smoke After - CS-376

<!-- Commentaire global: cette preuve finale documente le smoke provider theme astral sans stocker de contenu provider brut. -->

## Implementation proof

- Test file: `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py`.
- Pytest marker: `provider_smoke` declared in `backend/pyproject.toml`.
- Opt-in env: `RUN_THEME_ASTRAL_PROVIDER_SMOKE=1`.
- Optional model override: `THEME_ASTRAL_PROVIDER_SMOKE_MODEL`.
- Payload source: `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`.
- Response contract: canonical `THEME_ASTRAL_RESPONSE_SCHEMA`.
- Provider attempt limit in smoke helper: one direct `ResponsesClient.execute` call.
- Timeout: `60` seconds.
- Raw provider output persisted by default: `false`.

## Local validation

- `python -B -m pytest -q tests\llm_orchestration\test_theme_astral_provider_smoke.py --tb=short`: `3 passed, 1 skipped`.
- `python -B -m pytest -q tests\llm_orchestration\test_theme_astral_provider_smoke.py -m provider_smoke --tb=short`: `1 skipped, 3 deselected`.
- `python -B -m pytest -q tests --tb=short -m "not provider_smoke"`: `1239 passed, 235 deselected`.
- `ruff check .`: PASS.

## Safe metadata shape

The deterministic metadata proof keeps only:

- `schema_valid`
- `model`
- `total_tokens`
- `estimated_cost_usd`
- `contract_trace`
- `raw_output_persisted`

It does not persist request messages, raw provider output, authorization headers, or credential values.

## Real provider command

Run only when an explicit local provider smoke is desired and credentials are configured:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
$env:RUN_THEME_ASTRAL_PROVIDER_SMOKE='1'
python -B -m pytest -q tests\llm_orchestration\test_theme_astral_provider_smoke.py -m provider_smoke --tb=short
```

## Residual limitation

The non-interactive implementation run did not enable `RUN_THEME_ASTRAL_PROVIDER_SMOKE=1`, so no external provider cost was incurred and no real provider output was stored.
