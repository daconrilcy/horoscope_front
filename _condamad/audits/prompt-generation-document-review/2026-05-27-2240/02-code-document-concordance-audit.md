<!-- Commentaire global: audit CS-352 de concordance entre la cartographie prompt LLM et le code executable backend. -->

# CS-352 Code-Document Concordance Audit

## Resume executif

Verdict: `acceptable with documentation-only corrections`.

Le document `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` est concordant avec le code executable pour le flux nominal natal moderne: use case canonique, assembly, rendu des placeholders, `llm_astrology_input_v1`, filtrage prompt-visible, composition des messages, handoff provider, validation, repair, persistence et observability.

Deux corrections documentaires candidates restent necessaires:

- clarifier que `evidence` et `evidence_refs` sont validation-owned, exclus du prompt provider, et peuvent alimenter la persistence audit-only;
- remplacer la formulation stricte `backend-only runtime` de `request_id`, `trace_id` et `use_case` par `runtime/provider-only metadata, not prompt-visible payload`.

## Methode de concordance code-document

| Axe | Source documentaire | Source code/test | Evidence |
|---|---|---|---|
| Sections et symboles cites | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` headings, owner table and boundary lists | targeted `rg` and source reads | E-005 |
| Flux nominal | configuration, renderer, gateway, natal input and service files | symbol scans and source context | E-007, E-008, E-009 |
| Exclusions prompt-visible | boundary section and tests list in document | gateway projection, LLM input roles and pytest guards | E-010, E-012 |
| Handoff provider | provider parameters section | gateway, provider manager and OpenAI adapter scans | E-008, E-011 |
| Historique domaine | prior CS-351 and CS-343 to CS-349 artifacts | prior audit/source-map reads | E-004, E-006 |

## Trace code du flux nominal

| Step | code source | real responsibility | status | evidence |
|---|---|---|---|---|
| 1. Selection du use case canonique | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` / `CanonicalUseCaseContract`, `CANONICAL_USE_CASE_CONTRACTS`, `list_modern_natal_use_case_contracts` | Declare les contrats canoniques et identifie les use cases modernes exigeant `llm_astrology_input_v1`. | confirmed | E-007 |
| 2. Resolution d'assembly | `backend/app/domain/llm/runtime/gateway.py` / `_resolve_plan`; `backend/app/domain/llm/configuration/assembly_resolver.py` / `resolve_assembly` | Charge l'assembly active quand disponible, refuse le use-case-first pour familles supportees sauf exceptions bornees, et produit le plan runtime. | confirmed | E-007, E-008 |
| 3. Developer prompt | `backend/app/domain/llm/configuration/assembly_resolver.py` / `assemble_developer_prompt` | Concatene les blocs resolus de l'assembly avant rendu. | confirmed | E-007 |
| 4. Rendu placeholders | `backend/app/domain/llm/prompting/prompt_renderer.py` / `PromptRenderer.render`, `extract_placeholders` | Valide les placeholders par famille, refuse les required manquants et applique les fallbacks optionnels gouvernes. | confirmed | E-007 |
| 5. Input natal riche | `backend/app/services/llm_generation/natal/interpretation_service.py` / `_build_llm_astrology_input_v1`; `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` / `LLMAstrologyInputV1Builder` | Compose `facts`, `signals`, `limits`, `shaping`, `evidence` et `provenance` depuis owners internes autorises. | confirmed | E-009 |
| 6. Projection prompt-visible | `backend/app/domain/llm/runtime/gateway.py` / `_prompt_visible_llm_astrology_input`; `LLM_ASTROLOGY_INPUT_DATA_ROLES` | Extrait uniquement les blocs `prompt_visible` et exclut audit/validation/runtime-only surfaces. | confirmed | E-010 |
| 7. Message composition | `backend/app/domain/llm/runtime/gateway.py` / `_build_messages`, `compose_structured_messages`, `compose_chat_messages` | Produit le dernier payload gateway-owned avant provider selon mode structured ou chat. | confirmed | E-008 |
| 8. Provider handoff | `backend/app/domain/llm/runtime/gateway.py` / `_call_provider`; `provider_runtime_manager.py` / `execute_with_resilience`; `openai_responses_client.py` / `ResponsesClient.execute` | Transmet messages et parametres provider; request/trace/use-case deviennent headers adapter, pas prompt-visible payload. | confirmed with wording correction | E-008, E-011 |
| 9. Validation et repair | `backend/app/domain/llm/runtime/gateway.py` / `_validate_and_normalize`, `_handle_repair_or_fallback`; `output_validator.py`, `repair.py` imports | Valide la sortie, tente repair puis fallback borne selon statut et use case. | confirmed | E-008 |
| 10. Persistence et observability | `backend/app/services/llm_generation/natal/interpretation_service.py` / `_apply_narrative_answer_audit`; gateway `log_call`; admin LLM observability routers | Persiste les ancres audit et expose des surfaces d'investigation, sans prouver la justesse semantique complete. | confirmed | E-009, E-011 |

