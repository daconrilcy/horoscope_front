# CS-223 — Chart Object Interpretation Input Adapter

## Résumé

CS-223 crée un adaptateur déterministe entre le runtime de calcul `chart_objects` et la couche interprétative.

Après CS-217 à CS-222, le résultat natal expose un graphe de thème unifié : objets, aspects, motion/visibility, dignités, dominance et conjonctions aux étoiles fixes. CS-223 doit fournir à la couche d’interprétation une entrée propre, stable et typée, construite depuis `NatalResult.chart_objects`.

La cible est :

```text
NatalResult.chart_objects
→ ChartObjectInterpretationInputAdapter
→ ChartInterpretationInputRuntimeData
→ interpretation services / prompt generation
```

Cette story ne doit pas écrire d’interprétation. Elle prépare uniquement le matériau structuré que la couche interprétative pourra consommer.

---

## Contexte

Le contrat `ChartObjectRuntimeData` porte désormais les informations calculatoires du thème :

```python
code
object_type
display_name
longitude
latitude
zodiac_position
source
capabilities
classifications
payloads
```

Les payloads peuvent contenir :

```python
motion
visibility
dignity
dominance
fixed_star
fixed_star_conjunctions
house_position
rulership
angle
house_cusp
```

Mais la couche d’interprétation ne doit pas consommer directement tous les contrats bas niveau. Elle a besoin d’un input adapté : stable, compact, ordonné, sans duplication et sans recalcul.

CS-223 crée cette frontière explicite entre calcul et interprétation.

---

## Problème à résoudre

Sans adaptateur dédié, les interprétations risquent de consommer directement plusieurs surfaces :

```text
planet_positions
houses
angles
aspects
dignity_results
dominance_result
advanced_conditions
fixed_star_conjunctions
chart_objects
```

Ce mélange crée des risques :

- duplication de mapping ;
- prompts incohérents ;
- dépendances au format historique ;
- branches conditionnelles par type d’objet ;
- confusion entre calcul et interprétation ;
- difficulté à nettoyer les anciennes surfaces runtime.

CS-223 doit imposer une entrée canonique pour l’interprétation.

---

## Objectifs

### Objectif fonctionnel

Fournir un objet d’entrée unique pour l’interprétation du thème natal.

Exemple cible :

```python
interpretation_input = chart_object_interpretation_input_adapter.build(
    natal_result=natal_result,
)
```

Le résultat doit contenir des sections structurées :

```text
objects
aspects
dominance
dignities
house_positions
rulerships
fixed_star_contacts
chart_metadata
```

Ces sections doivent être construites depuis `chart_objects` et les résultats chart-level nécessaires.

### Objectif architectural

Installer la règle suivante :

```text
La couche interprétative ne consomme plus directement les collections spécialisées du calcul natal.
Elle consomme un contrat d’entrée interprétatif construit depuis chart_objects.
```

Les anciennes collections peuvent rester exposées pour compatibilité API/front/debug, mais elles ne doivent plus être la source cible des nouveaux flux interprétatifs.

---

## Périmètre inclus

CS-223 couvre :

1. La création de `ChartInterpretationInputRuntimeData`.
2. La création de `ChartObjectInterpretationRuntimeData`.
3. La création de sous-contrats légers pour aspects, dignités, dominance, maisons, rulerships, motion, visibility et étoiles fixes.
4. La création d’un adaptateur `ChartObjectInterpretationInputAdapter` ou `ChartInterpretationInputBuilder`.
5. La sélection des objets interprétables via `capabilities.supports_interpretation`.
6. La projection des payloads utiles vers un format stable.
7. Le maintien d’une séparation stricte entre données calculées et textes narratifs.
8. L’adaptation du service d’interprétation ou du générateur de prompt pour consommer le nouvel input.
9. La conservation temporaire des anciennes entrées si nécessaire via une façade legacy isolée.
10. Les tests unitaires, d’intégration et d’architecture.

---

## Hors périmètre

CS-223 ne doit pas :

