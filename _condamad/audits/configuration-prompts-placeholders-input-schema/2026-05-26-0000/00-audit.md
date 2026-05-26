# Audit - Configuration Prompts Placeholders Input Schema

Ce fichier est la synthese story-specific CS-327. Le rapport CONDAMAD standard est dans `00-audit-report.md`.

## Conclusion

Readiness globale: `bloquant`.

La configuration LLM natale sait transporter des donnees astrologiques via `chart_json`, `natal_data` et `astro_context`, mais elle ne declare pas encore de contrat moderne `llm_astrology_input` ou equivalent. Les use cases natals actifs declarent `chart_json` dans `input_schema` et dans `required_prompt_placeholders`; les prompts bootstrap v3 gardent `{{chart_json}}` comme source unique.

## Reponses obligatoires

1. Placeholders astrologiques supportes: `chart_json` est le placeholder nominal; `persona_name`, `locale` et `use_case` sont des placeholders d'encadrement; `natal_data` existe dans le contexte/preview mais n'est pas le placeholder nominal des prompts natals lus.
2. Schemas d'entree natals: les schemas exigent `chart_json` et autorisent `locale`; ils ne decrivent pas facts, signals, limits ou proofs.
3. Injection `llm_astrology_input`: non compatible sans decision de contrat; aucun symbole cible n'existe dans le perimetre LLM scanne.
4. Dependances `chart_json`: use-case registry, prompts seeds, runtime contracts, gateway validation payload et prompt rendering.
5. Fallback legacy: fallback output interdit pour features supportees, mais fallback target vers `natal_interpretation_short` et carriers `chart_json`/`natal_data` restent des surfaces de readiness legacy.
6. Declaration cible: a cadrer dans `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, avec support possible dans `backend/app/domain/llm/runtime/contracts.py`.
7. Contraintes renderer: `PromptRenderer` rend des placeholders plats `{{snake_case}}` et des blocs `context_quality`; plusieurs blocs structures doivent etre declares explicitement ou regroupes dans un placeholder/schema unique.

## Sources citees

- `backend/app/domain/llm/configuration/assemblies.py` - entrypoint assembly.
- `backend/app/domain/llm/configuration/assembly_registry.py` - resolution assembly DB/snapshot.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - preview/resolution placeholders, mock `chart_json`/`natal_data`.
- `backend/app/domain/llm/configuration/prompt_versions.py` - entrypoint prompt version.
- `backend/app/domain/llm/configuration/prompt_version_lookup.py` - lookup actif.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - `input_schema` et `required_prompt_placeholders`.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - rendu placeholders.
- `backend/app/domain/llm/prompting/catalog.py` - catalog runtime et fallback configs.
- `backend/app/domain/llm/runtime/input_validation.py` - entrypoint validation.
- `backend/app/domain/llm/runtime/input_validator.py` - JSON Schema Draft 7.
- `backend/app/domain/llm/runtime/gateway.py` - rendu, `build_user_payload`, validation payload, fallback.
- `backend/app/ops/llm/bootstrap/**` - seeds use cases, taxonomy et prompts.
- `backend/tests/llm_orchestration/**` - guards/tests d'orchestration consultes par scans.

## Findings

| ID | Severite | Classe | Resume | Evidence |
|---|---|---|---|---|
| F-001 | High | configuration-blocker | Les use cases natals actifs restent centres sur `chart_json`; aucun contrat `llm_astrology_input` n'est declare. | E-007, E-008, E-019, E-020 |
| F-002 | Medium | data-blocker | La validation runtime peut satisfaire `chart_json` depuis `natal_data` ou `chart_json`, ce qui masque le carrier effectif. | E-012, E-013, E-016 |
| F-003 | Medium | configuration-blocker | Le renderer ne porte pas de contrat multi-blocs facts/signals/limits/proofs. | E-014, E-017, E-023 |
| F-004 | Medium | legacy fallback | Les fallback targets natals et carriers historiques doivent rester separes de la readiness cible. | E-007, E-008, E-021, E-022 |

## Historique Consulte

- Prior same-domain audit: none.
- Adjacent audits: CS-324 `calculs-interpretations-vers-llm`, CS-325 `pipeline-prompt-llm-natal`, CS-326 `projections-interpretatives-llm-input-readiness`.
- Guardrails: `_condamad/stories/regression-guardrails.md`, especially RG-018, RG-021, RG-022.

## Changement Applicatif

Aucun fichier sous `backend/app/**`, `backend/tests/**` ou `frontend/**` n'a ete modifie par l'audit.
