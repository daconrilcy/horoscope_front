# CS-232 — Remove Legacy Runtime Surfaces And Aspect Compatibility Aliases

## Résumé

CS-232 planifie la suppression effective des surfaces legacy devenues inutiles après la migration vers `chart_objects`, le graphe de calcul et la séparation structural/interprétatif des aspects.

Cette story doit être exécutée seulement après :

```text
CS-229 — contrats structural / interpretive
CS-230 — migration du runtime d’aspects
CS-231 — guardrails de frontière
```

La cible est de réduire les surfaces historiques qui entretiennent la confusion :

```text
planet_positions comme source métier
houses comme source métier
advanced_conditions comme source métier
dignities comme source métier
fixed_star_conjunctions top-level
AspectRuntimeData.interpretation alias legacy
champs de valence dans les résultats structurels d’aspects
```

La suppression doit être progressive et prouvée par tests, OpenAPI et compatibilité front.

---

## Contexte

`docs/architecture/astrology-runtime-surfaces.md` documente déjà plusieurs surfaces comme projections de compatibilité.

Certaines resteront peut-être exposées publiquement longtemps, mais elles ne doivent plus exister comme chemins métier internes.

La séparation des aspects ajoute un nouveau legacy à nettoyer :

```text
AspectRuntimeData.interpretation
AspectCalculationResult.default_valence
AspectCalculationResult.interpretive_valence
AspectCalculationResult.energy_type
AspectModifierRuntimeData.interpretive_weight
```

Si CS-230 conserve des alias temporaires, CS-232 doit les supprimer ou les enfermer dans un adapter public explicitement legacy.

---

## Problème à résoudre

Un système peut être officiellement migré tout en restant pratiquement legacy si les anciens chemins restent faciles à utiliser.

Exemples à éviter :

```python
natal_result.planet_positions
natal_result.houses
natal_result.advanced_conditions
aspect_runtime.interpretation.energy_type
aspect.default_valence
```

Ces chemins doivent soit disparaître des couches internes, soit être confinés à :

```text
serializers publics
adapters legacy
tests de compatibilité
fixtures historiques
```

---

## Objectifs

### Objectif fonctionnel

Supprimer ou confiner les surfaces legacy qui ne sont plus nécessaires aux flux internes.

### Objectif architectural

Faire respecter la hiérarchie :

```text
1. chart_objects + structural runtime
2. interpretive runtime / hints
3. public projections
4. legacy adapters temporaires
```

Aucune couche interne nouvelle ne doit dépendre du niveau 4.

---

## Périmètre inclus

CS-232 couvre :

1. L’inventaire final des lectures internes de surfaces legacy.
2. La suppression des alias de compatibilité d’aspects si CS-230 les a créés.
3. La suppression des champs interprétatifs des résultats structurels d’aspects.
4. La migration des derniers consommateurs internes vers `chart_objects`, structural runtime ou interpretive hints.
5. La limitation des surfaces legacy aux serializers/API publics et tests de compatibilité.
6. La mise à jour de `docs/architecture/astrology-runtime-surfaces.md`.
7. La comparaison OpenAPI avant/après si une surface publique est touchée.
8. La validation front si un payload public change.
9. Les tests d’architecture anti-régression.
10. La suppression des allowlists temporaires devenues inutiles.

---

## Hors périmètre

CS-232 ne doit pas :

- supprimer un champ public sans preuve d’absence d’usage front/API ;
- supprimer des tables DB de référence sans story dédiée ;
- changer les textes d’interprétation ;
- changer les scores de prédiction ;
- migrer des domaines non liés aux surfaces natal/aspect ;
- faire un refactor massif de fichiers non concernés ;
- créer une nouvelle branche Git.

---

## Inventaire attendu

Produire un tableau dans la story ou dans la documentation.

Format recommandé :

| Surface | Statut avant | Statut cible | Action | Preuve |
|---|---|---|---|---|
| `NatalResult.chart_objects` | canonical | canonical | conserver | tests graph/runtime |
| `NatalResult.planet_positions` | compatibility projection | public projection only | confiner | OpenAPI/front |
| `NatalResult.houses` | compatibility projection | public projection only | confiner | OpenAPI/front |
| `NatalResult.advanced_conditions` | compatibility projection | adapter legacy ou suppression interne | migrer | rg/tests |
| `AspectRuntimeData.interpretation` | compatibility alias | supprimé ou adapter only | supprimer | tests aspect |
| `AspectCalculationResult.default_valence` | hybrid runtime | supprimé du structurel | supprimer | guardrails |
| `AspectModifierRuntimeData.interpretive_weight` | ambigu | interpretive hints only | déplacer/supprimer | guardrails |
| `AspectDefinitionRuntimeData.default_valence` | hybrid reference view | profil interprétatif séparé | déplacer | tests reference |
| `AstrologyRuntimeReference.aspects` | potentiellement hybride | vues structurelle/interprétative | scinder ou adapter | tests mapper |

