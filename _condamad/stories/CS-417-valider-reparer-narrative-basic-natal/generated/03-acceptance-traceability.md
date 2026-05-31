# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Missing requested Basic section is invalid. | `validate_basic_natal_draft_against_plan` compares expected `BasicNatalReadingPlan.sections` to draft sections. | `python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py --tb=short` | PASS |
| AC2 | Unauthorized Basic section is invalid. | Unauthorized section delta is reported as `unauthorized_section:<code>`. | same validator pytest | PASS |
| AC3 | Unsupported generated fact is invalid. | Draft `fact_ids` and known public astro terms are checked against plan facts/public evidence. | same validator pytest | PASS |
| AC4 | Date-only draft cannot mention Ascendant. | Date-only plan limitations activate time-surface denylist. | same validator pytest + VC11 scan with expected validator/test hits | PASS |
| AC5 | Technical score marker or unexplained jargon is invalid. | Basic denylist rejects `ranking_score`, `condition_axis`, `audit_input`, `visibility_expression`, score/jargon markers. | same validator pytest + VC10 scan with expected denylist hits only | PASS |
| AC6 | Mixed grammatical person is invalid. | Public text check rejects simultaneous `tu/ton/tes` and `vous/votre/vos`. | same validator pytest | PASS |
| AC7 | Prescriptive advice is invalid. | Prescriptive phrase denylist rejects imperative advice patterns. | same validator pytest | PASS |
| AC8 | Valid Basic draft keeps limitations. | Required `reading_plan.limitations` are exact-match mandatory. | same validator pytest | PASS |
| AC9 | Rejection audit stores structured metadata. | `BasicNatalDraftValidationResult.to_metadata` and `build_basic_natal_rejection_outcome`. | same validator pytest | PASS |
| AC10 | First invalid draft triggers constrained repair. | `validate_repair_or_fallback_basic_natal_draft` calls one callback with validation errors and original plan. | same validator pytest | PASS |
| AC11 | Second invalid draft produces audited rejection or short fallback. | Same orchestrator validates deterministic fallback built only from plan public evidence. | same validator pytest + existing schema guard pytest | PASS |
| AC12 | Rejected Basic output stays audit-only. | Existing `RejectedNarrativeAnswerOutcome.to_client_payload` boundary remains used; no public serializer changed. | `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --long --tb=short` | PASS |
| AC13 | Quota waits for valid acceptance. | No quota path changed; existing acceptance gate remains owner. | `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short` | PASS |
| AC14 | Story evidence artifacts are persisted. | Evidence files under story `evidence/` and generated traceability/final evidence. | `condamad_validate.py <capsule> --final` | PASS |
| AC15 | Basic plan-backed validation has durable registry guardrail. | `RG-166` is present in `_condamad/stories/regression-guardrails.md`. | `rg -n "RG-166\|Basic plan validation\|BasicNatalReadingPlan" ../_condamad/stories/regression-guardrails.md` | PASS |
| AC16 | Unsupported vocation section is invalid. | Vocation/carriere text is rejected when `vocation` is absent from plan sections. | validator pytest | PASS |
| AC17 | Valid Basic draft keeps disclaimers. | Required `reading_plan.disclaimers` are exact-match mandatory. | validator pytest | PASS |
| AC18 | Valid Basic draft keeps public sources. | Draft public evidence ids/sources and section evidence ids are required and plan-scoped. | validator pytest | PASS |

All ACs are implemented with fresh code/test evidence. Full fast backend pytest has unrelated pre-existing guard failures outside the story surface; see `10-final-evidence.md`.
