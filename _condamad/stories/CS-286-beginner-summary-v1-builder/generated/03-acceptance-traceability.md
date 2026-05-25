# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Existing summary owners are audited. | Existing owner search found `structured_facts_v1_builder.py`; `beginner_summary_v1_builder.py` was added adjacent to the canonical interpretation owner. | `evidence/architecture-guard.txt`; AST guard in `test_beginner_summary_v1_builder.py`. | PASS |
| AC2 | `beginner_summary_v1` is generated. | `BeginnerSummaryV1Builder.build()` emits `projection_id=beginner_summary_v1`, stable fields, JSON output and sample payload. | `python -B -m pytest -q tests/unit/domain/astrology/test_beginner_summary_v1_builder.py --tb=short`; `evidence/beginner-summary-v1-sample.json`. | PASS |
| AC3 | `structured_facts_v1` is the source. | Builder imports `STRUCTURED_FACTS_V1_PROJECTION_ID`, accepts `structured_facts_v1`, and rejects any other `projection_id`. | AST/source guard test; architecture evidence. | PASS |
| AC4 | Output states are controlled. | Builder supports `normal`, `empty`, `degraded`, `unavailable` with stable message codes. | Unit tests for normal, empty, degraded and unavailable states. | PASS |
| AC5 | Missing birth time is degraded. | `no_time` missing data produces degraded output and suppresses `ascendant` and `dominant_house`. | `test_beginner_summary_v1_missing_birth_time_is_degraded`. | PASS |
| AC6 | Internal primitives are absent. | Payload contains only client-safe fields and excludes hash/source/runtime/audit/debug surfaces. | `test_beginner_summary_v1_excludes_internal_and_llm_owned_fields`; negative scan in `evidence/architecture-guard.txt`. | PASS |
| AC7 | Messages are deterministic. | Builder emits message codes only; no prompt, provider response or LLM output field. | Unit assertions and targeted `rg` negative scan. | PASS |
| AC8 | Public API surface stays unchanged. | No `backend/app/api/**` changes; loaded app route/OpenAPI guards pass. | `evidence/public-surface-guard.txt`; TestClient `/health` smoke in unit test. | PASS |
| AC9 | Evidence artifacts are persisted. | Required evidence files were created under `evidence/`; generated evidence files updated. | `condamad_validate.py` PASS; validation transcript exists. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
