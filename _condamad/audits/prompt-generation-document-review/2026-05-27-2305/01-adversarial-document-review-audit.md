<!-- Commentaire global: revue adversariale ligne par ligne du document final de cartographie prompt LLM CS-350. -->

# Adversarial Document Review Audit

## Resume executif

Decision finale: `acceptable with corrections`.

Le document `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` est globalement source-aligne avec CS-343 a CS-349 et les owners backend inspectes. Il separe correctement les chemins nominaux, fallback, legacy, seed, tests et audit-only. Deux corrections documentaires sont recommandees: clarifier le double role validation/audit des `evidence_refs`, et remplacer la formulation `backend-only runtime` pour `request_id` et `trace_id` par `runtime/provider-only metadata, not prompt-visible payload`.

## Methode de revue adversariale

La revue a confronte les affirmations du document cible avec:

| Source family | Paths | Usage |
|---|---|---|
| Document cible | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | Claims reviewed line by line through headings, tables and sensitive terms. |
| CS-343 a CS-347 | `_condamad/audits/prompt-generation-cartography/**` | Source map, configuration, handoff, natal input, validation and persistence checks. |
| CS-348 | `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` | Boundary vocabulary, blockers, owner decisions. |
| CS-349 | `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/**` | Evidence gaps and final report constraints. |
| Backend owners | `backend/app/domain/llm/runtime/gateway.py`, `backend/app/infra/providers/llm/openai_responses_client.py`, `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`, `backend/app/services/llm_generation/natal/interpretation_service.py` | Source-level verification for provider metadata, prompt-visible filtering and audit persistence. |

Categories appliquees: `erreur factuelle`, `omission`, `ambiguite`, `contradiction`, `risque de formulation`.

## Matrice des affirmations validees

| claim | expected source | status | finding category | evidence | recommended correction |
|---|---|---|---|---|---|
| Le flux nominal moderne part d'un use case canonique, resout une assembly, rend le developer prompt, construit `llm_astrology_input_v1`, filtre les blocs prompt-visible, compose les messages provider, valide la sortie, puis persiste les ancres d'audit. | CS-343 surface inventory, CS-344 config audit, CS-345 handoff audit, CS-346 natal input audit, CS-347 persistence audit. | validated | none | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 7, 34-40; `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` surface rows; `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` rows 21-28; `backend/app/domain/llm/runtime/gateway.py` `execute_request`. | none |
| Les blocs prompt-visible de `llm_astrology_input_v1` sont `facts`, `signals`, `limits` et `shaping`. | CS-346 and `LLMAstrologyInputV1Builder`. | validated | none | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 135-140; `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` rows 42-43 and 57-67; `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` `PROMPT_INFLUENCING_BLOCKS` and `build_llm_input_hash_material`. | none |
| `evidence`, `provenance`, hashes, provider responses and persisted answers are excluded from provider prompt material. | CS-345, CS-346, CS-347 and gateway filtering code. | validated | none | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` rows 97-106; `backend/app/domain/llm/runtime/gateway.py` `_prompt_visible_llm_astrology_input` and `_without_prompt_excluded_keys`; `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` `LLM_ASTROLOGY_INPUT_DATA_ROLES`. | none |
| Output schema ownership remains split and must not be presented as a stable product contract. | CS-344 F-002 and CS-348 blocker. | validated | none | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 82, 187, 238, 246; `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` lines 7, 69, 97; `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` blocker rows. | none |
| Fallback, legacy, seed, bootstrap and test paths are non-nominal or non-runtime unless explicitly proven otherwise. | CS-343 source map and CS-344/CS-345 fallback classifications. | validated | none | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 99-105, 189-196, 214-218, 229-242; `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` rows 26-43; `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` line 7. | none |
| No real provider call validates this documentation. | CS-345, CS-349 and document verification section. | validated | none | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 26 and 267; `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` rows 24-25 and 133; `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` lines 123 and 140. | none |

## Matrice des affirmations a corriger ou a nuancer

| claim | expected source | status | finding category | evidence | recommended correction |
|---|---|---|---|---|---|
| Boundary list: `validation-only: evidence, grounding_status, validation_owner, evidence_refs`; persistence section: `evidence_refs` and `grounding_status` are backend-only and audit-only. | CS-346 role matrix, CS-347 persistence matrix, `LLMAstrologyInputV1Builder`, `NatalInterpretationService`. | nuance required | ambiguite | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 137 and 212; `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` lines 57-67; `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` lines 48-57; `backend/app/services/llm_generation/natal/interpretation_service.py` `_apply_narrative_answer_audit`, `_evidence_refs_for_audit`. | State that `evidence` and `evidence_refs` are validation-owned, excluded from prompt material, and may be persisted as audit-only anchors. |
| `backend-only runtime: request_id, trace_id, profils et metadata d'execution`. | Gateway and OpenAI adapter source. | correction required | risque de formulation | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` lines 136, 156, 185; `backend/app/domain/llm/runtime/gateway.py` `_call_provider` lines 1593-1605; `backend/app/infra/providers/llm/openai_responses_client.py` lines 81-83 and 145-150. | Replace with `runtime/provider-only metadata, not prompt-visible payload` for `request_id`, `trace_id` and `use_case`. |