## Matrice document section -> code source -> statut

| document section | code source | status | evidence | candidate correction |
|---|---|---|---|---|
| Executive summary lines 7-9 | gateway, registry, assembly resolver, renderer, natal input builder, service | confirmed | E-005, E-007, E-008, E-009 | none |
| Carte des owners de code | listed backend owner files | confirmed | E-005, E-007, E-008, E-009 | none |
| Use case et contrats canoniques | `canonical_use_case_registry.py` | confirmed | E-007 | none |
| Resolution d'assembly et developer prompt | `assembly_resolver.py`, `gateway.py` | confirmed | E-007, E-008 | none |
| Gouvernance des placeholders | `prompt_renderer.py`, `gateway.py`, boundary tests | confirmed | E-007, E-010, E-012 | none |
| Construction de `llm_astrology_input_v1` | `interpretation_service.py`, `llm_astrology_input_v1.py` | confirmed | E-009 | none |
| Projection prompt-visible vs backend-only | `llm_astrology_input_v1.py`, `gateway.py` | erreur documentaire | E-005, E-009, E-010 | Clarify validation-owned audit persistence and provider-only metadata wording. |
| Composition des messages provider | `gateway.py` | confirmed | E-008 | none |
| Modes `structured` et `chat` | `gateway.py` | confirmed | E-008 | none |
| Provider parameters et output schema | `gateway.py`, `provider_runtime_manager.py`, `openai_responses_client.py` | erreur documentaire | E-008, E-011 | Replace strict backend-only wording with provider-only metadata wording. |
| Validation, repair, fallback et rejet | `gateway.py`, `output_validator.py`, `repair.py` imports | confirmed | E-008 | none |
| Persistence audit et observability | `interpretation_service.py`, `gateway.py`, admin observability routers | absence documentaire | E-009, E-011 | Add nuance that observability is source-proven for investigation only; no real provider call or semantic verifier proof. |
| Seeds/bootstrap et chemins non nominaux | `gateway.py`, prior CS-344/CS-345 artifacts, legacy tests | confirmed | E-006, E-008, E-010, E-012 | none |
| Tests et guardrails | listed pytest files and guardrail registry | risque de test coverage | E-003, E-010, E-012 | Note exact code-document concordance guardrail gap remains. |

## Matrice symbole cite -> presence -> responsabilite reelle

| cited symbol | presence | real responsibility | evidence | candidate correction |
|---|---|---|---|---|
| `CanonicalUseCaseContract` | present | Describes canonical use-case contracts and required prompt placeholders/input schemas. | E-007 | none |
| `CANONICAL_USE_CASE_CONTRACTS` | present | Registry of canonical contracts, including modern natal contracts requiring `llm_astrology_input_v1`. | E-007 | none |
| `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA` | present | Input schema declaring `llm_astrology_input_v1` requirement for natal modern contracts. | E-007 | none |
| `resolve_assembly` | present | Resolves a `PromptAssemblyConfigModel` into a runtime assembly artifact. | E-007 | none |
| `assemble_developer_prompt` | present | Concatenates resolved assembly blocks into developer prompt text. | E-007 | none |
| `PromptRenderer.render` | present | Renders governed placeholders and enforces required placeholder resolution. | E-007 | none |
| `extract_placeholders` | present | Extracts placeholder names from templates. | E-007 | none |
| `LLMAstrologyInputV1Builder` | present | Builds the rich natal LLM input from approved internal projections and evidence/provenance blocks. | E-009 | none |
| `build_llm_input_hash_material` | present | Builds hash material only from prompt-influencing blocks. | E-009, E-012 | none |
| `_build_llm_astrology_input_v1` | present | Natal service orchestration helper building the rich LLM input. | E-009 | none |
| `_apply_narrative_answer_audit` | present | Persists audit anchors including projection/hash/evidence refs on narrative answer models. | E-009 | none |
| `LLMGateway` | present | Runtime orchestrator for plan resolution, message build, provider call, validation/recovery and logging. | E-008 | none |
| `compose_structured_messages` | present | Gateway method composing structured mode messages. | E-008 | none |
| `compose_chat_messages` | present | Gateway method composing chat mode messages. | E-008 | none |
| `execute_request` | present | Gateway public execution method for the nominal request flow. | E-008 | none |
| `_resolve_plan` | present | Gateway stage resolving use case, assembly, model/provider profile and output schema. | E-008 | none |
| `_build_messages` | present | Gateway stage building messages from plan and request context. | E-008 | none |
| `_call_provider` | present | Gateway stage sending messages and provider parameters to runtime manager. | E-008, E-011 | none |
| `_prompt_visible_llm_astrology_input` | present | Gateway filter selecting only canonical prompt-visible LLM input blocks. | E-010 | none |
| `chart_json` | present as legacy/non-natal or runtime-only carrier | Excluded from modern rich natal prompt path when `llm_astrology_input_v1` is present. | E-010, E-012 | none |
| `natal_data` | present as legacy/runtime-only carrier | Excluded from modern rich natal prompt path when `llm_astrology_input_v1` is present. | E-010, E-012 | none |
| `request_id`, `trace_id`, `use_case` | present | Runtime/provider metadata sent as adapter headers; not prompt-visible user payload. | E-008, E-011 | Use provider-only wording. |

