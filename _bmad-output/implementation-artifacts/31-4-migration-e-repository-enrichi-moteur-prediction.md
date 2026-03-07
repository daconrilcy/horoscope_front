# Story 31.4 : Migration E — Repository enrichi avec méthodes de lecture pour le moteur de prédiction

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want que le repository expose des méthodes ciblées permettant au moteur de charger les données sémantiques (catégories, profils planètes/maisons, matrices de pondération, ruleset, paramètres, maîtrises) en une seule passe sans parsing ad hoc,
so that le moteur de calcul peut lire ses règles en DB de manière efficace et typée, sans dupliquer la logique de requête.

## Contexte métier

Le `ReferenceRepository` actuel expose `get_reference_data()` qui retourne un dict générique adapté au thème natal (planètes, signes, maisons, aspects, characteristics). Cette méthode est insuffisante pour le moteur de prédiction quotidienne qui a besoin :
- de matrices de pondération planète/maison → catégorie
- des profils interprétatifs des planètes et maisons
- du ruleset et de ses paramètres
- des maîtrises de signes
- des profils d'aspects

Au lieu d'étendre `get_reference_data()` (qui deviendrait ingérable), il faut créer un nouveau `PredictionReferenceRepository` dédié, plus un `PredictionRulesetRepository` pour le ruleset.

Cette story est la dernière du sprint DB 1 (Epic 31). Elle ne modifie pas le schéma DB.

## Acceptance Criteria

### AC1 — Classe `PredictionReferenceRepository`

Une nouvelle classe `PredictionReferenceRepository` est créée dans `backend/app/infra/db/repositories/prediction_reference_repository.py`.

Elle expose les méthodes suivantes (toutes `def`, pas `async`) :

#### `get_categories(reference_version_id: int) -> list[CategoryData]`

Retourne les 12 catégories actives triées par `sort_order`.

`CategoryData` est un dataclass/TypedDict :
```python
@dataclass
class CategoryData:
    id: int
    code: str
    name: str
    display_name: str
    sort_order: int
    is_enabled: bool
```

#### `get_planet_profiles(reference_version_id: int) -> dict[str, PlanetProfileData]`

Retourne un dict `planet_code → PlanetProfileData` pour toutes les planètes de la version, joint avec `planet_profiles`.

`PlanetProfileData` :
```python
@dataclass
class PlanetProfileData:
    planet_id: int
    code: str
    name: str
    class_code: str
    speed_rank: int
    speed_class: str
    weight_intraday: float
    weight_day_climate: float
    typical_polarity: str | None
    orb_active_deg: float | None
    orb_peak_deg: float | None
    keywords: list[str]   # parsé depuis keywords_json
```

#### `get_house_profiles(reference_version_id: int) -> dict[int, HouseProfileData]`

Retourne un dict `house_number → HouseProfileData`.

`HouseProfileData` :
```python
@dataclass
class HouseProfileData:
    house_id: int
    number: int
    name: str
    house_kind: str
    visibility_weight: float
    base_priority: int
    keywords: list[str]
```

#### `get_planet_category_weights(reference_version_id: int) -> list[PlanetCategoryWeightData]`

Retourne toutes les lignes de `planet_category_weights` pour les planètes de cette version, avec join sur `prediction_categories` pour avoir le code catégorie.

`PlanetCategoryWeightData` :
```python
@dataclass
class PlanetCategoryWeightData:
    planet_id: int
    planet_code: str
    category_id: int
    category_code: str
    weight: float
    influence_role: str
```

#### `get_house_category_weights(reference_version_id: int) -> list[HouseCategoryWeightData]`

Analogue pour les maisons.

#### `get_sign_rulerships(reference_version_id: int) -> dict[str, str]`

Retourne un dict `sign_code → planet_code` pour `rulership_type = 'domicile'` et `is_primary = True`.

#### `get_aspect_profiles(reference_version_id: int) -> dict[str, AspectProfileData]`

Retourne un dict `aspect_code → AspectProfileData`.

`AspectProfileData` :
```python
@dataclass
class AspectProfileData:
    aspect_id: int
    code: str
    intensity_weight: float
    default_valence: str
    orb_multiplier: float
    phase_sensitive: bool
```

#### `get_astro_points(reference_version_id: int) -> dict[str, AstroPointData]`

