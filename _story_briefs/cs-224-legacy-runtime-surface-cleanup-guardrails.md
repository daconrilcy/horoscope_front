# CS-224 — Legacy Runtime Surface Cleanup & Guardrails

## Résumé

CS-224 sécurise la fin de la migration vers `ChartObjectRuntimeData`.

Après CS-217 à CS-223, le backend dispose d’un graphe de thème unifié consommé par les aspects, motion/visibility, dignités/dominance, conjonctions aux étoiles fixes et input interprétatif.

CS-224 doit maintenant verrouiller l’architecture pour éviter que les anciennes surfaces redeviennent des sources de vérité parallèles.

Cette story ne supprime pas brutalement les champs historiques exposés au front ou aux APIs. Elle les requalifie comme projections de compatibilité et ajoute des guardrails pour que les nouveaux développements passent par `chart_objects`.

---

## Contexte

Les stories précédentes ont déplacé la source runtime vers :

```python
NatalResult.chart_objects
```

Mais le résultat natal conserve encore plusieurs collections historiques :

```text
planet_positions
astral_points
houses
angles
aspects
dignity_results
dominance_result
advanced_conditions
fixed_star_conjunctions
```

Ces collections peuvent rester nécessaires pour :

- compatibilité front ;
- compatibilité API ;
- debug ;
- comparaison de non-régression ;
- transition progressive ;
- sorties publiques existantes.

Mais elles ne doivent plus être consommées comme sources primaires par les nouveaux calculateurs.

---

## Problème à résoudre

Sans cleanup et guardrails, le code peut régresser vers :

```text
nouveau calculateur → planet_positions
nouvel adapter → dignity_results
nouveau prompt builder → advanced_conditions
nouveau service → if object_type == "planet"
```

Cela recrée le problème initial :

- duplication ;
- branches conditionnelles ;
- explosion de builders spécialisés ;
- incohérence entre `chart_objects` et les anciennes collections ;
- difficulté à maintenir le moteur ;
- dette accrue à chaque nouvel objet astrologique.

CS-224 doit empêcher cette régression.

---

## Objectifs

### Objectif fonctionnel

Faire de `chart_objects` la surface runtime canonique pour les nouveaux consommateurs.

Les anciennes collections restent disponibles, mais elles sont documentées et traitées comme :

```text
legacy compatibility projections
```

ou :

```text
public API projections
```

et non comme sources métier.

### Objectif architectural

Installer trois niveaux clairs :

```text
1. Source canonique interne
   NatalResult.chart_objects

2. Projections de compatibilité
   planet_positions, houses, angles, dignity_results, etc.

3. Sorties API/front/LLM
   contrats exposés ou adaptés, construits depuis les projections nécessaires
```

Les calculateurs doivent consommer le niveau 1. Les adaptateurs externes peuvent exposer le niveau 2 si la compatibilité l’exige.

---

## Périmètre inclus

CS-224 couvre :

1. L’inventaire des anciennes surfaces runtime.
2. La documentation de leur statut : canonical, projection, legacy, deprecated, public compatibility, chart-level result.
3. L’ajout ou le renforcement de tests d’architecture.
4. La restriction des nouveaux calculateurs à `chart_objects`.
5. La suppression ou consolidation des duplications évidentes de builders/mappers devenus inutiles.
6. La création d’un module de projection centralisé si nécessaire.
7. La stabilisation de `NatalResult` comme contrat de transition.
8. La vérification que les sorties historiques restent cohérentes avec `chart_objects`.
9. Les recherches `rg` anti-régression.
10. La documentation de la trajectoire de suppression future.

---

## Hors périmètre

CS-224 ne doit pas :

- casser l’API publique ;
- supprimer brutalement les champs utilisés par le front ;
- modifier la doctrine astrologique ;
- modifier les scores ;
- réécrire les calculateurs déjà migrés ;
- migrer un nouveau domaine fonctionnel majeur ;
- faire une refonte de sérialisation HTTP ;
- supprimer des tables DB ;
- changer les prompts LLM.

CS-224 est une story de consolidation, pas une nouvelle feature astrologique.

---

## Décisions d’architecture

### `chart_objects` devient la surface canonique

