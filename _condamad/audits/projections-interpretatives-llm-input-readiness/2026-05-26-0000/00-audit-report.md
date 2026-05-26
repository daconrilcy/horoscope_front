# Audit Report - Projections Interpretatives LLM Input Readiness

## Scope

- Domain key: `projections-interpretatives-llm-input-readiness`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend interpretation projection contracts, narrative input readiness and narrative audit surfaces.
- Output folder: `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/`

## Executive Conclusion

`AINarrativeInputContract` is the recommended-target for future LLM injection, with `structured_facts_v1` as factual/hashable source and `client_interpretation_projection_v1` as product projection only. The current natal LLM path does not consume these recent contracts (E-016), so the correct status is `available-not-injected`, not `injected`.

`narrative_answer_audit_v1` is audit-only: it stores `projection_hash`, `llm_input_hash`, `prompt_version`, `provider`, `model`, `grounding_status` and `evidence_refs`; it must not become prompt payload (E-012, E-015, E-022).

## Required Questions

1. Best canonical candidate: `AINarrativeInputContract`, because it contains structural facts, interpretive signals, readiness_flags, source_versions, masking policy and projection links (E-009, E-010).
2. Factual fields: `structured_facts_v1.structural_facts.positions`, `houses`, `major_aspects`, `source_metadata`, plus `dominants` when used as calculated evidence; hashable through `hash_input` (E-006, E-017).
3. Support/editorial fields: `beginner_summary_v1.allowed_fields`, `display_messages`, `summary_items`; `client_interpretation_projection_v1.llm_input_selection`, `editorial_depth_profile`, `frontend_visibility_rules`, `sections`, `support_elements` (E-007, E-008).
4. Explicit exclusions: raw runtime objects, debug traces, provider responses, prompt payloads, full structured facts in client summaries and audit internals are excluded by builders (E-006, E-007, E-008, E-019).
5. Hashable data: `structured_facts_v1.hash_input`, persisted `projection_hash`, `llm_input_hash`, and evidence proof hashes validated as SHA-256 (E-006, E-011, E-012, E-015).
6. Readiness flags: `structural_facts_ready`, `interpretive_signals_ready`, `public_projection_links_ready`, `ready_for_scoring`, `ready_for_narrative`; they prove builder-local completeness, not current prompt injection (E-009, E-010, E-020).
7. Plan granularity: B2C granularity exists in `client_interpretation_projection_v1` for free/basic/premium sections and depth profiles; LLM injection granularity remains missing because the current prompt path does not consume the candidate contract (E-008, E-016).

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md` | used | E-001 | Source contract for audit scope and target artifacts. | None. |
| `_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md` | used | E-002 | Source brief and mandatory questions. | None. |
| `_condamad/stories/regression-guardrails.md` | used | E-003 | Required registry consulted; no exact new invariant added. | Registry has no exact projection-readiness guard. |
| `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/**` | out-of-domain | E-004 | Prior adjacent LLM surface audit consulted for closure context. | Context only. |
| `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/**` | out-of-domain | E-005 | Prior adjacent prompt pipeline audit consulted for current injection status. | Context only. |
| `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` / `StructuredFactsV1Builder` | used | E-006, E-017 | Canonical factual projection, hashable source. | Not current prompt input. |
| `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py` / `BeginnerSummaryV1Builder` | used | E-007, E-018 | Public beginner summary from structured facts. | Product projection, not canonical prompt facts. |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` / `ClientInterpretationProjectionV1Builder` | used | E-008, E-019 | Public plan-aware projection and shaping surface. | Product projection, not canonical prompt input. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` / `AINarrativeInputContract` | intentional-public-export | E-009, E-020 | Internal domain contract explicitly versioned and tested as scoring/narration input. | Current prompt path non-usage proven by E-016. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` / `AINarrativeInputBuilder` | used | E-010, E-020 | Builds candidate narrative input from canonical interpretation input. | Current prompt path non-usage proven by E-016. |
| `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` | used | E-011, E-013, E-021 | Validates audit evidence refs and hashes for rejection workflow. | Audit validation, not prompt content. |
| `backend/app/infra/db/models/user_natal_interpretation.py` / `UserNatalInterpretationModel` | used | E-012, E-022 | Stores narrative answer audit fields and payload. | Persistence surface only. |
| `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | used | E-013, E-021 | Uses evidence refs and hashes to reject ungrounded answers. | Rejection path, not input readiness. |
| `backend/app/services/projections/projection_endpoint_service.py` | used | E-014 | Current consumer for public projection builders and persistence hash. | Public projection endpoint, not LLM prompt path. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | used | E-015, E-016 | Current audit persistence and natal LLM service context. | Does not consume candidate contracts in scoped scan. |
| `backend/tests/unit/domain/astrology/**` selected projection tests | test-only | E-017, E-018, E-019, E-020 | Own regression coverage for builders and contract. | Full suite validation recorded separately. |
| `backend/tests/unit/test_rejected_narrative_answer_workflow.py` | test-only | E-021 | Own rejection workflow coverage. | None. |
| `backend/tests/unit/test_narrative_answer_audit_model.py` and `test_narrative_answer_audit_sensitive_data.py` | test-only | E-022 | Own audit model and sensitive metadata coverage. | None. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: no duplicate audit vocabulary is introduced; `02-field-classification.md` is the canonical field classification for CS-326.
- No Legacy: no route, prompt, projection, alias, shim, fallback or compatibility path is added.
- Mono-domain: findings stay in backend interpretation projection / LLM input readiness. Frontend, migrations, auth, provider choice and prompt rewrites are deferred non-domain concerns.
- Dependency direction: future migration should let LLM services consume domain interpretation contracts; domain astrology must remain provider-free.

## Closure Analysis

- Prior audit folders consulted: `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/`, `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/`.
- Story keys consulted: CS-324, CS-325, CS-326 plus registry references RG-002, RG-022, RG-041, RG-047, RG-052.
- Active findings after current evidence: F-001, F-002, F-003, F-004.
- Closed prior findings: none closed by CS-326 because it is audit-only.
- Implementation files in audited domain: none changed.
- Governance/test files in audited domain: only audit artifacts are created.
- Deferred non-domain concerns: prompt rewrite, gateway payload composition, DB migration, frontend display, provider/model policy and public API exposure.

## Exhaustive Active Finding Surface

- F-001: `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`, `ai_narrative_input_builder.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/domain/llm/runtime/**`.
- F-002: `structured_facts_v1_builder.py`, `beginner_summary_v1_builder.py`, `client_interpretation_projection_v1_builder.py`, `backend/app/services/projections/projection_endpoint_service.py`.
- F-003: `evidence_refs_validation.py`, `rejected_answer_workflow.py`, `user_natal_interpretation.py`, `interpretation_service.py`.
- F-004: `_condamad/stories/regression-guardrails.md` and future story guard artifacts only; no current registry edit justified.

