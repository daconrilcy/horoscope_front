# CS-226 — Natal Calculation Graph Definition

## Résumé

CS-226 déclare le graphe de calcul du thème natal à partir des contrats introduits par CS-225.

Le but est de rendre explicite l’ordre logique du pipeline natal sans encore remplacer l’exécution procédurale existante. Le graphe devient une carte vérifiable des dépendances : les maisons ne sont pas calculées "avant" les positions par hasard, les dignités ne dépendent pas implicitement d’un état déjà enrichi, la signature ne pioche pas dans plusieurs surfaces historiques sans le déclarer.

Exemple cible :

```text
prepared_birth_data -> planet_positions
prepared_birth_data + runtime_reference -> astral_points
julian_day + coordinates + house_system -> houses_runtime
planet_positions + astral_points + houses_runtime + runtime_reference -> chart_objects
chart_objects -> aspects_runtime
chart_objects + houses_runtime -> house_positions
chart_objects + houses_runtime + runtime_reference -> house_rulerships
chart_objects + aspects_runtime + houses_runtime -> dignities
chart_objects + aspects_runtime + dignities -> dominance
chart_objects + signs_runtime + houses_runtime + aspects_runtime -> chart_signature
```

---

## Contexte

CS-225 a créé les contrats de graphe de calcul. CS-226 doit les appliquer à un cas concret : le thème natal.

Le pipeline actuel contient déjà les étapes fonctionnelles, mais leur dépendance est portée par l’ordre du code dans `natal_calculation.py`. Ce modèle rend les futurs ajouts coûteux :

- ajouter des transits demande de savoir quel sous-ensemble du thème natal est réutilisable ;
- ajouter la synastrie demande de composer deux graphes nataux ;
- ajouter des profections ou progressions demande de produire des graphes temporels dérivés ;
- ajouter des returns demande de partager des nodes de positions, maisons, aspects et signatures.

CS-226 doit donc produire une définition déclarative stable de `natal_chart_v1`.

---

## Objectifs

### Objectif fonctionnel

Fournir une définition de graphe natal validée par les tests, utilisable comme documentation exécutable.

Exemple :

```python
definition = build_natal_calculation_graph_definition()
validation = CalculationGraphValidator().validate(definition)
assert validation.is_valid
```

### Objectif architectural

Créer une source de vérité déclarative pour les dépendances du thème natal, sans changer le résultat produit par `build_natal_result`.

La story doit permettre de répondre simplement à :

```text
De quoi dépend `houses_runtime` ?
Quelles étapes consomment `chart_objects` ?
Quelle étape produit `dominance_result` ?
Quelle surface legacy est une projection et non une dépendance canonique ?
```

---

## Périmètre inclus

CS-226 couvre :

1. La création de `build_natal_calculation_graph_definition`.
2. La déclaration des inputs natals.
3. La déclaration des nodes existants du pipeline natal.
4. La déclaration des outputs canonique vs compatibility projection.
5. La validation du graphe via le validator CS-225.
6. Un test d’alignement entre la définition et les noms de surfaces runtime documentées.
7. Une documentation courte de chaque node.
8. Une évidence listant les dépendances principales.

---

## Hors périmètre

CS-226 ne doit pas :

- exécuter le graphe ;
- migrer `build_natal_result` ;
- supprimer le pipeline procédural ;
- modifier les sorties publiques ;
- ajouter de nouvelles données astrologiques ;
- changer les calculateurs existants ;
- ajouter des transits, synastrie, progressions ou returns ;
- déplacer massivement les fichiers.

---

## Graphe cible recommandé

### Inputs

Inputs recommandés :

```text
birth_datetime
timezone
coordinates
house_system
zodiac_mode
runtime_reference
locale
calculation_options
```

Inputs dérivés possibles :

```text
prepared_birth_data
julian_day
effective_house_system
```

### Nodes de base

```text
prepare_birth_data
planet_positions
astral_points
houses_raw
houses_runtime
signs_runtime
chart_objects_base
```

### Nodes d’enrichissement

```text
house_positions
house_rulerships
fixed_star_conjunctions
aspects_runtime
advanced_conditions
motion_visibility_payloads
dignities
dominance
chart_signature
interpretation_input
```

### Nodes de projection de compatibilité

```text
planet_positions_projection
astral_points_projection
houses_projection
aspects_projection
dignity_results_projection
advanced_conditions_projection
fixed_star_conjunctions_projection
public_natal_result
```

Ces nodes peuvent être déclarées, mais elles doivent être marquées `compatibility_projection` ou `public_projection`.

---

## Contrats attendus

### `NatalCalculationGraphNodeCode`

Enum recommandé :

