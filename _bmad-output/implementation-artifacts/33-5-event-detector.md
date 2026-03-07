# Story 33.5 : Détecteur d'événements astrologiques V1

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `EventDetector` qui transforme la séquence de `StepAstroState` en événements atomiques horodatés (`enter_orb`, `exact`, `exit_orb`, `moon_sign_ingress`, `asc_sign_change`, `planetary_hour_change`),
so that le pipeline de scoring (epic 34) dispose d'une liste d'événements enrichis et triés chronologiquement.

## Acceptance Criteria

### AC1 — Aspects V1 uniquement

Seuls les 5 aspects majeurs ptolémaïques sont détectés : 0° (conjonction), 60° (sextile), 90° (carré), 120° (trigone), 180° (opposition).

### AC2 — Cibles natales V1

Cibles natales : 10 planètes natales + Asc natal + MC natal. Tout autre corps est ignoré.

### AC3 — `enter_orb`, `exact`, `exit_orb`

- `enter_orb` : orbe passe sous `orb_max(planète, aspect)` en descendant
- `exact` : orbe atteint son minimum local (changement de signe de la dérivée)
- `exit_orb` : orbe repasse au-dessus de `orb_max`
- Si le pas de 15 min est trop grossier, utiliser `TemporalSampler.refine_around()` pour affiner à ±5 min

### AC4 — `applying` / `separating`

`applying = True` si l'orbe décroît entre deux pas. `separating = True` si l'orbe croît. Stocké dans `AstroEvent.metadata["phase"]`.

### AC5 — `moon_sign_ingress`

Détecté quand la Lune change de `sign_code` entre deux pas. `AstroEvent` créé avec `from_sign`, `to_sign` dans `metadata`.

### AC6 — `asc_sign_change`

Détecté quand l'Ascendant change de `sign_code` entre deux pas.

### AC7 — 24 heures planétaires

Calculées depuis `DayGrid.sunrise_ut` et `DayGrid.sunset_ut` selon la séquence chaldéenne. 24 événements `planetary_hour_change` par journée complète.

### AC8 — Enrichissement complet de `AstroEvent`

Chaque événement porte : `event_type`, `ut_time`, `local_time`, `body`, `target`, `aspect`, `orb_deg`, `priority`, `base_weight`, `metadata`.

## Tasks / Subtasks

### T1 — `EventDetector` (AC1–AC8)

- [ ] Créer `backend/app/prediction/event_detector.py`
  - [ ] Constante `ASPECTS_V1: dict[int, str]` = `{0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}`
  - [ ] Classe `EventDetector(ctx: LoadedPredictionContext, natal_positions: dict[str, float])`
  - [ ] `detect(steps: list[StepAstroState], day_grid: DayGrid) -> list[AstroEvent]`
    - [ ] `_detect_aspects(steps)` — boucle sur tous les transits × cibles natales V1 × aspects V1
    - [ ] `_orb(transit_lon, natal_lon, aspect_deg) -> float`
    - [ ] `_orb_max(planet_code, aspect_code) -> float` — depuis `PlanetProfileData.orb_active_deg` × `AspectProfileData.orb_multiplier`
    - [ ] Détection `enter_orb`/`exact`/`exit_orb` sur l'évolution d'orbe entre pas consécutifs
    - [ ] `_detect_moon_ingress(steps)`
    - [ ] `_detect_asc_sign_change(steps)`
    - [ ] `_detect_planetary_hours(day_grid)`
  - [ ] Séquence chaldéenne : `["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]`
  - [ ] Retourner liste triée par `ut_time`

### T2 — Tests unitaires (AC1–AC8)

- [ ] Créer `backend/app/tests/unit/test_event_detector.py`
  - [ ] `test_exact_detected` — séquence orbe `[1.5, 0.05, 0.8]` → événement `exact` au pas 1
  - [ ] `test_enter_orb_detected` — orbe `[2.5, 1.8]` avec orb_max=2.0 → `enter_orb`
  - [ ] `test_exit_orb_detected` — orbe `[1.8, 2.5]` → `exit_orb`
  - [ ] `test_applying_true_on_decreasing_orb` — orbe décroissant → `phase="applying"`
  - [ ] `test_separating_true_on_increasing_orb` — orbe croissant → `phase="separating"`
  - [ ] `test_moon_ingress_detected` — Moon `sign_code` passe de 1 à 2 → `moon_sign_ingress`
  - [ ] `test_asc_change_detected` — Asc `sign_code` change → `asc_sign_change`
  - [ ] `test_24_planetary_hours` — journée complète → 24 événements `planetary_hour_change`
  - [ ] `test_non_v1_target_ignored` — cible hors V1 dans `natal_positions` → ignorée
  - [ ] `test_minor_aspect_ignored` — 150° (quinconce) → aucun événement
  - [ ] `test_events_sorted_by_time` — liste retournée triée par `ut_time` croissant

## Dev Notes

### Calcul de l'orbe

```python
def _orb(self, transit_lon: float, natal_lon: float, aspect_deg: int) -> float:
    """Orbe en degrés (toujours positif)."""
    diff = abs(transit_lon - natal_lon) % 360
    if diff > 180:
        diff = 360 - diff
    return abs(diff - aspect_deg)
```

### `orb_max` depuis le contexte

```python
def _orb_max(self, planet_code: str, aspect_code: str) -> float:
    planet_profile = self.ctx.prediction_context.planet_profiles.get(planet_code)
    orb_active = planet_profile.orb_active_deg if planet_profile else 2.0
    aspect_profile = self.ctx.prediction_context.aspect_profiles.get(aspect_code)
    multiplier = aspect_profile.orb_multiplier if aspect_profile else 1.0
    return orb_active * multiplier
```

### Heures planétaires

```python
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

def _planetary_hour_ruler(day_of_week: int, hour_index: int) -> str:
    """day_of_week: 0=Dimanche (Sun), 1=Lundi (Moon), etc."""
    # Planète du jour : Sun=0, Moon=1, Mars=2, Mercury=3, Jupiter=4, Venus=5, Saturn=6
    DAY_RULERS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    first_ruler_idx = CHALDEAN_ORDER.index(DAY_RULERS[day_of_week])
    return CHALDEAN_ORDER[(first_ruler_idx + hour_index) % 7]
```

### `EventTypeData` depuis le contexte

`priority` et `base_weight` viennent de `ctx.ruleset_context.event_types[event_type_code]`. Si le type n'existe pas dans le contexte, utiliser des valeurs par défaut raisonnables (priority=50, base_weight=1.0).

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/event_detector.py` | Créer |
| `backend/app/tests/unit/test_event_detector.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/astro_calculator.py`
- `backend/app/prediction/temporal_sampler.py`
- `backend/app/infra/db/`

### Références

- [Source: docs/model_de_calcul_journalier.md — Orbes V1, aspects, heures planétaires]
- [Source: backend/app/infra/db/repositories/prediction_schemas.py — AspectProfileData, EventTypeData]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