- écrire les textes d’interprétation ;
- modifier profondément les prompts LLM ;
- changer la doctrine astrologique ;
- changer les scores ;
- supprimer les anciennes collections du `NatalResult` ;
- supprimer l’ancien pipeline d’interprétation si une migration progressive est nécessaire ;
- ajouter de nouveaux calculs astrologiques ;
- appeler un LLM depuis le domaine ;
- mélanger contrats API HTTP et contrats domaine.

---

## Contrats attendus

### `ChartInterpretationInputRuntimeData`

Créer un contrat de haut niveau :

```python
@dataclass(frozen=True, slots=True)
class ChartInterpretationInputRuntimeData:
    chart_id: str | None
    chart_type: str
    locale: str | None
    objects: tuple[ChartObjectInterpretationRuntimeData, ...]
    aspects: tuple[AspectInterpretationRuntimeData, ...]
    dominance: tuple[DominanceInterpretationRuntimeData, ...]
    fixed_star_contacts: tuple[FixedStarContactInterpretationRuntimeData, ...]
    metadata: ChartInterpretationMetadataRuntimeData
```

Adapter les champs aux conventions existantes. Ce contrat est une entrée structurée, pas un résultat narratif.

### `ChartObjectInterpretationRuntimeData`

Créer un contrat objet :

```python
@dataclass(frozen=True, slots=True)
class ChartObjectInterpretationRuntimeData:
    code: str
    display_name: str
    object_type: str
    classifications: tuple[str, ...]
    zodiac_position: ZodiacPositionRuntimeData | None
    house_number: int | None
    house_modality: str | None
    dignity: DignityInterpretationRuntimeData | None
    motion: MotionInterpretationRuntimeData | None
    visibility: VisibilityInterpretationRuntimeData | None
    dominance: DominanceInterpretationRuntimeData | None
    rulership: RulershipInterpretationRuntimeData | None
    fixed_star_contacts: tuple[FixedStarContactInterpretationRuntimeData, ...]
    source_codes: tuple[str, ...]
```

Ce contrat peut reprendre les données des payloads, mais sous forme compacte et stable.

### Sous-contrats interprétatifs

Créer des projections légères, par exemple :

```python
@dataclass(frozen=True, slots=True)
class DignityInterpretationRuntimeData:
    essential_score: float
    accidental_score: float
    total_score: float
    condition_codes: tuple[str, ...]
    breakdown_codes: tuple[str, ...]
```

```python
@dataclass(frozen=True, slots=True)
class MotionInterpretationRuntimeData:
    motion_state: str
    speed_condition: str | None
    is_retrograde: bool
    is_stationary: bool
```

```python
@dataclass(frozen=True, slots=True)
class VisibilityInterpretationRuntimeData:
    solar_phase: str | None
    solar_separation_deg: float | None
    oriental_occidental: str | None
```

```python
@dataclass(frozen=True, slots=True)
class FixedStarContactInterpretationRuntimeData:
    target_code: str
    fixed_star_code: str
    fixed_star_display_name: str
    orb_deg: float
    rule_code: str
```

Ces contrats ne doivent contenir aucun texte narratif.

---

## Règles de sélection

### Objets interprétables

Les objets doivent être sélectionnés par :

```python
obj.capabilities.supports_interpretation
```

Interdit :

```python
if obj.object_type == "planet":
```

ou :

```python
if obj.code in ("sun", "moon", "mars"):
```

Le builder runtime décide en amont quels objets sont interprétables.

### Objets non interprétables

Les objets avec `supports_interpretation=False` ne doivent pas apparaître dans `objects`. Ils peuvent apparaître indirectement comme contexte si un résultat les référence explicitement, mais ce cas doit être contrôlé et testé.

### Ordre déterministe

L’ordre des objets doit être stable. Recommandation : conserver l’ordre canonique de `chart_objects`. Ne jamais utiliser un `set` pour construire l’input final.

---

## Règles de projection

### Ne pas recalculer

L’adaptateur ne doit pas recalculer :

- dignités ;
- dominance ;
- aspects ;
- conjonctions aux étoiles fixes ;
- positions en maison ;
- rulerships ;
- motion ;
- visibility.

