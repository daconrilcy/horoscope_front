# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/remove-llm-narrator-legacy-direct-openai/00-story.md`
- Review date: 2026-05-01
- Scope: implemented changes for removing the executable `LLMNarrator` direct OpenAI runtime.

## Inputs reviewed

- Story contract and generated capsule evidence.
- `_condamad/stories/regression-guardrails.md` with `RG-016` and `RG-017`.
- Diff for backend contract imports, deleted legacy module/test, guard tests, migration tests, and story evidence.
- Residual symbol scans for `LLMNarrator`, `llm_narrator`, `openai.AsyncOpenAI`, and `chat.completions.create`.

## Diff summary

- `backend/app/prediction/llm_narrator.py` deleted.
- `NarratorAdvice` and `NarratorResult` moved to `backend/app/domain/llm/prompting/narrator_contract.py`.
- Runtime imports in `AIEngineAdapter` and `horoscope_daily/narration_service.py` now use the canonical contract.
- Nominal tests were updated away from `app.prediction.llm_narrator`.
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` now checks legacy module absence and direct provider patterns.

## Findings

No blocking or actionable findings found for this story.

## Acceptance audit

| AC | Review result |
|---|---|
| AC1 | PASS. Before/after scans and removal audit exist; the legacy executable module is deleted. Residual `llm_narrator` hits are classified as flag naming, guard code, or historical docs. |
| AC2 | PASS. Runtime and tests import `NarratorResult` / `NarratorAdvice` from `app.domain.llm.prompting.narrator_contract`. |
| AC3 | PASS. Reviewer scan found zero active hits for `LLMNarrator(`, direct legacy class import, `chat.completions.create`, and `openai.AsyncOpenAI` in `backend/app` and `backend/tests`. |
| AC4 | PASS. Migration tests pass and still exercise `AIEngineAdapter.generate_horoscope_narration`. |
| AC5 | PASS. `RG-016` and `RG-017` are represented by the deprecation guard test and targeted scans. |

## Validation audit

Reviewer commands run from `c:\dev\horoscope_front`:

| Command | Result |
|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | PASS, 3 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/llm_orchestration/test_narrator_migration.py` | PASS, 10 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .` | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; print(app.title)"` | PASS, imports app |
| `git diff --check` | PASS, line-ending warnings only |
| `cd backend; rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests` | PASS, zero hits |
| `rg -n "openai\.AsyncOpenAI|chat\.completions\.create" backend/app backend/tests` | PASS, zero hits |

Full `pytest -q` was not rerun by the reviewer because the evidence records the prior attempt timing out after about 304 seconds. After review, the user confirmed that the full suite was run manually and passed. This review therefore relies on targeted reviewer-run tests plus the user-confirmed full-suite pass.

## DRY / No Legacy audit

- No compatibility wrapper, alias, or re-export for `app.prediction.llm_narrator` was preserved.
- The useful dataclasses now have one canonical owner.
- Residual `llm_narrator_enabled` naming is not an executable legacy path and is classified in `legacy-narrator-scan-after.md`.
- The canonical OpenAI provider remains under `backend/app/infra/providers/llm/openai_responses_client.py`.

## Residual risks

- The worktree contains unrelated untracked CONDAMAD story/audit directories and guardrail rows for other stories. They were treated as outside this review target.
- Full backend regression was not independently rerun by the reviewer, but it was manually run and confirmed passing by the user after review.

## Verdict

CLEAN
