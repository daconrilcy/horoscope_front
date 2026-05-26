# CS-324 — Audit Surfaces Calculs Et Interpretations Vers LLM

## Résumé

Auditer les surfaces backend qui portent aujourd'hui les calculs astrologiques, les interpretations pre-narratives et les projections factuelles avant leur entree dans les generateurs LLM.

L'objectif est de distinguer clairement :

- ce qui vient encore de surfaces legacy ou de projections historiques ;
- ce qui est deja issu de la refonte recente `ChartObjectRuntimeData` / `CalculationGraph` / interpretation input ;
- ce qui manque pour injecter dans les prompts LLM une base plus riche, structuree, concrete et non inventee.

## Contexte

Le runtime astrologique a ete refondu autour de surfaces plus canoniques :

- `backend/app/domain/astrology/runtime/**`
- `backend/app/domain/astrology/builders/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`

Mais la generation LLM natale semble encore consommer principalement `chart_json`, `natal_data`, `evidence_catalog` et `astro_context`, construits depuis `build_chart_json`, `build_enriched_evidence_catalog` et `build_astral_point_interpretation_context`.

Cette story doit etablir la carte exacte entre les calculs disponibles et les donnees reellement disponibles pour l'injection LLM.

## Objectif

Produire un audit cible, reproductible et actionnable des surfaces calculatoires et interpretatives pouvant alimenter les prompts LLM, sans modifier les prompts ni le runtime.

## Sources obligatoires

Lire et citer explicitement :

- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/app/domain/astrology/runtime/natal_result_assembler.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- tests backend associes sous `backend/tests/unit/domain/astrology/**`

## Questions obligatoires

1. Quels calculs existent aujourd'hui dans le runtime canonique mais ne sont pas injectes dans l'entree LLM ?
2. Quels champs LLM actuels proviennent d'une projection legacy ou publique historique ?
3. Quels champs LLM actuels proviennent deja d'un owner recent et canonique ?
4. Quelle est la difference entre `chart_json`, `natal_data`, `astro_context`, `evidence_catalog`, `structured_facts_v1`, `client_interpretation_projection_v1` et `AINarrativeInputContract` ?
5. Quelles donnees sont structurelles, pre-interpretatives, narratives, publiques, debug ou internes ?
6. Quels owners doivent rester source de verite et lesquels ne doivent servir qu'a la compatibilite ?

## Périmètre inclus

1. Inventorier les sorties disponibles du calcul natal.
2. Inventorier les enrichissements interpretatifs disponibles avant narration.
3. Comparer ces sorties avec ce qui est envoye au gateway LLM.
4. Classer chaque surface comme `legacy`, `recent-refonte`, `transition`, `target-candidate` ou `out-of-scope`.
5. Produire une matrice `surface -> owner -> type -> contenu -> consommateur LLM actuel -> potentiel cible`.
6. Identifier les doublons de representation qui risquent de creer des contradictions dans les prompts.

## Hors périmètre

- Modifier les prompts.
- Modifier les generateurs LLM.
- Modifier la securite, le CI ou les astrologues.
- Ajouter une projection.
- Supprimer du legacy.
- Changer les contrats publics.

## Livrable attendu

Créer un dossier d'audit :

```text
_condamad/audits/calculs-interpretations-vers-llm/<YYYY-MM-DD-HHMM>/
```

avec :

- `00-audit.md` : synthese et matrices ;
- `01-evidence-log.md` : commandes, fichiers et extraits courts cites ;
- `02-surface-matrix.md` : matrice des surfaces ;
- `03-gap-register.md` : ecarts entre donnees disponibles et donnees injectees LLM ;
- `04-legacy-register.md` : surfaces legacy ou de transition encore dans la chaine.

## Critères d'acceptation

1. L'audit distingue explicitement `legacy`, `recent-refonte`, `transition` et `target-candidate`.
2. Chaque surface cite un owner code precis.
3. Les champs actuellement passes a `NatalExecutionInput` sont enumeres.
4. Les owners recents non exploites dans l'injection LLM sont identifies.
5. Aucune modification applicative n'est realisee.
6. Les constats sont suffisamment precis pour alimenter une story d'architecture.

## Validation attendue

```powershell
rg -n "build_chart_json|build_enriched_evidence_catalog|NatalExecutionInput|astro_context|structured_facts_v1|AINarrativeInput|client_interpretation_projection_v1|ChartInterpretationInputBuilder|ChartObjectRuntimeData|CalculationGraph" .\backend\app .\backend\tests
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## Risques

Le risque principal est de confondre projection publique historique et source canonique. L'audit doit prouver le sens des dependances avant toute proposition de refactor.
