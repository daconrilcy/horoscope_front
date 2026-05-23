# CS-222 — Fixed Star Conjunction Runtime from Chart Objects

## Résumé

CS-222 raccorde les étoiles fixes au runtime unifié `ChartObjectRuntimeData` et calcule les conjonctions entre les objets du thème et les étoiles fixes depuis `NatalResult.chart_objects`.

Après CS-217 à CS-220, le graphe de thème porte déjà les objets unifiés, les aspects, les payloads motion/visibility, les dignités et la dominance. CS-222 doit empêcher que les étoiles fixes restent une famille parallèle avec son propre builder, ses DTOs dédiés et des branches du type `if object_type == "planet"` ou `if object_type == "fixed_star"`.

La cible est simple : les étoiles fixes sont des `ChartObjectRuntimeData` avec un payload `fixed_star`, et les objets pouvant recevoir une conjonction aux étoiles fixes sont sélectionnés par capacité.

```python
fixed_stars = [
    obj for obj in chart_objects
    if obj.payloads.fixed_star is not None
]

targets = [
    obj for obj in chart_objects
    if obj.capabilities.supports_fixed_star_conjunction
]
```

Le runtime ne doit pas produire d’interprétation symbolique. Il doit seulement exposer des contacts calculés : étoile, cible, longitude, orbe, règle appliquée, source.

---

## Contexte

Le backend possède déjà ou va posséder un catalogue d’étoiles fixes : `Regulus`, `Algol`, `Spica`, `Antares`, `Aldebaran`, etc. Ces données sont documentaires ou astronomiques : nom, longitude, constellation, magnitude éventuelle, système de référence, époque, source.

Le risque actuel est de construire une chaîne parallèle :

```text
fixed_star_catalog
→ fixed_star_builder
→ fixed_star_conjunctions
→ interpretation layer
```

alors que la trajectoire d’architecture est désormais :

```text
chart_objects
→ capabilities
→ typed payloads
→ selectors / projectors / enrichers
```

CS-222 doit donc faire entrer les étoiles fixes dans le graphe de thème, puis calculer les conjonctions depuis ce graphe.

---

## Objectifs

### Objectif fonctionnel

Permettre au résultat natal d’exposer les conjonctions aux étoiles fixes à partir de `chart_objects`.

Exemple cible :

```python
mars.payloads.fixed_star_conjunctions == (
    FixedStarConjunctionRuntimePayload(
        fixed_star_code="regulus",
        fixed_star_display_name="Regulus",
        target_code="mars",
        target_display_name="Mars",
        fixed_star_longitude_deg=150.0,
        target_longitude_deg=150.42,
        orb_deg=0.42,
        max_orb_deg=1.0,
        rule_code="default_fixed_star_conjunction",
        source="fixed_star_conjunction_calculator",
    ),
)
```

### Objectif architectural

Faire passer les étoiles fixes de :

```text
catalogue séparé + calcul spécialisé
```

à :

```text
fixed stars as ChartObjectRuntimeData
+ targets selected by supports_fixed_star_conjunction
+ conjunction payloads enriched back into chart_objects
```

Les anciennes sorties éventuelles peuvent rester disponibles comme projections de compatibilité, mais les nouveaux consommateurs doivent utiliser `chart_objects`.

---

## Périmètre inclus

CS-222 couvre :

1. La création ou stabilisation de `FixedStarRuntimePayload`.
2. La création de `FixedStarConjunctionRuntimePayload`.
3. L’ajout de `fixed_star_conjunctions` dans `ChartObjectPayloads` si absent.
4. La construction des étoiles fixes comme `ChartObjectRuntimeData`.
5. La sélection des étoiles fixes via `payloads.fixed_star`.
6. La sélection des cibles via `capabilities.supports_fixed_star_conjunction`.
7. Le calcul déterministe des conjonctions par distance angulaire normalisée.
8. Le respect des règles d’orbe depuis un référentiel, un contrat de règles ou une constante centralisée.
9. L’enrichissement immuable des objets cibles avec les conjonctions détectées.
10. La conservation des sorties historiques si elles existent.
11. Les tests unitaires, d’intégration et d’architecture.

---

## Hors périmètre