Retourne un dict `point_code → AstroPointData` pour les points actifs.

`AstroPointData` :
```python
@dataclass
class AstroPointData:
    point_id: int
    code: str
    name: str
    point_type: str
```

#### `get_point_category_weights(reference_version_id: int) -> list[PointCategoryWeightData]`

Analogue à `get_planet_category_weights` mais pour les points astrologiques.

### AC2 — Classe `PredictionRulesetRepository`

Une nouvelle classe `PredictionRulesetRepository` est créée dans `backend/app/infra/db/repositories/prediction_ruleset_repository.py`.

Elle expose :

#### `get_ruleset(version: str) -> RulesetData | None`

`RulesetData` :
```python
@dataclass
class RulesetData:
    id: int
    version: str
    reference_version_id: int
    zodiac_type: str
    coordinate_mode: str
    house_system: str
    time_step_minutes: int
    is_locked: bool
```

#### `get_parameters(ruleset_id: int) -> dict[str, Any]`

Retourne un dict `param_key → valeur_typée`. La conversion selon `data_type` est effectuée ici :
- `float` → `float(param_value)`
- `int` → `int(param_value)`
- `bool` → `param_value.lower() in ('true', '1', 'yes')`
- `json` → `json.loads(param_value)`
- `string` → `param_value`

#### `get_event_types(ruleset_id: int) -> dict[str, EventTypeData]`

`EventTypeData` :
```python
@dataclass
class EventTypeData:
    id: int
    code: str
    name: str
    event_group: str | None
    priority: int
    base_weight: float
```

#### `get_calibrations(ruleset_id: int, category_id: int, reference_date: date) -> CalibrationData | None`

Retourne la calibration active à `reference_date` (`valid_from <= reference_date <= valid_to OR valid_to IS NULL`), la plus récente si plusieurs.

`CalibrationData` :
```python
@dataclass
class CalibrationData:
    p05: float | None
    p25: float | None
    p50: float | None
    p75: float | None
    p95: float | None
    sample_size: int | None
```

### AC3 — Méthode de chargement complet `load_prediction_context()`

Dans `PredictionReferenceRepository`, une méthode de commodité :

```python
def load_prediction_context(self, reference_version_id: int) -> PredictionContext:
```

Elle agrège les résultats de toutes les méthodes de la classe en un seul objet `PredictionContext` :
```python
@dataclass
class PredictionContext:
    categories: list[CategoryData]
    planet_profiles: dict[str, PlanetProfileData]
    house_profiles: dict[int, HouseProfileData]
    planet_category_weights: list[PlanetCategoryWeightData]
    house_category_weights: list[HouseCategoryWeightData]
    sign_rulerships: dict[str, str]
    aspect_profiles: dict[str, AspectProfileData]
    astro_points: dict[str, AstroPointData]
    point_category_weights: list[PointCategoryWeightData]
```

Cette méthode est le point d'entrée principal pour le moteur de calcul.

### AC4 — Méthode `get_active_ruleset_context()` dans `PredictionRulesetRepository`

```python
def get_active_ruleset_context(self, version: str, reference_date: date | None = None) -> RulesetContext | None:
```

`RulesetContext` :
```python
@dataclass
class RulesetContext:
    ruleset: RulesetData
    parameters: dict[str, Any]
    event_types: dict[str, EventTypeData]
```

Si le ruleset n'existe pas, retourne `None`.

### AC5 — Dataclasses dans un module dédié

Tous les dataclasses (`CategoryData`, `PlanetProfileData`, etc.) sont définis dans `backend/app/infra/db/repositories/prediction_schemas.py` (module partagé entre les deux repositories).

### AC6 — Aucune logique métier dans les repositories

Les repositories ne font que des requêtes et des transformations de données (parsing JSON, conversion de types). Aucune règle de scoring, aucun calcul astrologique.

### AC7 — `get_reference_data()` non modifié

La méthode existante `ReferenceRepository.get_reference_data()` n'est pas touchée. Elle continue de servir le thème natal.

### AC8 — Tests unitaires

