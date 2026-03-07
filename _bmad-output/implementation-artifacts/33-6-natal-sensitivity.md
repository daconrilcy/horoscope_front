# Story 33.6 : Calculateur de sensibilité natale `NS(c)`

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `NatalSensitivityCalculator` qui calcule une seule fois par run le coefficient `NS(c)` pour chaque catégorie active,
so that le calculateur de contribution (story 34-2) peut moduler l'intensité des événements selon le thème natal de l'utilisateur.

## Acceptance Criteria

### AC1 — `NS(c)` calculé pour toutes les catégories actives

`NatalSensitivityCalculator.compute(natal, ctx)` retourne `dict[str, float]` avec une entrée pour chaque catégorie `is_enabled=True`.

### AC2 — Formule V1 avec 4 composantes

```
NS(c) = clip(1.0 + w_occ × Occ(c) + w_rul × Rul(c) + w_ang × Ang(c) + w_dom × Dom(c), 0.75, 1.25)
```
Poids `w_occ`, `w_rul`, `w_ang`, `w_dom` depuis `ctx.ruleset_context.parameters`.

### AC3 — `Occ` : occupation natale des maisons liées

Somme des poids nataux des planètes natales dans les maisons associées à `c` (via `HouseCategoryWeightData`). Poids natal de chaque planète = `PlanetProfileData.weight_day_climate`.

### AC4 — `Rul` : rulership

Si le maître du signe de la cuspide d'une maison associée à `c` est en maison angulaire (1, 4, 7, 10) → contribution au rulership. Rulerships depuis `ctx.prediction_context.sign_rulerships`.

### AC5 — `Ang` : angularité

Planètes natales en maisons angulaires (1, 4, 7, 10) qui ont un lien avec la catégorie `c` → contribuent à `Ang`.

### AC6 — `Dom` optionnel

`w_dom = ctx.ruleset_context.parameters.get("ns_weight_dom", 0.0)`. Si 0.0, `Dom = 0` sans exception.

### AC7 — Borne `[0.75, 1.25]` stricte

Chaque `NS(c)` clampé après calcul. Aucune valeur hors de cette plage.

## Tasks / Subtasks

### T1 — `NatalSensitivityCalculator` (AC1–AC7)

- [ ] Créer `backend/app/prediction/natal_sensitivity.py`
  - [ ] Dataclass `NatalChart(planet_positions: dict[str, float], planet_houses: dict[str, int], house_sign_rulers: dict[int, str])`
  - [ ] Constantes `NS_MIN = 0.75`, `NS_MAX = 1.25`
  - [ ] Classe `NatalSensitivityCalculator`
  - [ ] `compute(natal: NatalChart, ctx: LoadedPredictionContext) -> dict[str, float]`
    - [ ] Lire `w_occ`, `w_rul`, `w_ang`, `w_dom` depuis `ctx.ruleset_context.parameters` (avec defaults)
    - [ ] Pour chaque catégorie active : calculer `Occ`, `Rul`, `Ang`, `Dom`, puis clamp
  - [ ] `_compute_occ(natal, cat_code, pc) -> float`
  - [ ] `_compute_rul(natal, cat_code, pc) -> float`
  - [ ] `_compute_ang(natal, cat_code, pc) -> float`
  - [ ] `_compute_dom(natal, cat_code, pc) -> float` (retourner 0.0 si w_dom == 0)

### T2 — Tests unitaires (AC1–AC7)

- [ ] Créer `backend/app/tests/unit/test_natal_sensitivity.py`
  - [ ] `test_all_active_categories_present` — toutes les catégories `is_enabled=True` dans le résultat
  - [ ] `test_bounds_always_respected` — contexte synthétique extrême → NS ∈ [0.75, 1.25]
  - [ ] `test_no_occupation_neutral` — aucune planète dans maisons liées → NS ≈ 1.0
  - [ ] `test_strong_occupation_above_1` — plusieurs planètes lourdes → NS > 1.0
  - [ ] `test_angular_ruler_raises_ns` — maître de maison angulaire → NS augmenté
  - [ ] `test_dom_zero_no_exception` — `w_dom=0` dans params → aucune exception
  - [ ] `test_ns_capped_at_1_25` — contexte extrême → NS exactement 1.25 (jamais > 1.25)
  - [ ] `test_ns_floored_at_0_75` — contexte inverse → NS exactement 0.75 (jamais < 0.75)

## Dev Notes

### Pattern de calcul Occ

```python
def _compute_occ(self, natal: NatalChart, cat_code: str, pc) -> float:
    # Trouver les maisons associées à cette catégorie
    associated_houses = {
        w.house_number for w in pc.house_category_weights
        if w.category_code == cat_code and w.weight > 0
    }
    total = 0.0
    for planet_code, house_num in natal.planet_houses.items():
        if house_num in associated_houses:
            profile = pc.planet_profiles.get(planet_code)
            if profile:
                total += profile.weight_day_climate
    return total
```

### Pattern de calcul Ang

```python
ANGULAR_HOUSES = {1, 4, 7, 10}

def _compute_ang(self, natal: NatalChart, cat_code: str, pc) -> float:
    # Planètes natales angulaires qui ont un poids > 0 sur la catégorie
    planet_cat_weights = {
        w.planet_code: w.weight for w in pc.planet_category_weights
        if w.category_code == cat_code
    }
    total = 0.0
    for planet_code, house_num in natal.planet_houses.items():
        if house_num in ANGULAR_HOUSES:
            weight = planet_cat_weights.get(planet_code, 0.0)
            total += weight
    return total
```

### Paramètres par défaut V1

```python
w_occ = float(params.get("ns_weight_occ", 0.15))
w_rul = float(params.get("ns_weight_rul", 0.10))
w_ang = float(params.get("ns_weight_ang", 0.10))
w_dom = float(params.get("ns_weight_dom", 0.0))   # désactivé V1
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/natal_sensitivity.py` | Créer |
| `backend/app/tests/unit/test_natal_sensitivity.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/context_loader.py`
- `backend/app/infra/db/`

### Références

- [Source: docs/model_de_calcul_journalier.md — Architecture de scoring, NS(c)]
- [Source: backend/app/infra/db/repositories/prediction_schemas.py — HouseCategoryWeightData, PlanetCategoryWeightData]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