Il lit les payloads et résultats existants.

### Ne pas interpréter

Interdit dans l’adaptateur :

```text
strong personality
emotional intensity
career ambition
malefic influence
positive meaning
```

Autorisé : codes, scores, conditions, rangs, orbes, classifications, sources.

### Tolérance contrôlée

Si un objet interprétable est incohérent, l’adaptateur doit échouer explicitement plutôt que produire une entrée silencieusement incomplète.

Exemple :

```text
Chart object 'mars' is interpretation-capable but has no zodiac position.
```

---

## Composants techniques recommandés

### `ChartObjectInterpretationSelector`

```python
@dataclass(frozen=True, slots=True)
class ChartObjectInterpretationSelector:
    def select(
        self,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        ...
```

Responsabilités : filtrer `supports_interpretation=True`, valider les codes uniques, préserver l’ordre déterministe.

### `ChartObjectInterpretationProjector`

```python
@dataclass(frozen=True, slots=True)
class ChartObjectInterpretationProjector:
    def project(
        self,
        chart_object: ChartObjectRuntimeData,
    ) -> ChartObjectInterpretationRuntimeData:
        ...
```

Responsabilités : copier les champs stables, projeter les payloads utiles, ne pas recalculer, ne pas interpréter.

### `ChartInterpretationInputBuilder`

```python
@dataclass(frozen=True, slots=True)
class ChartInterpretationInputBuilder:
    def build(
        self,
        natal_result: NatalResult,
    ) -> ChartInterpretationInputRuntimeData:
        ...
```

Responsabilités : sélectionner les objets, projeter les objets, projeter les aspects, projeter la dominance chart-level, projeter les conjonctions aux étoiles fixes et produire un contrat unique.

### Adapter le service d’interprétation

Le service d’interprétation ou de génération de prompt doit consommer `ChartInterpretationInputRuntimeData`.

Si la migration complète est trop large, créer une façade temporaire :

```python
LegacyInterpretationInputAdapter
```

Elle doit être explicitement isolée et documentée comme transitoire.

---

## Flux cible

```text
NatalResult
→ chart_objects
→ ChartObjectInterpretationSelector
→ ChartObjectInterpretationProjector
→ ChartInterpretationInputBuilder
→ interpretation service / prompt assembly
```

Flux interdit hors façade legacy :

```text
interpretation service
→ planet_positions + houses + aspects + dignity_results + advanced_conditions
```

---

## Fichiers probablement concernés

À ajuster selon l’arborescence réelle :

```text
backend/app/domain/astrology/interpretation/contracts.py
backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py
backend/app/domain/astrology/interpretation/chart_object_interpretation_projector.py
backend/app/domain/astrology/interpretation/chart_object_interpretation_selector.py
backend/app/domain/astrology/runtime/contracts.py
backend/app/domain/astrology/natal/contracts.py
backend/app/services/astrology/
backend/app/services/llm/
backend/tests/domain/astrology/interpretation/
backend/tests/integration/astrology/
backend/tests/architecture/
```

Recherche initiale :

```powershell
rg "interpretation|prompt|llm|planet_positions|dignity_results|dominance_result|advanced_conditions" backend/app backend/tests
```

---

## Tests attendus

1. Sélection des objets interprétables : Sun et Mars sélectionnés, cuspide ignorée.
2. Projection d’un objet complet avec zodiac position, house position, dignity, motion, visibility, dominance et fixed star contacts.
3. Objet interprétable invalide : erreur explicite.
4. Pas de recalcul : l’adaptateur ne doit pas appeler les calculateurs d’aspects, dignités ou dominance.
5. Construction d’un input complet depuis un `NatalResult`.
6. Non-régression du pipeline d’interprétation existant ou façade legacy opérationnelle.
7. Guardrail architecture : pas de consommation directe des collections historiques dans les nouveaux flux interprétatifs.
8. Guardrail anti-narratif : pas de texte interprétatif dans les contrats runtime.

---

## Critères d’acceptation

La story est acceptée si :