Des tests couvrent :
- `get_categories()` retourne 12 catégories dans l'ordre `sort_order`
- `get_planet_profiles()` retourne un dict avec les 10 planètes et que `keywords` est une `list[str]` (pas une string JSON brute)
- `get_parameters()` convertit correctement les types (`float`, `int`, `bool`, `json`)
- `get_sign_rulerships()` retourne 12 entrées `sign_code → planet_code`
- `load_prediction_context()` retourne un objet complet non vide

### AC9 — Durcissement post-review des repositories

Le chargement des matrices versionnées filtre aussi `prediction_categories.reference_version_id == reference_version_id` dans :
- `get_planet_category_weights()`
- `get_house_category_weights()`
- `get_point_category_weights()`

La conversion des paramètres de ruleset est stricte :
- une valeur invalide pour `float`, `int`, `bool` ou `json` lève une exception explicite
- aucun fallback silencieux à `0`, `0.0`, `{}` ou `False` n'est autorisé
- tout `data_type` inconnu est refusé par la contrainte de schéma, et reste rejeté côté repository si jamais il contourne la DB

## Tasks / Subtasks

### T1 — Module des schemas de données (AC5)

- [x] Créer `backend/app/infra/db/repositories/prediction_schemas.py`
  - [x] `CategoryData`
  - [x] `PlanetProfileData` (avec `keywords: list[str]`)
  - [x] `HouseProfileData`
  - [x] `PlanetCategoryWeightData`
  - [x] `HouseCategoryWeightData`
  - [x] `AstroPointData`
  - [x] `PointCategoryWeightData`
  - [x] `AspectProfileData`
  - [x] `RulesetData`
  - [x] `EventTypeData`
  - [x] `CalibrationData`
  - [x] `PredictionContext`
  - [x] `RulesetContext`

### T2 — `PredictionReferenceRepository` (AC1, AC3)

- [x] Créer `backend/app/infra/db/repositories/prediction_reference_repository.py`
  - [x] `get_categories()` — SELECT avec filter `is_enabled = True`, ORDER BY `sort_order`
  - [x] `get_planet_profiles()` — JOIN `planets` + `planet_profiles`, retourner dict
  - [x] `get_house_profiles()` — JOIN `houses` + `house_profiles`, retourner dict
  - [x] `get_planet_category_weights()` — JOIN `planet_category_weights` + `planets` + `prediction_categories`
  - [x] `get_house_category_weights()` — JOIN `house_category_weights` + `houses` + `prediction_categories`
  - [x] `get_sign_rulerships()` — filter `rulership_type = 'domicile'`, `is_primary = True`
  - [x] `get_aspect_profiles()` — JOIN `aspects` + `aspect_profiles`
  - [x] `get_astro_points()` — filter `is_enabled = True`
  - [x] `get_point_category_weights()` — JOIN `point_category_weights` + `astro_points` + `prediction_categories`
  - [x] `load_prediction_context()` — agrège toutes les méthodes ci-dessus

### T3 — `PredictionRulesetRepository` (AC2, AC4)

- [x] Créer `backend/app/infra/db/repositories/prediction_ruleset_repository.py`
  - [x] `get_ruleset()` — SELECT par version
  - [x] `get_parameters()` — SELECT + conversion de types selon `data_type`
  - [x] `get_event_types()` — SELECT, retourner dict `code → EventTypeData`
  - [x] `get_calibrations()` — SELECT avec filtre date range, ORDER BY `valid_from DESC`, LIMIT 1
  - [x] `get_active_ruleset_context()` — agrège `get_ruleset()` + `get_parameters()` + `get_event_types()`

### T4 — Tests (AC8)

- [x] Créer `backend/app/tests/unit/test_prediction_reference_repository.py`
  - [x] Test `get_categories()` retourne 12 items (sur DB de test avec seed 31.3)
  - [x] Test `get_planet_profiles()` : `keywords` est `list[str]`, pas `str`
  - [x] Test `get_sign_rulerships()` : 12 entrées, `"aries" → "mars"` correct
  - [x] Test `load_prediction_context()` : objet non vide, tous les champs peuplés
- [x] Créer `backend/app/tests/unit/test_prediction_ruleset_repository.py`
  - [x] Test `get_parameters()` : `float` converti en float, `int` en int, `bool` en bool
  - [x] Test `get_ruleset("1.0.0")` retourne le ruleset
  - [x] Test `get_active_ruleset_context("1.0.0")` retourne un `RulesetContext` complet
  - [x] Test `get_parameters()` lève une erreur explicite sur valeur invalide
  - [x] Test la contrainte de schéma refuse un `data_type` inconnu
  - [x] Test les requêtes de matrices ignorent les catégories d'une autre `reference_version`

