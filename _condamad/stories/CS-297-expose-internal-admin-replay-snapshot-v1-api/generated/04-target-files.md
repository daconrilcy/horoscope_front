# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg "<main symbol or feature name>" .
rg "legacy|compat|shim|fallback|deprecated|alias" .
git diff --stat -- <story paths>
git diff --name-only -- <story paths>
```

Adapt searches to the story and repository layout.

## Modified files

- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/services/api_contracts/admin/audit.py`
- `backend/app/services/replay_snapshot_v1_service.py`
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
- `backend/tests/unit/test_admin_endpoint_segmentation_contract.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_ownership.py`
- `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/access-control.txt`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/validation.txt`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/generated/10-final-evidence.md`
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/generated/11-code-review.md`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/src/**`
- `backend/app/api/v1/routers/public/**`
- `backend/app/api/v1/routers/support/**`
- `backend/app/api/v1/routers/registry.py` unless a new router owner is introduced
- `backend/migrations/**`
