# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `rejected` is terminal. | `docs/architecture/ungrounded-narrative-rejection-workflow.md` defines `status: rejected` as terminal and non-reversible within the same generation cycle. | `evidence/validation.txt` contains `rejected`, terminal/auditable wording and workflow identifiers. | PASS |
| AC2 | Transition conditions are explicit. | The workflow lists transitions from `grounding_status: ungrounded`, invalid `evidence_refs`, `unfounded` sections and missing audit provenance. | `evidence/validation.txt` records `ungrounded`, `evidence_refs`, invalid proof states and transition lines. | PASS |
| AC3 | Rejected raw answer is retained. | `raw_answer_storage` is mandatory internal-only retained content with prompt, provider, model and proof metadata. | `evidence/validation.txt` records `raw_answer_storage` and "réponse rejetée" retention lines. | PASS |
| AC4 | Client response is controlled. | `client_message` defines controlled support wording and bans raw answer, prompt, hashes, provider details and audit rows from client surfaces. | `evidence/validation.txt` records `client_message`, `message contrôlé` and raw-answer masking rules. | PASS |
| AC5 | Rejection reasons are structured. | `rejection_reason` taxonomy includes stable values for ungrounded claim, missing/unsupported evidence, hash mismatch, missing metadata and unsafe exposure. | `evidence/validation.txt` records `rejection_reason` and taxonomy lines. | PASS |
| AC6 | Internal log is required. | `log_event` requires `event_type: narrative_answer_rejected` plus answer, reason, grounding, provider/model and masked hash fields; `alert_event` semantics are documented. | `evidence/validation.txt` records `narrative_answer_rejected`, log and alert fields. | PASS |
| AC7 | Privacy minimums are defined. | `privacy_controls` documents masking, access scope, client exposure and `final_retention_decision: product_policy_pending`. | `evidence/validation.txt` records `privacy_controls`, masking/access scope and retention decision lines. | PASS |
| AC8 | Retry stays outside scope. | `retry_policy: future_story_decision` states no retry queue, automatic retry, fallback provider, silent regeneration or admin retry button is created. | `evidence/no-legacy-dry-scan.txt` records no retry queue/retry runtime boundary. | PASS |
| AC9 | Calculation debug stays separate. | `debug_boundary` separates rejection audit from calculation debug data and astrology runtime traces. | `evidence/no-legacy-dry-scan.txt` records calculation debug and astrology runtime separation lines. | PASS |
| AC10 | Public API surface stays unchanged. | No backend route/schema/source file was changed; the story adds a documentation contract only. | `evidence/api-surface.txt` shows 193 OpenAPI paths, 221 routes and `forbidden_rejection_paths=[]`. | PASS |
| AC11 | Application source surfaces remain unchanged. | No `backend/app` or `frontend/src` delta was introduced by this story. | `evidence/app-surface-status.txt` is empty for `git status --short -- backend/app frontend/src`; full backend pytest passed. | PASS |
| AC12 | Evidence artifacts are persisted. | CS-261 generated files and `evidence/` artifacts are present in the target capsule. | `condamad_validate.py` passes after evidence update; final evidence lists persisted artifacts. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