Règle :

```text
Tout nouveau calculateur astrologique doit consommer chart_objects ou une projection explicitement construite depuis chart_objects.
```

Autorisé :

```python
objects = chart_object_selector.select(natal_result.chart_objects)
```

Interdit hors projection/compatibilité :

```python
objects = natal_result.planet_positions
```

### Les anciennes collections deviennent des projections

Les collections suivantes doivent être marquées/documentées comme projections ou surfaces de compatibilité :

```text
planet_positions
astral_points
houses
angles
dignity_results
advanced_conditions
fixed_star_conjunctions
```

Certaines sorties restent des résultats chart-level légitimes, par exemple :

```text
aspects
dominance_result
```

mais leur production ou consommation future doit rester cohérente avec `chart_objects`.

### Les exceptions doivent être explicites

Une exception est acceptable uniquement si elle est documentée :

```text
legacy API serializer
public compatibility adapter
test fixture
migration bridge
debug snapshot
```

Toute exception doit être whitelistée dans les tests d’architecture.

---

## Inventaire attendu

Créer un document ou une constante de gouvernance listant les surfaces runtime.

Emplacement recommandé :

```text
docs/architecture/astrology-runtime-surfaces.md
```

Tableau attendu :

| Surface | Statut | Source cible | Autorisée dans calculateurs | Commentaire |
|---|---|---|---|---|
| `chart_objects` | canonical | runtime builder | oui | Source interne cible |
| `planet_positions` | compatibility projection | chart_objects / legacy bridge | non | Conservé API/front |
| `astral_points` | compatibility projection | chart_objects / legacy bridge | non | Conservé API/front |
| `houses` | compatibility projection | chart_objects / house runtime | non | Conservé API/front |
| `angles` | compatibility projection | chart_objects / angle runtime | non | Conservé API/front |
| `aspects` | calculated result | chart_objects | lecture contrôlée | Calculé depuis chart_objects |
| `dignity_results` | compatibility projection | payloads.dignity | non | Conservé temporairement |
| `dominance_result` | chart-level result | dominance calculator | lecture contrôlée | Résultat global |
| `advanced_conditions` | compatibility projection | motion/visibility/condition payloads | non | À migrer en lecture |
| `fixed_star_conjunctions` | compatibility projection | payloads.fixed_star_conjunctions | non | Si sortie historique existe |

---

## Composants techniques recommandés

### `ChartRuntimeProjectionBuilder`

Si plusieurs projections historiques doivent être maintenues, créer un composant centralisé :

```python
@dataclass(frozen=True, slots=True)
class ChartRuntimeProjectionBuilder:
    def build_planet_positions_projection(
        self,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
    ) -> tuple[PlanetPositionRuntimeData, ...]:
        ...

    def build_dignity_results_projection(
        self,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
    ) -> tuple[PlanetDignityResult, ...]:
        ...
```

Attention : ce composant ne doit pas devenir un nouveau monolithe. Il est acceptable seulement s’il réduit les duplications existantes.

### `ChartRuntimeSurfaceValidator`

Créer ou renforcer un validateur :

```python
@dataclass(frozen=True, slots=True)
class ChartRuntimeSurfaceValidator:
    def validate(
        self,
        natal_result: NatalResult,
    ) -> None:
        ...
```

Responsabilités possibles :

- vérifier que les objets historiques sont cohérents avec `chart_objects` ;
- vérifier les codes présents ;
- vérifier les scores projetés ;
- vérifier les conjonctions aux étoiles fixes projetées ;
- détecter les divergences évidentes.

Ce validateur peut être utilisé en tests plutôt qu’en production si le coût runtime est trop élevé.

### Tests d’architecture

Ajouter ou renforcer des tests AST/regex pour interdire les consommations directes non autorisées :

```text
planet_positions
astral_points
advanced_conditions
dignity_results
fixed_star_conjunctions
```

Interdire également :

```text
if obj.object_type == ...
if object_type == "planet"
ChartObjectType.PLANET
```

hors whitelists explicites.

---

## Règles de nettoyage

### Pas de suppression risquée

Ne pas supprimer une surface historique si :