1. `ChartInterpretationInputRuntimeData` existe.
2. `ChartObjectInterpretationRuntimeData` existe.
3. L’input interprétatif est construit depuis `chart_objects`.
4. Les objets sont sélectionnés via `supports_interpretation`.
5. Les payloads utiles sont projetés sans recalcul.
6. Aucun texte narratif n’est produit par l’adaptateur.
7. Les anciennes collections ne sont plus consommées directement par les nouveaux flux interprétatifs.
8. Une façade legacy est isolée si nécessaire.
9. Le pipeline d’interprétation existant reste compatible.
10. Les tests unitaires et d’intégration couvrent la projection.
11. Les guardrails empêchent les nouvelles dépendances directes aux collections historiques.
12. Les contrats restent dans la couche domaine/service appropriée, sans dépendance FastAPI/HTTP.

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
pytest backend/tests/domain/astrology/interpretation -q
pytest backend/tests/integration/astrology -q
pytest backend/tests/architecture -q
```

Recherches anti-régression :

```powershell
rg "planet_positions|advanced_conditions|dignity_results|dominance_result" backend/app/domain/astrology/interpretation backend/app/services
rg "meaning|narrative|psychological|prompt|llm" backend/app/domain/astrology/interpretation backend/app/domain/astrology/runtime
```

Les résultats doivent être justifiés. `prompt` et `llm` ne doivent pas apparaître dans les contrats runtime de domaine.

---

## Évidence finale attendue

```markdown
## CS-223 Final Evidence

### Interpretation input
- Added ChartInterpretationInputRuntimeData.
- Added ChartObjectInterpretationRuntimeData.
- Interpretation input is built from chart_objects.

### Projection
- Objects are selected through supports_interpretation.
- Runtime payloads are projected without recalculation.
- No narrative text is generated.

### Compatibility
- Existing interpretation pipeline remains compatible.
- Legacy adapters, if any, are isolated.

### Validation
- ruff format .
- ruff check .
- pytest -q

### Guardrails
- No direct consumption of planet_positions/dignity_results/etc. by new interpretation flows.
- No LLM/prompt dependency in runtime contracts.
```

---

## Risques à surveiller

Le premier risque est de laisser la couche interprétative consommer à la fois `chart_objects` et les anciennes collections. Cela annulerait l’intérêt de la migration.

Le deuxième risque est de commencer à écrire du sens dans l’adaptateur. CS-223 doit rester déterministe et calculatoire.

Le troisième risque est de coupler le domaine astrologique au pipeline LLM. Le contrat d’entrée peut servir à un LLM, mais il ne doit pas dépendre d’OpenAI, de prompts ou d’un format HTTP.

Le quatrième risque est d’oublier les résultats chart-level, comme la dominance globale. L’interprétation a besoin des contributions par objet, mais aussi du classement global.

---

## Formulation courte pour Codex

```markdown
Implémente CS-223 — Chart Object Interpretation Input Adapter.

Objectif:
Créer un adaptateur déterministe qui construit un ChartInterpretationInputRuntimeData depuis NatalResult.chart_objects, pour que la couche interprétative ne consomme plus directement planet_positions, dignity_results, dominance_result, advanced_conditions et autres collections spécialisées.

À faire:
- Créer ChartInterpretationInputRuntimeData.
- Créer ChartObjectInterpretationRuntimeData et sous-contrats légers.
- Créer selector supports_interpretation.
- Créer projectors depuis ChartObjectRuntimeData vers les contrats interprétatifs.
- Créer ChartInterpretationInputBuilder.
- Adapter le service d’interprétation ou ajouter une façade legacy isolée.
- Ajouter tests unitaires, intégration et architecture.

Interdictions:
- Pas de texte narratif dans l’adaptateur.
- Pas de recalcul des dignités/aspects/dominance.
- Pas de dépendance LLM/prompt dans les contrats runtime.
- Pas de nouvelle consommation directe des collections historiques dans les flux interprétatifs.

Validation:
- ruff format .
- ruff check .
- pytest -q
- rg anti-régression sur les anciennes collections et les dépendances prompt/LLM.
```
