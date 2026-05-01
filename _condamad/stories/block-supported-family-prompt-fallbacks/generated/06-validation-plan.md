# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Backend working directory for Python checks: `backend/`
- Python commands require `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md` | `backend/` | yes | PASS |
| Story lint | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md` | `backend/` | yes | PASS |
| Reintroduction guard | `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py` | `backend/` | yes | all tests pass |
| Bootstrap exception allowlist | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | yes | all tests pass |
| Missing assembly rejection | `pytest -q tests/llm_orchestration/test_assembly_resolution.py` | `backend/` | yes | all tests pass |
| Existing QA legacy guard | `pytest -q tests/integration/test_llm_legacy_extinction.py` | `backend/` | yes | all tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Fallback/legacy scan | `rg -n "PROMPT_FALLBACK_CONFIGS|legacy_use_case_fallback" app tests` | `backend/` | yes | only catalog, guard tests, enum/test historical hits |
| Forbidden key scan | `rg -n "\"chat\"|\"chat_astrologer\"|\"guidance_contextual\"|\"natal_interpretation\"|\"horoscope_daily\"" backend\app\domain\llm\prompting\catalog.py backend\tests\llm_orchestration\test_llm_legacy_extinction.py backend\tests\llm_orchestration\test_prompt_governance_registry.py _condamad\stories\block-supported-family-prompt-fallbacks\fallback-exception-audit.md` | repo root | yes | no forbidden keys under `PROMPT_FALLBACK_CONFIGS`; test/audit hits expected |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no unintended churn |
| Lint/fix imports | `ruff check . --fix` | `backend/` | conditional | only mechanical import fixes |
| Lint | `ruff check .` | `backend/` | yes | PASS |
| App import/start smoke | `python -B -c "from app.main import app; print(app.title)"` | `backend/` | yes | prints `horoscope-backend` |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | `backend/` | yes | preferred PASS; document timeout if environment-limited |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related tracked files plus pre-existing dirty registry |
| Whitespace check | `git diff --check` | repo root | yes | no whitespace errors |
| Worktree status | `git status --short` | repo root | yes | expected files documented |