CS-222 ne doit pas traiter :

- l’interprétation symbolique des étoiles fixes ;
- les textes astrologiques associés aux étoiles ;
- les aspects autres que la conjonction ;
- les parans ;
- les levers héliaques ;
- la visibilité astronomique réelle des étoiles ;
- la précession avancée si elle n’est pas déjà supportée ;
- la refonte du catalogue ;
- la modification des règles d’orbes existantes sans décision explicite.

Si une donnée astronomique manque, CS-222 doit échouer explicitement ou l’ignorer de manière contrôlée selon la règle métier existante. Elle ne doit pas inventer de coordonnées ou de seuils.

---

## Contrats attendus

### `FixedStarRuntimePayload`

Si ce contrat existe déjà, le stabiliser. Sinon, créer un payload de ce type :

```python
@dataclass(frozen=True, slots=True)
class FixedStarRuntimePayload:
    catalog_code: str
    display_name: str
    constellation_code: str | None
    magnitude: float | None
    reference_system: str
    reference_epoch: str | None
    source_code: str
    categories: tuple[str, ...] = ()
```

Ce payload décrit l’étoile fixe comme objet de thème. Il ne doit contenir aucune interprétation narrative.

### `FixedStarConjunctionRuntimePayload`

Créer un payload de contact :

```python
@dataclass(frozen=True, slots=True)
class FixedStarConjunctionRuntimePayload:
    fixed_star_code: str
    fixed_star_display_name: str
    target_code: str
    target_display_name: str
    fixed_star_longitude_deg: float
    target_longitude_deg: float
    orb_deg: float
    max_orb_deg: float
    rule_code: str
    source: str = "fixed_star_conjunction_calculator"
```

Champs optionnels autorisés si le moteur les supporte déjà :

```python
applying: bool | None = None
separating: bool | None = None
confidence: str | None = None
```

Interdit dans ce payload : `meaning`, `interpretation`, `good`, `bad`, `malefic`, `benefic` sous forme de texte libre.

### Extension de `ChartObjectPayloads`

Ajouter si absent :

```python
fixed_star_conjunctions: tuple[FixedStarConjunctionRuntimePayload, ...] = ()
```

Recommandation : préférer un tuple vide à `None`. Une absence de conjonction est un résultat calculé vide, pas une donnée manquante.

---

## Règles de capacités

### Étoiles fixes

Une étoile fixe dans le graphe doit avoir :

```python
object_type = ChartObjectType.FIXED_STAR
payloads.fixed_star is not None
```

Capacités recommandées par défaut :

```python
ChartObjectCapabilities(
    supports_aspects=False,
    supports_dignities=False,
    supports_house_position=False,
    supports_visibility=False,
    supports_motion=False,
    supports_interpretation=True,
    supports_dominance=False,
    supports_fixed_star_conjunction=False,
)
```

Une étoile fixe n’est pas une cible de conjonction avec elle-même dans CS-222.

### Cibles de conjonction

Les objets pouvant recevoir des conjonctions aux étoiles fixes doivent déclarer :

```python
supports_fixed_star_conjunction=True
```

Candidats possibles selon la doctrine du moteur : planètes, luminaires, nœuds, Lilith, angles, parts, points calculés. La décision ne doit pas être prise par `object_type` dans le calculateur.

---

## Règles de calcul

### Longitude obligatoire

Toute cible avec `supports_fixed_star_conjunction=True` doit avoir une longitude.

Erreur attendue :

```text
Chart object 'mars' declares supports_fixed_star_conjunction=True but has no longitude.
```

Toute étoile fixe doit avoir une longitude.

Erreur attendue :

```text
Fixed star chart object 'regulus' has no longitude.
```

### Référence zodiacale cohérente

Le calcul doit vérifier que les longitudes comparées sont cohérentes : même système de référence, même zodiaque ou transformation déjà appliquée, même époque ou précession gérée en amont.

Si le moteur ne gère pas encore la précession dynamique, CS-222 doit documenter que les longitudes du catalogue sont consommées telles qu’exposées par le runtime.

### Orbes

L’orbe doit venir d’un contrat de règles :

