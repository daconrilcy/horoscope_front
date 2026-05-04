# CONDAMAD Code Review

## Review target

- Story: `CS-013-propager-ids-correlation-narration-horoscope`
- Capsule: `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/`
- Review date: 2026-05-04

## Inputs reviewed

- `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/00-story.md`
- `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/generated/06-validation-plan.md`
- `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Current repository diff and untracked CS-013 capsule files.

## Diff summary

- Added propagation coverage in `backend/app/tests/unit/test_daily_prediction_service.py`.
- Added anti-reintroduction guard in `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- Added CS-013 CONDAMAD capsule evidence.
- Added `RG-033` to `_condamad/stories/regression-guardrails.md`.
- Synchronized CS-013 status to `done` in `_condamad/stories/story-status.md`.
- Note: `story-status.md` also contains a pre-existing CS-001 status change; it is unrelated to CS-013 and must not be included in the CS-013 commit.

## Review layers

- Diff integrity: PASS. No application production drift outside the story scope; runtime code was already in target shape at preflight.
- Acceptance audit: PASS. AC1-AC5 have code and executable evidence.
- Validation audit: PASS. Required targeted tests, scans, Ruff checks, capsule validation, and smoke startup were rerun in the activated venv where applicable.
- DRY / No Legacy audit: PASS. No compatibility wrapper, fallback, duplicate tracing path, or local projection UUID generation found.
- Edge/security audit: PASS. The public payload remains unchanged; no secret, auth, persistence, or input validation surface was broadened.

## Findings

Aucun constat actionnable.

## Acceptance audit

| AC | Evidence reviewed | Result |
|---|---|---|
| AC1 | `correlation-source.md`; `backend/app/api/v1/routers/public/predictions.py:12`, `:351`, `:352` use `app.core.request_id`. | PASS |
| AC2 | `backend/app/services/prediction/public_predictions.py:118`, `:119`; `backend/app/tests/unit/test_daily_prediction_service.py:644`. | PASS |
| AC3 | Forbidden scan on `app/prediction/public_projection.py`; guard test at `backend/app/tests/unit/test_daily_prediction_guardrails.py:278`. | PASS |
| AC4 | Projection and API integration tests pass; no public correlation field added. | PASS |
| AC5 | `test_public_projection_does_not_generate_local_correlation_ids` is executable and included in guardrail suite. | PASS |

## Validation audit

| Command | Working directory | Result |
|---|---|---|
| `pytest -q app/tests/unit/test_request_id.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_public_projection.py app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | PASS, 51 passed |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend/` | PASS, 25 passed |
| `pytest -q app/tests/unit/test_ai_engine_adapter.py` | `backend/` | PASS, 6 passed |
| `ruff check app tests` | `backend/` | PASS |
| `ruff format --check app tests` | `backend/` | PASS |
| `rg -n "uuid\.uuid4\(|request_id = str\(|trace_id = str\(" app/prediction/public_projection.py` | `backend/` | PASS, zero hit |
| `rg -n "LLMNarrator\(|chat\.completions\.create|openai\.AsyncOpenAI" app tests` | `backend/` | PASS, zero hit |
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope` | repo root | PASS |
| `uvicorn app.main:app --host 127.0.0.1 --port 8013` then `GET /health` | `backend/` | PASS, HTTP 200 |
| `git diff --check` | repo root | PASS, line-ending warnings only |

## DRY / No Legacy audit

- `public_projection.py` remains a deterministic public assembler and does not own correlation ID generation.
- Correlation IDs are resolved in the API request path and passed explicitly to narration enrichment.
- The narration gateway receives caller-provided `request_id` and `trace_id`.
- No `LLMNarrator`, direct OpenAI provider, or `chat.completions.create` active hit was found in the scoped app/tests scan.

## Commands run by reviewer

All commands listed in the validation audit were rerun by the reviewer on 2026-05-04. Python, pytest, Ruff, and uvicorn commands were executed after activating `.\.venv\Scripts\Activate.ps1`.

## Residual risks

Aucun risque restant identifie.

## Verdict

CLEAN
