# Dev Log

## Preflight

- Initial `git status --short`: pre-existing modified `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`; untracked story folders CS-009 through CS-013.
- AGENTS.md considered: `AGENTS.md`.
- Regression guardrails read: `RG-017`, `RG-019`, `RG-029` applicable.
- Capsule generated: yes, required files created under `generated/`.

## Search evidence

- `rg -n "AIEngineAdapter|uuid\\.uuid4\\(|settings|Session" backend/app/prediction/public_projection.py backend/app/tests/unit/test_daily_prediction_guardrails.py backend/app/tests/unit/test_public_projection.py` found the original forbidden runtime dependencies in `public_projection.py`.
- Post-change scan `rg -n "AIEngineAdapter|uuid\\.uuid4\\(|settings|Session" app/prediction/public_projection.py` returned no hits.

## Implementation notes

- Removed direct LLM narration from `PublicPredictionAssembler`.
- Added service orchestration in `enrich_public_prediction_with_horoscope_narration`.
- Updated public and internal QA routeurs to provide request-scoped correlation IDs.
- Updated tests to patch the canonical service function, not the projection.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/integration/test_horoscope_daily_variant_narration.py` | PASS | 33 passed before final formatting. |
| `pytest -q app/tests/unit/test_public_projection.py app/tests/unit/test_daily_prediction_service.py app/tests/integration/test_daily_prediction_api.py` | PASS | 55 passed. |
| `pytest -q app/tests/unit/test_ai_engine_adapter.py tests/unit/prediction/test_astrologer_prompt_builder.py` | PASS | 9 passed. |
| `ruff format app tests` | PASS | 5 files reformatted. |
| `ruff check app tests` plus combined targeted pytest command | PASS | 84 passed after formatting. |
| `rg -n "AIEngineAdapter|uuid\\.uuid4\\(|settings|Session" app/prediction/public_projection.py` | PASS | No hits. |

## Issues encountered

- The capsule helper normalized the story key to lowercase on a case-insensitive filesystem. The CS-009 story file was recreated from the already loaded source content, and the capsule files were regenerated under the requested story directory.

## Final `git status --short`

- Recorded in `10-final-evidence.md`.
