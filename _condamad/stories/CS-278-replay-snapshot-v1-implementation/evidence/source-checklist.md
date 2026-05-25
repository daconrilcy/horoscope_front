# Source Checklist - CS-278

- PASS: Story-status row for `CS-278` points to `_condamad/stories/CS-278-replay-snapshot-v1-implementation/00-story.md`.
- PASS: Story-status row for `CS-278` points to `_story_briefs/cs-278-implement-replay-snapshot-v1-if-approved.md`.
- PASS: Source story requires CS-277 approval before implementation and requires a stop when retention, access, storage, purge or redaction policy remains undecided.
- BLOCKED: CS-277 is marked `done`, but the canonical contract `docs/architecture/replay-snapshot-v1-storage-security-model.md` records `approval_state` as `non approuve`.
- BLOCKED: CS-277 final evidence states retention remains blocked by `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001` and CS-278 must not implement runtime replay until DPO/security approval exists.
- PASS: Existing replay owners were found under `backend/app/ops/llm`, `backend/app/services/llm_observability`, `backend/app/infra/db/models/llm`, `backend/app/core/sensitive_data.py` and `backend/app/domain/audit/safe_details.py`.
