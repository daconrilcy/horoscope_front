<!-- Commentaire global: synthese courte de l'audit CS-360 admin manual execution provider-capable. -->

# Executive Summary - CS-360 Admin Manual Execution

Decision recommandee: `migrate`.

The audited surface is admin-only and provider-capable. The backend route `POST /v1/admin/llm/catalog/{manifest_entry_id}/execute-sample` is mounted from the canonical admin LLM router, requires `require_admin_user`, builds a `LLMExecutionRequest` from a sample payload, and calls `LLMGateway.execute_request`.

Sample payload CRUD is separate from live execution. CRUD validates and persists admin sample payloads and records audit events, but does not call the provider. Live manual execution reuses a runtime preview, copies the sample payload into `ExecutionContext.extra_context`, and can therefore send legacy sample material to the gateway.

`chart_json` remains required for natal admin sample payloads. That makes it tolerable only as a temporary admin/test carrier, not a stable supported provider-execution contract.

Findings by severity:

- High: 2 findings, selected migration policy not implemented and `chart_json` legacy carrier in live admin execution.
- Medium: 2 findings, policy metadata absent from audit events and exact anti-promotion guard missing.

Validation:

- `pytest -q --long backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py` -> `40 passed`.
- Bounded app/test/frontend status guard passed.

Recommended next action: write an implementation story from SC-001 to migrate admin manual execution samples away from natal `chart_json` while preserving admin-only provider-capable behavior.
