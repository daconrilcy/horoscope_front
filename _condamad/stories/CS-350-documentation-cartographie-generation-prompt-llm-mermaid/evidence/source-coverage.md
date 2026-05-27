<!-- Commentaire global: couverture des sources obligatoires utilisees pour la documentation CS-350. -->

# Source Coverage - CS-350

| Source obligatoire | Statut | Usage |
|---|---|---|
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | covered | Surface owners, boundaries, debt and test surfaces. |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | covered | Configuration, assembly, placeholders, schema split, fallbacks. |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | covered | Gateway handoff, messages, structured/chat modes. |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | covered | `llm_astrology_input_v1`, prompt-visible blocks, backend-only exclusions. |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | covered | Validation, repair, rejection, persistence, observability, replay. |
| `_condamad/architecture/prompt-generation-cartography/2026-05-27-0000/architecture-prompt-generation-llm.md` | covered | Architecture decisions, blockers, roadmap and operational rules. |
| `_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md` | covered | Delivery synthesis and residual risks. |
| `backend/app/domain/llm/runtime/gateway.py` | covered by targeted scan | `LLMGateway`, message composition, repair/fallback, provider handoff. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | covered by targeted scan | `assemble_developer_prompt`, assembly resolution. |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | covered by targeted scan | `CanonicalUseCaseContract`, modern natal input schema. |
| `backend/app/domain/llm/prompting/prompt_renderer.py` | covered by targeted scan | `PromptRenderer`, placeholders and fallback classification. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | covered by targeted scan | `LLMAstrologyInputV1Builder`, hash and backend-only exclusions. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | covered by targeted scan | Natal orchestration and persistent audit anchors. |

## Source blockers

No mandatory CS-343 to CS-349 artifact is missing in this workspace at implementation time. Residual blockers are domain blockers already documented by CS-348: output schema ownership split and bounded semantic grounding.
