# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: converge-api-v1-route-architecture
- Source story: `_condamad/stories/converge-api-v1-route-architecture/00-story.md`
- Capsule path: `_condamad/stories/converge-api-v1-route-architecture`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/converge-api-v1-route-architecture/00-story.md`
- Initial `git status --short`: `M backend/horoscope.db`, `?? _condamad/stories/converge-api-v1-route-architecture/`
- Pre-existing dirty files: `backend/horoscope.db`; left untouched intentionally.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC15 mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated starting map. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Story commands followed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No Legacy applied. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `router-root-audit.md`; expected roots in `test_api_router_architecture.py`. | Audit plus OpenAPI contract test. | PASS | Inventory focused on active moved/non-v1 routes. |
| AC2 | Ops B2B routers moved to `routers/ops/b2b`. | Architecture test; negative scan `prefix="/v1/ops"` in `routers/b2b` and `routers/public` returned no hits. | PASS | |
| AC3 | Credentials route moved to `routers/b2b/credentials.py`. | Architecture test; negative scan `prefix="/v1/b2b"` in `routers/public` and `routers/ops` returned no hits. | PASS | |
| AC4 | `NON_V1_ROUTE_EXCEPTIONS` lists `/api/email/unsubscribe`. | `pytest -q app/tests/unit/test_api_router_architecture.py` passed. | PASS | `/health` is outside `app.api.v1`. |
| AC5 | `router_logic` APIRouter declarations and wildcard imports removed. | Architecture test; `rg -n "APIRouter\|import \*" app/api/v1/router_logic` returned no hits. | PASS | |
| AC6 | Router imports moved to `schemas`/`router_logic`; exact registry allowlist documented. | Architecture test; router import scan only hits `__init__.py` registries and `admin/llm/observability.py`. | PASS | |
| AC7 | Existing error helpers preserved without payload/status/header changes. | Targeted integration tests and full backend suite passed. | PASS | No broad helper added. |
| AC8 | `backend/app/main.py` imports canonical router modules. | Architecture test and old-path scans. | PASS | |
| AC9 | OpenAPI baseline for moved routes added. | `pytest -q app/tests/integration/test_api_v1_router_contracts.py` passed. | PASS | |
| AC10 | Formatting, lint and tests passed in venv. | `ruff format .`; `ruff check .`; targeted tests; `pytest -q`. | PASS | |
| AC11 | Old files deleted; no re-export modules added. | Architecture negative import tests and scans old module paths. | PASS | Remaining old-path hits are test guard expected hits. |
| AC12 | `operationId` baseline added and generated client scan run. | OpenAPI contract test; generated-client scan found no generator/client, operationId hits only in test baseline. | PASS | |
| AC13 | `backend/app/api/v1/errors.py` and `schemas/common.py` centralize error codes, envelope models and JSONResponse creation. | `pytest -q app/tests/unit/test_api_error_contracts.py`; architecture helper/model guards. | PASS | Payload shape remains `{"error": ...}` with `code`, `message`, `details`, `request_id`. |
| AC14 | Shared constants moved to `backend/app/api/v1/constants.py` and imported by routers, schemas and router_logic. | Architecture constant guard and Ruff unused-import checks. | PASS | No router-local redefinition for tracked shared constants. |
| AC15 | Flat schema modules moved under `schemas/routers/<surface>`; `schema-audit.md` documents the anti-duplication audit. | Architecture canonical schema-root guard and `ErrorPayload/ErrorEnvelope` scan. | PASS | Only `schemas/common.py` remains at schema root besides `__init__.py`. |
| AC16 | `router_logic/admin/llm/prompts.py` split release snapshot and manual execution responsibilities into dedicated modules. | Architecture responsibility guard; admin LLM targeted tests; full suite. | PASS | File reduced from about 67 KB to about 50 KB. |
| AC17 | `routers/ops/entitlement_mutation_audits.py` delegates the mutation-audit list flow to `build_mutation_audit_list_response`. | Architecture thin-route guard; `test_ops_entitlement_mutation_audits_api.py`; full suite. | PASS | File reduced below the target responsibility guard. |
| AC18 | Target route business flow moved out of the HTTP handler and residual DB orchestration documented in `service-boundary-audit.md`. | Targeted guard + service-boundary audit + full suite. | PASS_WITH_LIMITATIONS | Existing non-target endpoints still contain direct DB orchestration; audit records this as residual reviewer focus. |
| AC19 | API constants audit completed and additional shared constants moved into `constants.py`. | Constant guard + uppercase constant scan + full suite. | PASS | Scan returns tracked constants only from `app/api/v1/constants.py`. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/main.py` | modified | Use canonical router imports. | AC8 |
| `backend/app/api/v1/routers/ops/b2b/*` | added/moved | Canonical ops B2B route owners. | AC2, AC8, AC11 |
| `backend/app/api/v1/routers/b2b/credentials.py` | added/moved | Canonical B2B credentials route owner. | AC3, AC8, AC11 |
| `backend/app/api/v1/router_logic/**` | modified/moved | Remove FastAPI routers/wildcards; align helper namespaces. | AC5, AC6 |
| `backend/app/api/v1/schemas/routers/ops/b2b/*` | added/moved | Canonical ops B2B schemas. | AC2, AC6 |
| `backend/app/api/v1/schemas/routers/b2b/credentials.py` | added/moved | Canonical B2B credentials schemas. | AC3, AC6 |
| `backend/app/api/v1/schemas/routers/admin/llm/error_codes.py` | added/moved | Canonical owner for `AdminLlmErrorCode`. | AC6, AC11 |
| `backend/app/api/v1/errors.py` | added | Central API v1 error response factory and shared error codes. | AC13 |
| `backend/app/api/v1/constants.py` | added | Central shared constants for API v1 route/schema/logic modules. | AC14, AC19 |
| `backend/app/api/v1/schemas/common.py` | added | Common response/error Pydantic contracts. | AC13, AC15 |
| `backend/app/api/v1/router_logic/admin/llm/manual_execution.py` | added | Manual execution payload/audit helpers extracted from admin LLM prompts. | AC16, AC18 |
| `backend/app/api/v1/router_logic/admin/llm/release_snapshots.py` | added | Release snapshot timeline/diff helpers extracted from admin LLM prompts. | AC16 |
| `backend/app/api/v1/router_logic/ops/entitlement_mutation_audits.py` | modified | Adds `build_mutation_audit_list_response` for the ops audit list flow. | AC17, AC18 |
| `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` | modified | Delegates the mutation-audit list endpoint to router logic. | AC17, AC18 |
| `backend/app/api/v1/schemas/routers/admin/{ai,audit,entitlements,exports,logs,support,users}.py` | added/moved | Canonical admin schema folders. | AC15 |
| `backend/app/api/v1/schemas/routers/public/{consultation,entitlements,natal_interpretation}.py` | added/moved | Canonical public schema folders. | AC15 |
| `backend/app/api/v1/routers/internal/llm/qa.py` | modified | Import prediction helpers from `router_logic`. | AC6 |
| `backend/app/api/v1/routers/public/natal_interpretation.py` | modified | Import `ErrorEnvelope` from schemas. | AC6 |
| `backend/app/tests/unit/test_api_router_architecture.py` | modified | Add route-root, no-legacy, error inheritance, constants and responsibility guards. | AC1-AC6, AC8, AC11, AC13, AC16-AC19 |
| `backend/app/tests/unit/test_api_error_contracts.py` | added | Verify the documented central error envelope and headers. | AC13 |
| `backend/app/tests/integration/test_api_v1_router_contracts.py` | modified | Add OpenAPI baseline for moved routes. | AC9, AC12 |
| `backend/app/tests/integration/test_enterprise_credentials_api.py` | modified | Update patch paths to canonical modules. | AC3, AC11 |
| `backend/tests/evaluation/__init__.py` | modified | Update evaluation router registry imports. | AC8, AC11 |
| `_condamad/stories/converge-api-v1-route-architecture/**` | added/modified | Capsule, audits and evidence. | AC1-AC19 |