## Omissions potentielles

| claim | expected source | status | finding category | evidence | recommended correction |
|---|---|---|---|---|---|
| Exact guardrail coverage for provider/post-provider documentation. | Guardrail registry and CS-348 story candidates. | unresolved | omission | `_condamad/stories/regression-guardrails.md` RG-042; `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` line 242; `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` story candidates. | Keep the exact guardrail registry gap visible; do not imply RG-042 fully covers `_condamad/docs` provider/post-provider handoff. |

## Contradictions ou tensions entre document, audits et code

| claim | expected source | status | finding category | evidence | recommended correction |
|---|---|---|---|---|---|
| `evidence_refs` is both validation-only and persisted audit data. | CS-346 and CS-347. | nuance required | contradiction | CS-346 classifies the evidence block as validation-only and not prompt-visible; CS-347 records `evidence_refs` and `grounding_status` as validation/audit-only persisted fields. | Wording should present this as layered ownership, not competing roles. |
| `request_id` and `trace_id` are backend-only while the provider adapter sends them as headers. | Gateway and adapter source. | correction required | risque de formulation | `LLMGateway._call_provider` passes identifiers to `execute_with_resilience`; `ResponsesClient.execute` maps them to provider headers. | Say they are not prompt-visible, but are provider request metadata. |
| The document says provider handoff occurs, while no real provider call validates the documentation. | CS-345 and CS-349 limitations. | validated | none | The document already states no provider call in non-goals and verification; CS-345/CS-349 record local/source proof only. | none |

## Corrections documentaires recommandees

| Source finding | Recommended correction | Scope | Runtime change allowed |
|---|---|---|---|
| F-001 | Add one sentence near `Projection prompt-visible vs backend-only`: `evidence` and `evidence_refs` are validation-owned, excluded from provider prompt material, and may be persisted as audit-only anchors. | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` only | no |
| F-002 | Replace `backend-only runtime: request_id, trace_id, profils et metadata d'execution` with wording such as `runtime/provider-only metadata: request_id, trace_id, use_case, profiles and execution metadata; not prompt-visible payload`. | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` only | no |
| F-003 | Keep the exact guardrail gap visible and avoid treating RG-042 as full coverage for `_condamad/docs` provider/post-provider handoff. | Future guardrail story only if needed | no |

## Decision finale

Decision finale: `acceptable with corrections`.

The source document is not rejected because the main path, blockers, fallbacks, seeds, tests, backend-only, validation-only and audit-only distinctions are present and source-backed. Corrections are still required before treating it as a critical future-agent contract without caveat.
