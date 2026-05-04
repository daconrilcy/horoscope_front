# Final Evidence — CS-009-separer-projection-publique-enrichissement-llm

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-009-separer-projection-publique-enrichissement-llm
- Source story: `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/00-story.md`
- Capsule path: `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: pre-existing modified `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`; untracked CS-009 through CS-013 story folders.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-010-*`, `_condamad/stories/CS-011-*`, `_condamad/stories/CS-012-*`, `_condamad/stories/CS-013-*`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story preserved; status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated brief present. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 mapped to evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Initial generated map present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Story-specific commands recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific forbidden symbols recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Removed `settings`, `AIEngineAdapter`, `uuid`, local LLM call and DB/prompt parameters from `backend/app/prediction/public_projection.py`; added AST guard. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; scan `rg -n "AIEngineAdapter\|uuid\\.uuid4\\(\|settings\|Session" app/prediction/public_projection.py` returned no hits. | PASS | Projection is deterministic. |
| AC2 | Payload assembly remains in `PublicPredictionAssembler`; enrichment occurs after assembly. | Projection/API tests passed; `public-payload-before.md` and `public-payload-after.md` show same key shape and `same: true`; `openapi-daily-before-after.md` shows unchanged OpenAPI operation. | PASS | JSON and OpenAPI shape preserved on runtime baseline. |
| AC3 | Added `enrich_public_prediction_with_horoscope_narration` in `services/prediction/public_predictions.py`, delegating to `generate_horoscope_narration_via_gateway`. | `pytest -q app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py` passed. | PASS | No new adapter created. |
| AC4 | Added `projection-exceptions.md`; guard test blocks forbidden runtime dependencies in projection. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` passed. | PASS | Exception limited to deterministic helpers. |
| AC5 | Added `public-payload-before.md`, `public-payload-after.md` and `openapi-daily-before-after.md`. | Runtime comparison old vs current assembler returned `same: true`; OpenAPI operation comparison returned `same: true`. | PASS | Before sources loaded from `git show HEAD:...` and a temporary detached worktree. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/prediction/public_projection.py` | modified | Remove direct LLM runtime and local correlation ID generation. | AC1, AC2 |
| `backend/app/services/prediction/public_predictions.py` | modified | Add canonical service orchestration for horoscope narration. | AC3 |
| `backend/app/api/v1/routers/public/predictions.py` | modified | Call enrichment service with request-scoped IDs. | AC1, AC3 |
| `backend/app/api/v1/routers/internal/llm/qa.py` | modified | Keep QA route aligned with the new service orchestration. | AC3 |
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Add AST guard for forbidden projection runtime dependencies. | AC1, AC4 |
| `backend/app/tests/unit/prediction/test_public_projection_evidence.py` | modified | Move regeneration assertion to service-layer enrichment. | AC2, AC3 |
| `backend/app/tests/integration/test_horoscope_daily_variant_narration.py` | modified | Patch canonical narration service instead of projection/adapter. | AC3 |
| `_condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/*` | added/modified | Capsule, payload/OpenAPI snapshots, exception register and final evidence. | AC1-AC5 |
| `_condamad/stories/story-status.md` | modified | Set CS-009 to `ready-to-review`. | AC1-AC5 |

## Files deleted

- None.

## Tests added or updated

- Updated `backend/app/tests/unit/prediction/test_public_projection_evidence.py`.
- Updated `backend/app/tests/integration/test_horoscope_daily_variant_narration.py`.
- Added guard coverage in `backend/app/tests/unit/test_daily_prediction_guardrails.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | PASS | 0 | 33 passed. |
| `ruff check app tests` | `backend/` | PASS | 0 | All checks passed before formatting. |
| `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py` | `backend/` | PASS | 0 | 55 passed. |
| `pytest -q app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py` | `backend/` | PASS | 0 | 9 passed. |
| `rg -n "AIEngineAdapter\|uuid\\.uuid4\\(\|settings\|Session" app/prediction/public_projection.py` | `backend/` | PASS | 0 | No hits, exit 1 normalized to success for zero matches. |
| `ruff format app tests` | `backend/` | PASS | 0 | 5 files reformatted. |
| `ruff check app tests; pytest -q app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | PASS | 0 | Ruff passed; 84 tests passed after formatting. |
| runtime before/after comparison script using `git show HEAD:backend/app/prediction/public_projection.py` | `backend/` | PASS | 0 | `same: true`; key list persisted in snapshot artifacts. |
| OpenAPI before/after comparison using a temporary detached worktree at `HEAD` and current `app.openapi()` | `backend/` | PASS | 0 | `GET /v1/predictions/daily` operation unchanged; artifact persisted in `openapi-daily-before-after.md`. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-009-separer-projection-publique-enrichissement-llm` | repo root | PASS | 0 | CONDAMAD validation passed. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |
| `git status --short` | repo root | PASS | 0 | Final status recorded below. |
| `ruff format app tests; ruff check app tests; ruff format --check app tests; pytest -q app/tests/unit/test_request_id.py app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/integration/test_horoscope_daily_variant_narration.py` | `backend/` | PASS | 0 | Follow-up fixes validated; 90 tests passed and formatting/lint are clean. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | no | Full backend suite is broader than the story and targeted/regression story suites passed. | A failure outside prediction public flow could remain undiscovered. | 84 targeted tests across projection, service, API, adapter, prompt builder and narration variant passed; Ruff passed. |
| Starting the local web server | no | Refactor validated through FastAPI integration tests and no runtime startup command is required by the story. | A server-only startup issue outside tested imports could remain. | API integration tests import and exercise `app.main` through `TestClient`. |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `AIEngineAdapter` | `app/prediction/public_projection.py` | active_legacy_removed | Removed direct import/call. | PASS |
| `settings` | `app/prediction/public_projection.py` | active_legacy_removed | Removed projection dependency; service owns the setting check. | PASS |
| `uuid.uuid4()` | `app/prediction/public_projection.py` | active_legacy_removed | Routeurs provide request-scoped IDs. | PASS |
| `Session` | `app/prediction/public_projection.py` | active_legacy_removed | Projection no longer accepts DB/session. | PASS |

## Diff review

- `git diff --stat`: story-related backend files plus CONDAMAD evidence/status files.
- `git diff --check`: PASS, line-ending warnings only.
- No dependency changes.
- No frontend changes.
- No compatibility wrapper, alias, fallback, re-export, or duplicate narrator introduced.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/api/v1/routers/internal/llm/qa.py
 M backend/app/api/v1/routers/public/predictions.py
 M backend/app/core/request_id.py
 M backend/app/prediction/public_projection.py
 M backend/app/services/prediction/public_predictions.py
 M backend/app/tests/integration/test_horoscope_daily_variant_narration.py
 M backend/app/tests/unit/prediction/test_public_projection_evidence.py
 M backend/app/tests/unit/test_daily_prediction_guardrails.py
 M backend/app/tests/unit/test_request_id.py
?? _condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/
?? _condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/
?? _condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/
?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/
?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/
```

## Remaining risks

- Pre-existing dirty CONDAMAD story files for CS-010 through CS-013 remain untouched.
- Full `pytest -q` was not run; targeted story validation passed.

## Suggested reviewer focus

- Confirm the service-layer enrichment boundary in `backend/app/services/prediction/public_predictions.py`.
- Confirm public and QA routeurs propagate `request_id` and `trace_id` as intended.
- Confirm `public_projection.py` should retain only the staged deterministic exception until namespace convergence completes.
