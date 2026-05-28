# Validation Plan

## Required Checks Run

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format app/domain/llm/configuration/theme_astral_contracts.py app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py app/domain/llm/runtime/gateway.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py
ruff format app/domain/astrology/runtime/astrology_doctrine_governance.py
ruff check .
python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short
python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/llm/test_theme_astral_provider_payload_handoff.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/test_theme_astral_prompt_contract_migration.py --tb=short
python -B -m pytest -q tests --tb=short
python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Static Evidence

- `evidence/legacy-scan-before.txt`
- `evidence/legacy-scan-after.txt`
- Example JSON shape check: PASS
- `app.routes` / `app.openapi()` loaded hash check: PASS
- `git diff --check`: PASS

## Skipped

- No frontend checks: story is backend-domain and no frontend files changed.
- No real provider LLM call: explicit non-goal.
