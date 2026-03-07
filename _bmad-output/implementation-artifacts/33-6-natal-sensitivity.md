# Story 33.6 : Calculateur de sensibilité natale `NS(c)`

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `NatalSensitivityCalculator` qui calcule une seule fois par run le coefficient `NS(c)` pour chaque catégorie active,
so that le calculateur de contribution (story 34-2) peut moduler l'intensité des événements selon le thème natal de l'utilisateur.

## Acceptance Criteria

### AC1 — `NS(c)` calculé pour toutes les catégories actives

- [x] `NatalSensitivityCalculator.compute(natal, ctx)` retourne `dict[str, float]` avec une entrée pour chaque catégorie `is_enabled=True`.

### AC2 — Formule V1 avec 4 composantes

- [x] `NS(c) = clip(1.0 + w_occ × Occ(c) + w_rul × Rul(c) + w_ang × Ang(c) + w_dom × Dom(c), 0.75, 1.25)`
- [x] Poids `w_occ`, `w_rul`, `w_ang`, `w_dom` depuis `ctx.ruleset_context.parameters`.

### AC3 — `Occ` : occupation natale des maisons liées

- [x] Somme des poids nataux des planètes natales dans les maisons associées à `c` (via `HouseCategoryWeightData`). Poids natal de chaque planète = `PlanetProfileData.weight_day_climate`.

### AC4 — `Rul` : rulership

- [x] Si le maître du signe de la cuspide d'une maison associée à `c` est en maison angulaire (1, 4, 7, 10) → contribution au rulership. Rulerships depuis `ctx.prediction_context.sign_rulerships`.

### AC5 — `Ang` : angularité

- [x] Planètes natales en maisons angulaires (1, 4, 7, 10) qui ont un lien avec la catégorie `c` → contribuent à `Ang`.

### AC6 — `Dom` optionnel

- [x] `w_dom = ctx.ruleset_context.parameters.get("ns_weight_dom", 0.0)`. Si 0.0, `Dom = 0` sans exception.

### AC7 — Borne `[0.75, 1.25]` stricte

- [x] Chaque `NS(c)` clampé après calcul. Aucune valeur hors de cette plage.

## Tasks / Subtasks

### T1 — `NatalSensitivityCalculator` (AC1–AC7)

- [x] Créer `backend/app/prediction/natal_sensitivity.py`
  - [x] Dataclass `NatalChart(planet_positions: dict[str, float], planet_houses: dict[str, int], house_sign_rulers: dict[int, str])` -> Ajouté dans `schemas.py`
  - [x] Constantes `NS_MIN = 0.75`, `NS_MAX = 1.25`
  - [x] Classe `NatalSensitivityCalculator`
  - [x] `compute(natal: NatalChart, ctx: LoadedPredictionContext) -> dict[str, float]`
    - [x] Lire `w_occ`, `w_rul`, `w_ang`, `w_dom` depuis `ctx.ruleset_context.parameters` (avec defaults)
    - [x] Pour chaque catégorie active : calculer `Occ`, `Rul`, `Ang`, `Dom`, puis clamp
  - [x] `_compute_occ(natal, cat_code, pc) -> float`
  - [x] `_compute_rul(natal, cat_code, pc) -> float`
  - [x] `_compute_ang(natal, cat_code, pc) -> float`
  - [x] `_compute_dom(natal, cat_code, pc) -> float` (retourner 0.0 si w_dom == 0)

### T2 — Tests unitaires (AC1–AC8)

- [x] Créer `backend/app/tests/unit/test_natal_sensitivity.py`
  - [x] `test_all_active_categories_present` — toutes les catégories `is_enabled=True` dans le résultat
  - [x] `test_bounds_always_respected` — contexte synthétique extrême → NS ∈ [0.75, 1.25]
  - [x] `test_no_occupation_neutral` — aucune planète dans maisons liées → NS ≈ 1.0
  - [x] `test_strong_occupation_above_1` — plusieurs planètes lourdes → NS > 1.0
  - [x] `test_angular_ruler_raises_ns` — maître de maison angulaire → NS augmenté
  - [x] `test_dom_zero_no_exception` — `w_dom=0` dans params → aucune exception
  - [x] `test_ns_capped_at_1_25` — contexte extrême → NS exactement 1.25 (jamais > 1.25)
  - [x] `test_ns_floored_at_0_75` — contexte inverse → NS exactement 0.75 (jamais < 0.75)

## Dev Notes

### Structure des données

Le `NatalChart` a été ajouté à `backend/app/prediction/schemas.py` pour être utilisé comme structure pivot.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Implémentation du service `NatalSensitivityCalculator` avec les 4 piliers de sensibilité : Occupation, Rulership, Angularité et Domination (V1: stub).
- Respect strict des bornes [0.75, 1.25].
- Tests unitaires complets validant les interactions complexes entre maisons, planètes et catégories.

### File List

- `backend/app/prediction/natal_sensitivity.py` (Nouveau)
- `backend/app/tests/unit/test_natal_sensitivity.py` (Nouveau)
- `backend/app/prediction/schemas.py` (Modifié)
