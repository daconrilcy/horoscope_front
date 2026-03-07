# Story 34.1 : Service de routage domaine `D(e,c)`

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `DomainRouter` qui calcule pour chaque événement astrologique son vecteur de distribution vers les catégories (`D(e,c)`),
so that le calculateur de contribution peut appliquer un poids de domaine cohérent à chaque signal.

## Acceptance Criteria

### AC1 — Vecteur maison normalisé

- Maison natale cible `h_natal ≠` maison transitante `h_transit` → poids `0.70` sur `h_natal`, `0.30` sur `h_transit`
- Si `h_natal == h_transit` → poids `1.00` sur `h_natal`
- Somme du vecteur = 1.0

### AC2 — Projection maison → catégories via `HouseCategoryWeightData`

Pour chaque maison dans le vecteur : `contribution_cat += H_e[house] × house_to_cat_weight`.

### AC3 — Blend planétaire `[0.5, 1.0]`

`D_planet(c) = 0.50 + 0.50 × W_planet_to_cat(c)`. Toujours dans `[0.5, 1.0]` — la couleur planétaire n'annule jamais le routage maison.

### AC4 — `D(e,c)` pour toutes les catégories actives

`D(e,c) = sum_maisons(H_e[h] × house_to_cat[h][c]) × D_planet(c)`. Calculé pour toutes les catégories `is_enabled=True`.

### AC5 — Événements sans cible natale

Pour `AstroEvent.target = None` (heures planétaires, ingresses) : vecteur maison uniforme ou absent, routage via blend planétaire seul. Pas d'exception.

## Tasks / Subtasks

### T1 — `DomainRouter` (AC1–AC5)

- [ ] Créer `backend/app/prediction/domain_router.py`
  - [ ] Classe `DomainRouter`
  - [ ] `route(event: AstroEvent, ctx: LoadedPredictionContext) -> dict[str, float]`
    - [ ] `_build_house_vector(event) -> dict[int, float]`
    - [ ] `_project_houses_to_categories(house_vector, ctx) -> dict[str, float]`
    - [ ] `_compute_planet_blend(planet_code, ctx) -> dict[str, float]`
    - [ ] Combiner : `D(e,c) = house_projection[c] * planet_blend[c]`

### T2 — Tests unitaires (AC1–AC5)

- [ ] Créer `backend/app/tests/unit/test_domain_router.py`
  - [ ] `test_house_vector_sum_1` — vecteur 70/30 → somme = 1.0
  - [ ] `test_single_house_weight_1` — maison cible = transitante → poids 1.0
  - [ ] `test_planet_blend_in_range` — `D_planet(c) ∈ [0.5, 1.0]` pour toutes catégories
  - [ ] `test_all_categories_covered` — résultat contient toutes les catégories actives
  - [ ] `test_no_target_no_exception` — événement sans cible → pas d'exception
  - [ ] `test_planet_blend_never_cancels` — `D_planet(c) ≥ 0.5` toujours

## Dev Notes

### Accès aux matrices

```python
# Matrices de poids depuis le contexte
house_cat_weights: list[HouseCategoryWeightData] = ctx.prediction_context.house_category_weights
planet_cat_weights: list[PlanetCategoryWeightData] = ctx.prediction_context.planet_category_weights

# Construire index rapide
house_to_cat: dict[int, dict[str, float]] = {}
for w in house_cat_weights:
    house_to_cat.setdefault(w.house_number, {})[w.category_code] = w.weight

planet_to_cat: dict[str, dict[str, float]] = {}
for w in planet_cat_weights:
    planet_to_cat.setdefault(w.planet_code, {})[w.category_code] = w.weight
```

### Construction du vecteur maison

```python
def _build_house_vector(self, event: AstroEvent) -> dict[int, float]:
    # AstroEvent doit porter natal_house_target et natal_house_transit
    natal_house = (event.metadata or {}).get("natal_house_target")
    transit_house = (event.metadata or {}).get("natal_house_transited")
    if natal_house is None:
        return {}
    if transit_house is None or transit_house == natal_house:
        return {natal_house: 1.0}
    return {natal_house: 0.70, transit_house: 0.30}
```

Note : vérifier que `AstroEvent` (défini en 33-1) porte bien `natal_house_target` et `natal_house_transited` dans ses `metadata`. Si ce n'est pas le cas, adapter le schema `AstroEvent` dans `backend/app/prediction/schemas.py`.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/domain_router.py` | Créer |
| `backend/app/tests/unit/test_domain_router.py` | Créer |
| `backend/app/prediction/schemas.py` | Modifier si `AstroEvent` manque `natal_house_target` |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/`
- `backend/app/prediction/event_detector.py`

### Références

- [Source: backend/app/infra/db/repositories/prediction_schemas.py — HouseCategoryWeightData, PlanetCategoryWeightData]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