## Files deleted

- `backend/app/api/v1/routers/b2b/reconciliation.py`
- `backend/app/api/v1/routers/b2b/entitlement_repair.py`
- `backend/app/api/v1/routers/b2b/entitlements_audit.py`
- `backend/app/api/v1/routers/public/enterprise_credentials.py`
- `backend/app/api/v1/router_logic/b2b/reconciliation.py`
- `backend/app/api/v1/router_logic/b2b/entitlement_repair.py`
- `backend/app/api/v1/router_logic/b2b/entitlements_audit.py`
- `backend/app/api/v1/router_logic/public/enterprise_credentials.py`
- `backend/app/api/v1/schemas/routers/b2b/reconciliation.py`
- `backend/app/api/v1/schemas/routers/b2b/entitlement_repair.py`
- `backend/app/api/v1/schemas/routers/b2b/entitlements_audit.py`
- `backend/app/api/v1/schemas/routers/public/enterprise_credentials.py`
- `backend/app/api/v1/routers/admin/llm/error_codes.py`
- `backend/app/api/v1/schemas/admin_ai.py`
- `backend/app/api/v1/schemas/admin_audit.py`
- `backend/app/api/v1/schemas/admin_entitlements.py`
- `backend/app/api/v1/schemas/admin_exports.py`
- `backend/app/api/v1/schemas/admin_logs.py`
- `backend/app/api/v1/schemas/admin_support.py`
- `backend/app/api/v1/schemas/admin_users.py`
- `backend/app/api/v1/schemas/consultation.py`
- `backend/app/api/v1/schemas/entitlements.py`
- `backend/app/api/v1/schemas/natal_interpretation.py`