```python
class NatalCalculationGraphNodeCode(StrEnum):
    PREPARE_BIRTH_DATA = "prepare_birth_data"
    PLANET_POSITIONS = "planet_positions"
    ASTRAL_POINTS = "astral_points"
    HOUSES_RUNTIME = "houses_runtime"
    CHART_OBJECTS_BASE = "chart_objects_base"
    ASPECTS_RUNTIME = "aspects_runtime"
    HOUSE_RULERSHIP_PAYLOADS = "house_rulership_payloads"
    FIXED_STAR_CONJUNCTIONS = "fixed_star_conjunctions"
    DIGNITIES = "dignities"
    DOMINANCE = "dominance"
    CHART_SIGNATURE = "chart_signature"
    PUBLIC_NATAL_RESULT = "public_natal_result"
```

Adapter les noms aux conventions réelles, mais éviter les libellés vagues comme `step_1`, `postprocess` ou `misc`.

### `build_natal_calculation_graph_definition`

Emplacement recommandé :

```text
backend/app/domain/astrology/runtime/natal_calculation_graph.py
```

Signature recommandée :

```python
def build_natal_calculation_graph_definition() -> CalculationGraphDefinition:
    ...
```

La fonction ne doit pas importer FastAPI, SQLAlchemy, services HTTP ou repositories.

---

## Règles de dépendances

### Pas de dépendance à une projection legacy

Un node calculatoire ne doit pas dépendre de :

```text
planet_positions_projection
dignity_results_projection
advanced_conditions_projection
public_natal_result
```

Ces surfaces sont des sorties de compatibilité, pas des sources de calcul.

### Dépendances chart objects

Les nodes suivants doivent dépendre de `chart_objects` ou de son output enrichi approprié :

```text
aspects_runtime
fixed_star_conjunctions
dignities
dominance
interpretation_input
```

Si un node a besoin d’un état enrichi précis, la dépendance doit le dire :

```text
chart_objects_with_house_payloads
chart_objects_with_dignity_payloads
chart_objects_with_fixed_star_payloads
```

### Éviter les dépendances circulaires

Risque typique à bloquer :

```text
dignities depends on dominance
dominance depends on dignities
```

Si la dominance consomme des dignités, alors les dignités ne doivent pas consommer la dominance dans le même graphe.

---

## Tests attendus

1. `build_natal_calculation_graph_definition()` retourne un graphe valide.
2. Les inputs minimaux sont déclarés.
3. Les nodes majeurs du pipeline natal sont présents.
4. `houses_runtime` dépend de `julian_day`, `coordinates`, `house_system`.
5. `house_rulerships` dépend de `houses_runtime` et `chart_objects`.
6. `chart_signature` dépend des signes, maisons et aspects runtime.
7. Aucune node calculatoire ne dépend d’une projection legacy.
8. L’ordre topologique place les prérequis avant les enrichissements.
9. Les tags `canonical_runtime`, `compatibility_projection` et `public_projection` sont utilisés de façon cohérente.

---

## Critères d’acceptation

La story est acceptée si :

1. Le graphe natal `natal_chart_v1` est déclaré.
2. La définition passe le validator CS-225.
3. Les dépendances critiques sont explicites.
4. Les projections legacy sont déclarées comme projections, pas comme sources de calcul.
5. Aucun comportement runtime n’est modifié.
6. Aucune API publique ne change.
7. Les tests documentent l’ordre et les dépendances principales.

---

## Validation technique

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Tests ciblés :

```powershell
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

Scans anti-régression :

```powershell
rg -n "natal_chart_v1|build_natal_calculation_graph_definition|compatibility_projection" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "public_natal_result.*depends_on|dignity_results_projection.*depends_on" backend/app/domain/astrology/runtime -g "*.py"
```

---

## Évidence finale attendue

```markdown
## CS-226 Final Evidence

### Natal Graph
- Declared natal_chart_v1 calculation graph.
- Declared inputs, canonical runtime nodes and projection nodes.
- Graph validates without cycles or unknown dependencies.

### Dependency Proof
- houses_runtime depends on julian_day, coordinates and house_system.
- house_rulerships depends on houses_runtime and chart_objects.
- chart_signature depends on signs, houses and aspects runtime.

### Compatibility
- No runtime execution changed.
- Legacy surfaces are tagged as projections.
- No API, DB or frontend changes.

### Commands
- ruff format .
- ruff check .
- pytest -q
- targeted natal graph tests
```

---

## Formulation courte pour Codex

```markdown
Implémente CS-226 — Natal Calculation Graph Definition.

Objectif:
Déclarer le graphe de calcul natal `natal_chart_v1` avec ses inputs, nodes, outputs et dépendances, sans changer l’exécution actuelle de build_natal_result.

À faire:
- Ajouter build_natal_calculation_graph_definition.
- Déclarer les inputs natals.
- Déclarer les nodes canonical runtime et projections compatibility/public.
- Vérifier les dépendances clés: houses, house_rulerships, signature.
- Ajouter tests d’alignement et validation par le validator CS-225.

Interdictions:
- Pas d’exécution du graphe en production.
- Pas de migration de build_natal_result.
- Pas de changement API/front/DB.
- Pas de dépendance calculatoire à une projection legacy.

Validation:
- ruff format .
- ruff check .
- pytest -q
- tests ciblés natal graph definition.
```
