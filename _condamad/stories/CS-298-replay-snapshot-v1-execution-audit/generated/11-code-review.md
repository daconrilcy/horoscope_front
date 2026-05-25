# Implementation Review CS-298 replay-snapshot-v1-execution-audit

Verdict: CLEAN

Review date: 2026-05-25

## Scope

- Reviewed story: `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/00-story.md`.
- Source brief: `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md`.
- Tracker row: `_condamad/stories/story-status.md` entry `CS-298`.
- Implementation files reviewed: replay service, replay snapshot service, admin audit router, safe audit details, audit sanitization and CS-298 tests.

## Iteration 1 Finding

- Finding: the admin endpoint audited acceptance of replay attempts, but the real provider execution path in
  `backend/app/ops/llm/replay_service.py` did not record `replay_snapshot_v1.replay_attempt` audit events for provider success or provider failure.
- Impact: AC2 was only partially proven; a real replay execution could occur after snapshot validation without the CS-298 audit event.
- Fix: added bounded real execution audit recording through `AuditService.record_event`, with safe details for success, snapshot refusal,
  integrity mismatch and provider failure. Updated audit sanitization to allow only operational replay diff keys and to avoid allowing
  `payload_enc` as generic audit metadata.
- Proof: `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py` now proves real `replay()` success and provider failure audit events
  without raw provider output in the audit details.

## Fresh Review Result

- Brief alignment: PASS.
- Tracker path and brief source alignment: PASS.
- AC1 metadata read audit: PASS.
- AC2 replay attempt audit: PASS for admin acceptance and real `replay()` execution success/failure.
- AC3 purge outcome audit: PASS.
- AC4 unsafe snapshot refusal before provider execution: PASS.
- AC5 audit non-leakage: PASS with classified scan hits only in test constants, masked admin email paths and purge tombstone assignment.
- AC6 internal admin API wiring: PASS.
- AC7 bounded replay execution ownership: PASS.
- AC8 reproducibility evidence: PASS.
- AC9 persisted evidence artifacts: PASS.

## Validation

- PASS: `ruff format .` from `backend`.
- PASS: `ruff check .` from `backend`.
- PASS: `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py tests\unit\test_replay_snapshot_v1_service_audit.py tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_replay_snapshot_v1_execution_boundary.py --tb=short` -> 18 passed.
- PASS: OpenAPI admin-only replay path check.
- PASS: runtime absence check for `/replay_snapshot_v1`.
- PASS: app import/startup smoke check.
- PASS: scoped sensitive scan with classified non-issue hits.
- PASS: `python -B -m pytest -q tests\unit tests\integration tests\api\admin --tb=short` -> 828 passed, 215 deselected.
- PASS: `python -B -m pytest -q --tb=short` -> 3421 passed, 1 skipped, 1216 deselected.
- PASS: `git diff --check`.
- PASS: `condamad_story_validate.py`.
- PASS: `condamad_story_lint.py --strict`.

All Python validation commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Propagation

No-propagation: the correction is local to CS-298 replay execution audit behavior and its bounded audit sanitization keys.

## Residual Risk

Aucun risque restant identifie.