## Tests added or updated

- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- `backend/app/tests/integration/test_api_v1_router_contracts.py`
- `backend/app/tests/integration/test_enterprise_credentials_api.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\converge-api-v1-route-architecture\00-story.md --root . --story-key converge-api-v1-route-architecture --with-optional` | repo root, venv active | PASS | 0 | Capsule generated. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\converge-api-v1-route-architecture` | repo root, venv active | PASS | 0 | Capsule structure valid. |
| `pytest -q app/tests/unit/test_api_router_architecture.py` | `backend/`, venv active | FAIL | 1 | Red evidence: 10 failed before refactor. |
| `pytest -q app/tests/unit/test_api_router_architecture.py` | `backend/`, venv active | PASS | 0 | 28 passed after refactor. |
| `ruff check . --fix` | `backend/`, venv active | FAIL | 1 | 21 import-order issues fixed; 4 line-length issues remained and were patched. |
| `ruff format .; ruff check .` | `backend/`, venv active | PASS | 0 | 21 files reformatted; all checks passed. |
| `pytest -q app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_v1_router_contracts.py app/tests/integration/test_enterprise_credentials_api.py app/tests/integration/test_llm_qa_router.py app/tests/integration/test_daily_prediction_api.py` | `backend/`, venv active | PASS | 0 | 64 passed. |
| `pytest -q` | `backend/`, venv active | FAIL | 1 | AC13 regression caught: datetime in error details was not JSON serializable. |
| `ruff format .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py` | `backend/`, venv active | PASS | 0 | 34 passed after first AC13-AC15 additions. |
| `ruff format .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py tests/integration/test_story_66_36_admin_integration.py::test_publish_prompt_blocks_on_golden_regression tests/integration/test_story_66_36_admin_integration.py::test_publish_prompt_blocks_on_golden_invalid` | `backend/`, venv active | PASS | 0 | 37 passed after central factory switched to FastAPI `jsonable_encoder`. |
| `pytest -q` | `backend/`, venv active | PASS | 0 | 3103 passed, 12 skipped. |
| `ruff format .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py tests/unit/test_admin_manual_execute_response.py` | `backend/`, venv active | PASS | 0 | 42 passed after AC16-AC19 refactors. |
| `pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py app/tests/integration/test_api_v1_router_contracts.py app/tests/integration/test_llm_qa_router.py` | `backend/`, venv active | PASS | 0 | 82 passed. |
| `ruff format .; ruff check .; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_enterprise_credentials_api.py app/tests/integration/test_daily_prediction_api.py` | `backend/`, venv active | PASS | 0 | 70 passed. |
| `pytest -q` | `backend/`, venv active | FAIL | 1 | AC16/AC19 regressions caught: consultation aliases and release timeline fields. |
| `ruff format .; ruff check .; pytest -q app/tests/unit/test_consultation_request_schema.py app/tests/integration/test_consultation_catalogue.py app/tests/integration/test_consultation_third_party.py app/tests/integration/test_consultations_router.py tests/integration/test_admin_llm_catalog.py::test_admin_llm_release_timeline_returns_snapshot_history_and_proofs tests/integration/test_admin_llm_catalog.py::test_admin_llm_release_timeline_keeps_unmapped_backend_events_explicit` | `backend/`, venv active | PASS | 0 | 24 passed after restoring exact alias and timeline behavior. |
| `pytest -q` | `backend/`, venv active | PASS | 0 | 3107 passed, 12 skipped. |
| `ruff check .` | `backend/`, venv active | PASS | 0 | All checks passed after full tests. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\converge-api-v1-route-architecture --final` | repo root, venv active | PASS | 0 | CONDAMAD validation PASS. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local long-running server start | no | FastAPI app was imported and OpenAPI generated repeatedly by tests; full suite passed. | Low. | `app.openapi()` exercised in architecture and integration tests. |

