# CS-325 — Audit Pipeline Prompt LLM Natal Legacy Vs Canonique

## Résumé

Auditer le pipeline effectif qui transforme une demande d'interpretation natale en appel LLM, depuis `NatalInterpretationService` jusqu'au `LLMGateway`, afin de comprendre ou et comment les donnees astrologiques sont injectees aujourd'hui.

## Contexte

Le service natal construit actuellement une entree `NatalExecutionInput` contenant notamment :

- `chart_json`
- `natal_data`
- `evidence_catalog`
- `astro_context`
- `plan`
- `level`
- `variant_code`
- `module`

Le gateway compose ensuite un bloc utilisateur via `build_user_payload`, qui injecte notamment `Technical Data: {chart_json}` si le template ne contient pas deja le placeholder `{{chart_json}}`.

Cette story doit documenter le chemin reel, y compris les branches `free_short`, `short`, `complete` et modules thematiques, sans traiter la redaction du prompt lui-meme.

## Objectif

Produire un audit cible de la chaine d'injection LLM natale actuelle, avec une separation nette entre compatibilite legacy et pipeline canonique cible.

## Sources obligatoires

Lire et citer explicitement :

- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/prompt_context.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/prompting/context.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- tests `backend/tests/llm_orchestration/**`
- tests `backend/app/tests/integration/test_llm_qa_runtime_contracts.py` si present

## Questions obligatoires

1. Quelles donnees astrologiques entrent reellement dans le `LLMGateway` ?
2. Quelles donnees sont injectees dans le message utilisateur et lesquelles restent seulement dans le contexte runtime ?
3. Le placeholder `{{chart_json}}` change-t-il la strategie d'injection ?
4. Les branches `free_short`, `short`, `complete` et modules thematiques utilisent-elles les memes donnees ?
5. Les `evidence_catalog` sont-ils utilises pour contraindre la generation ou seulement pour validation/audit ?
6. Ou les donnees recemment refondues sont-elles perdues, aplaties ou converties en labels ?
7. Quels comportements sont explicitement legacy : routes `/users`, payload simplifie, fallback, compatibilite schema v1/v2/v3 ?

## Périmètre inclus

1. Tracer le flow `NatalInterpretationService.interpret` -> `NatalExecutionInput` -> `AIEngineAdapter.generate_natal_interpretation` -> `LLMExecutionRequest` -> `LLMGateway._build_messages`.
2. Documenter les branches `free_short`, `short`, `complete`, modules thematiques.
3. Identifier les points ou `chart_json` est serialise, injecte, ignore ou remplace par un placeholder.
4. Identifier les zones ou les donnees canoniques pourraient etre ajoutees sans modifier les prompts dans cette story.
5. Produire une matrice `input field -> producer -> consumer -> injection effective -> statut`.

## Hors périmètre

- Recrire les prompts.
- Modifier `PromptRenderer`.
- Modifier les schemas de sortie LLM.
- Changer la selection des use cases ou des modeles.
- Traiter les astrologues/personas.
- Traiter securite, CI ou couts provider.

## Livrable attendu

Créer un dossier d'audit :

```text
_condamad/audits/pipeline-prompt-llm-natal/<YYYY-MM-DD-HHMM>/
```

avec :

- `00-audit.md` : flow runtime et synthese ;
- `01-sequence.md` : sequence step-by-step ;
- `02-input-field-matrix.md` : matrice des champs injectables ;
- `03-branch-matrix.md` : comparaison free/basic/premium, short/complete/module ;
- `04-legacy-vs-canonical.md` : separation legacy/canonique.

## Critères d'acceptation

1. Le chemin exact d'injection LLM est documente avec fichiers et fonctions.
2. Les champs effectivement visibles par le prompt sont distingues des champs seulement transmis au runtime.
3. La logique `chart_json_in_prompt` est expliquee.
4. Les branches de generation natale sont comparees.
5. Les points de perte d'information issue de la refonte astrologique sont listes.
6. Aucune modification applicative n'est realisee.

## Validation attendue

```powershell
rg -n "NatalExecutionInput|generate_natal_interpretation|LLMExecutionRequest|build_user_payload|chart_json_in_prompt|Technical Data|astro_context|evidence_catalog|variant_code|module" .\backend\app .\backend\tests
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## Risques

Le risque principal est de supposer que tout le contexte envoye au gateway est automatiquement injecte dans le prompt. L'audit doit verifier la composition effective des messages.
