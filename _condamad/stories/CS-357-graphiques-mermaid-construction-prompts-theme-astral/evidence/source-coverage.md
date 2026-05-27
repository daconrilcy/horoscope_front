# Source Coverage

## Scope

Cette carte relie les primitives du brief CS-357 aux sources consultees et aux livrables produits pour les diagrammes Mermaid.

## Mandatory Sources

| Source | Coverage | Status |
|---|---|---|
| `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md` | Objectif, diagrammes obligatoires, hors perimetre, validations attendues. | covered |
| `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | Cartographie CS-350, frontieres prompt-visible et flux provider-capable. | covered |
| `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` | Document CS-356 cite comme document parent et source d'alignement par plan. | covered |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | Handoff gateway, ordre des messages et frontiere avant provider. | covered |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | Sources de `llm_astrology_input_v1` et exclusions modernes. | covered |
| `backend/app/domain/llm/runtime/gateway.py` | `LLMGateway` et composition des messages provider-ready. | cited |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | Resolution assembly, hard policy, plan rules et persona. | cited |
| `backend/app/domain/llm/prompting/prompt_renderer.py` | Rendu des placeholders du developer prompt. | cited |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Blocs `facts`, `signals`, `limits`, `shaping`, `evidence`, `provenance`. | cited |

## Brief Primitive Coverage

| Primitive | Diagram or section | Evidence |
|---|---|---|
| `llm_astrology_input_v1` | Pipeline global, donnees injectees, frontiere prompt-visible. | `natal-prompt-construction-mermaid.md` |
| `facts`, `signals`, `limits`, `shaping` | Construction des donnees injectees. | `rg` validation PASS |
| `evidence`, `provenance` | Donnees injectees et frontiere exclusions. | `rg` validation PASS |
| `system_core`, `developer prompt`, `payload user` | Messages finaux provider. | `rg` validation PASS |
| `persona astrologue` | Introduction astrologue/persona. | `rg` validation PASS |
| `free`, `basic`, `premium` | Differenciation par plan. | `rg` validation PASS |
| `hard policy`, `non-invention` | Securite et non-invention. | `rg` validation PASS |
| `projection_hash`, `llm_input_hash`, `provider_response`, `observability` | Frontiere prompt-visible vs backend-only et exclusions no-call. | `rg` validation PASS |
| `chart_json`, `natal_data` | Frontiere prompt-visible vs backend-only. | `rg` validation PASS |

## Blockers

- Aucun blocker restant: le document CS-356 existe et cite l'annexe Mermaid.
- Aucun appel provider n'a ete execute ou represente au-dela de la frontiere `no provider call`.
