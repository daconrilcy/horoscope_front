# CS-356 - Documenter La Construction Des Prompts Theme Astral Par Plan

<!-- Commentaire global: ce brief cadre le document de reference qui explique comment les prompts de theme astral sont construits pour free, basic et premium. -->

## Resume

Rediger un document precis et detaille qui decrit la construction des prompts de theme astral pour les plans `free`, `basic` et `premium`, depuis la reception des donnees par le process de prompt jusqu'au payload compile juste avant envoi au moteur LLM.

La story doit documenter ce qui est injecte, comment les astrologues/personas sont introduits, comment les consignes de securite sont ajoutees, et quelles donnees restent exclues du prompt.

## Contexte

La cartographie CS-350 documente le flux general de generation de prompt LLM. Il manque un document plus operationnel centre sur le theme astral natal et lisible par plan produit:

- `free`: prompt et sortie courts, profondeur limitee;
- `basic`: interpretation plus riche, sections plus nombreuses;
- `premium`: interpretation complete, profondeur editoriale maximale autorisee;
- tous les plans doivent conserver les calculs et interpretations backend;
- la differenciation porte sur les donnees prompt-visibles, la profondeur redactionnelle, les sections et les budgets.

## Objectif

Creer une documentation qui permet de repondre sans ambiguite:

- quelles donnees astrologiques et interpretatives arrivent au process de prompt;
- quels builders produisent `facts`, `signals`, `limits`, `shaping`, `evidence` et `provenance`;
- quels blocs de `llm_astrology_input_v1` sont prompt-visibles;
- quelles donnees sont backend-only, validation-only ou audit-only;
- comment le `system_core`, le `developer prompt`, la persona astrologue et le payload user sont composes;
- comment le plan `free`, `basic` ou `premium` modifie le prompt final;
- comment les garde-fous de securite, non-invention, limites et disclaimers entrent dans la chaine;
- a quel moment le payload final est pret pour le provider LLM.

## Perimetre inclus

1. Lire la cartographie CS-350 et les audits CS-343 a CS-347.
2. Relire les stories de differenciation par plan, notamment CS-320 et les stories CS-330 a CS-342.
3. Inspecter les owners backend du flux prompt natal moderne.
4. Produire un document source-aligne dedie au theme astral par plan.
5. Decrire les donnees injectees par bloc et par plan.
6. Decrire l'introduction des astrologues/personas via assembly et gateway.
7. Decrire la securite: hard policy, limites, non-invention, exclusion legacy, validation de sortie et rejet.
8. Nommer les chemins de code, symboles, tests et artefacts d'audit qui supportent chaque section.

## Hors perimetre

- Modifier les prompts en base ou les seeds.
- Modifier le code runtime.
- Ajouter ou modifier des schemas de sortie.
- Faire un appel provider LLM.
- Generer les exemples JSON finaux: cela appartient a CS-358.
- Produire les schemas Mermaid complets: cela appartient a CS-357, sauf si un diagramme minimal est utile dans ce document.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`

## Livrable attendu

Creer:

```text
_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md
```

## Structure obligatoire

1. Executive summary.
2. Scope: theme astral natal, plans `free`, `basic`, `premium`.
3. Vocabulaire: prompt-visible, backend-only, validation-only, audit-only.
4. Point de depart: donnees recues par le process de prompt.
5. Construction de `llm_astrology_input_v1`.
6. Matrice des donnees injectees par bloc et par plan.
7. Resolution use case, assembly, placeholders et plan rules.
8. Introduction de l'astrologue/persona.
9. Construction de la securite et des limites.
10. Composition finale des messages provider.
11. Frontiere exacte avant handoff provider.
12. Differences `free` / `basic` / `premium`.
13. Chemins non nominaux, repair, fallback et rejet.
14. Tests et commandes de verification.
15. Risques residuels et questions ouvertes.

## Contraintes de contenu

- Ne pas inventer de prompt exact si le texte vient de la base ou de seeds non inspectes.
- Quand un texte de prompt est inconnu, documenter le chemin de resolution et l'owner, puis marquer l'inconnu comme "a extraire depuis la configuration runtime".
- Distinguer le `developer prompt` de la persona astrologue: la persona est un bloc `developer` optionnel compose separement.
- Distinguer securite pre-provider et post-provider:
  - pre-provider: hard policy, renderer, required placeholders, exclusions, limites dans `llm_astrology_input_v1`;
  - post-provider: output validation, repair, rejet, persistence audit.
- Expliquer que `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, provider response et observability ne doivent pas entrer dans le prompt.
- Utiliser des tableaux pour les matrices par plan.

## Criteres d'acceptation

1. Le document existe au chemin attendu.
2. Les trois plans `free`, `basic`, `premium` ont chacun une section claire.
3. La documentation couvre tout le trajet entre entree du process de prompt et payload compile avant provider.
4. Les donnees injectees sont classees par source, bloc, role et plan.
5. L'introduction des astrologues/personas est expliquee avec les owners de code.
6. La securite est decrite avec ses controles pre-provider et post-provider.
7. Les exclusions prompt-visible sont explicites.
8. Chaque affirmation technique importante cite un chemin de fichier, un symbole ou un audit.
9. Le document ne pretend pas qu'un appel LLM reel a ete effectue.

## Validation attendue

```powershell
rg -n "free|basic|premium|persona|astrologue|hard policy|non-invention|prompt-visible|backend-only|LLMGateway|PromptRenderer|llm_astrology_input_v1" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md
rg -n "chart_json|natal_data|evidence|provenance|projection_hash|llm_input_hash" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md
```

## Risques

Le risque principal est de transformer une cartographie source-alignee en documentation speculative. Toute valeur non prouvee par code, audit ou configuration doit etre marquee comme inconnue ou a extraire.
