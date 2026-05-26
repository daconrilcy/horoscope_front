# CS-327 — Audit Configuration Prompts Placeholders Input Schema

## Résumé

Auditer la configuration LLM qui determine les prompts, assemblies, placeholders, input schemas et use cases, uniquement sous l'angle de la capacite a recevoir demain des injections astrologiques plus riches.

## Contexte

Le pipeline LLM dispose d'une couche de configuration :

- registry de use cases ;
- prompt versions ;
- assemblies ;
- prompt renderer ;
- input validation ;
- output schemas ;
- placeholders requis ;
- fallback legacy.

Cette story ne doit pas analyser la qualite redactionnelle des prompts. Elle doit verifier si la configuration actuelle permet d'injecter proprement les nouveaux contrats calculs + interpretations, ou si elle force encore une entree legacy du type `chart_json`.

## Objectif

Produire un audit cible de la capacite des prompts/configurations a accepter une entree astrologique structuree moderne sans inventer de donnees.

## Sources obligatoires

Lire et citer explicitement :

- `backend/app/domain/llm/configuration/assemblies.py`
- `backend/app/domain/llm/configuration/assembly_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/prompt_versions.py`
- `backend/app/domain/llm/configuration/prompt_version_lookup.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/input_validation.py`
- `backend/app/domain/llm/runtime/input_validator.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/ops/llm/bootstrap/**`
- tests `backend/tests/llm_orchestration/**`

## Questions obligatoires

1. Quels placeholders lies aux donnees astrologiques sont supportes aujourd'hui ?
2. Les input schemas de use cases natals decrivent-ils les donnees astrologiques attendues ?
3. Les prompts/assemblies peuvent-ils recevoir un nouveau bloc `llm_astrology_input` ou equivalent sans hack ?
4. Quelles configurations dependent encore implicitement de `chart_json` ?
5. Quels fallback legacy peuvent contourner une injection cible ?
6. Ou faudrait-il declarer le contrat d'entree cible pour le rendre validable et testable ?
7. Quelles contraintes de rendu empechent d'injecter plusieurs blocs : faits, signaux, limites, preuves ?

## Périmètre inclus

1. Inventorier les placeholders et schemas d'entree natals.
2. Identifier les use cases natals et modules thematiques concernes.
3. Verifier la relation entre `required_prompt_placeholders`, `input_schema`, `PromptRenderer` et `build_user_payload`.
4. Classer les points de config comme `compatible`, `partiel`, `bloquant`, `legacy fallback`.
5. Produire une matrice `use case -> prompt config -> input schema -> placeholders -> readiness injection`.

## Hors périmètre

- Modifier le texte des prompts.
- Modifier les providers.
- Modifier les astrologues/personas.
- Modifier la securite, le CI ou la gouvernance de release.
- Implementer le nouveau contrat d'injection.

## Livrable attendu

Créer un dossier d'audit :

```text
_condamad/audits/configuration-prompts-placeholders-input-schema/<YYYY-MM-DD-HHMM>/
```

avec :

- `00-audit.md` : synthese ;
- `01-use-case-matrix.md` : matrice des use cases natals ;
- `02-placeholder-schema-matrix.md` : matrice placeholders / schemas ;
- `03-legacy-fallbacks.md` : chemins legacy ou fallback impactant l'injection ;
- `04-readiness.md` : capacite a recevoir le contrat cible.

## Critères d'acceptation

1. Les use cases natals actifs sont listes.
2. Les placeholders astrologiques existants sont inventories.
3. Les input schemas et validations liees a l'astrologie sont documentes.
4. Les dependances implicites a `chart_json` sont identifiees.
5. Les blockers de configuration sont separes des blockers de donnees.
6. Aucune modification applicative n'est realisee.

## Validation attendue

```powershell
rg -n "required_prompt_placeholders|input_schema|chart_json|natal_data|astro_context|prompt_version|assembly|natal_interpretation|natal_long_free|PromptRenderer" .\backend\app .\backend\tests
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## Risques

Le risque principal est de preparer un contrat d'injection astrologique sans verifier que les assemblies et schemas peuvent le porter. L'audit doit isoler les contraintes de configuration avant tout refactor.
