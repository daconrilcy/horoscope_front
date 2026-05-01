# Dev Log

## Preflight

- Repository root: `c:\dev\horoscope_front`.
- Source story: `_condamad/stories/remove-llm-narrator-legacy-direct-openai/00-story.md`.
- Initial `git status --short`: pre-existing dirty `_condamad/stories/regression-guardrails.md`; untracked `_condamad/audits/prompt-generation/`; untracked story directories including this capsule.
- AGENTS.md considered: `AGENTS.md`.
- Regression guardrails considered: `RG-016`, `RG-017`, `RG-006`.

## Baseline searches before implementation

- `rg -n "LLMNarrator|llm_narrator" backend/app backend/tests docs`: active hits in `backend/app/prediction/llm_narrator.py`, contract imports, migration tests, app tests, docs, and `llm_narrator_enabled` settings.
- `rg -n "chat\.completions\.create|openai\.AsyncOpenAI" backend/app backend/tests`: active hits in `backend/app/prediction/llm_narrator.py`; test comment hit in migration test.
- `rg -n "from app\.prediction\.llm_narrator import LLMNarrator|LLMNarrator\(|LLMNarrator\.narrate" backend/tests backend/app/tests -g "test_*.py"`: zero hits before implementation.

## Implementation notes

- Moved `NarratorAdvice` and `NarratorResult` into `app.domain.llm.prompting.narrator_contract`.
- Migrated app and test imports to the canonical contract module.
- Deleted `backend/app/prediction/llm_narrator.py` instead of preserving a shim.
- Deleted obsolete direct narrator unit tests.
- Hardened `test_llm_narrator_deprecation_guard.py` with runtime surface and direct provider guards.

## Validation notes

- Targeted story checks passed in the venv.
- `ruff check .` passed after import sorting.
- `ruff format --check .` passed after formatting three touched files.
- Full `pytest -q` was attempted in the venv and timed out after about 304 seconds.
