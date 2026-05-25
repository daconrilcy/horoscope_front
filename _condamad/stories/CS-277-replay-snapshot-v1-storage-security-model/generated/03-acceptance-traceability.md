# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The storage model exists. | `docs/architecture/replay-snapshot-v1-storage-security-model.md` exists with French global comment and `model_id`. | Targeted pytest, `rg` story scan, `git diff --check`. | PASS |
| AC2 | Minimal snapshot content is defined. | `minimal_stored_content` table lists calculation identity, input reconstruction reference, version identity, provenance, diagnostics link and AI audit link. | `test_minimal_content_and_sensitive_data_rules_are_explicit`; `rg` over `docs` and `_story_briefs`. | PASS |
| AC3 | Sensitive data handling is defined. | `forbidden_data` and `masking_policy` deny raw birth data, exact coordinates, direct identifiers, raw prompts, raw model payloads and secrets. | `python -B -m pytest -q backend/tests/unit/test_replay_snapshot_v1_storage_security_model.py --tb=short` PASS. | PASS |
| AC4 | Authorized roles are limited. | `authorized_roles` reuses CS-270/CS-271 roles: `ADMIN`, target-only `TECHNO`, target-only `ASTRO_EXPERT`; `MARKETER` and public/client roles are denied. | `test_roles_retention_and_purge_are_restricted`; `rg` story/document scans. | PASS |
| AC5 | Retention has a decision state. | `retention_policy` records `DPO-open`, blocker `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`, and held-back implementation surfaces. | `test_roles_retention_and_purge_are_restricted`; document scan. | PASS |
| AC6 | Purge behavior is defined. | `purge_policy` covers expiry purge, manual deletion, linked diagnostics and linked AI audit records, without cascade deletion. | `test_roles_retention_and_purge_are_restricted` PASS. | PASS |
| AC7 | Diagnostics links stay separate. | `diagnostics_link` references `admin_chart_diagnostics_v1` metadata without embedding replay payloads. | `test_diagnostics_and_ai_audit_links_remain_separate` PASS. | PASS |
| AC8 | AI audit links stay separate. | `ai_audit_link` references `narrative_answer_audit_v1` and rejected-answer audit records without merge/copy/replace. | `test_diagnostics_and_ai_audit_links_remain_separate` PASS. | PASS |
| AC9 | Runtime exposure is absent. | No backend runtime code, route, OpenAPI path, migration or frontend code was added for `replay_snapshot_v1`. | `app.openapi()` and `app.routes` Python checks PASS; TestClient openapi check PASS. | PASS |
| AC10 | Application source surfaces remain unchanged. | Intended app delta is none; scoped status shows only pre-existing unrelated `backend/app` changes, no `frontend/src` CS-277 changes. | `git status --short -- backend/app frontend/src` captured in evidence; `rg -n "replay_snapshot_v1" backend/app frontend/src backend/migrations` exit 1 = PASS/no matches. | PASS |
| AC11 | Evidence artifacts are persisted. | `generated/03-acceptance-traceability.md`, `generated/10-final-evidence.md`, `evidence/source-checklist.md`, `evidence/validation.txt`, `evidence/app-surface-status.txt`. | Capsule validation PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
