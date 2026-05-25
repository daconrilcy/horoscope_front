# Final Evidence — CS-300-replay-snapshot-v1-payload-hash-integrity

## Story status

- Validation outcome: pass
- Ready for review: yes
- Story key: CS-300-replay-snapshot-v1-payload-hash-integrity
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-300-replay-snapshot-v1-payload-hash-integrity`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story/status alignment: `story-status.md` row `CS-300` points to the target story and source brief.
- Initial `git status --short`: clean.
- AGENTS.md files considered: repository prompt instructions for `C:\dev\horoscope_front`.
- Capsule generated/repaired: yes; `condamad_validate.py` PASS.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by CONDAMAD helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC8 classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Story surface recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Applicable commands recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Guardrails preserved. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Ready-for-review evidence complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Real `log_call -> create_snapshot -> replay` path tested. | Execution audit pytest PASS. | PASS |
| AC2 | Snapshot `input_hash` and `input_enc` derive from the same canonical replay payload. | DB redaction pytest PASS. | PASS |
| AC3 | Incomplete/expired/purged behavior preserved; canonical mismatch refuses with `input_hash_mismatch`. | Execution audit pytest PASS. | PASS |
| AC4 | Fabricated `encrypt_input(user_input)` success fixture removed. | Targeted `rg` PASS: no matches. | PASS |
| AC5 | Replay payload remains sanitized; audit `purged_count` kept as operational metadata. | Redaction pytest PASS. | PASS |
| AC6 | Public replay exposure remains absent; admin exposure unchanged. | Admin API, architecture, `app.routes`, and `app.openapi()` checks PASS. | PASS |
| AC7 | Canonical payload/hash ownership stays in replay snapshot service. | Architecture boundary pytest PASS. | PASS |
| AC8 | Evidence artifacts persisted under story evidence directory. | Capsule validation PASS. | PASS |

## Files changed

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

## Files deleted

- none

## Tests added or updated

- Updated replay execution audit tests to build snapshots through `log_call`.
- Added canonical hash mismatch refusal coverage.
- Updated DB redaction/storage tests to assert encrypted payload hash integrity.

## Commands run

See `evidence/validation.txt` for exact commands and outputs. Summary:

- `ruff format` targeted modified Python files: PASS.
- `ruff check .`: PASS.
- Replay snapshot unit/integration/admin/architecture tests: PASS.
- Replay snapshot expanded suite with `--long`: PASS, 36 passed.
- Negative scans for fabricated raw replay setup and public replay paths: PASS.
- Runtime `app.openapi()` and `app.routes` exposure assertions: PASS.
- `git diff --check`: PASS.
- `condamad_validate.py`: PASS.

## Commands skipped or blocked

- Full repository pytest was not run; the capsule validation scope is replay_snapshot_v1-specific and the expanded replay suite passed.
- Frontend checks were not run; frontend is explicitly out of scope and no frontend files changed.

## DRY / No Legacy evidence

- One canonical replay payload helper and one payload hash helper own the contract.
- Replay no longer compares decrypted replay payloads to the original call-log hash.
- No compatibility hash fallback, shim, alias, second store, public route, or frontend surface was added.
- `rg -n "encrypt_input\(user_input\)" backend\tests\unit\test_replay_snapshot_v1_execution_audit.py` returned no matches.

## Diff review

- `git diff --stat` reviewed for story surface.
- `git diff --name-only` reviewed for story surface.
- `git diff --check`: PASS.

## Final worktree status

- Modified backend service/runtime/tests and story capsule evidence files only.
- `story-status.md` synchronized to `ready-to-review`.

## Remaining risks

- Existing line-ending warnings report LF files will be converted to CRLF when Git touches them; no whitespace errors were reported.

## Suggested reviewer focus

- Confirm the canonical replay payload remains the approved sanitized payload and that replay fidelity limits remain acceptable under the DPO/security model.