- elle est exposée par une API ;
- elle est utilisée par le front ;
- elle est utilisée par l’admin ;
- elle est utilisée par le pipeline LLM ;
- elle sert de fixture de non-régression.

La suppression doit faire l’objet d’une story dédiée avec preuve de non-usage.

### Suppression autorisée

Supprimer ou fusionner uniquement les éléments devenus manifestement redondants :

- builders spécialisés non utilisés ;
- adaptateurs morts ;
- fonctions privées remplacées par selectors/projectors `chart_objects` ;
- tests obsolètes qui valident une ancienne frontière devenue fausse.

Chaque suppression doit être justifiée par une recherche `rg`, un test ou une preuve de non-usage.

### Documentation obligatoire

Toute surface legacy conservée doit avoir une raison explicite.

Exemple :

```text
planet_positions is retained as a public compatibility projection for current API consumers.
New domain calculators must not consume it directly.
```

---

## Guardrails attendus

### Interdire les nouvelles entrées spécialisées dans les calculateurs

Patterns à surveiller :

```text
natal_result.planet_positions
natal_result.astral_points
natal_result.advanced_conditions
natal_result.dignity_results
```

Exceptions possibles : projection builders, legacy adapters, serializers API, tests.

### Interdire l’éligibilité par `object_type`

Patterns à surveiller :

```text
object_type == "planet"
object_type == "angle"
object_type == "fixed_star"
.object_type ==
ChartObjectType.PLANET
ChartObjectType.ANGLE
ChartObjectType.FIXED_STAR
```

Exceptions possibles : `ChartObjectRuntimeBuilder`, projection builders, tests.

### Interdire les builders spécialisés futurs

Patterns à surveiller dans les nouveaux modules :

```text
Planet*Builder
Angle*Builder
AstralPoint*Builder
FixedStar*Builder
```

Ces noms peuvent exister s’ils sont historiques, mais toute nouvelle création doit être justifiée. La cible est `ChartObject selector/projector/enricher`.

### Interdire les seuils magiques

Continuer à refuser les orbes, seuils de station, seuils de combustion ou seuils fixed stars codés en dur dans les calculateurs. Ils doivent venir de règles runtime, référentiels ou constantes nommées.

---

## Tests attendus

### 1. Test d’inventaire documentaire

Vérifier que la documentation des surfaces runtime existe et mentionne au minimum :

```text
chart_objects
planet_positions
astral_points
houses
angles
aspects
dignity_results
dominance_result
advanced_conditions
fixed_star_conjunctions
```

### 2. Test de cohérence des projections historiques

Sur un thème natal de test, vérifier que :

```text
planet_positions correspond aux objets chart_objects concernés.
dignity_results correspond aux payloads.dignity.
fixed_star_conjunctions correspond aux payloads.fixed_star_conjunctions si la sortie existe.
```

Adapter selon les surfaces réellement présentes.

### 3. Test architecture : pas de consommation directe legacy

Un test doit échouer si un nouveau calculateur consomme directement :

```text
planet_positions
advanced_conditions
dignity_results
```

hors whitelist.

### 4. Test architecture : pas de logique `object_type`

Un test doit échouer si un consommateur métier ajoute :

```python
if obj.object_type == ...
```

hors whitelist.

### 5. Test architecture : pas de builders spécialisés

Un test doit détecter les nouveaux builders spécialisés non autorisés.

### 6. Test de compatibilité `NatalResult`

Vérifier que le contrat de `NatalResult` expose toujours les anciennes collections nécessaires. Attendu : aucune rupture front/API involontaire.

### 7. Test du flux canonique

Créer un test d’intégration qui vérifie le flux cible :

```text
natal calculation
→ chart_objects
→ aspects/motion/dignity/dominance/fixed stars/interpretation input
```

sans consommation directe des anciennes surfaces dans les nouveaux composants.

---

## Critères d’acceptation

La story est acceptée si :

