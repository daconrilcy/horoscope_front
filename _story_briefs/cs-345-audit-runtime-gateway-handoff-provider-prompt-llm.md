# CS-345 - Audit Runtime Gateway Handoff Provider Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit du gateway LLM et du handoff provider qui produisent les messages envoyes au modele. -->

## Resume

Auditer le pipeline runtime du gateway: resolution de plan, validation d'entree, construction du payload utilisateur, composition des messages, appel provider, validation de sortie, recovery et observability.

## Contexte

CS-344 documente la configuration des prompts. Cette story documente le chemin execute qui transforme cette configuration en messages provider.

## Objectif

Prouver comment se construit le prompt complet a l'execution:

- system core;
- developer prompt;
- persona block;
- historique chat si applicable;
- user payload;
- parametres provider;
- output schema;
- metadata d'audit et observability.

## Perimetre inclus

1. Auditer `LLMGateway.execute_request`.
2. Auditer `_resolve_plan`, `_build_messages`, `build_user_payload`, `compose_chat_messages`, `compose_structured_messages`.
3. Auditer `_prompt_visible_llm_astrology_input` et les exclusions prompt provider.
4. Auditer `_call_provider`, `ProviderRuntimeManager`, `ProviderParameterMapper`.
5. Auditer validation input/output, repair et fallback.
6. Auditer logs, call logs, snapshots, usage et metadata liees au prompt.
7. Produire une trace sequencee du handoff provider.

## Hors perimetre

- Modifier le gateway.
- Tester un provider reel.
- Auditer la production de `llm_astrology_input_v1`, qui releve de CS-346.
- Corriger la validation output, qui releve de CS-347 si un gap est confirme.

## Sources a lire

- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`

## Fichiers a inspecter en priorite

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/provider_runtime_manager.py`
- `backend/app/domain/llm/runtime/provider_parameter_mapper.py`
- `backend/app/domain/llm/runtime/providers.py`
- `backend/app/domain/llm/runtime/output_validator.py`
- `backend/app/domain/llm/runtime/input_validation.py`
- `backend/app/domain/llm/runtime/repair.py`
- `backend/app/domain/llm/runtime/observability.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/03-runtime-gateway-handoff-audit.md
```

Le document doit contenir:

1. Sequence runtime par etape.
2. Forme exacte des messages provider par mode `structured` et `chat`.
3. Matrice des champs inclus/exclus dans `llm_astrology_input_v1`.
4. Conditions de fallback, repair et validation.
5. Parametres provider derives du plan.
6. Metadata d'observability.
7. Tests et gaps.

## Criteres d'acceptation

1. Le dernier point avant provider est identifie.
2. Les contenus system, developer, persona, history et user sont differencies.
3. Les champs audit-only et validation-only sont explicitement exclus du prompt provider.
4. Les chemins `structured` et `chat` sont compares.
5. Les fallbacks sont classes comme non nominaux.

## Validation attendue

```powershell
rg -n "execute_request|_resolve_plan|_build_messages|build_user_payload|compose_chat_messages|compose_structured_messages|_call_provider|_prompt_visible_llm_astrology_input" backend/app/domain/llm/runtime backend/tests
rg -n "runtime-gateway-handoff-audit" _condamad
```

## Risques

Le risque principal est de documenter le plan resolu au lieu du message effectivement envoye. L'audit doit toujours remonter au dernier payload avant provider.

