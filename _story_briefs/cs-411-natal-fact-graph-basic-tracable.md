# CS-411 - Construire Un Fact Graph Natal Basic Tracable

<!-- Commentaire global: ce brief cadre l'extraction de faits astrologiques atomiques et tracables pour la lecture Basic. -->

## Resume

Creer `NatalFactGraph`, une couche d'extraction de faits atomiques, types et tracables depuis
le theme natal calcule. Le graphe doit fournir la matiere astrologique utilisable par le
scoring et les themes, sans produire de texte final ni exposer de details techniques au public.

## Contexte

Le plan source exige que le backend sache expliquer pourquoi une section existe, quelles
donnees elle utilise et quels signaux ont ete exclus. Le LLM ne doit recevoir que des faits
selectionnes. Cette story construit la base factuelle avant toute priorisation.

## Objectif

Extraire les familles minimales:

- `luminary_fact`;
- `angle_fact`;
- `planet_position_fact`;
- `house_emphasis_fact`;
- `sign_emphasis_fact`;
- `element_balance_fact`;
- `modality_balance_fact`;
- `aspect_fact`;
- `rulership_fact`;
- `condition_fact`;
- `node_fact`.

Chaque fait doit porter un identifiant stable, une famille, des objets, un niveau de confiance,
un indicateur `requires_birth_time` et des `source_paths`.

## Perimetre Inclus

1. Creer le builder de `NatalFactGraph` a partir des resultats runtime existants.
2. Respecter `EligibilityContext` pour exclure ou degrader les faits dependants de l'heure.
3. Produire des identifiants stables, deterministes et testables.
4. Capturer les `source_paths` internes pour audit, sans les rendre publics.
5. Distinguer facts internes et candidats a preuve editoriale.
6. Couvrir Soleil, Lune, Ascendant, MC, planetes en signes/maisons, aspects majeurs,
   dominantes, dignites/conditions et noeuds.
7. Ajouter des tests unitaires sur fixtures riches, date-only et donnees partielles.
8. Ajouter une garde anti-recalcul: le builder consomme les projections runtime existantes et
   ne recalcule pas aspects, dignites, maisons ou conditions avancees.

## Hors Perimetre

- Attribuer un score de salience.
- Choisir les sections narratives.
- Formuler des phrases utilisateur.
- Ajouter de nouveaux calculs astrologiques.
- Modifier le contrat frontend.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-144` - `ChartObjectRuntimeData` reste le contrat canonique des objets exploitables.
  - `RG-145` - les aspects viennent du moteur d'aspects existant, pas d'un recalcul local.
  - `RG-146` - motion et visibilite sont consommees depuis les payloads runtime.
  - `RG-147` - dignite et dominance sont des projections des resultats historiques.
  - `RG-148` - house position et rulership viennent des resolvers existants.
  - `RG-156` - la couverture Basic doit utiliser une diversite de familles.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
  - `rg -n "calculate_.*aspect|calculate_.*dignity|swe|SwissEph|HouseRulerResolver\\(" backend/app/domain/astrology/interpretation -g "*.py"`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant l'ownership du `NatalFactGraph` et l'interdiction de
    recalcul local.
- Allowed differences:
  - De nouveaux faits internes auditables sont disponibles pour le pipeline Basic.

## Criteres D'acceptation

1. Les faits sont deterministes pour une meme fixture.
2. Les faits dependants de l'heure sont absents ou degrades selon `EligibilityContext`.
3. Les source paths internes existent pour audit mais ne sont pas publics.
4. Les aspects majeurs gardent l'identite stable de la paire et du type d'aspect.
5. Les faits mineurs ne sont pas filtres par opinion narrative dans cette couche.
6. Aucun texte utilisateur final n'est produit dans le domaine d'extraction.
7. Les tests couvrent au moins une fixture riche et une fixture sans heure.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_fact_graph.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_chart_object_runtime_architecture.py --tb=short
```

## Dependances

- CS-404.
- CS-405.

## Risques

Le risque principal est de transformer le fact graph en moteur d'interpretation cache. Il doit
rester une couche factuelle: selection, nuance et narration appartiennent aux stories
suivantes.
