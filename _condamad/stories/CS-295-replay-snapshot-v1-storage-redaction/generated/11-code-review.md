# Implementation Review CS-295 replay-snapshot-v1-storage-redaction

Verdict: CLEAN

## Scope

- Reviewed story: `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`.
- Source brief: `_story_briefs/cs-295-implement-replay-snapshot-v1-storage-redaction.md`.
- Tracker row: `_condamad/stories/story-status.md`, path and source brief matched CS-295.
- Review mode: implementation review after backend changes and persisted CONDAMAD evidence.

## Alignment Checks

- AC1 owner reuse: `LlmReplaySnapshotModel` and `llm_replay_snapshots` remain the single replay snapshot owner.
- AC2 schema: approved v1 fields are on the existing model and migration.
- AC3 retention: new snapshots derive `expires_at` from `created_at + 30 days`.
- AC4 and AC5 redaction: inspectable metadata and DB scan exclude raw forbidden values; encrypted payload boundary remains isolated.
- AC6 migration: Alembic head and SQLAlchemy metadata include the required replay snapshot columns.
- AC7 purge: expired replay snapshots are deleted without deleting unrelated active call logs.
- AC8 exposure: no `replay_snapshot_v1` public route, OpenAPI path, frontend route or generated client exposure was added.
- AC9 evidence: source, schema, redaction, runtime and validation evidence files are present.

## Findings

- Fixed: encrypted replay payload still preserved raw user-authored prompt text and raw birth data after decryption. This contradicted the
  source brief and DPO/security model, which require stored content to be limited to references, hashes, versions and approved metadata.
  `Sink.LLM_REPLAY_SNAPSHOTS` now hashes direct identifiers, correlable identifiers, user-authored content, birth data and exact coordinates
  before encryption; provider secrets remain forbidden.

## Validation Results

- PASS: `ruff check .` from `backend`.
- PASS: CS-295 owner, storage, redaction, retention, purge, DB redaction and DB invariant pytest set from `backend`.
- PASS: `ruff format --check .` from `backend`.
- PASS: `python -B -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"` from `backend`.
- PASS: `python -B -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"` from `backend`.
- PASS: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\00-story.md`.
- PASS: `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\00-story.md`.
- PASS: `git diff --check`.
- PASS after fix: CS-295 redaction, storage and DB redaction pytest set.
- PASS after fix: `ruff check .` from `backend`.
- PASS after fix: CS-295 owner, storage, redaction, retention, purge, DB redaction and DB invariant pytest set.
- PASS after fix: `ruff format --check .` from `backend`.
- PASS after fix: runtime route and OpenAPI guards.
- PASS after fix: brief validation command `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_storage_security_model.py tests\integration --tb=short`.
- PASS after fix: `condamad_story_validate.py`, `condamad_story_lint.py --strict`, `git diff --check`.
- All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Propagation

- no-propagation: no reusable learning or cross-story guardrail update was required.

## Residual Risk

- The encrypted `input_enc` boundary now stores transformed replay input only; no raw prompt, birth data, exact coordinate, direct identifier
  or secret residual risk remains identified for CS-295.
