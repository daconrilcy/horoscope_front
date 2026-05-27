# CS-344 - Audit Configuration Assemblies Placeholders Prompts LLM

<!-- Commentaire global: ce brief cadre l'audit de la configuration LLM qui selectionne, assemble et rend les prompts. -->

## Resume

Auditer la chaine de configuration des prompts: use cases canoniques, assemblies, templates, personas, plan rules, placeholders, schemas de sortie et profils d'execution.

## Contexte

CS-343 doit inventorier les surfaces. Cette story approfondit la couche configuration afin de documenter comment un use case devient un developer prompt et quels registres gouvernent les variables autorisees.

## Objectif

Produire une carte des proprietaires de configuration qui repond a:

- quel registre declare les use cases et leurs placeholders requis;
- comment un assembly est resolu;
- quels blocs composent le developer prompt;
- comment les variables sont validees ou remplacees;
- quelles differences existent entre chemin nominal, fallback borne et seed/bootstrap.

## Perimetre inclus

1. Auditer `canonical_use_case_registry.py`.
2. Auditer `assembly_resolver.py`, `assembly_registry.py`, `assemblies.py`, `active_release.py`.
3. Auditer `prompt_renderer.py`, `placeholder_policy.py`, `prompt_governance_registry.py`.
4. Auditer `execution_profile_registry.py`, `execution_profiles.py` et les profils runtime associes.
5. Auditer les seeds/bootstrap LLM qui creent prompts, use cases, schemas, personas et assemblies.
6. Auditer les tests de prompt resolution, differentiation et coherence.
7. Produire une matrice: owner, source de donnees, sortie, garde, test.

## Hors perimetre

- Modifier les templates.
- Ajouter une nouvelle regle de gouvernance.
- Corriger les placeholders.
- Auditer le handoff provider, qui releve de CS-345.

## Sources a lire

- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`
- `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`

## Fichiers a inspecter en priorite

- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/assembly_registry.py`
- `backend/app/domain/llm/governance/prompt_governance_registry.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/prompting/placeholder_policy.py`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/evaluation/test_prompt_resolution.py`
- `backend/tests/evaluation/test_differentiation.py`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/02-configuration-assembly-placeholder-audit.md
```

Le document doit contenir:

1. Diagramme texte de la resolution configuration.
2. Matrice des registres.
3. Matrice des blocs de developer prompt.
4. Liste des placeholders autorises par famille.
5. Liste des fallbacks et conditions d'activation.
6. Tests existants qui prouvent ou ne prouvent pas la configuration.
7. Gaps de couverture.

## Criteres d'acceptation

1. Les use cases natals modernes et non natals sont differencies.
2. `llm_astrology_input_v1` est trace depuis le contrat de use case jusqu'au rendu.
3. Les blocs feature, subfeature, persona, plan rules, hard policy, length budget et context quality sont classes.
4. Les chemins fallback ne sont pas presentes comme nominaux.
5. Les seeds/bootstrap sont separes du runtime.

## Validation attendue

```powershell
rg -n "required_prompt_placeholders|assemble_developer_prompt|PromptRenderer|PLACEHOLDER|PLAN_RULES|length_budget|context_quality" backend/app backend/tests
rg -n "configuration-assembly-placeholder-audit" _condamad
```

## Risques

Le risque principal est d'oublier que la configuration DB et les seeds peuvent differer du chemin runtime actif. Le livrable doit separer source persistante, registre code et comportement execute.