1. Une documentation des surfaces runtime existe.
2. `chart_objects` est documenté comme source canonique interne.
3. Les anciennes collections sont documentées comme projections ou résultats chart-level.
4. Les calculateurs migrés ne consomment plus directement les anciennes collections.
5. Les exceptions sont explicites et whitelistées.
6. Les tests d’architecture empêchent la réintroduction de logique `object_type`.
7. Les tests d’architecture empêchent la consommation directe legacy non autorisée.
8. Les projections historiques restent cohérentes avec `chart_objects`.
9. Les sorties publiques ne sont pas cassées.
10. Les suppressions éventuelles sont justifiées par preuves.
11. Aucun changement de doctrine astrologique n’est introduit.
12. Les commandes de validation passent.

---

## Validation technique

```powershell
cd backend
ruff format .
ruff check .
pytest -q
```

Tests ciblés :

```powershell
pytest backend/tests/domain/astrology/runtime -q
pytest backend/tests/integration/astrology -q
pytest backend/tests/architecture -q
```

Recherches anti-régression :

```powershell
rg "natal_result\.planet_positions|natal_result\.astral_points|natal_result\.advanced_conditions|natal_result\.dignity_results" backend/app/domain/astrology
rg "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.ANGLE|ChartObjectType\.FIXED_STAR" backend/app/domain/astrology
rg "Planet.*Builder|Angle.*Builder|AstralPoint.*Builder|FixedStar.*Builder" backend/app/domain/astrology
```

Les résultats doivent être vides, limités aux whitelists ou documentés dans l’évidence finale.

---

## Évidence finale attendue

```markdown
## CS-224 Final Evidence

### Runtime surfaces
- Documented canonical and legacy runtime surfaces.
- chart_objects is the canonical internal source.
- Legacy collections are retained as compatibility projections.

### Cleanup
- Removed or consolidated redundant builders/adapters where safe.
- No public API/front-breaking removal.

### Guardrails
- Added architecture tests for direct legacy consumption.
- Added architecture tests for object_type-driven logic.
- Added guardrails against specialized builders.

### Consistency
- Historical projections remain coherent with chart_objects.
- NatalResult compatibility is preserved.

### Validation
- ruff format .
- ruff check .
- pytest -q

### Exceptions
- Listed all whitelisted legacy usages and reasons.
```

---

## Risques à surveiller

Le premier risque est de vouloir supprimer trop tôt. CS-224 doit consolider et verrouiller, pas casser l’existant.

Le deuxième risque est de rendre les tests d’architecture trop stricts et de bloquer des zones historiques non encore migrées. La bonne approche est : strict pour les nouveaux composants, whitelist explicite pour le legacy, preuve de trajectoire pour le reste.

Le troisième risque est de créer un énorme projection builder qui devient une nouvelle dette. Centraliser oui, mais seulement là où cela réduit réellement la duplication.

Le quatrième risque est de confondre résultat chart-level et projection legacy. Par exemple, `dominance_result` peut rester un vrai résultat global ; il doit simplement être cohérent avec les payloads de contribution portés par les objets.

---

## Formulation courte pour Codex

```markdown
Implémente CS-224 — Legacy Runtime Surface Cleanup & Guardrails.

Objectif:
Consolider la migration vers ChartObjectRuntimeData en documentant chart_objects comme source canonique interne, en requalifiant les anciennes collections comme projections de compatibilité ou résultats chart-level, et en ajoutant des guardrails empêchant les nouveaux calculateurs de consommer directement planet_positions, advanced_conditions, dignity_results, etc.

À faire:
- Inventorier les surfaces runtime existantes.
- Documenter leur statut: canonical, compatibility projection, chart-level result, legacy.
- Ajouter/renforcer les tests d’architecture anti-consommation legacy.
- Ajouter/renforcer les tests anti object_type-driven logic.
- Vérifier la cohérence entre projections historiques et chart_objects.
- Supprimer uniquement les builders/adapters manifestement morts et prouvés non utilisés.
- Préserver l’API/front/LLM.
- Produire une évidence finale avec whitelists et résultats de validation.

Interdictions:
- Pas de suppression publique cassante.
- Pas de changement de doctrine astrologique.
- Pas de refonte API.
- Pas de nouveau calculateur branché sur les collections historiques.
- Pas de branche métier if object_type == ...

Validation:
- ruff format .
- ruff check .
- pytest -q
- rg anti-régression sur usages legacy, object_type et builders spécialisés.
```
