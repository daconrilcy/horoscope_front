# Implementation Review - CS-277 replay-snapshot-v1-storage-security-model

Verdict: CLEAN

## Review Scope

- Story: `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/00-story.md`
- Source brief: `_story_briefs/cs-277-define-replay-snapshot-v1-storage-and-security-model.md`
- Tracker row: `_condamad/stories/story-status.md` row `CS-277`
- Implementation surfaces:
  - `docs/architecture/replay-snapshot-v1-storage-security-model.md`
  - `backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py`
  - `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/evidence/**`
  - `_condamad/stories/CS-277-replay-snapshot-v1-storage-security-model/generated/**`

## Review Cycle

- Iteration 1: implementation review found stale review/status evidence only.
- Fix batch: refreshed this implementation review artifact, changed story header status to `done`, updated tracker status to `done`, and refreshed validation evidence.
- Iteration 2: fresh implementation review found no actionable issue.
- Final brief-alignment pass: found missing persisted source checklist evidence; added `evidence/source-checklist.md` and refreshed AC11 evidence.

## Acceptance Criteria Alignment

- AC1: storage model exists at `docs/architecture/replay-snapshot-v1-storage-security-model.md` and starts with a French global comment.
- AC2: minimal stored content names calculation identity, input reconstruction reference, version identity, provenance, diagnostics link and AI audit link.
- AC3: forbidden data and masking policy cover raw birth data, exact coordinates, identifiers, raw prompts, raw model payloads and secrets.
- AC4: access is limited to CS-270/CS-271 role vocabulary, with public, client, marketing and unmapped roles denied.
- AC5: retention is explicitly blocked by `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`, with implementation surfaces held back.
- AC6: purge behavior covers expiry, manual deletion, linked diagnostics and linked AI audit records without cascade deletion.
- AC7: diagnostics links remain metadata references and stay separate from `admin_chart_diagnostics_v1` payloads.
- AC8: AI audit links remain metadata references and do not merge narrative answer audit records.
- AC9: route, OpenAPI and TestClient checks confirm no runtime exposure of `replay_snapshot_v1`.
- AC10: targeted runtime scan shows no CS-277 replay symbol under `backend/app`, `frontend/src` or `backend/migrations`.
- AC11: source-checklist, validation, app-surface and final evidence artifacts are persisted in the CS-277 capsule.

## Validation Results

- `ruff format backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py`: PASS, file unchanged.
- `ruff check backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py`: PASS.
- `python -B -m pytest -q backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py --tb=short`: PASS, 5 passed.
- `python -B -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"` from `backend`: PASS.
- `python -B -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"` from `backend`: PASS.
- `rg -n "replay_snapshot_v1" backend\app frontend\src backend\migrations ...`: PASS, exit code 1/no matches.
- `git status --short -- backend\app frontend\src`: PASS for CS-277 scope; output contains unrelated pre-existing backend/app changes and no frontend/src change.
- `git diff --check -- <CS-277 paths>`: PASS.

All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Skipped Checks

- Full `ruff check .`: not run because this story changes one scoped Python test and the worktree already contains many unrelated dirty files.
- Full `pytest -q`: not run for the same dirty-worktree isolation reason; targeted tests and loaded FastAPI runtime checks cover CS-277.
- Local server start: not run because CS-277 is documentation/test only; the FastAPI app loads through `app.openapi()`, `app.routes` and TestClient.

## Guardrails And Runtime Neutrality

- RG-002: route and OpenAPI checks confirm no replay route exposure.
- RG-047 and RG-052: frontend is out of scope; scoped status shows no `frontend/src` change.
- No replay route, service, builder, DB model, migration, frontend UI, generated client, fallback storage path or compatibility alias was added.

## Propagation

- no-propagation: the correction was local to stale CS-277 status/review evidence and does not reveal reusable guardrail or skill learning.

## Residual Risk

- Retention remains intentionally blocked by `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`; any future runtime replay implementation must stay blocked until DPO/security approval exists.
