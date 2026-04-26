# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `M backend/horoscope.db`, untracked `_condamad/stories/converge-api-v1-route-architecture/`.
- AGENTS considered: `AGENTS.md`.
- Capsule generated: yes, via `condamad_prepare.py`.

## Red Test Evidence

- `pytest -q app/tests/unit/test_api_router_architecture.py` before refactor: 10 failed, 17 passed.
- Failures proved old modules importable, routes registered from non-canonical modules, `router_logic` APIRouter/wildcard drift, and forbidden router imports.

## Implementation Notes

- Moved `/v1/ops/b2b/*` route modules from `routers/b2b` to `routers/ops/b2b`.
- Moved `/v1/b2b/credentials` from `routers/public` to `routers/b2b/credentials.py`.
- Moved matching schemas and router_logic helpers to canonical namespaces.
- Removed `APIRouter` and wildcard schema imports from `router_logic`.
- Moved `AdminLlmErrorCode` to `schemas/routers/admin/llm/error_codes.py`.
- Replaced route-to-route imports in internal QA and natal interpretation.
- Added AC13 central error contract in `schemas/common.py` and `errors.py`.
- Added AC14 shared API v1 constants in `constants.py`.
- Added AC15 schema organization audit in `schema-audit.md` and moved flat schema files under canonical `schemas/routers/<surface>` folders.
- Added AC16 split for admin LLM prompt helpers: `manual_execution.py` and `release_snapshots.py`.
- Added AC17/AC18 targeted delegation for `list_mutation_audits` into router logic and documented residual route/service boundaries.
- Added AC19 constants audit and moved remaining tracked API constants into `constants.py`.

## Commands Run

| Command | Result | Notes |
|---|---|---|
| `ruff format .` | PASS | 21 files reformatted. |
| `ruff check .` | PASS | All checks passed. |
| `pytest -q app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_v1_router_contracts.py app/tests/integration/test_enterprise_credentials_api.py app/tests/integration/test_llm_qa_router.py app/tests/integration/test_daily_prediction_api.py` | PASS | 64 passed. |
| `pytest -q` | PASS | 3103 passed, 12 skipped after AC13-AC15 additions. |
| `ruff format .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py` | PASS | 34 passed after first AC13-AC15 pass. |
| `pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py tests/integration/test_story_66_36_admin_integration.py::test_publish_prompt_blocks_on_golden_regression tests/integration/test_story_66_36_admin_integration.py::test_publish_prompt_blocks_on_golden_invalid` | PASS | 37 passed after JSON encoding fix. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\converge-api-v1-route-architecture --final` | PASS | CONDAMAD validation PASS. |
| `pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py tests/unit/test_admin_manual_execute_response.py` | PASS | 42 passed for AC13/AC16/AC19 guards and manual execution extraction. |
| `pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py app/tests/integration/test_api_v1_router_contracts.py app/tests/integration/test_llm_qa_router.py` | PASS | 82 passed. |
| `pytest -q` | FAIL | Full suite caught consultation alias and release timeline field regressions after extraction. |
| `pytest -q app/tests/unit/test_consultation_request_schema.py app/tests/integration/test_consultation_catalogue.py app/tests/integration/test_consultation_third_party.py app/tests/integration/test_consultations_router.py tests/integration/test_admin_llm_catalog.py::test_admin_llm_release_timeline_returns_snapshot_history_and_proofs tests/integration/test_admin_llm_catalog.py::test_admin_llm_release_timeline_keeps_unmapped_backend_events_explicit` | PASS | 24 passed after restoring exact behavior. |
| `pytest -q` | PASS | 3107 passed, 12 skipped. |

## Decisions Made

- No compatibility modules or re-export wrappers were kept for moved Python paths.
- The existing `admin/llm/observability.py` registry import is allowed only as an exact, documented registry exception.
- A common `api_error_response` factory was added only after AC13 required a documented central contract; local route helpers now delegate to it to preserve existing payload shape.
- AC18 is recorded as PASS_WITH_LIMITATIONS because the story-targeted route flow is extracted and guarded, while older direct DB orchestration remains documented for follow-up instead of hidden by a broad allowlist.

## Final `git status --short`

- Recorded in `generated/10-final-evidence.md`.