## DRY / No Legacy evidence

- No compatibility wrapper or re-export module was added for old moved Python paths.
- Old moved route modules are deleted and guarded by negative import tests.
- Error envelope models are defined only in `schemas/common.py`.
- Shared constants tracked by AC14 are defined only in `constants.py`.
- API v1 schema files live only in `schemas/common.py` or `schemas/routers/<surface>`.
- `rg -n "^[A-Z][A-Z0-9_]+\\s*[:=]" app/api --glob "*.py"` reports tracked constants only in `app/api/v1/constants.py`.
- `rg -n "select\\(|db\\.execute\\(|db\\.commit\\(|db\\.rollback\\(" app/api/v1/routers/ops/entitlement_mutation_audits.py app/api/v1/routers/admin/llm/prompts.py` is classified in `service-boundary-audit.md`; target list flow is now delegated.
- `rg -n "prefix=\"/v1/ops" app/api/v1/routers/b2b app/api/v1/routers/public`: no hits.
- `rg -n "prefix=\"/v1/b2b" app/api/v1/routers/public app/api/v1/routers/ops`: no hits.
- `rg -n "APIRouter\|import \*" app/api/v1/router_logic`: no hits.
- `rg -n "from app\.api\.v1\.routers\." app/api/v1/schemas app/api/v1/router_logic app/api/v1/routers`: only `__init__.py` registries and documented `admin/llm/observability.py`.
- Old path scans for `public.enterprise_credentials` and `b2b.(reconciliation|entitlement_repair|entitlements_audit)` hit only architecture guard expected references.
- Generated-client scan found no generated client; operationId hits are only the OpenAPI baseline test.

## Diff review

- `git diff --stat`: route/schema/helper moves, architecture tests, OpenAPI contract, capsule evidence.
- `git diff --check`: PASS; CRLF warnings only.
- Unrelated/pre-existing dirty file: `backend/horoscope.db`.

## Final worktree status

- `git status --short` includes expected story changes plus pre-existing `M backend/horoscope.db`.
- Git emitted permission warnings for pytest artifact temp directories during status; no story files were blocked.

## Remaining risks

- `backend/horoscope.db` was dirty before work began and remains dirty; review should avoid attributing it to this story without separate DB diff evidence.
- The `admin/llm/observability.py` import from `prompts.py` remains as an exact registry exception; extracting those handlers would be a separate cleanup.
- AC18 is satisfied for the newly targeted flow and documented with limitations: several older endpoints in the two large route files still contain direct DB orchestration and should be reviewed as follow-up service extraction candidates.

## Suggested reviewer focus

- Verify canonical module moves and absence of old Python import compatibility.
- Review `router_logic` wildcard removal for any accidental import omission, although Ruff and full tests passed.
- Review OpenAPI baseline coverage for moved routes.
- Review the AC18 limitation in `service-boundary-audit.md` and decide whether the remaining direct DB orchestration should become a separate story.
