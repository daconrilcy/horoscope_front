<!-- Commentaire global: rapport CONDAMAD standard pour l'audit CS-360 admin manual execution. -->

# Audit Report - Admin Manual LLM Execution

Domain closure status: `open`.

Primary recommendation: `migrate`.

This standard CONDAMAD report accompanies the requested specialized deliverable `01-admin-manual-execution-provider-capable-audit.md`.

## Audited Domain

Domain key: `admin-manual-llm-execution`.

Bounded responsibility: classify the admin manual LLM execution route, its sample payload input path, provider capability, permissions, logs/audit events, legacy carrier status and follow-up implementation candidates.

Out of scope: runtime code changes, backend/frontend behavior changes, DB migrations, provider calls, prompt-generation cartography edits and guardrail registry enrichment.

## Executive Summary

The surface is backend admin-only and provider-capable. The route handler requires `require_admin_user`, builds a runtime preview from a selected sample payload, copies that sample payload into `ExecutionContext.extra_context`, constructs `LLMExecutionRequest`, and calls `LLMGateway.execute_request`.

The policy should be `migrate`: do not decommission the admin tool now, and do not merely document the existing `chart_json` carrier. Migrate natal admin sample payloads away from `chart_json` before treating manual execution as a stable supported admin surface.

## Mandatory Audit Dimensions

| Dimension | Verdict | Evidence |
|---|---|---|
| DRY | PASS with migration risk | CRUD and live execution are separate; no duplicate provider execution route found. `chart_json` creates carrier overlap with legacy natal contexts. Evidence: E-007, E-010, E-017. |
| No Legacy | FAIL for carrier policy | Natal sample payloads still require `chart_json`, and live execution copies sample payload fields into gateway context. Evidence: E-007, E-010, E-015. |
| Mono-domain ownership | PASS | Route is owned by admin LLM router; CRUD by sample payload router/service; frontend caller is out-of-domain admin UI. Evidence: E-008, E-010, E-014. |
| Dependency direction | PASS with accepted API orchestration | API handler calls domain gateway and service helpers; services/domain dependency on `app.api` not found for this surface in targeted scans. Evidence: E-007, E-017. |
| Security/policy | OPEN | Admin dependency and denial tests exist; policy decision remains open. Evidence: E-012, E-015. |
| Observability | PARTIAL | Logs/audit events/redaction exist; policy classification missing. Evidence: E-013. |

## Findings

See `02-finding-register.md`.

Summary:

- F-001 High: policy not closed for provider-capable admin execution.
- F-002 High: natal sample payloads still require `chart_json`.
- F-003 Medium: policy status missing from execution audit details.
- F-004 Medium: no exact anti-promotion guard.

## Prior Audit And Story History Consulted

| Prior source | Classification | Current evidence |
|---|---|---|
| `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md` F-003 | `still-active` | E-005, E-007, E-015 |
| `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | `still-active context` | E-004 |
| `_condamad/stories/regression-guardrails.md` RG-149 | `active invariant` | E-003 |
| CS-359 `event_guidance` closure | `non-domain` | E-004 |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/core/api_constants.py::ADMIN_MANUAL_EXECUTE_ROUTE_PATH` | used | E-006, E-008 | Shared route contract used by router, middleware and tests. | None. |
| `backend/app/api/v1/constants.py::ADMIN_MANUAL_EXECUTE_ROUTE_PATH` | intentional-public-export | E-006 | API v1 re-export consumed by admin router/tests. | Intent inferred from source usage. |
| `backend/app/api/v1/routers/admin/llm/prompts.py::execute_admin_catalog_sample_payload` | used | E-007, E-008, E-015 | Runtime admin manual execution route. | No real provider call executed. |
| `backend/app/services/api_contracts/admin/llm/prompts.py::AdminCatalogManualExecutePayload` | used | E-009 | Execute-sample request contract. | None. |
| `backend/app/services/api_contracts/admin/llm/prompts.py::AdminCatalogManualExecuteResponseData` | used | E-009, E-013 | Execute-sample response contract. | None. |
| `backend/app/services/api_contracts/admin/llm/prompts.py::AdminCatalogManualExecuteResponse` | used | E-009 | Route response envelope. | None. |
| `backend/app/services/llm_generation/admin_manual_execution.py::_build_admin_manual_execute_response_payload` | used | E-013, E-015 | Builds redacted admin execution response. | Private helper. |
| `backend/app/services/llm_generation/admin_manual_execution.py::_record_admin_manual_execution_audit` | used | E-013, E-015 | Records execution audit events. | AuditService internals not re-audited. |
| `backend/app/services/llm_generation/admin_sample_payloads.py::_validate_payload_json` | used | E-010, E-015 | Validates sample payloads and current natal `chart_json` requirement. | Target of migration. |
| `backend/app/api/v1/routers/admin/llm/sample_payloads.py` | used | E-010, E-015 | Owns sample payload CRUD. | None. |
| `backend/app/services/llm_generation/admin_prompts.py` sample runtime preview path | used | E-011, E-015 | Resolves sample payload values before live execution. | Full admin prompt module out of scope. |
| `backend/tests/integration/test_admin_llm_catalog.py` | test-only | E-012, E-013, E-015 | Integration coverage for catalog/manual execution. | Requires `--long`. |
| `backend/tests/integration/test_admin_llm_sample_payloads.py` | test-only | E-010, E-015 | Integration coverage for sample payload CRUD/validation. | Requires `--long`. |
| `backend/tests/unit/test_admin_manual_execute_response.py` | test-only | E-013 | Unit coverage for response redaction. | Not run in targeted integration command. |
| `frontend/src/api/admin-prompts/index.ts::executeAdminCatalogSamplePayload` | out-of-domain | E-014 | Admin UI client demonstrates indirect admin exposure only. | Frontend not audited deeply. |
| `frontend/src/tests/AdminPromptsPage.test.tsx` execute-sample coverage | out-of-domain | E-014 | Frontend confirmation/POST test evidence. | Not executed. |

## Closure Analysis

Closure status: `open`, because implementation findings remain.

Active findings after implemented stories: F-001, F-002, F-003, F-004.

Findings now closed: none in this audit.

Complete active implementation surface:

- Backend implementation: `backend/app/api/v1/routers/admin/llm/prompts.py`, `backend/app/services/llm_generation/admin_manual_execution.py`, `backend/app/services/llm_generation/admin_sample_payloads.py`, `backend/app/services/llm_generation/admin_prompts.py`, relevant contracts under `backend/app/services/api_contracts/admin/llm/`.
- Governance/test: `backend/tests/integration/test_admin_llm_catalog.py`, `backend/tests/integration/test_admin_llm_sample_payloads.py`, `backend/tests/unit/test_admin_manual_execute_response.py`, later `_condamad/stories/regression-guardrails.md`.
- Deferred non-domain: frontend admin UX and production data migration, only if selected by a follow-up story.

## Evidence And Validation

Evidence log: `01-evidence-log.md`.

Validation commands run with venv activated:

- `pytest -q --long backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py` -> `40 passed in 3.09s`.
- bounded status guard for `backend/app`, `backend/tests`, `frontend/src` -> PASS.

No real provider call was made.