```python
@dataclass(frozen=True, slots=True)
class FixedStarConjunctionRulesRuntimeData:
    default_max_orb_deg: float
    orb_by_star_code: Mapping[str, float]
    orb_by_category: Mapping[str, float]
```

Interdit :

```python
if orb <= 1.0:
```

hors constante nommée, règle runtime ou test.

### Séparation angulaire

Utiliser une fonction centralisée de séparation angulaire normalisée :

```python
orb = angular_distance_deg(target.longitude, fixed_star.longitude)
```

La distance doit être comprise entre `0` et `180`.

### Conjonction uniquement

CS-222 calcule uniquement les conjonctions. Les oppositions, carrés, trigones, parans et levers héliaques feront l’objet de stories dédiées si nécessaire.

---

## Composants techniques recommandés

### `FixedStarChartObjectSelector`

```python
@dataclass(frozen=True, slots=True)
class FixedStarChartObjectSelector:
    def select(
        self,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        ...
```

Responsabilités :

- sélectionner les objets avec `payloads.fixed_star is not None` ;
- valider la longitude ;
- valider les codes uniques ;
- préserver un ordre déterministe.

### `FixedStarConjunctionTargetSelector`

```python
@dataclass(frozen=True, slots=True)
class FixedStarConjunctionTargetSelector:
    def select(
        self,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        ...
```

Responsabilités :

- sélectionner `supports_fixed_star_conjunction=True` ;
- valider la longitude ;
- valider les codes uniques ;
- ne pas sélectionner les étoiles fixes sauf décision explicite.

### `FixedStarConjunctionCalculator`

```python
@dataclass(frozen=True, slots=True)
class FixedStarConjunctionCalculator:
    rules: FixedStarConjunctionRulesRuntimeData

    def calculate(
        self,
        targets: tuple[ChartObjectRuntimeData, ...],
        fixed_stars: tuple[ChartObjectRuntimeData, ...],
    ) -> tuple[FixedStarConjunctionRuntimePayload, ...]:
        ...
```

Le calculateur retourne des payloads. Il ne mute pas les objets.

### `FixedStarConjunctionEnricher`

```python
@dataclass(frozen=True, slots=True)
class FixedStarConjunctionEnricher:
    def enrich(
        self,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
        conjunctions: tuple[FixedStarConjunctionRuntimePayload, ...],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        ...
```

Responsabilités :

- enrichir uniquement les cibles éligibles ;
- conserver les autres payloads ;
- retourner de nouvelles instances ;
- échouer si une conjonction cible un code inconnu.

---

## Flux cible

```text
Natal calculation
→ base chart_objects
→ fixed stars represented as chart_objects
→ select fixed stars
→ select conjunction targets
→ calculate conjunctions
→ enrich target chart_objects
→ NatalResult
```

Le point important : le calculateur consomme uniquement `chart_objects`, pas un catalogue parallèle ou une liste de planètes.

---

## Fichiers probablement concernés

À ajuster selon l’arborescence réelle :

```text
backend/app/domain/astrology/runtime/contracts.py
backend/app/domain/astrology/runtime/chart_object_builder.py
backend/app/domain/astrology/runtime/payload_validator.py
backend/app/domain/astrology/fixed_stars/contracts.py
backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py
backend/app/domain/astrology/fixed_stars/fixed_star_selectors.py
backend/app/domain/astrology/fixed_stars/fixed_star_enricher.py
backend/app/domain/astrology/natal/natal_chart_calculator.py
backend/app/domain/astrology/natal/contracts.py
backend/tests/domain/astrology/fixed_stars/
backend/tests/domain/astrology/runtime/
backend/tests/integration/astrology/
backend/tests/architecture/
```

Recherche initiale :

```powershell
rg "fixed_star|FixedStar|Regulus|Algol|Spica|Antares|Aldebaran" backend/app backend/tests
```

---

## Tests attendus