---

## Stratégie de migration

### Étape 1 — Mesurer

Rechercher :

```powershell
rg -n "planet_positions|astral_points|houses|advanced_conditions|dignities|fixed_star_conjunctions|aspect_runtime\\.interpretation|default_valence|interpretive_valence|energy_type|interpretive_weight" backend/app backend/tests frontend/src docs/architecture
```

Classer chaque hit :

```text
source métier interne
projection publique
adapter interprétatif
prediction
test/fixture
legacy temporaire
```

Inclure explicitement les résultats dans :

```text
backend/app/domain/prediction/**
backend/app/services/prediction/**
backend/app/infra/db/repositories/**
frontend/src/**
```

### Étape 2 — Migrer les consommateurs internes

Remplacer les lectures métier par :

```text
chart_objects
payloads
structural aspect runtime
interpretive hints
chart interpretation input
calculation graph outputs
```

### Étape 3 — Confiner les projections publiques

Si le JSON public garde un champ, il doit être produit par :

```text
public serializer
public projection adapter
```

et non par le calculateur structurel.

Avant toute suppression publique :

```text
1. comparer OpenAPI ;
2. rechercher les usages frontend ;
3. vérifier les tests API publics ;
4. documenter la migration si un champ disparaît.
```

### Étape 4 — Supprimer les alias

Supprimer les alias et allowlists temporaires après migration des consommateurs.

---

## Tests attendus

### Tests d’architecture

Renforcer :

```text
test_chart_runtime_surface_guardrails.py
test_chart_interpretation_input_boundary.py
test_structural_runtime_boundary.py
```

Prouver que :

1. les nouveaux calculateurs ne lisent pas les surfaces legacy ;
2. les champs interprétatifs ne reviennent pas dans le structurel ;
3. les allowlists temporaires sont supprimées ou justifiées ;
4. les serializers publics sont les seuls endroits où certains champs legacy subsistent.

### Tests de compatibilité publique

Si les sorties API restent identiques :

```text
test_natal_public_contract_compatibility.py
test_chart_json_builder.py
```

Si une sortie publique change, ajouter :

```text
comparaison OpenAPI
test front ciblé
note de migration README ou docs
```

### Tests prediction

Valider les tests prediction qui utilisent :

```text
default_valence
energy_type
public tonality
contribution calculator
natal sensitivity
```

Ces tests doivent prouver que prediction ne dépend plus d’un runtime structurel hybride.

### Tests d’intégration

Valider :

```text
test_natal_calculation_graph_integration.py
test_chart_interpretation_input_pipeline.py
```

---

## Critères d’acceptation

### AC1 — Aucun consommateur métier legacy

Les surfaces legacy ne sont plus lues comme sources métier internes.

### AC2 — Aspects non hybrides

Le runtime structurel d’aspects ne contient plus de champs semi-interprétatifs.

### AC3 — Hints interprétatifs centralisés

La valence, l’energy type, les axes sémantiques et les poids interprétatifs passent par les contrats de hints.

### AC4 — Projections publiques contrôlées

Les champs publics conservés sont produits par un serializer ou adapter explicitement public.

### AC5 — Allowlists réduites

Les allowlists temporaires ajoutées pendant CS-229 à CS-231 sont supprimées ou justifiées avec une story de sortie.

### AC6 — API/front non cassés

L’API publique et le front sont validés si une surface exposée est touchée.

### AC7 — Référentiel non hybride côté calculateurs

Les calculateurs structurels ne consomment plus de définition d’aspect qui oblige à fournir valence ou energy type.

### AC8 — Prediction explicitement routée

Le domaine prediction conserve ses données de valence via un contrat dédié ou une projection, pas via le runtime structurel.

---

## Validation recommandée

PowerShell, après activation du venv :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/tests/architecture backend/tests/unit/domain/astrology backend/tests/integration/astrology backend/app/tests/unit/test_chart_json_builder.py
```

Si le frontend ou l’OpenAPI publique change, compléter avec les commandes front du projet.

---

## Risques et points d’attention

Le risque principal est de confondre suppression interne et suppression publique.

Une surface peut être supprimée comme source métier interne tout en restant exposée comme projection publique stable.

Règle :

```text
Ne supprimer un champ public que si son usage front/API est prouvé absent
ou si une migration produit explicite l’autorise.
```

Le second risque est de garder des alias temporaires trop longtemps. Chaque alias doit avoir une story de sortie, sinon il devient une nouvelle surface legacy.

Le troisième risque est d’oublier que certaines surfaces legacy sont aussi utilisées par le front. Une suppression interne réussie ne doit pas être confondue avec une suppression du contrat public.
