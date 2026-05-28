<!-- Commentaire global: rapport specialise CS-360 sur la surface admin manual execution provider-capable. -->

# Admin Manual Execution Provider-Capable Audit - CS-360

Domain closure status: `open`.

Primary recommendation: `migrate`.

## Resume executif

La surface auditee est strictement admin-only dans le backend courant et provider-capable. Elle n'est pas une simple CRUD de sample payload: `execute_admin_catalog_sample_payload` reconstruit une execution runtime depuis un sample payload admin, cree un `LLMExecutionRequest`, puis appelle `LLMGateway.execute_request`.

La decision recommandee est `migrate`: conserver la capacite admin-only de test manuel, mais migrer les carriers natals de sample payload hors `chart_json` avant de documenter cette surface comme supportee durablement. `chart_json` est aujourd'hui tolerable comme carrier admin temporaire dans les samples et fixtures existants, mais c'est une cible de migration pour l'execution live provider.

Findings actifs: F-001, F-002, F-003, F-004. Prior finding CS-353 F-003 est `still-active`, avec evidence courante plus precise.

## Scope And Method

Audit target: `admin-manual-llm-execution`.

Archetype: custom audit with API adapter, contract-shape, entitlement/policy, observability, No Legacy and DRY dimensions.

Read-only constraint: no backend runtime, backend test, frontend, database, migration or provider behavior was changed.

## Prior Audit And Story History Consulted

| Source | Status | Current classification | Evidence |
|---|---|---|---|
| CS-353 audit F-003 | Admin manual execution policy decision was blocked | `still-active` | E-005, E-007, E-015 |
| CS-350 cartography | Admin manual execution listed admin-only provider-capable and policy-open | `still-active` until CS-360 follow-up | E-004 |
| RG-149 | Requires explicit classification of provider-capable admin path | `active guardrail` | E-003 |
| CS-359 event_guidance removal | Adjacent legacy `chart_json` decision closed for event_guidance | `closed non-domain context` | E-004 |

## Trace route -> sample payload -> gateway

| Step | Surface | Evidence | Provider capability | Exposure | Decision |
|---|---|---|---|---|---|
| Route constant | `backend/app/core/api_constants.py::ADMIN_MANUAL_EXECUTE_ROUTE_PATH` | E-006 | Provider-capable when handler executes | Admin route namespace | keep route only under admin namespace |
| Router registration | `backend/app/api/v1/routers/registry.py` | E-008 | Route is included in canonical API v1 router registry | Backend API route | keep canonical registration; no alias |
| Handler | `backend/app/api/v1/routers/admin/llm/prompts.py::execute_admin_catalog_sample_payload` | E-007 | Calls `LLMGateway.execute_request` | `Depends(require_admin_user)` | migrate carrier, keep admin-only |
| Runtime preview prerequisite | `_build_admin_resolved_catalog_view(... inspection_mode="runtime_preview")` | E-007, E-011 | Blocks incomplete preview before provider call | Admin-only | keep separation from CRUD |
| Sample payload load | `get_sample_payload(db, payload.sample_payload_id)` | E-007 | Not provider-capable alone | Admin-only | classify as execution input |
| Context construction | `ExecutionContext(extra_context=extra_ctx)` | E-007 | Provider material can include sample fields | Admin-only | migrate legacy fields |
| Gateway handoff | `LLMExecutionRequest` -> `LLMGateway.execute_request` | E-007, E-015 | Provider-capable live execution | Admin-only | supported only after migration |

## Matrice permissions logs et audit

| Surface | Evidence | Provider capability | Exposure | Risk | Decision |
|---|---|---|---|---|---|
| `require_admin_user` on execute handler | E-007, E-012, E-015 | Allows provider execution only after admin dependency | admin-only | role bypass would be high impact | preserve and guard |
| 401 without token | E-012, E-015 | No provider call | denied | proves unauthenticated denial | preserve |
| 403 without admin role | E-012, E-015 | No provider call | denied | proves non-admin denial | preserve |
| Frontend admin client | E-014 | Can trigger backend provider call | admin UI caller | indirect exposure exists through admin frontend only | keep as admin-only; do not promote public |
| Start/success/failure logs | E-013 | Observes provider execution lifecycle | internal logs | no policy status field | add after migration |
| Audit event `llm_catalog_execute_sample` | E-013, E-015 | Observes execution result | audit storage | policy classification missing | add policy metadata |
| Response redaction | E-013, E-015 | Protects prompt/raw/structured output returned to admin | admin API response | redaction failure returns placeholder | preserve |

