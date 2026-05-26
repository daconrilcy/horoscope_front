# Audit - Projections Interpretatives LLM Input Readiness

Ce fichier est la synthese story-specific CS-326. Le rapport CONDAMAD standard est dans `00-audit-report.md`.

## Readiness Synthesis

recommended-target: `AINarrativeInputContract`.

Raison: `AINarrativeInputContract` separe deja `structural_facts`, `interpretive_signals`, `readiness_flags`, `source_versions`, `masking_policy`, `public_projection_links` et `debug_context`. Il est construit par `AINarrativeInputBuilder` depuis l'input interpretatif canonique, sans provider externe. Il est donc le meilleur candidat pour une future entree LLM canonique, mais son statut courant est `available-not-injected`, pas `injected`.

`structured_facts_v1` est la source factuelle hashable la plus stable: positions, maisons, aspects majeurs, metadonnees source, signaux pre-interpretatifs, dominantes, `missing_data` et `hash_input`. Il doit alimenter le contrat cible ou l'audit, mais il ne porte pas seul les politiques de readiness narrative.

`beginner_summary_v1` et `client_interpretation_projection_v1` sont des projections client. Elles ajoutent du shaping editorial, des budgets de profondeur, des labels de support, des codes de messages, des disclaimers, des regles de visibilite frontend et une granularite par plan. Elles sont utiles comme contexte produit, pas comme payload prompt canonique.

`narrative_answer_audit_v1` est une surface d'audit. Elle porte `projection_hash`, `llm_input_hash`, `prompt_version`, `provider`, `model`, `grounding_status` et `evidence_refs`. Ces champs prouvent provenance et ancrage; ils ne doivent pas etre injectes comme contexte narratif.

## Mandatory Answers

1. Meilleur contrat candidat: `AINarrativeInputContract`, avec `structured_facts_v1` comme source factuelle amont.
2. Champs factuels: `structural_facts.positions`, `houses`, `major_aspects`, `source_metadata`, `dominants`, `missing_data`, `source_versions`.
3. Labels/support/shaping: `allowed_fields`, `display_messages`, `summary_items`, `llm_input_selection`, `editorial_depth_profile`, `frontend_visibility_rules`, `sections`, `support_elements`, `precision_level`.
4. Exclusions: `excluded_surfaces`, `excluded_audit_surfaces`, `masking_policy.redact_fields`, absence de `prompt`, `llm_output`, `final_narrative`, `provider_response` dans le contrat IA.
5. Hashable: `structured_facts_v1.hash_input`, `projection_hash`, `llm_input_hash`, `source_hash` dans `evidence_refs`.
6. Readiness flags: `structural_facts_ready`, `interpretive_signals_ready`, `public_projection_links_ready`, `ready_for_scoring`, `ready_for_narrative`; ils prouvent une completude locale du builder, pas une injection prompt effective.
7. Granularite par plan: free/basic/premium existe dans `client_interpretation_projection_v1`; la granularite d'injection LLM cible reste a definir dans une story d'architecture ou migration.

## Required Source Citations

- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`: `StructuredFactsV1Builder`, `hash_input`, `excluded_surfaces`.
- `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py`: `BeginnerSummaryV1Builder`, `allowed_fields`, `display_messages`, exclusions.
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`: `_PLAN_SHAPING`, `llm_input_selection`, `editorial_depth_profile`, `frontend_visibility_rules`, `audit_input`.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`: `AINarrativeInputBuilder.from_interpretation_input`, readiness flag assembly.
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`: `AINarrativeInputContract`, `AINarrativeReadinessFlags`, `AINarrativePersistedProjectionIdentity`.
- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`: `AUTHORIZED_EVIDENCE_SOURCE_TYPES`, `build_audit_source_proofs`, hash validation.
- `backend/app/infra/db/models/user_natal_interpretation.py`: audit columns `projection_hash`, `llm_input_hash`, `prompt_version`, `provider`, `model`, `evidence_refs`.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`: validation and rejection from `evidence_refs`.
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`: hashability, exclusion and owner guards.
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`: client-safe exclusions and source guard.
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`: plan differentiation and product shaping tests.
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`: versioned contract, readiness and forbidden fields.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py`: grounding rejection tests.

## Current Pipeline Status

current-llm-use: `available-not-injected`.

Evidence E-016 records a zero-hit scan for recent projection/narrative input symbols inside the scoped LLM generation/runtime paths. Prior audits CS-324 and CS-325 also classify the current natal prompt path as centered on `chart_json`, `natal_data`, `astro_context` and `evidence_catalog`, with `chart_json` as prompt-visible and `evidence_catalog` validation-only.

## Findings Summary

See `02-finding-register.md`: F-001 High, F-002 Medium, F-003 Medium, F-004 Low.

