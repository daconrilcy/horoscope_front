# Target Files

## Inspected Before Implementation

- `AGENTS.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md`
- `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md` targeted IDs: RG-002, RG-047, RG-052
- `_condamad/stories/CS-270-internal-role-model/00-story.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md`
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/00-story.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
- `backend/app/core/sensitive_data.py`
- `backend/app/infra/db/models/llm/llm_canonical_perimeter.py`
- Existing docs/tests near admin role and diagnostics contracts.

## Modified Files

- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/generated/04-target-files.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/generated/06-validation-plan.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/generated/10-final-evidence.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/source-checklist.md`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/validation.txt`
- `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/app-surface-status.txt`
- `_condamad/stories/story-status.md`

## Forbidden Or High-Risk Files

These surfaces were intentionally left without CS-277 edits:

- `backend/app/**`
- `backend/migrations/**`
- `frontend/src/**`
- generated clients
- public OpenAPI contracts