## Matrice sample payloads et carriers legacy

| Surface | Evidence | Carrier | Provider capability | Exposure | Risk | Decision |
|---|---|---|---|---|---|---|
| Sample payload CRUD routes | E-010, E-015 | arbitrary JSON with sensitive-key validation | CRUD-only | admin-only | can store provider input material | keep separate from execution |
| Natal sample validation | E-010, E-015 | `chart_json` required | CRUD-only until selected for execution | admin-only | legacy carrier remains required | migrate |
| Runtime preview with sample payload | E-011, E-015 | sample fields resolve placeholders | not live provider call by itself | admin-only | can hide execution-readiness issue | keep preview prerequisite |
| Manual execution context | E-007 | sample payload copied into `extra_context` | provider-capable | admin-only | sends legacy carrier to gateway if template uses it | migrate |
| Execute response structured output | E-013, E-015 | provider output sanitized | post-provider | admin-only | sensitive output leakage if sanitizer regresses | guard existing tests |
| Test fixtures | E-015 | `chart_json` examples | test-only | test-only | can be mistaken as runtime truth | retain as classified tests until migration updates them |

`chart_json` classification: `migration target`. It is necessary under current natal sample validation, but should not be accepted as the durable live provider execution carrier for admin manual execution.

## Decision recommandee

Primary decision: `migrate`.

Rejected alternatives:

- `document`: rejected as primary because it would freeze `chart_json` as a supported admin execution carrier.
- `restrict`: rejected as primary because current admin-only restrictions and denial tests are already present; restriction alone does not close the legacy carrier.
- `decommission`: rejected as primary because tests and frontend admin workflow prove an intentional admin operator tool, and no source demands removal.

Policy after migration:

- admin manual execution remains admin-only;
- provider execution remains possible for admin QA/ops;
- sample payload CRUD remains separate from live provider execution;
- live execution no longer depends on natal `chart_json`;
- audit events include the policy classification.

## Stories candidates d'implementation

| Candidate | Findings | Decision | Closure |
|---|---|---|---|
| SC-001 `migrate-admin-manual-execution-sample-payload-carriers` | F-001, F-002 | migrate | full closure if no production data blocker |
| SC-004 `remove-chart-json-requirement-from-admin-sample-payloads` | F-002 | migrate carrier removal | full closure for the concrete validation requirement if replacement carrier is accepted |
| SC-002 `add-admin-manual-execution-policy-audit-metadata` | F-003 | migrate follow-up | full closure after SC-001 |
| SC-003 `guard-admin-manual-execution-admin-only-provider-capable-policy` | F-004 | guard | full closure after SC-001 |

