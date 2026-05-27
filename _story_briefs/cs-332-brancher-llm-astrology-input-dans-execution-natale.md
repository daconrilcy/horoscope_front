# CS-332 - Brancher llm_astrology_input_v1 Dans L'Execution Natale

<!-- Commentaire global: ce brief cadre le branchement runtime du contrat LLM astrologique dans le chemin natal. -->

## Resume

Brancher `llm_astrology_input_v1` dans le chemin d'execution natal afin que `NatalExecutionInput`, `ExecutionContext` et la composition de message utilisent le contrat riche au lieu de s'appuyer sur `chart_json` comme contenu prompt-visible principal.

## Contexte

CS-330 definit le contrat cible et CS-331 le builder. Cette story rend le contrat executable dans le chemin natal audite.

Le rapport indique que `chart_json` est aujourd'hui la surface prompt-visible prouvee. Le but est d'introduire un champ explicite, versionne et schema-owned, dedie aux donnees astrologiques/interpretees utiles au generateur de prompt.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`

Relire les fichiers critiques:

- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/prompt_renderer.py`
- `backend/app/domain/llm/runtime/models.py`

## Objectif

Faire transiter `llm_astrology_input_v1` dans le runtime LLM natal de facon explicite, testee et prompt-visible.

## Perimetre inclus

1. Ajouter le champ ou wrapper `llm_astrology_input_v1` au point d'entree natal approprie.
2. Mapper ce champ vers `NatalExecutionInput` ou son equivalent courant.
3. Porter dans `ExecutionContext` uniquement les informations de controle necessaires, sans y cacher les faits astrologiques comme source de verite parallele.
4. Rendre le bloc utilisable par le renderer de prompt via un placeholder ou une entree schema-owned explicite.
5. Ajouter des tests de composition de message prouvant que le contrat riche est prompt-visible.
6. Ajouter des tests prouvant que `chart_json` ne sert plus de fallback silencieux quand `llm_astrology_input_v1` est disponible.
7. Conserver une compatibilite de transition documentee si certains use cases ne sont pas encore migres.

## Hors perimetre

- Recrire les prompts redactionnels sur le fond.
- Modifier l'orchestration generale de generation LLM, les providers, retries, politiques d'appel ou workflows hors payload d'entree.
- Traiter la securite, le CI ou les profils astrologues.
- Retirer physiquement `chart_json` / `natal_data`.
- Modifier les endpoints publics ou le frontend.
- Executer un appel LLM reel.

## Criteres d'acceptation

1. Le chemin natal construit et transporte `llm_astrology_input_v1`.
2. Le message utilisateur ou le payload rendu au generateur de prompt contient la version structuree du contrat.
3. `ExecutionContext` ne devient pas un second owner des faits astrologiques.
4. Les tests prouvent la visibilite prompt du contrat cible.
5. Les tests prouvent l'absence de fallback silencieux vers `chart_json` quand le contrat cible est present.
6. Les branches de compatibilite restantes sont nommees et bornees.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "llm_astrology_input_v1|NatalExecutionInput|ExecutionContext|PromptRenderer|chart_json|natal_data|fallback" app tests
```

Les occurrences restantes de `chart_json`, `natal_data` ou `fallback` doivent etre classees dans la sortie de validation: compatibilite de transition bornee, guard negatif, ou dette bloquante.

## Risques

Le risque principal est d'ajouter le contrat riche au runtime sans le rendre effectivement prompt-visible. Les tests doivent inspecter la composition finale envoyee au renderer/gateway, pas seulement les objets intermediaires.
