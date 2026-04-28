# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Consumption audit classifies `/api/email/unsubscribe`. | Add `route-consumption-audit.md`; preserve runtime route. | OpenAPI import smoke; `route-consumption-audit.md`; unsubscribe `rg`. | PASS |
| AC2 | The target decision blocks external-active deletion. | Add `decision-record.md` with `needs-user-decision` and blockers for permanence, deletion, and migration. | `rg -n "Decision|User decision|Risk" decision-record.md`. | PASS |
| AC3 | `API_ROUTE_MOUNT_EXCEPTIONS` reflects the selected decision exactly. | Update `public_email_unsubscribe` reason/decision text to match the pending explicit decision. | `pytest -q app/tests/unit/test_api_router_architecture.py`. | PASS |
| AC4 | Pending explicit decision preserves route behavior. | No handler/link behavior change. | OpenAPI before/after snapshots; `pytest -q tests/integration/test_email_unsubscribe.py`. | PASS |
| AC5 | Migrate decision makes new links canonical. | Not applicable because selected decision is `needs-user-decision`, not migrate. | Decision record documents no migration approval. | NOT_APPLICABLE |
| AC6 | Delete-approved decision leaves no wrapper. | Not applicable because deletion is blocked by `external-active` classification and no approval. | Decision record documents deletion blocker; no route removal attempted. | NOT_APPLICABLE |
| AC7 | No duplicate active unsubscribe implementation exists. | Preserve single active handler; test route owner through runtime register. | `rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" backend/app`; architecture test. | PASS |
