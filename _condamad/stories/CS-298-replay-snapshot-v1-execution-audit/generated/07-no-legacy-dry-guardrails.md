# No Legacy / DRY guardrails - CS-298

Enforced:
- one audit DTO owner: `app.domain.audit.safe_details`;
- one audit persistence owner: `AuditService.record_event`;
- one replay snapshot lifecycle owner: `ReplaySnapshotV1Service`;
- one provider execution owner: `backend/app/ops/llm/replay_service.py` through the existing runtime gateway;
- no route outside `/v1/admin/audit`;
- no frontend or generated-client surface.

Negative evidence:
- AST guard blocks provider execution from the admin router.
- Runtime route checks block `/replay_snapshot_v1` and public/support variants.
- Touched audit details do not include forbidden raw fields.

Classified existing debt:
- route SQL dependency/commit entries remain in the exact router SQL allowlist because the admin router already owns DB session injection.
- SQLite in-memory factory test path classified in the backend DB harness allowlist.
