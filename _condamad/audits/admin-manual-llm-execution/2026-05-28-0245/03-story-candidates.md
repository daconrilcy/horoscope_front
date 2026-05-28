<!-- Commentaire global: propositions de stories candidates issues de l'audit CS-360. -->

# Story Candidates - CS-360 Admin Manual Execution

Primary recommendation label: `migrate`.

## SC-001 - Migrate Admin Manual Execution Away From Natal `chart_json`

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: `migrate-admin-manual-execution-sample-payload-carriers`
- Suggested archetype: implementation / No Legacy migration
- Primary domain: admin-manual-llm-execution
- Required contracts: Runtime Source of Truth, Ownership Routing, No Legacy, Contract Shape, Reintroduction Guard, Persistent Evidence
- Draft objective: keep `execute-sample` admin-only and provider-capable, but migrate natal admin manual execution samples/templates away from prompt-visible `chart_json`.
- Closure intent: `full-closure` for F-001 and F-002 if no production data migration blocker is found.
- Must include: inventory active sample payload templates and fixture data; introduce an explicit non-legacy carrier or `llm_astrology_input_v1`-aligned admin sample contract; update validation/tests; keep sample CRUD separate from live execution; block public promotion.
- Validation hints: `pytest -q --long backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py`; targeted scans for `execute_admin_catalog_sample_payload`, `AdminCatalogManualExecute`, `chart_json`, `LLMGateway`; bounded status guard on `backend/app`, `backend/tests`, `frontend/src`.
- Blockers: stop if product wants decommission instead of migration, or if production samples contain `chart_json` values that require manual data cleanup.

## SC-004 - Remove Natal `chart_json` Requirement From Admin Samples

- Candidate ID: SC-004
- Source finding: F-002
- Suggested story title: `remove-chart-json-requirement-from-admin-sample-payloads`
- Suggested archetype: legacy-carrier-removal
- Primary domain: admin-manual-llm-execution
- Required contracts: No Legacy, Runtime Source of Truth, Contract Shape, Reintroduction Guard
- Draft objective: close the concrete carrier finding by replacing the natal `chart_json` requirement in admin sample payload validation and tests.
- Closure intent: `full-closure`
- Must include: exact replacement carrier rule, update sample validation, update runtime preview tests, classify any remaining `chart_json` hit.
- Validation hints: `pytest -q --long backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py`; `rg -n "chart_json" backend/app/services/llm_generation/admin_sample_payloads.py backend/tests/integration/test_admin_llm_sample_payloads.py backend/tests/integration/test_admin_llm_catalog.py`.
- Blockers: stop if no replacement carrier is accepted by product/runtime owner.

### Exhaustive Files To Modify

Implementation files:

- `backend/app/services/llm_generation/admin_sample_payloads.py`
- `backend/app/services/llm_generation/admin_prompts.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/services/api_contracts/admin/llm/sample_payloads.py` if contract shape changes
- `backend/app/services/api_contracts/admin/llm/prompts.py` if execution response metadata changes

Governance/test files:

- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/integration/test_admin_llm_sample_payloads.py`
- `backend/tests/unit/test_admin_manual_execute_response.py`
- `_condamad/stories/regression-guardrails.md` only after a durable invariant exists

Deferred non-domain files:

- `frontend/src/**` only if user-facing admin wording or form validation must change after backend contract migration.

Before/after evidence:

- Before: current `rg` hits for `chart_json` in admin sample payloads and execute-sample tests.
- After: zero or explicitly allowlisted `chart_json` hits in live admin manual execution carrier paths; retained historical/test hits must be classified.

No-wildcard allowlist and No Legacy checks:

- No broad folder allowlist.
- Any remaining `chart_json` hit must be exact-path classified as historical, test-only, or non-provider material.

Stop condition:

- The finding closes when `execute-sample` can execute provider calls from non-legacy admin samples and no live admin manual execution path requires `chart_json`.

## SC-002 - Persist Policy Classification In Manual Execution Audit Events

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: `add-admin-manual-execution-policy-audit-metadata`
- Suggested archetype: observability-guard-hardening
- Primary domain: admin-manual-llm-execution
- Required contracts: Runtime Source of Truth, Contract Shape, Reintroduction Guard
- Draft objective: include the implemented policy status in `llm_catalog_execute_sample` audit details.
- Closure intent: `full-closure`
- Must include: add an exact metadata key such as `policy_status: "migrated"` after SC-001, and tests for success and failure audit events.
- Validation hints: targeted tests in `backend/tests/integration/test_admin_llm_catalog.py`; scan `llm_catalog_execute_sample|policy_status|admin_catalog_manual_execute_sample`.
- Blockers: do not implement before SC-001 or an alternate policy decision defines the allowed vocabulary.

### Exhaustive Files To Modify

Implementation files:

- `backend/app/services/llm_generation/admin_manual_execution.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py` only if route-owned details are changed

Governance/test files:

- `backend/tests/integration/test_admin_llm_catalog.py`

Deferred non-domain files:

- none.

## SC-003 - Add Exact Guard For Admin-Only Provider-Capable Classification

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: `guard-admin-manual-execution-admin-only-provider-capable-policy`
- Suggested archetype: architecture-guard-hardening
- Primary domain: admin-manual-llm-execution
- Required contracts: Reintroduction Guard, No Legacy, Ownership Routing
- Draft objective: prevent accidental public promotion or carrier regression of `execute-sample`.
- Closure intent: `full-closure`
- Must include: deterministic guard for route path, `require_admin_user`, admin frontend-only caller, response header, no new public route alias, and post-migration carrier classification.
- Validation hints: architecture/unit guard plus `rg` scans for `execute-sample`, `ADMIN_MANUAL_EXECUTE_ROUTE_PATH`, `require_admin_user`, `chart_json`.
- Blockers: wait until SC-001 defines final carrier policy; otherwise the guard would freeze a transitional state.

### Exhaustive Files To Modify

Implementation files:

- none required unless adding a reusable guard helper is justified.

Governance/test files:

- `backend/app/tests/unit/test_api_router_architecture.py` or an adjacent exact architecture guard
- `_condamad/stories/regression-guardrails.md`

Deferred non-domain files:

- none.

## Deferred Non-Domain Context

- Frontend UX wording and admin confirmation flow are downstream of the backend policy decision. They do not keep this audit open.
- Production database sample migration may require an infra/data migration story if live rows with `chart_json` exist; this audit did not inspect production data.
