# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Prompt-visible roles exclude `evidence`. | `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` is now `facts`, `signals`, `limits`, `shaping`; `evidence` moved to `validation_only`. | `python -B -c` role check PASS; `pytest ... test_llm_astrology_input_payload_boundaries.py` PASS. | PASS |
| AC2 | Provider payload omits top-level `evidence`. | Gateway still projects through canonical role map; provider handoff tests assert no `evidence` key. | `pytest ... test_llm_astrology_input_boundaries.py` PASS; `evidence/prompt-boundary-after.json` contains only `facts`, `signals`, `limits`, `shaping`. | PASS |
| AC3 | Empty evidence payload expectations are gone. | Removed `prompt_payload["evidence"] == {}` expectation. | `rg -n -F 'prompt_payload["evidence"] == {}' backend\app backend\tests` returned no matches. | PASS |
| AC4 | The full internal LLM input keeps evidence refs. | Full `llm_astrology_input_v1` still returns `evidence.evidence_refs`, `grounding_status`, `validation_owner`, provenance and hashes. | `pytest ... test_llm_astrology_input_v1.py test_llm_astrology_input_evidence.py` PASS. | PASS |
| AC5 | Persistent audit stores evidence refs. | Audit persistence still reads backend-only evidence refs, grounding status, `projection_hash`, and `llm_input_hash`. | `pytest ... test_natal_llm_astrology_input_audit.py` PASS. | PASS |
| AC6 | Grounded generated writing passes validation. | Grounded payload path remains non-rejected. | `pytest ... test_rejected_narrative_answer_workflow.py::test_grounded_validation_does_not_create_rejection` PASS. | PASS |
| AC7 | Unsupported generated claims fail validation. | Backend validation rejects unsupported generated terms against internal facts, even without a LLM marker. | `pytest ... test_backend_detects_unsupported_generated_claim_without_llm_marker` PASS. | PASS |
| AC8 | Ignored critical limits fail validation. | Backend validation rejects text using unavailable fact surfaces from internal `limits`, even without a LLM marker. | `pytest ... test_backend_detects_ignored_critical_limit_without_llm_marker` PASS. | PASS |
| AC9 | Audit-only prompt boundary guards remain active. | Architecture and orchestration guards include `evidence` among forbidden prompt surfaces. | `pytest ... test_llm_astrology_input_payload_boundaries.py test_llm_astrology_input_boundaries.py` PASS. | PASS |
| AC10 | Legacy natal prompt carrier guards remain active. | Existing `chart_json` and `natal_data` sentinel tests remain unchanged and passing. | `pytest ... test_llm_astrology_input_boundaries.py` PASS. | PASS |
| AC11 | Story evidence artifacts are persisted. | `evidence/prompt-boundary-before.json`, `evidence/prompt-boundary-after.json`, traceability, final evidence, and story status updated. | `python -B condamad_validate.py ...` PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
