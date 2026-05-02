# Validation Plan

## Environment assumptions

- Commands run on Windows / PowerShell.
- Every Python command must start with `.\.venv\Scripts\Activate.ps1`.
- Python package commands run from `backend/` after activation.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story tests | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py` | `backend/` | yes | all tests pass |
| Nearby runtime/bootstrap tests | `pytest -q tests/llm_orchestration/test_resolved_execution_plan.py tests/llm_orchestration/test_runtime_convergence.py app/tests/unit/test_gateway_modes.py` | `backend/` | yes | all tests pass |

## Unit tests

Covered by targeted checks above; no separate unit command is needed.

## Integration tests

`test_assembly_resolution.py` is the integration-style runtime contract for this story.

## Architecture / negative scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Fallback runtime scan | `rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config" app tests` | `backend/` | yes | only catalog, gateway, and expected guard/test hits |
| Converged key scan | `rg -n '"natal_long_free"|"natal_interpretation_short"|"guidance_daily"|"guidance_weekly"|"event_guidance"|"astrologer_selection_help"' backend\app\domain\llm\prompting\catalog.py backend\tests\llm_orchestration\test_prompt_governance_registry.py backend\tests\llm_orchestration\test_llm_legacy_extinction.py _condamad\stories\classify-converge-remaining-prompt-fallbacks\fallback-classification.md` | repo root | yes | no removed key appears as a `PROMPT_FALLBACK_CONFIGS` entry; runtime metadata and guards are expected hits |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff check | `ruff check .` | `backend/` | yes | no lint errors |

## Full regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression | `pytest -q` | `backend/` | yes | all tests pass |
| App startup smoke | `python -c "from app.main import app; print(app.title)"` | `backend/` | yes | FastAPI app imports |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace/conflict errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Worktree state | `git status --short` | repo root | yes | expected files plus pre-existing `backend/horoscope.db` |

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
