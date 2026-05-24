# Validation Evidence — CS-254

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-254-ai-scoring-narrative-input-contract` | repo root | PASS |
| `ruff format app\domain\astrology\interpretation\ai_narrative_input_contracts.py app\domain\astrology\interpretation\ai_narrative_input_builder.py tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py tests\architecture\test_ai_narrative_input_boundary.py tests\architecture\test_api_contract_neutrality.py` | `backend` | PASS |
| `python -B -m pytest -q tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py tests\architecture\test_ai_narrative_input_boundary.py tests\architecture\test_api_contract_neutrality.py` | `backend` | PASS, 22 passed |
| `python -B -m pytest -q tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py tests\architecture\test_ai_narrative_input_boundary.py tests\architecture\test_api_contract_neutrality.py tests\unit\domain\astrology\test_astral_point_interpretation_service.py app\tests\unit\test_llm_generation_shared_natal_context.py app\tests\unit\test_natal_interpretation_service.py` | `backend` | PASS, 53 passed |
| `python -B -c "from app.main import app; assert 'AI' not in str(app.openapi().get('components', {}).get('schemas', {}))"` | `backend` | PASS |
| `python -B -c "from app.main import app; assert all('ai_narrative' not in getattr(r, 'path', '') for r in app.routes)"` | `backend` | PASS |
| forbidden-token `rg` scan over `backend\app\domain\astrology\runtime` and `backend\app\domain\astrology\interpretation` | repo root | PASS, no matches |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-254-ai-scoring-narrative-input-contract\00-story.md` | repo root | PASS |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-254-ai-scoring-narrative-input-contract\00-story.md` | repo root | PASS |
| `ruff format --check .` | `backend` | PASS, 1593 files already formatted |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q` | `backend` | PASS, 3236 passed, 1 skipped, 1182 deselected |

OpenAPI before/after SHA256 hashes match, proving no public OpenAPI delta.
