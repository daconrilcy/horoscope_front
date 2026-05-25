# Final Evidence — CS-295-replay-snapshot-v1-storage-redaction

## Story status

- Validation outcome: pass
- Ready for review: complete
- Implementation review outcome: CLEAN
- Story key: CS-295-replay-snapshot-v1-storage-redaction
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction`
- Source finding closure status: full-closure

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-295-replay-snapshot-v1-storage-redaction/00-story.md`
- Story registry match: `CS-295` row path and brief source matched.
- Initial `git status --short`: clean for repository before generated repair/code edits.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule generated/repaired: yes, with `condamad_prepare.py --repair-generated-only`, then `condamad_validate.py` PASS.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Target story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by skill helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC9 classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Repaired by skill helper. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Repaired by skill helper. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Repaired by skill helper. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Single owner remains `LlmReplaySnapshotModel` / `llm_replay_snapshots`; no second replay store. | `test_replay_snapshot_v1_ownership.py`; owner `rg` scan. | PASS |
| AC2 | Approved schema fields and JSON metadata shape implemented. | `test_replay_snapshot_v1_storage.py`; model column inspection. | PASS |
| AC3 | New snapshots derive expiry from creation + 30 days. | `test_replay_snapshot_v1_retention.py`. | PASS |
| AC4 | Replay metadata excludes raw prompt, birth data, coordinates, identifiers and secrets. | `test_replay_snapshot_v1_redaction.py`; scoped negative storage scan. | PASS |
| AC5 | Persisted DB row metadata and decrypted replay payload exclude raw sensitive values. | `test_replay_snapshot_v1_db_redaction.py`. | PASS |
| AC6 | Alembic head and model metadata align on replay columns. | `test_llm_db_invariants.py`; `alembic heads` => `20260525_0140 (head)`. | PASS |
| AC7 | Purge deletes expired snapshot row without deleting unrelated active logs. | `test_replay_snapshot_v1_purge.py`. | PASS |
| AC8 | No public route/OpenAPI/frontend exposure. | Runtime `app.routes` and `app.openapi()` guards PASS; `frontend/src` clean. | PASS |
| AC9 | Story evidence persisted. | Evidence files created and capsule validation PASS. | PASS |

## Files changed

- Backend model/service/security: replay model, observability service and `backend/app/core/sensitive_data.py`
- Migration: `backend/migrations/versions/20260525_0140_replay_snapshot_v1_storage_redaction.py`
- Tests/guards: `backend/tests/unit/test_replay_snapshot_v1_*.py`, replay DB redaction, DB invariants and storage-security tests
- Capsule/evidence: CS-295 `generated/**`, CS-295 `evidence/**`, and `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added: CS-295 owner, storage, redaction, retention, purge and DB redaction tests
- Updated: `test_llm_db_invariants.py`, `test_replay_snapshot_v1_storage_security_model.py`, `test_backend_db_test_harness.py`

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --repair-generated-only ...` | repo root | PASS | Missing generated capsule files repaired. |
| `condamad_validate.py` | repo root | PASS | Capsule structure valid. |
| `ruff format <changed python files>` | `backend` | PASS | Scoped formatting done. |
| `ruff check .` | `backend` | PASS | Full backend lint passed. |
| CS-295 targeted pytest set | `backend` | PASS | `8 passed, 19 deselected`. |
| `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_storage_security_model.py tests\integration --tb=short` | `backend` | PASS | `5 passed, 213 deselected`. |
| `python -B -m pytest -q --tb=short` | `backend` | PASS | `3388 passed, 1 skipped, 1214 deselected`. |
| Runtime OpenAPI/route guards | `backend` | PASS | No `replay_snapshot_v1` route or OpenAPI exposure. |
| `git diff --check` | repo root | PASS | Whitespace check passed; Git emitted CRLF warnings only. |
| Alignment fix validation rerun | `backend` and repo root | PASS | CS-295 targeted tests, brief validation command, lint, story validation and diff check passed. |

## Commands skipped or blocked

- none

## DRY / No Legacy evidence

- Reused replay model/table, `log_call`, `purge_expired_logs`, `compute_input_hash`, `sanitize_payload` and encrypted boundary.
- Alignment fix: `Sink.LLM_REPLAY_SNAPSHOTS` now hashes direct identifiers, correlable identifiers, user-authored content, birth data and exact coordinates before encryption.
- No new table, model tree, writer service, route, frontend surface, generated client, shim, alias, fallback path or manual mutation script was added.
- Scoped negative storage scan and DB replay tests prove forbidden raw values are absent from inspectable metadata and decrypted replay payload.
- Broad forbidden-token scan is diagnostic only; DB and scoped storage tests provide the AC proof.

## Diff review

- `git diff --check`: PASS.
- Story-scope diff reviewed: no frontend or API route file changed.

## Final worktree status

- Story changes remain uncommitted after clean implementation review.
- Expected modified/untracked paths are limited to backend replay storage, migration, tests/guards, capsule evidence and story status.

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Verify future replay execution stories work from transformed references/hashes without reintroducing forbidden raw storage.

## Feedback loop routing

- no-propagation: validation failures were resolved by local tests/guard classification and did not require a reusable skill or AGENTS.md update.
