# Source Checklist - CS-277 replay_snapshot_v1 storage security model

## Source Brief

- `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md`: inspected.
- Brief objective retained: define what is stored for replay, who can access it and for how long.
- Brief scope retained: minimal snapshot content, forbidden or masked data, permissions, retention/purge, diagnostics link and AI audit link.
- Brief non-goals retained: no replay implementation, no production replay execution, no UI and no RGPD policy change without validation.
- Brief validation retained: document/static scan plus scoped status over `backend/app` and `frontend/src`.

## Dependencies

- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md`: used for diagnostics retention, redaction and replay prerequisite boundary.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md`: used to keep `admin_chart_diagnostics_v1` separate from replay snapshots.
- `_condamad/stories/CS-270-internal-role-model/00-story.md`: used for approved internal role vocabulary.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`: used for admin data-domain permission boundaries and denied marketing access.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`: used to keep narrative answer audit records separate.
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`: used for audit access-log boundary.

## Existing Owners

- `backend/app/core/sensitive_data.py`: reused as the sensitive data classification owner.
- `backend/app/infra/db/models/llm/llm_canonical_perimeter.py`: inspected for existing LLM replay snapshot naming.
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`: selected as the single canonical documentation owner for this story.

## Alignment Result

- PASS: the implementation remains documentation/test only and does not create a route, service, builder, database model, migration, frontend UI or public OpenAPI exposure.
- PASS: retention remains `non approuve` behind `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`, matching the brief risk that the story may conclude blocked by DPO decision.
- PASS: diagnostics and AI audit are referenced by metadata links only and are not merged into replay storage.