## Matrice exclusions prompt-visible/backend-only

| Field | code source | status | evidence | candidate correction |
|---|---|---|---|---|
| `evidence` | `llm_astrology_input_v1.py` / validation role; gateway prompt projection | confirmed excluded from prompt-visible | E-009, E-010, E-012 | clarify may feed audit persistence through nested refs |
| `provenance` | `llm_astrology_input_v1.py` / provenance block; gateway prompt projection | confirmed audit-only | E-009, E-010, E-012 | none |
| `projection_hash` | provenance/audit helpers and persistence helpers | confirmed audit-only/backend-only | E-009, E-010, E-012 | none |
| `llm_input_hash` | `build_llm_input_hash_material`, provenance/audit helpers | confirmed audit-only/backend-only | E-009, E-012 | none |
| `chart_json` | gateway, natal service, legacy extinction tests | confirmed excluded from modern prompt when rich input exists | E-010, E-012 | none |
| `natal_data` | gateway, legacy extinction tests | confirmed excluded from modern prompt when rich input exists | E-010, E-012 | none |
| `evidence_refs` | `_evidence_block`, `_evidence_refs_for_audit`, architecture tests | confirmed validation-owned and audit-persisted | E-009, E-010, E-012 | clarify dual role and non-prompt status |
| `request_id`, `trace_id`, `use_case` | `_call_provider`, provider adapter headers | not prompt-visible; provider metadata | E-008, E-011 | use provider-only metadata wording |

## Tests et guardrails confirmes ou insuffisants

| Test or guardrail | Status | Proof | Gap |
|---|---|---|---|
| `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | confirmed | included in E-012 run | none |
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | confirmed | included in E-012 run | none |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | confirmed | included in E-012 run | none |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` | confirmed | included in E-012 run | none |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` | confirmed | included in E-012 run | none |
| `backend/tests/integration/test_llm_legacy_extinction.py` | confirmed with limitation | included in E-012 run | 7 long tests deselected by default |
| RG-002 | applicable adjacent guardrail | registry read in E-003 | protects against opportunistic backend movement, not document concordance |
| RG-022 | applicable adjacent guardrail | registry read in E-003 | protects validation paths, not exact code-document concordance |
| Exact CS-352 code-document concordance guardrail | insufficient | registry read in E-003 | no exact durable guardrail exists for `_condamad/docs` concordance |

## Gaps de concordance

| Gap | Category | Evidence | Impact | Candidate correction |
|---|---|---|---|---|
| `evidence_refs` role needs one explicit dual-role sentence | erreur documentaire | E-005, E-009, E-010, E-012 | Future agents may treat audit persistence anchors as prompt material or as unrelated to validation-owned evidence. | Documentation-only correction. |
| `request_id`, `trace_id`, `use_case` wording should be provider-only metadata | erreur documentaire | E-005, E-008, E-011 | Future agents may infer these values never leave backend process memory, while source sends headers to provider adapter. | Documentation-only correction. |
| Exact guardrail for code-document concordance is absent | risque de test coverage | E-003, E-012 | Boundary behavior is guarded, but documentation concordance drift still depends on audit process. | Dedicated documentation-governance story only if desired. |
| Real provider call not executed | absence documentaire | E-005, E-011 | Source handoff is verified, but external provider behavior is not proven by this audit. | Keep as explicit limitation, not runtime correction. |

## Corrections documentaires candidates

| Source finding | Target document | Candidate correction | Runtime impact |
|---|---|---|---|
| F-001 | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | Add one sentence near `Projection prompt-visible vs backend-only`: `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may be persisted as audit-only anchors. | none |
| F-002 | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | Replace `backend-only runtime: request_id, trace_id, profils et metadata d'execution` with `runtime/provider-only metadata: request_id, trace_id, use_case, profiles and execution metadata; not prompt-visible payload`. | none |
| F-003 | future governance artifact only if approved | Add an exact documentation-concordance guardrail only through a dedicated governance story. | none |

## Decision finale

Decision: `acceptable with documentation-only corrections`.

No code refactor, migration, prompt rewrite, test edit or provider call is recommended by this audit. The audited code supports the final cartography document's nominal flow. The remaining gaps are wording and governance coverage risks, not backend implementation defects.
