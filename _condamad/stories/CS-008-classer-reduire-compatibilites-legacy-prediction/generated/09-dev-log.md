# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial dirty files included `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, and untracked story capsules CS-008 through CS-013.
- Applicable instructions: root `AGENTS.md`, `condamad-dev-story`, `condamad-regression-guardrails`.
- Capsule generated because CS-008 initially had only `00-story.md`.

## Search evidence

- Baseline scans found `schemas.TimeBlock`, `EngineOutput`, `save(engine_output=...)`, public `categories`, and no active `LLMNarrator` runtime.
- Frontend scan proved `categories` is externally active.
- Canonical service owners for orchestrator/persistence are under `backend/app/services/prediction`.

## Implementation notes

- Deleted only the removable `schemas.TimeBlock` facade.
- Removed the persistence compatibility keyword and migrated internal tests to `bundle=`.
- Added an AST guard for both deleted surfaces.
- Preserved `EngineOutput` and `categories` with explicit classification.

## Commands run

| Command | Result | Notes |
|---|---|---|
| Targeted story tests | PASS | 37 passed. |
| `pytest -q app/tests/unit/test_schemas_v3.py` | PASS | 28 passed. |
| OpenAPI smoke | PASS | `app.openapi()` generated. |
| `ruff check app tests` | PASS | All checks passed. |
| `git diff --check` | PASS | CRLF warnings only. |
| `pytest -q` | PASS | 3580 passed, 12 skipped. |
| Uvicorn smoke `/openapi.json` | PASS | Local server answered 200 on `127.0.0.1:8765`. |

## Issues encountered

- The generated capsule was minimal and required story-specific completion.
- `EngineOutput` is still an active V2 DTO, so deletion would exceed this story.

## Decisions made

- `EngineOutput`: keep as `canonical-active`.
- `categories`: keep as `external-active`.
- `schemas.TimeBlock`: delete.
- `save(engine_output=...)`: replace consumers and delete compatibility keyword.

## Final `git status --short`

- Recorded in final evidence and final response.
