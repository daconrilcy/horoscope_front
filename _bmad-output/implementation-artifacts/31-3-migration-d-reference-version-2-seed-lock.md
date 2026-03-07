# Story 31.3 : Migration D — Reference version 2.0.0, seed complet des tables de prédiction et verrouillage

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want créer la reference_version `2.0.0` en clonant `1.0.0`, puis seeder toutes les nouvelles tables du moteur (catégories, profils planètes/maisons, matrices de pondération, points astrologiques, maîtrises de signes, profils d'aspects, ruleset, event types, paramètres) sur cette version,
so that le moteur de prédiction peut lire une sémantique astrologique complète depuis la base de données dès son premier appel, sans aucun hard-coding Python.

## Contexte métier

Les stories 31.1 et 31.2 ont créé la structure des tables. Cette story crée la **donnée initiale** : la version de référentiel `2.0.0` dédiée au moteur de prédiction, seedée avec la sémantique astrologique complète.

Principe directeur :
- Ne pas modifier la version `1.0.0` (utilisée par le thème natal en production)
- Créer une nouvelle version `2.0.0` via clonage de `1.0.0` (planètes, signes, maisons, aspects, characteristics)
- Enrichir `2.0.0` avec toutes les nouvelles tables
- Verrouiller `2.0.0` une fois le seed validé

Le seed est implémenté sous forme d'un script Python autonome `backend/scripts/seed_31_prediction_reference_v2.py`, NOT dans une migration Alembic (les seeds de données ne doivent pas être dans des migrations).

## Acceptance Criteria

### AC1 — Création de la reference_version 2.0.0

Le script crée la version `2.0.0` si elle n'existe pas, avec `description = "Moteur de prédiction quotidienne v1 — référentiel sémantique complet"` et `is_locked = False` initialement.

### AC2 — Clone de 1.0.0

La version `1.0.0` est clonée vers `2.0.0` via `ReferenceRepository.clone_version_data()`. Après clonage, `2.0.0` contient : 10 planètes, 12 signes, 12 maisons, 5 aspects, les characteristics de base.

### AC3 — Seed des 12 catégories de prédiction

Les 12 catégories suivantes sont créées dans `prediction_categories` pour `reference_version_id = 2.0.0` :

| code | name | display_name | sort_order |
|------|------|--------------|------------|
| `energy` | Energy | Énergie | 1 |
| `mood` | Mood | Humeur | 2 |
| `health` | Health | Santé | 3 |
| `work` | Work | Travail | 4 |
| `career` | Career | Carrière | 5 |
| `money` | Money | Argent | 6 |
| `love` | Love | Amour | 7 |
| `sex_intimacy` | Sex & Intimacy | Intimité | 8 |
| `family_home` | Family & Home | Famille & Foyer | 9 |
| `social_network` | Social Network | Réseau social | 10 |
| `communication` | Communication | Communication | 11 |
| `pleasure_creativity` | Pleasure & Creativity | Plaisir & Créativité | 12 |

Toutes les catégories ont `is_public = True`, `is_enabled = True`.

### AC4 — Seed des profils planètes (`planet_profiles`)

Les 10 profils planétaires sont créés avec la classification suivante :

| planet_code | class_code | speed_rank | speed_class | weight_intraday | weight_day_climate | typical_polarity |
|-------------|------------|------------|-------------|-----------------|-------------------|-----------------|
| sun | luminary | 1 | slow | 0.6 | 1.0 | positive |
| moon | luminary | 0 | fast | 1.0 | 0.8 | neutral |
| mercury | personal | 2 | fast | 0.9 | 0.7 | neutral |
| venus | personal | 3 | medium | 0.7 | 0.8 | positive |
| mars | personal | 4 | medium | 0.8 | 0.9 | negative |
| jupiter | social | 5 | slow | 0.4 | 1.0 | positive |
| saturn | social | 6 | slow | 0.3 | 1.0 | negative |
| uranus | transpersonal | 7 | slow | 0.1 | 0.5 | neutral |
| neptune | transpersonal | 8 | slow | 0.1 | 0.4 | neutral |
| pluto | transpersonal | 9 | slow | 0.1 | 0.3 | neutral |

Champs `keywords_json` : fournir un array JSON de 3-5 mots-clés par planète.
- sun: `["identité", "vitalité", "volonté", "ego", "créativité"]`
- moon: `["émotions", "instinct", "humeur", "inconscient", "réceptivité"]`
- mercury: `["pensée", "communication", "analyse", "adaptation", "arbitrage"]`
- venus: `["amour", "beauté", "harmonie", "plaisir", "relation"]`
- mars: `["action", "énergie", "désir", "conflits", "sexualité"]`
- jupiter: `["expansion", "chance", "philosophie", "sagesse", "optimisme"]`
- saturn: `["structure", "discipline", "limites", "responsabilité", "karma"]`
- uranus: `["rupture", "originalité", "innovation", "liberté", "révolution"]`
- neptune: `["dissolution", "spiritualité", "illusion", "idéal", "compassion"]`
- pluto: `["transformation", "pouvoir", "mort-renaissance", "profondeur", "obsession"]`

### AC5 — Seed des profils maisons (`house_profiles`)

Les 12 profils de maisons sont créés :

| number | house_kind | visibility_weight | base_priority |
|--------|------------|-------------------|---------------|
| 1 | angular | 1.0 | 10 |
| 2 | succedent | 0.7 | 6 |
| 3 | cadent | 0.5 | 4 |
| 4 | angular | 0.9 | 9 |
| 5 | succedent | 0.7 | 6 |
| 6 | cadent | 0.6 | 5 |
| 7 | angular | 0.9 | 9 |
| 8 | succedent | 0.7 | 7 |
| 9 | cadent | 0.5 | 4 |
| 10 | angular | 1.0 | 10 |
| 11 | succedent | 0.6 | 5 |
| 12 | cadent | 0.4 | 3 |

### AC6 — Seed des matrices planète → catégorie (`planet_category_weights`)

Matrices de pondération principales. Seules les relations avec `weight >= 0.2` sont créées. Les poids reflètent la force de contribution de chaque planète à chaque catégorie.

Matrice planète/catégorie (extrait des relations primaires) :

| planet | energy | mood | health | work | career | money | love | sex_intimacy | family_home | social_network | communication | pleasure_creativity |
|--------|--------|------|--------|------|--------|-------|------|-------------|-------------|---------------|---------------|---------------------|
| sun | 0.8/primary | 0.6 | 0.5 | 0.6 | 0.8/primary | 0.5 | 0.5 | - | - | - | - | 0.6/primary |
| moon | 0.4 | 0.9/primary | 0.6/primary | - | - | - | 0.7/primary | 0.4 | 0.8/primary | 0.4 | - | 0.4 |
| mercury | 0.3 | 0.4 | - | 0.8/primary | 0.5 | 0.3 | 0.3 | - | - | 0.7 | 0.9/primary | 0.4 |
| venus | 0.3 | 0.6 | 0.4 | - | - | 0.6 | 0.9/primary | 0.7/primary | 0.5 | 0.6 | 0.4 | 0.8/primary |
| mars | 0.9/primary | 0.4 | 0.6 | 0.7 | 0.5 | 0.3 | 0.4 | 0.8/primary | - | - | - | 0.4 |
| jupiter | 0.5 | 0.6 | 0.4 | 0.5 | 0.8/primary | 0.7/primary | 0.4 | - | 0.4 | 0.6 | 0.4 | 0.6 |
| saturn | 0.3 | - | 0.5 | 0.7/primary | 0.7/primary | 0.5 | - | - | 0.4 | - | - | - |
| uranus | 0.4 | 0.3 | - | 0.4 | 0.4 | - | - | 0.3 | - | 0.5 | 0.4 | 0.5 |
| neptune | - | 0.5 | 0.3 | - | - | - | 0.5 | 0.4 | 0.3 | 0.4 | - | 0.5 |
| pluto | 0.5 | 0.3 | 0.4 | 0.4 | 0.5 | 0.5 | 0.4 | 0.6 | - | - | - | 0.3 |

*Note : les cellules sans valeur (—) ne génèrent pas de ligne en DB (poids implicite = 0).*
*Format : `weight/influence_role` ; si pas de rôle précisé → `secondary`.*

### AC7 — Seed des matrices maison → catégorie (`house_category_weights`)

| house | category | weight | routing_role |
|-------|----------|--------|-------------|
| 1 | energy | 0.8 | primary |
| 1 | mood | 0.6 | secondary |
| 2 | money | 0.9 | primary |
| 2 | work | 0.5 | secondary |
| 3 | communication | 0.9 | primary |
| 3 | social_network | 0.5 | secondary |
| 4 | family_home | 0.9 | primary |
| 4 | mood | 0.5 | secondary |
| 5 | pleasure_creativity | 0.9 | primary |
| 5 | love | 0.6 | secondary |
| 6 | health | 0.9 | primary |
| 6 | work | 0.7 | secondary |
| 7 | love | 0.8 | primary |
| 7 | social_network | 0.6 | secondary |
| 8 | sex_intimacy | 0.8 | primary |
| 8 | money | 0.6 | secondary |
| 9 | pleasure_creativity | 0.5 | secondary |
| 9 | career | 0.4 | secondary |
| 10 | career | 0.9 | primary |
| 10 | work | 0.6 | secondary |
| 11 | social_network | 0.9 | primary |
| 11 | pleasure_creativity | 0.5 | secondary |
| 12 | mood | 0.5 | secondary |
| 12 | health | 0.4 | secondary |

### AC8 — Seed des points astrologiques (`astro_points`)

Les 4 points angulaires sont créés pour `reference_version_id = 2.0.0` :

| code | name | point_type |
|------|------|------------|
| `asc` | Ascendant | angle |
| `dsc` | Descendant | angle |
| `mc` | Midheaven (MC) | angle |
| `ic` | Imum Coeli (IC) | angle |


Avec les pondérations `point_category_weights` :

| point | category | weight |
|-------|----------|--------|
| asc | energy | 0.8 |
| asc | mood | 0.7 |
| mc | career | 0.9 |
| mc | work | 0.6 |
| dsc | love | 0.7 |
| dsc | social_network | 0.6 |
| ic | family_home | 0.9 |
| ic | mood | 0.5 |

### AC9 — Seed des maîtrises de signes (`sign_rulerships`)

Les 12 domiciles planétaires principaux (rulership_type = `domicile`) :

| sign | planet | is_primary |
|------|--------|------------|
| aries | mars | true |
| taurus | venus | true |
| gemini | mercury | true |
| cancer | moon | true |
| leo | sun | true |
| virgo | mercury | true |
| libra | venus | true |
| scorpio | mars | true |
| sagittarius | jupiter | true |
| capricorn | saturn | true |
| aquarius | saturn | true |
| pisces | jupiter | true |

### AC10 — Seed des profils d'aspects (`aspect_profiles`)

| aspect_code | intensity_weight | default_valence | orb_multiplier | phase_sensitive |
|-------------|-----------------|-----------------|----------------|-----------------|
| conjunction | 1.5 | contextual | 1.0 | false |
| sextile | 0.8 | favorable | 0.9 | false |
| square | 1.2 | challenging | 1.0 | false |
| trine | 1.0 | favorable | 1.0 | false |
| opposition | 1.3 | polarizing | 1.0 | true |

### AC11 — Seed du ruleset `1.0.0`

Un ruleset initial est créé dans `prediction_rulesets` :

```
version: "1.0.0"
reference_version_id: → 2.0.0
zodiac_type: "tropical"
coordinate_mode: "geocentric"
house_system: "placidus"
time_step_minutes: 30
description: "Ruleset initial moteur prédiction quotidienne"
is_locked: false
```

### AC12 — Seed des event types

Les 8 types d'événements définis en AC2 de story 31.2 sont créés dans `ruleset_event_types`.

### AC13 — Seed des paramètres

Les 8 paramètres clés sont créés dans `ruleset_parameters` pour le ruleset `1.0.0`. `time_step_minutes` est **exclu** car c'est une colonne canonique de `prediction_rulesets` — source de vérité unique, pas à dupliquer en paramètre clé/valeur.

### AC14 — Verrouillage de 2.0.0

Après validation du seed (tous les counts attendus sont corrects), le script appelle `is_locked = True` sur la version `2.0.0` et commit. La version `1.0.0` reste inchangée.

### AC15 — Script idempotent avec 3 cas explicites

Le script gère trois états distincts, sans ambiguïté :

1. **`2.0.0` n'existe pas** → seed complet, lock, exit 0.
2. **`2.0.0` existe, est complète (counts corrects) ET verrouillée** → log `"2.0.0 already seeded and locked — skipping"`, exit 0. Aucune donnée n'est touchée.
3. **`2.0.0` existe mais est incomplète (counts incorrects) OU non verrouillée** → log d'erreur détaillé (counts attendus vs réels), exit 1 sans modification. L'opérateur doit investiguer et éventuellement supprimer `2.0.0` manuellement avant de relancer.

Ce comportement évite de masquer un état corrompu issu d'un seed partiellement exécuté ou d'un rollback incomplet.

### AC16 — Tests du script

Un test d'integration exécute le script sur une DB de test propre et vérifie :
- `prediction_categories` : 12 lignes pour `2.0.0`
- `planet_profiles` : 10 lignes
- `house_profiles` : 12 lignes
- `planet_category_weights` : N lignes (≥ 30)
- `house_category_weights` : N lignes (≥ 20)
- `astro_points` : 4 lignes
- `sign_rulerships` : 12 lignes
- `aspect_profiles` : 5 lignes
- `prediction_rulesets` : 1 ligne (`1.0.0`)
- `ruleset_event_types` : 8 lignes
- `ruleset_parameters` : 8 lignes (`time_step_minutes` exclu — colonne canonique du ruleset)
- `ReferenceVersionModel.is_locked == True` pour `2.0.0`

## Tasks / Subtasks

### T1 — Script de seed (AC1–AC14)

- [x] Créer `backend/scripts/seed_31_prediction_reference_v2.py`
  - [x] Vérifier existence de `1.0.0` et `2.0.0`
  - [x] Si `2.0.0` n'existe pas → seed complet
  - [x] Si `2.0.0` existe + complète + verrouillée → log "already seeded and locked" + exit 0
  - [x] Si `2.0.0` existe mais incomplète ou non verrouillée → log erreur détaillé (counts attendus vs réels) + exit 1 sans modification
  - [x] Créer `2.0.0` avec `is_locked = False`
  - [x] Cloner `1.0.0` → `2.0.0` via `ReferenceRepository.clone_version_data()`
  - [x] Seeder `prediction_categories` (12 catégories — AC3)
  - [x] Seeder `planet_profiles` (10 profils — AC4)
  - [x] Seeder `house_profiles` (12 profils — AC5)
  - [x] Seeder `planet_category_weights` (AC6) — résoudre les IDs planètes/catégories depuis la DB
  - [x] Seeder `house_category_weights` (AC7) — résoudre les IDs maisons/catégories depuis la DB
  - [x] Seeder `astro_points` (4 points — AC8)
  - [x] Seeder `point_category_weights` — résoudre les IDs points/catégories
  - [x] Seeder `sign_rulerships` (12 domiciles — AC9)
  - [x] Seeder `aspect_profiles` (5 profils — AC10)
  - [x] Créer le ruleset `1.0.0` dans `prediction_rulesets` (AC11)
  - [x] Seeder `ruleset_event_types` (8 types — AC12)
  - [x] Seeder `ruleset_parameters` (8 params — AC13)
  - [x] Verrouiller `2.0.0` (AC14)

### T2 — Validation count dans le script (AC14)

- [x] Ajouter une phase de validation dans le script avant le lock :
  - [x] `assert db.scalar(select(func.count()).select_from(PredictionCategoryModel).where(...)) == 12`
  - [x] Idem pour chaque table seedée
  - [x] En cas d'assertion failure → rollback + log erreur + exit 1

### T3 — Tests d'intégration (AC15, AC16)

- [x] Créer `backend/app/tests/integration/test_seed_31_prediction_v2.py`
  - [x] Exécuter le script sur DB de test propre (après migrations 0032 et 0033)
  - [x] Vérifier les counts attendus (AC16)
  - [x] Exécuter le script une seconde fois → pas d'erreur (idempotence)
  - [x] Vérifier `is_locked == True` pour `2.0.0`

## Dev Notes

### Pattern de résolution des IDs pour les matrices

Les matrices référencent des IDs DB, pas des codes. Le script doit charger les entités depuis la DB pour résoudre les IDs :

```python
# Charger les planètes de la version 2.0.0
planets = {p.code: p.id for p in db.scalars(
    select(PlanetModel).where(PlanetModel.reference_version_id == v2.id)
).all()}

categories = {c.code: c.id for c in db.scalars(
    select(PredictionCategoryModel).where(
        PredictionCategoryModel.reference_version_id == v2.id
    )
).all()}

# Exemple insertion matrice
db.add(PlanetCategoryWeightModel(
    planet_id=planets["mars"],
    category_id=categories["energy"],
    weight=0.9,
    influence_role="primary"
))
```

### Structure du script

```python
# backend/scripts/seed_31_prediction_reference_v2.py
import sys
from sqlalchemy.orm import Session
from app.infra.db.session import SessionLocal

def main():
    with SessionLocal() as db:
        with db.begin():
            run_seed(db)

EXPECTED_COUNTS = {
    "prediction_categories": 12,
    "planet_profiles": 10,
    "house_profiles": 12,
    "aspect_profiles": 5,
    "astro_points": 4,
    "sign_rulerships": 12,
    "ruleset_event_types": 8,
    "ruleset_parameters": 8,  # time_step_minutes exclu (colonne canonique du ruleset)
}

def run_seed(db: Session):
    # 1. Check idempotence — 3 cas explicites
    v2 = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == "2.0.0"))
    if v2 is not None:
        # Vérifier counts
        actual = _check_counts(db, v2.id)
        all_ok = all(actual.get(k, 0) == v for k, v in EXPECTED_COUNTS.items())
        if all_ok and v2.is_locked:
            print("2.0.0 already seeded and locked — skipping")
            return
        # Cas 3 : état corrompu ou incomplet → fail bruyamment
        import sys
        print("ERROR: 2.0.0 exists but is incomplete or unlocked. Manual investigation required.")
        for k, expected in EXPECTED_COUNTS.items():
            got = actual.get(k, 0)
            status = "OK" if got == expected else f"MISMATCH (expected {expected}, got {got})"
            print(f"  {k}: {status}")
        print(f"  is_locked: {v2.is_locked}")
        sys.exit(1)
    # 2. Seed...

if __name__ == "__main__":
    main()
```

### Ordre de résolution des dépendances dans le script

1. Créer et flush `reference_version 2.0.0` → obtenir `v2.id`
2. Cloner `1.0.0` vers `2.0.0` (planètes, signes, maisons, aspects)
3. Flush pour que les IDs soient disponibles
4. Seeder `prediction_categories` → flush → charger les IDs catégories
5. Seeder `planet_profiles` (dépend des planet IDs)
6. Seeder `house_profiles`
7. Seeder `planet_category_weights` (dépend des IDs planètes + catégories)
8. Seeder `house_category_weights`
9. Seeder `astro_points` → flush → charger les IDs points
10. Seeder `point_category_weights`
11. Seeder `sign_rulerships`
12. Seeder `aspect_profiles`
13. Créer ruleset → flush → charger ruleset ID
14. Seeder `ruleset_event_types`
15. Seeder `ruleset_parameters`
16. Validation counts
17. Lock `v2.is_locked = True`
18. Commit

### Dépendance sur stories 31.1 et 31.2

Ce script ne peut tourner qu'après l'application des migrations `0032` et `0033`. Le script doit être lancé manuellement après `alembic upgrade head`.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/scripts/seed_31_prediction_reference_v2.py` | Créer |
| `backend/app/tests/integration/test_seed_31_prediction_v2.py` | Créer |
| `backend/scripts/__init__.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/migrations/` — aucune migration dans cette story (c'est du seed, pas du schema)
- `backend/app/infra/db/models/reference.py` — pas de changement
- La version `1.0.0` — elle doit rester strictement inchangée

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Completion Notes List

- Created `backend/scripts/seed_31_prediction_reference_v2.py` with full astrological semantic seeding for reference version 2.0.0.
- Implemented idempotence logic with explicit error reporting for corrupted states.
- Handled cloning from 1.0.0 and enrichment with prediction-specific tables (categories, profiles, weights, points, rulerships, aspects, ruleset).
- Fixed issues with models not having `reference_version_id` by joining with parent tables in count checks.
- Created `backend/app/tests/integration/test_seed_31_prediction_v2.py` verifying full flow and idempotence.
- All tests passing.

### File List

- `backend/scripts/seed_31_prediction_reference_v2.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/scripts/__init__.py`
