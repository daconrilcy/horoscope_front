# Validation Plan

## Targeted Checks

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location backend
ruff format app\domain\astrology\interpretation\ai_narrative_input_contracts.py app\domain\astrology\interpretation\ai_narrative_input_builder.py tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py tests\architecture\test_ai_narrative_input_boundary.py tests\architecture\test_api_contract_neutrality.py
python -B -m pytest -q tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py
python -B -m pytest -q tests\architecture\test_ai_narrative_input_boundary.py
python -B -m pytest -q tests\architecture\test_api_contract_neutrality.py
```

## Runtime / API Neutrality

```powershell
python -B -c "from app.main import app; assert 'AI' not in str(app.openapi().get('components', {}).get('schemas', {}))"
python -B -c "from app.main import app; assert all('ai_narrative' not in getattr(r, 'path', '') for r in app.routes)"
```

## Architecture / Negative Scans

```powershell
rg -n "OpenAI|AIEngineAdapter|chat\.completions|LLMGateway" backend\app\domain\astrology\interpretation -g "*.py"
rg -n "prompt|llm_output|final_narrative|rendered_text|provider_response" backend\app\domain\astrology\interpretation\ai_narrative_input_contracts.py backend\app\domain\astrology\interpretation\ai_narrative_input_builder.py backend\app\domain\astrology\runtime -g "*.py"
rg -n "prompt|llm_output|final_narrative|rendered_text|provider_response" backend\app\domain\astrology\runtime backend\app\domain\astrology\interpretation -g "*.py"
```

## Lint / Full Regression

```powershell
ruff check .
python -B -m pytest -q
```
