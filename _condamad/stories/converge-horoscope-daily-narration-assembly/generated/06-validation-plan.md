# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands run after `.\.venv\Scripts\Activate.ps1`
- Backend working directory for pytest/ruff: `backend`

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story schema validation | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md` | `backend` | yes | PASS |
| Story lint | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md` | `backend` | yes | PASS |
| Builder guard | `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py` | `backend` | yes | PASS |
| Seed / assembly guard | `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py` | `backend` | yes | PASS |
| Narrator migration guard | `pytest -q tests/llm_orchestration/test_narrator_migration.py` | `backend` | yes | PASS |
| Admin observability guard | `pytest -q tests/integration/test_admin_llm_catalog.py::test_admin_llm_catalog_resolved_detail_exposes_horoscope_daily_narration_assembly` | `backend` | yes | PASS |
| RG-016 guard | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | yes | PASS |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Builder forbidden markers | `rg -n "Format attendu\|Interdiction\|daily_synthesis : strictement" backend\app\prediction\astrologer_prompt_builder.py` | repo root | yes | no hits |
| Adapter forbidden markers | `rg -n "Format attendu\|Interdiction\|daily_synthesis : strictement" backend\app\domain\llm\runtime\adapter.py backend\app\services\llm_generation\horoscope_daily` | repo root | yes | no hits |
| Assembly positive ownership | `rg -n "strictement 7 à 8\|strictement 10 à 12\|Ne produis pas de phrases creuses\|Génère uniquement du JSON valide" backend\app\ops\llm\bootstrap\seed_horoscope_narrator_assembly.py backend\app\domain\llm\configuration\assembly_resolver.py backend\app\prediction\astrologer_prompt_builder.py` | repo root | yes | hits only in assembly-owned files |
| RG-006 import boundary | `rg -n "from app\.api\|import app\.api" backend\app\services backend\app\domain backend\app\infra backend\app\core` | repo root | yes | no hits |
| RG-016 narrator imports | `rg -n "from app\.prediction\.llm_narrator import LLMNarrator\|LLMNarrator\(\|LLMNarrator\.narrate" backend\tests backend\app\tests -g "test_*.py"` | repo root | yes | no hits |
| Provider direct-call scan | `rg -n "LLMNarrator\(\|chat\.completions\.create\|openai\.AsyncOpenAI" backend\app backend\tests` | repo root | yes | no hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format check | `ruff format --check .` | `backend` | yes | PASS |
| Lint | `ruff check .` | `backend` | yes | PASS |
| Diff whitespace | `git diff --check` | repo root | yes | PASS |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression suite | `pytest -q` | `backend` | yes | Timed out after 10 minutes; targeted checks passed |
