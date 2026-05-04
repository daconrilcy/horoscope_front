# CONDAMAD Code Review

## Review target

- Story: `CS-009-separer-projection-publique-enrichissement-llm`
- Source: `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/00-story.md`
- Status reviewed: `ready-to-review`
- Review date: 2026-05-04

## Inputs reviewed

- Story capsule: `00-story.md`, generated traceability, validation plan, No Legacy guardrails, final evidence.
- Regression registry: `_condamad/stories/regression-guardrails.md`, including `RG-017`, `RG-019`, `RG-029`, `RG-033`.
- Evidence artifacts: `public-payload-before.md`, `public-payload-after.md`, `openapi-daily-before-after.md`, `projection-exceptions.md`.
- Diff scope: public prediction route, QA route, deterministic projection, service-layer enrichment, request/trace ID resolution, guardrail tests, public projection evidence tests, narration integration tests, CONDAMAD artifacts.

## Diff summary

- `backend/app/prediction/public_projection.py` no longer imports or calls `settings`, `AIEngineAdapter`, `uuid.uuid4()` or DB/session inputs.
- `backend/app/services/prediction/public_predictions.py` owns LLM enrichment orchestration and delegates to `generate_horoscope_narration_via_gateway`.
- `backend/app/api/v1/routers/public/predictions.py` now resolves `request_id` and sanitized `trace_id` before calling service-layer enrichment.
- `backend/app/core/request_id.py` centralizes printable, bounded correlation ID sanitization for request and trace IDs.
- `openapi-daily-before-after.md` persists the required before/after OpenAPI operation evidence for `GET /v1/predictions/daily`.

## Findings

No actionable findings.

Previously reported issues are resolved:

- CR-1: OpenAPI before/after evidence is now persisted in `openapi-daily-before-after.md` and referenced from `generated/10-final-evidence.md`.
- CR-2: `X-Trace-Id` is no longer read raw in the public prediction route; `resolve_trace_id()` sanitizes and bounds the value, with targeted unit tests.

## Acceptance audit

- AC1: PASS. `public_projection.py` is deterministic for the forbidden runtime dependencies; the AST guard and zero-hit scan support `RG-029`.
- AC2: PASS. JSON payload snapshots and the focused OpenAPI before/after artifact preserve the public contract.
- AC3: PASS. Enrichment delegates through `generate_horoscope_narration_via_gateway` in `services/prediction/public_predictions.py`.
- AC4: PASS. `projection-exceptions.md` is exact and the guard blocks forbidden projection dependencies.
- AC5: PASS. Required before/after payload and OpenAPI evidence is persisted.

## Validation audit

Reviewer commands run:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location backend
ruff check app tests
ruff format --check app tests
pytest -q app/tests/unit/test_request_id.py app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py
rg -n "AIEngineAdapter|uuid\.uuid4\(|settings|Session" app/prediction/public_projection.py
rg -n "X-Trace-Id|trace_id = request\.headers" app/api/v1/routers/public/predictions.py
git diff --check
```

Results:

- `ruff check app tests`: passed.
- `ruff format --check app tests`: passed, `1080 files already formatted`.
- Targeted tests: `90 passed`.
- Forbidden projection scan: no hits.
- Raw trace header scan in public prediction route: no hits.
- `git diff --check`: no whitespace errors; line-ending warnings only.

## DRY / No Legacy audit

- No second LLM adapter was introduced.
- No compatibility wrapper, alias, fallback, or re-export was found in the reviewed CS-009 diff.
- `AIEngineAdapter`, `settings`, `uuid.uuid4()` and `Session` are absent from `backend/app/prediction/public_projection.py`.
- Remaining deterministic projection exception is documented in `projection-exceptions.md`.
- Trace ID normalization reuses the existing correlation-ID owner instead of duplicating sanitization in the route.

## Residual risks

- Full `pytest -q` was not run by the reviewer; targeted story and regression coverage passed.
- The worktree contains unrelated/untracked CONDAMAD story folders CS-010 through CS-013, left untouched.
- Other public routes still contain raw `X-Trace-Id` reads, but they are outside CS-009 and the prediction public route is clean.

## Verdict

`CLEAN`

Required CS-009 acceptance criteria and regression guardrails are satisfied with executable evidence.