## Dev Notes

### Pattern de requête avec JOIN (SQLAlchemy)

```python
from sqlalchemy import select
from app.infra.db.models.prediction_reference import (
    PlanetProfileModel, PlanetCategoryWeightModel, PredictionCategoryModel
)
from app.infra.db.models.reference import PlanetModel

def get_planet_category_weights(self, reference_version_id: int) -> list[PlanetCategoryWeightData]:
    rows = self.db.execute(
        select(
            PlanetModel.code.label("planet_code"),
            PlanetCategoryWeightModel.planet_id,
            PredictionCategoryModel.code.label("category_code"),
            PlanetCategoryWeightModel.category_id,
            PlanetCategoryWeightModel.weight,
            PlanetCategoryWeightModel.influence_role,
        )
        .join(PlanetModel, PlanetCategoryWeightModel.planet_id == PlanetModel.id)
        .join(PredictionCategoryModel, PlanetCategoryWeightModel.category_id == PredictionCategoryModel.id)
        .where(PlanetModel.reference_version_id == reference_version_id)
        .order_by(PlanetModel.code, PredictionCategoryModel.code)
    ).all()
    return [
        PlanetCategoryWeightData(
            planet_id=row.planet_id,
            planet_code=row.planet_code,
            category_id=row.category_id,
            category_code=row.category_code,
            weight=row.weight,
            influence_role=row.influence_role,
        )
        for row in rows
    ]
```

### Parsing des keywords_json

```python
import json

def _parse_keywords(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(k) for k in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    return []
```

### Conversion de types dans `get_parameters()`

```python
def _convert_param(value: str, data_type: str) -> Any:
    match data_type:
        case "float": return float(value)
        case "int": return int(value)
        case "bool": return value.lower() in ("true", "1", "yes")
        case "json": return json.loads(value)
        case _: return value
```

### Injection dans la DI FastAPI

Les nouveaux repositories seront injectés via les dépendances FastAPI dans les futurs services du moteur. Pour l'instant, les classes sont autonomes et ne nécessitent pas de registration dans `app/dependencies.py` (ça sera fait lors de la story moteur de calcul).

### Fichiers à créer

| Fichier | Action |
|---------|--------|
| `backend/app/infra/db/repositories/prediction_schemas.py` | Créer |
| `backend/app/infra/db/repositories/prediction_reference_repository.py` | Créer |
| `backend/app/infra/db/repositories/prediction_ruleset_repository.py` | Créer |
| `backend/app/tests/unit/test_prediction_reference_repository.py` | Créer |
| `backend/app/tests/unit/test_prediction_ruleset_repository.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/repositories/reference_repository.py` — pas de modification
- `backend/app/infra/db/models/` — pas de modification
- Tout fichier frontend ou API router

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Completion Notes List

- Création du module `prediction_schemas.py` contenant les dataclasses pour le moteur de prédiction.
- Implémentation du `PredictionReferenceRepository` avec méthodes optimisées pour le chargement sémantique (AC1, AC3).
- Implémentation du `PredictionRulesetRepository` gérant les rulesets, paramètres typés et calibrations (AC2, AC4).
- Les repositories utilisent SQLAlchemy 2.0 (select, scalars, join).
- Durcissement post-review : filtrage explicite des catégories joinées par `reference_version_id` dans les méthodes de matrices.
- Durcissement post-review : conversion stricte des paramètres `ruleset_parameters` avec échec explicite en cas de valeur invalide, et rejet des `data_type` inconnus par la contrainte de schéma.
- Validation via tests unitaires dédiés et passage de l'intégralité de la suite de tests unitaires (927 tests).

### File List

- backend/app/infra/db/repositories/prediction_schemas.py
- backend/app/infra/db/repositories/prediction_reference_repository.py
- backend/app/infra/db/repositories/prediction_ruleset_repository.py
- backend/app/tests/unit/test_prediction_reference_repository.py
- backend/app/tests/unit/test_prediction_ruleset_repository.py
