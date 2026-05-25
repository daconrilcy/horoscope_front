# Source Checklist — CS-275-admin-chart-diagnostics-policy

## Brief source

- `_story_briefs/cs-275-decide-admin-chart-diagnostics-retention-redaction-replay-policy.md` read.
- Objective covered: decide retention, redaction and replay policy before `admin_chart_diagnostics_v1` implementation.
- Included work covered: diagnostic data, masked data, retention or DPO-open state, replay prerequisites and admin consultation logs.
- Out-of-scope preserved: no diagnostic implementation, no replay implementation, no calculation change and no client exposure.

## Repository sources

- `docs/architecture/product-architecture-current-state-2026-05-24.md` inspected for admin debug and replay blockers.
- `docs/architecture/official-product-primitives-public-projections.md` inspected for public projection exclusion.
- `backend/app/core/sensitive_data.py` reused as the sensitive birth-data classification owner.
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` reused for trace and replay separation.
- CS-271 and CS-272 dependency ownership preserved for permissions and admin endpoint segmentation.

## Implementation coverage

- `docs/architecture/admin-chart-diagnostics-v1-policy.md` records the canonical policy.
- `backend/tests/unit/test_admin_chart_diagnostics_policy.py` verifies contract fields, sensitive data, replay separation and runtime neutrality.
- `evidence/validation.txt` records targeted validation commands.
- `evidence/app-surface-status.txt` records forbidden surface and runtime neutrality checks.

## Review note

- Source checklist added during implementation review iteration 1 because the story named it as persistent evidence and it was missing.