Detailed candidate contracts are in `03-story-candidates.md`.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/core/api_constants.py::ADMIN_MANUAL_EXECUTE_ROUTE_PATH` | used | E-006, E-008 | Shared route contract used by router, middleware and tests. | None. |
| `backend/app/api/v1/constants.py::ADMIN_MANUAL_EXECUTE_ROUTE_PATH` | intentional-public-export | E-006 | API v1 constants module re-exports shared route constants for router/test contract. | Intent inferred from import/export usage, not a separate docstring. |
| `backend/app/api/v1/routers/admin/llm/prompts.py::execute_admin_catalog_sample_payload` | used | E-007, E-008, E-015 | Runtime admin route handler; provider-capable through gateway call. | No real provider call executed. |
| `backend/app/services/api_contracts/admin/llm/prompts.py::AdminCatalogManualExecutePayload` | used | E-009, E-015 | Request contract for execute-sample route. | None. |
| `backend/app/services/api_contracts/admin/llm/prompts.py::AdminCatalogManualExecuteResponseData` | used | E-009, E-013, E-015 | Response contract for execute-sample route and helper. | None. |
| `backend/app/services/api_contracts/admin/llm/prompts.py::AdminCatalogManualExecuteResponse` | used | E-009 | Route response model. | None. |
| `backend/app/services/llm_generation/admin_manual_execution.py::_build_admin_manual_execute_response_payload` | used | E-013, E-015 | Builds admin response with anonymization/sanitization. | Private helper but used by route and tests. |
| `backend/app/services/llm_generation/admin_manual_execution.py::_record_admin_manual_execution_audit` | used | E-013, E-015 | Records success/failure audit event for manual execution. | Storage implementation of `AuditService` not re-audited. |
| `backend/app/services/llm_generation/admin_sample_payloads.py::_validate_payload_json` | used | E-010, E-015 | Owns sample payload validation including sensitive keys and current `chart_json` requirement. | Policy target remains open until migration. |
| `backend/app/api/v1/routers/admin/llm/sample_payloads.py` routes | used | E-010, E-015 | Admin CRUD owner for sample payloads, separated from live provider execution. | No deletion candidate. |
| `backend/app/services/llm_generation/admin_prompts.py` runtime preview sample handling | used | E-011, E-015 | Resolves sample payload values for runtime preview and guards inactive/mismatch cases. | Inspected only for sample path, not full admin prompts domain. |
| `backend/tests/integration/test_admin_llm_catalog.py` execute-sample tests | test-only | E-012, E-013, E-015 | Owns integration coverage for runtime preview, mocked gateway execution, denial and failure paths. | Integration suite requires `--long`. |
| `backend/tests/integration/test_admin_llm_sample_payloads.py` | test-only | E-010, E-015 | Owns CRUD and sample validation coverage. | Integration suite requires `--long`. |
| `backend/tests/unit/test_admin_manual_execute_response.py` | test-only | E-013 | Owns response redaction/anonymization helper coverage. | Not part of targeted integration command. |
| `frontend/src/api/admin-prompts/index.ts::executeAdminCatalogSamplePayload` | out-of-domain | E-014 | Inspected only to classify indirect admin UI exposure; frontend changes out of scope. | Authorization UX not audited. |
| `frontend/src/tests/AdminPromptsPage.test.tsx` execute-sample tests | out-of-domain | E-014 | Confirms admin UI has a confirmation + POST flow; out of backend audit domain. | Frontend test not executed in this audit. |

## Closure Analysis

Active in-domain findings after current implementation: F-001, F-002, F-003, F-004. The audit decision is no longer blocked; the remaining work is implementation of the selected `migrate` policy and its guardrails.

Closed findings: none from this audit, because the deliverable is a policy audit and no implementation changes were authorized.

Prior finding status:

- CS-353 F-003: `still-active`; current evidence confirms and narrows it.
- CS-359 event_guidance legacy carrier: `closed non-domain context`; it does not keep this audited domain open.

Exhaustive implementation surfaces for active findings:

- F-001/F-002: `backend/app/services/llm_generation/admin_sample_payloads.py`, `backend/app/services/llm_generation/admin_prompts.py`, `backend/app/api/v1/routers/admin/llm/prompts.py`, contracts under `backend/app/services/api_contracts/admin/llm/`, and tests under `backend/tests/integration/test_admin_llm_catalog.py`, `backend/tests/integration/test_admin_llm_sample_payloads.py`.
- F-003: `backend/app/services/llm_generation/admin_manual_execution.py`, `backend/tests/integration/test_admin_llm_catalog.py`.
- F-004: architecture guard/test file to be selected by implementation story, plus `_condamad/stories/regression-guardrails.md` after durable invariant creation.

Governance/test files are separate from implementation files. Frontend and production data migration are deferred non-domain concerns unless the implementation story explicitly includes them.

## Validation

Executed:

```powershell
. .\.venv\Scripts\Activate.ps1
pytest -q --long backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py
```

Result: `40 passed in 3.09s`.

Executed:

```powershell
. .\.venv\Scripts\Activate.ps1
python -S -B -c "import subprocess; out=subprocess.check_output(['git','status','--short','backend/app','backend/tests','frontend/src'], text=True); print(out, end=''); assert out.strip()==''"
```

Result: PASS, no backend app/test/frontend source changes.

Skipped:

- Real provider call: forbidden by story.
- Runtime code changes and migrations: forbidden by story.