1. Sélection des étoiles fixes : Regulus et Spica avec `payloads.fixed_star` sont sélectionnées, Mars est ignoré.
2. Erreur étoile fixe sans longitude.
3. Sélection des cibles par `supports_fixed_star_conjunction`.
4. Erreur cible sans longitude.
5. Conjonction exacte : Mars 150.0°, Regulus 150.0°, orb 0.0°.
6. Conjonction dans l’orbe : Mars 150.4°, Regulus 150.0°, orb 0.4° si `max_orb=1.0`.
7. Hors orbe : Mars 152.0°, Regulus 150.0°, aucune conjonction si `max_orb=1.0`.
8. Enrichissement immuable : nouvelle instance, anciens payloads conservés.
9. Intégration `NatalResult` : les objets éligibles portent les conjonctions détectées.
10. Guardrail architecture : pas de logique métier `object_type` dans le domaine fixed stars.

---

## Critères d’acceptation

La story est acceptée si :

1. Les étoiles fixes sont représentées comme `ChartObjectRuntimeData`.
2. `FixedStarRuntimePayload` est typé et sans interprétation narrative.
3. `FixedStarConjunctionRuntimePayload` existe.
4. Les cibles sont sélectionnées par `supports_fixed_star_conjunction`.
5. Les étoiles fixes sont sélectionnées via `payloads.fixed_star`.
6. Les conjonctions sont calculées par distance angulaire normalisée.
7. Les orbes viennent d’un contrat de règles ou d’une constante centralisée.
8. Les objets invalides déclenchent des erreurs explicites.
9. Les résultats sont enrichis dans `chart_objects` sans mutation.
10. Les anciennes sorties restent disponibles si elles existaient.
11. Aucune logique métier ne dépend de `object_type`.
12. Aucune interprétation symbolique n’est ajoutée au runtime.
13. Les tests unitaires, intégration et architecture passent.

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
pytest backend/tests/domain/astrology/fixed_stars -q
pytest backend/tests/domain/astrology/runtime -q
pytest backend/tests/integration/astrology -q
pytest backend/tests/architecture -q
```

Recherches anti-régression :

```powershell
rg "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.FIXED_STAR" backend/app/domain/astrology/fixed_stars
rg "\b1\.0\b|\b1\.5\b|\b2\.0\b" backend/app/domain/astrology/fixed_stars
```

La seconde recherche vise les orbes codées en dur. Les résultats sont acceptables uniquement dans des constantes nommées ou des tests.

---

## Évidence finale attendue

```markdown
## CS-222 Final Evidence

### Runtime
- Fixed stars are represented as ChartObjectRuntimeData.
- FixedStarRuntimePayload and FixedStarConjunctionRuntimePayload are available.
- Eligible targets receive fixed_star_conjunctions payloads.

### Calculation
- Conjunctions are computed from chart_objects.
- Targets are selected through supports_fixed_star_conjunction.
- Orbs are driven by rules, not magic values.

### Compatibility
- Existing outputs are preserved.
- No interpretation text is introduced.

### Validation
- ruff format .
- ruff check .
- pytest -q

### Guardrails
- No object_type-driven eligibility.
- No duplicate fixed star calculators.
- No hardcoded orb thresholds outside rules/constants/tests.
```

---

## Formulation courte pour Codex

```markdown
Implémente CS-222 — Fixed Star Conjunction Runtime from Chart Objects.

Objectif:
Faire entrer les étoiles fixes dans le runtime chart_objects et calculer les conjonctions aux étoiles fixes depuis ChartObjectRuntimeData, sans logique object_type ni interprétation narrative.

À faire:
- Créer/stabiliser FixedStarRuntimePayload.
- Créer FixedStarConjunctionRuntimePayload.
- Ajouter fixed_star_conjunctions dans ChartObjectPayloads si absent.
- Sélectionner les étoiles fixes via payloads.fixed_star.
- Sélectionner les cibles via capabilities.supports_fixed_star_conjunction.
- Calculer les conjonctions par distance angulaire normalisée et règles d’orbe.
- Enrichir immuablement les objets cibles.
- Préserver les sorties historiques.
- Ajouter tests unitaires, intégration et architecture.

Interdictions:
- Pas de calcul par object_type.
- Pas d’orbe magique.
- Pas d’interprétation symbolique dans le runtime.
- Pas d’aspects autres que la conjonction.
- Pas de refonte du catalogue.

Validation:
- ruff format .
- ruff check .
- pytest -q
- rg anti-régression sur object_type et seuils codés en dur.
```
