# Story 31.1 : Migration A — Tables de profils planétaires/maisons, matrices de pondération et structures sémantiques du moteur de prédiction

Status: review

## Story

As a développeur du moteur de prédiction quotidienne,
I want que la base de données dispose des tables relationnelles portant la sémantique astrologique centrale (profils planètes/maisons, catégories de prédiction, matrices de pondération planète→catégorie et maison→catégorie, points astrologiques, maîtrises de signes, profils d'aspects),
so that le moteur de scoring quotidien peut lire ses règles directement en DB sans jamais coder en dur la sémantique dans Python.

## Contexte métier

Le référentiel actuel (`planets`, `houses`, `signs`, `aspects`, `astro_characteristics`) ne stocke que l'identité métier minimale des entités astrologiques. Il ne contient aucune pondération sémantique interprétative, aucune catégorie de prédiction, aucune règle de routage planète→catégorie ou maison→catégorie.

Pour construire un moteur de prédiction quotidienne (scores par catégorie : énergie, amour, travail, santé…), il faut externaliser en DB :
- les catégories de prédiction (pivot du scoring)
- les profils interprétatifs des planètes et maisons
- les matrices de pondération planète/maison → catégorie
- les points astrologiques (ASC, MC, DSC, IC) absents du référentiel actuel
- les maîtrises de signes (pour calculer le maître d'une maison)
- les profils d'aspects (valence, intensité)

Cette story couvre **Migration A** : création de toutes ces tables filles spécialisées, sans toucher aux tables canoniques existantes (`planets`, `houses`, `signs`, `aspects`).

## Acceptance Criteria

### AC1 — Table `prediction_categories`

La table `prediction_categories` est créée avec :
- `id` PK autoincrement
- `reference_version_id` FK → `reference_versions.id`, NOT NULL, indexé
- `code` VARCHAR(64) NOT NULL
- `name` VARCHAR(128) NOT NULL
- `display_name` VARCHAR(128) NOT NULL
- `description` TEXT nullable
- `sort_order` INTEGER NOT NULL DEFAULT 0
- `is_public` BOOLEAN NOT NULL DEFAULT TRUE
- `is_enabled` BOOLEAN NOT NULL DEFAULT TRUE
- Contrainte UNIQUE `(reference_version_id, code)`

### AC2 — Table `planet_profiles`

La table `planet_profiles` est créée avec :
- `id` PK autoincrement
- `planet_id` FK UNIQUE → `planets.id` (relation 1-1)
- `class_code` VARCHAR(32) NOT NULL — valeurs : `luminary`, `personal`, `social`, `transpersonal`
- `speed_rank` INTEGER NOT NULL DEFAULT 0
- `speed_class` VARCHAR(16) NOT NULL — valeurs : `fast`, `medium`, `slow`
- `weight_intraday` FLOAT NOT NULL DEFAULT 1.0
- `weight_day_climate` FLOAT NOT NULL DEFAULT 1.0
- `typical_polarity` VARCHAR(16) nullable — valeurs : `positive`, `negative`, `neutral`
- `orb_active_deg` FLOAT nullable
- `orb_peak_deg` FLOAT nullable
- `keywords_json` TEXT nullable — tableau JSON de mots-clés
- `micro_note` TEXT nullable

### AC3 — Table `house_profiles`

La table `house_profiles` est créée avec :
- `id` PK autoincrement
- `house_id` FK UNIQUE → `houses.id` (relation 1-1)
- `house_kind` VARCHAR(16) NOT NULL — valeurs : `angular`, `succedent`, `cadent`
- `visibility_weight` FLOAT NOT NULL DEFAULT 1.0
- `base_priority` INTEGER NOT NULL DEFAULT 0
- `keywords_json` TEXT nullable
- `micro_note` TEXT nullable

### AC4 — Table `planet_category_weights`

La table `planet_category_weights` est créée avec :
- `id` PK autoincrement
- `planet_id` FK → `planets.id`, NOT NULL
- `category_id` FK → `prediction_categories.id`, NOT NULL
- `weight` FLOAT NOT NULL — entre 0 et 1
- `influence_role` VARCHAR(16) NOT NULL DEFAULT `'secondary'` — valeurs : `primary`, `secondary`, `color`
- Contrainte UNIQUE `(planet_id, category_id)`

### AC5 — Table `house_category_weights`

La table `house_category_weights` est créée avec :
- `id` PK autoincrement
- `house_id` FK → `houses.id`, NOT NULL
- `category_id` FK → `prediction_categories.id`, NOT NULL
- `weight` FLOAT NOT NULL — entre 0 et 1
- `routing_role` VARCHAR(16) NOT NULL DEFAULT `'secondary'` — valeurs : `primary`, `secondary`
- Contrainte UNIQUE `(house_id, category_id)`

### AC6 — Table `astro_points`

La table `astro_points` est créée avec :
- `id` PK autoincrement
- `reference_version_id` FK → `reference_versions.id`, NOT NULL, indexé
- `code` VARCHAR(32) NOT NULL — valeurs initiales : `asc`, `dsc`, `mc`, `ic`
- `name` VARCHAR(64) NOT NULL
- `point_type` VARCHAR(32) NOT NULL DEFAULT `'angle'`
- `is_enabled` BOOLEAN NOT NULL DEFAULT TRUE
- Contrainte UNIQUE `(reference_version_id, code)`

### AC7 — Table `point_category_weights`

La table `point_category_weights` est créée avec :
- `id` PK autoincrement
- `point_id` FK → `astro_points.id`, NOT NULL
- `category_id` FK → `prediction_categories.id`, NOT NULL
- `weight` FLOAT NOT NULL
- Contrainte UNIQUE `(point_id, category_id)`

### AC8 — Table `sign_rulerships`

La table `sign_rulerships` est créée avec :
- `id` PK autoincrement
- `reference_version_id` FK → `reference_versions.id`, NOT NULL
- `sign_id` FK → `signs.id`, NOT NULL
- `planet_id` FK → `planets.id`, NOT NULL
- `rulership_type` VARCHAR(32) NOT NULL DEFAULT `'domicile'` — valeurs : `domicile`, `exaltation`, `detriment`, `fall`
- `weight` FLOAT NOT NULL DEFAULT 1.0
- `is_primary` BOOLEAN NOT NULL DEFAULT TRUE
- Contrainte UNIQUE `(reference_version_id, sign_id, planet_id, rulership_type)`

### AC9 — Table `aspect_profiles`

La table `aspect_profiles` est créée avec :
- `id` PK autoincrement
- `aspect_id` FK UNIQUE → `aspects.id` (relation 1-1)
- `intensity_weight` FLOAT NOT NULL DEFAULT 1.0
- `default_valence` VARCHAR(16) NOT NULL DEFAULT `'contextual'` — valeurs : `favorable`, `challenging`, `polarizing`, `contextual`
- `orb_multiplier` FLOAT NOT NULL DEFAULT 1.0
- `phase_sensitive` BOOLEAN NOT NULL DEFAULT FALSE
- `micro_note` TEXT nullable

### AC10 — Migration Alembic idempotente

Une migration Alembic unique (numéro de séquence `0032`) est créée et idempotente. Elle crée les 9 tables dans l'ordre suivant (respectant les dépendances FK) :
1. `prediction_categories` (dépend de `reference_versions`)
2. `planet_profiles` (dépend de `planets`)
3. `house_profiles` (dépend de `houses`)
4. `planet_category_weights` (dépend de `planets`, `prediction_categories`)
5. `house_category_weights` (dépend de `houses`, `prediction_categories`)
6. `astro_points` (dépend de `reference_versions`)
7. `point_category_weights` (dépend de `astro_points`, `prediction_categories`)
8. `sign_rulerships` (dépend de `reference_versions`, `signs`, `planets`)
9. `aspect_profiles` (dépend de `aspects`)

Le `downgrade()` supprime les tables dans l'ordre inverse.

### AC11 — Modèles SQLAlchemy

Les 9 modèles SQLAlchemy correspondants sont créés dans `backend/app/infra/db/models/prediction_reference.py` avec :
- Mapping `Mapped` complet pour chaque colonne
- Relations `relationship()` vers les entités parentes
- `__table_args__` avec les contraintes UNIQUE

### AC12 — Protection version verrouillée

Seuls les modèles ayant un `reference_version_id` **direct** héritent du mécanisme `before_update` via `_ensure_reference_version_is_mutable` (pattern existant dans `reference.py`) :
- `PredictionCategoryModel` ✓ (a `reference_version_id`)
- `AstroPointModel` ✓ (a `reference_version_id`)
- `SignRulershipModel` ✓ (a `reference_version_id`)

Les modèles **sans** `reference_version_id` direct ne peuvent pas utiliser ce mécanisme directement et ne sont **pas** protégés par ce listener en v1 :
- `PlanetProfileModel`, `HouseProfileModel` — liés à une planète/maison parente, pas à une version
- `PlanetCategoryWeightModel`, `HouseCategoryWeightModel` — idem
- `PointCategoryWeightModel`, `AspectProfileModel` — idem

Cette limitation est documentée et acceptée pour la v1 : la protection est appliquée aux tables pivots versionnées. Les tables filles d'entités (profils, matrices) sont implicitement protégées par le fait que la version parente est verrouillée avant toute utilisation en production.

### AC13 — Aucune donnée de seed dans cette story

Cette story ne seed aucune donnée. Le seed sera effectué en story 31.3 après la création de la version 2.0.0. Les tables doivent être créées vides.

### AC14 — Tests de migration

Un test d'intégration vérifie que les 9 tables sont créées correctement et que les contraintes UNIQUE sont actives (tentative d'insertion de doublon → exception).

## Tasks / Subtasks

### T1 — Migration Alembic (AC10)

- [x] Créer `backend/migrations/versions/{date}_0032_migration_a_prediction_reference_tables.py`
  - [x] Créer `prediction_categories` avec colonnes et contraintes
  - [x] Créer `planet_profiles` avec FK UNIQUE sur `planets.id`
  - [x] Créer `house_profiles` avec FK UNIQUE sur `houses.id`
  - [x] Créer `planet_category_weights` avec UNIQUE `(planet_id, category_id)`
  - [x] Créer `house_category_weights` avec UNIQUE `(house_id, category_id)`
  - [x] Créer `astro_points` avec UNIQUE `(reference_version_id, code)`
  - [x] Créer `point_category_weights` avec UNIQUE `(point_id, category_id)`
  - [x] Créer `sign_rulerships` avec UNIQUE `(reference_version_id, sign_id, planet_id, rulership_type)`
  - [x] Créer `aspect_profiles` avec FK UNIQUE sur `aspects.id`
  - [x] Implémenter `downgrade()` dans l'ordre inverse des FK

### T2 — Modèles SQLAlchemy (AC11, AC12)

- [x] Créer `backend/app/infra/db/models/prediction_reference.py`
  - [x] `PredictionCategoryModel` avec `reference_version_id`, `code`, `name`, `display_name`, `sort_order`, `is_public`, `is_enabled`
  - [x] `PlanetProfileModel` avec tous les champs (AC2)
  - [x] `HouseProfileModel` avec tous les champs (AC3)
  - [x] `PlanetCategoryWeightModel` avec `planet_id`, `category_id`, `weight`, `influence_role`
  - [x] `HouseCategoryWeightModel` avec `house_id`, `category_id`, `weight`, `routing_role`
  - [x] `AstroPointModel` avec `reference_version_id`, `code`, `name`, `point_type`, `is_enabled`
  - [x] `PointCategoryWeightModel` avec `point_id`, `category_id`, `weight`
  - [x] `SignRulershipModel` avec `reference_version_id`, `sign_id`, `planet_id`, `rulership_type`, `weight`, `is_primary`
  - [x] `AspectProfileModel` avec tous les champs (AC9)
  - [x] Ajouter les listeners `before_update` pour les modèles liés à `reference_version_id`
- [x] Importer les nouveaux modèles dans `backend/app/infra/db/models/__init__.py` (ou le point d'entrée des modèles) pour qu'Alembic les découvre

### T3 — Tests (AC14)

- [x] Créer `backend/app/tests/integration/test_migration_a_prediction_tables.py`
  - [x] Test : les 9 tables existent après migration
  - [x] Test : insertion d'un doublon dans `prediction_categories` (même `reference_version_id` + `code`) → IntegrityError
  - [x] Test : insertion d'un doublon dans `planet_category_weights` (même `planet_id` + `category_id`) → IntegrityError
  - [x] Test : `PlanetProfileModel` avec FK invalide → IntegrityError

## Dev Notes

### Ordre de création des tables (dépendances FK)

```
reference_versions (existant)
  └─► prediction_categories
  └─► astro_points
  └─► sign_rulerships (aussi → signs, planets)

planets (existant)
  └─► planet_profiles
  └─► planet_category_weights (aussi → prediction_categories)
  └─► sign_rulerships

houses (existant)
  └─► house_profiles
  └─► house_category_weights (aussi → prediction_categories)

aspects (existant)
  └─► aspect_profiles

astro_points
  └─► point_category_weights (aussi → prediction_categories)
```

### Modèle de référence pour la contrainte UNIQUE FK

Pour `planet_profiles` (relation 1-1 avec `planets`) :
```python
class PlanetProfileModel(Base):
    __tablename__ = "planet_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planets.id"), unique=True, nullable=False, index=True
    )
    class_code: Mapped[str] = mapped_column(String(32), nullable=False)
    speed_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    speed_class: Mapped[str] = mapped_column(String(16), nullable=False)
    weight_intraday: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    weight_day_climate: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    typical_polarity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    orb_active_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    orb_peak_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    keywords_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    micro_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    planet: Mapped["PlanetModel"] = relationship()
```

### Mécanisme de protection version verrouillée

Réutiliser le pattern de `reference.py` pour les 3 modèles directement versionnés uniquement :
```python
from app.infra.db.models.reference import _ensure_reference_version_is_mutable

@event.listens_for(PredictionCategoryModel, "before_update")
@event.listens_for(AstroPointModel, "before_update")
@event.listens_for(SignRulershipModel, "before_update")
def _prevent_update_on_locked_prediction_version(mapper, connection, target):
    del mapper, connection
    _ensure_reference_version_is_mutable(target)
```

Les modèles `PlanetProfileModel`, `HouseProfileModel`, `PlanetCategoryWeightModel`, `HouseCategoryWeightModel`, `PointCategoryWeightModel`, `AspectProfileModel` n'ont pas de `reference_version_id` direct → pas de listener en v1 (voir AC12 pour la justification).

### Numéro de migration

Le dernier numéro utilisé est `0031` (migration `20260307_0031_add_current_location_to_user_birth_profiles.py`).
La migration A utilisera `0032`.

Pattern de nommage : `{YYYYMMDD}_0032_migration_a_prediction_reference_tables.py`

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/migrations/versions/{date}_0032_migration_a_prediction_reference_tables.py` | Créer |
| `backend/app/infra/db/models/prediction_reference.py` | Créer |
| `backend/app/infra/db/models/__init__.py` | Modifier — importer les nouveaux modèles |
| `backend/app/tests/integration/test_migration_a_prediction_tables.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/models/reference.py` — les tables canoniques ne sont pas modifiées
- `backend/app/infra/db/repositories/reference_repository.py` — pas de changement dans cette story (story 31.4)
- Tout fichier frontend

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Completion Notes List

- Création de la migration Alembic 0032 créant les 9 tables de référentiel de prédiction.
- Implémentation des 9 modèles SQLAlchemy avec mapping complet et relations.
- Ajout des listeners SQLAlchemy pour la protection contre la mutation sur les versions verrouillées (AC12).
- Création d'un test d'intégration complet vérifiant la création des tables, les contraintes d'unicité et la protection des versions.
- Correction de la migration legacy 0005 pour assurer la compatibilité avec SQLite via `batch_alter_table` afin de permettre l'exécution des tests d'intégration.

### File List

- `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/tests/integration/test_migration_a_prediction_tables.py`
- `backend/migrations/versions/20260218_0005_add_user_id_to_chart_results.py`
