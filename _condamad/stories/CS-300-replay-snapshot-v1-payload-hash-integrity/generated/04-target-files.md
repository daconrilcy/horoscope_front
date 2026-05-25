# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg -n "create_snapshot|compute_input_hash|encrypt_input|sanitized_input|input_hash" backend\app\services\replay_snapshot_v1_service.py
rg -n "compute_input_hash|decrypt|input_hash|input_hash_mismatch|replay_snapshot" backend\app\ops\llm\replay_service.py
rg -n "encrypt_input\(user_input\)|log_call|create_snapshot|input_hash_mismatch" backend\tests\unit\test_replay_snapshot_v1_execution_audit.py
git diff --stat -- <story paths>
git diff --name-only -- <story paths>
```

Adapt searches to the story and repository layout.

## Likely modified files

- `backend/app/services/replay_snapshot_v1_service.py`
- `backend/app/ops/llm/replay_service.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/core/sensitive_data.py`
- `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_db_redaction.py`
- `backend/tests/unit/test_replay_snapshot_v1_storage.py`
- `backend/tests/unit/test_replay_snapshot_v1_redaction.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_retention.py`
- `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity/**`

## Forbidden or high-risk files

- `frontend/**` out of scope.
- `backend/alembic/**` out of scope.
- New public replay routes out of scope.
