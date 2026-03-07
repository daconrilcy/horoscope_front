# Story 33.5 : Détecteur d'événements astrologiques V1

Status: done

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

- [x] `enter_orb` : orbe passe sous `orb_max(planète, aspect)` en descendant
- [x] `exact` : orbe atteint son minimum local (changement de signe de la dérivée)
- [x] `exit_orb` : orbe repasse au-dessus de `orb_max`
- [ ] Si le pas de 15 min est trop grossier, utiliser `TemporalSampler.refine_around()` pour affiner à ±5 min (V1: pas de 15 min conservé, affinement pour V2 ou si requis par tests réels)

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

- [x] Créer `backend/app/prediction/event_detector.py`
  - [x] Constante `ASPECTS_V1: dict[int, str]` = `{0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}`
  - [x] Classe `EventDetector(ctx: LoadedPredictionContext, natal_positions: dict[str, float])`
  - [x] `detect(steps: list[StepAstroState], day_grid: DayGrid) -> list[AstroEvent]`
    - [x] `_detect_aspects(steps)` — boucle sur tous les transits × cibles natales V1 × aspects V1
    - [x] `_orb(transit_lon, natal_lon, aspect_deg) -> float`
    - [x] `_orb_max(planet_code, aspect_code) -> float` — depuis `PlanetProfileData.orb_active_deg` × `AspectProfileData.orb_multiplier`
    - [x] Détection `enter_orb`/`exact`/`exit_orb` sur l'évolution d'orbe entre pas consécutifs
    - [x] `_detect_moon_ingress(steps)`
    - [x] `_detect_asc_sign_change(steps)`
    - [x] `_detect_planetary_hours(day_grid)`
  - [x] Séquence chaldéenne : `["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]`
  - [x] Retourner liste triée par `ut_time`

### T2 — Tests unitaires (AC1–AC8)

- [x] Créer `backend/app/tests/unit/test_event_detector.py`
  - [x] `test_exact_detected` — séquence orbe `[1.5, 0.05, 0.8]` → événement `exact` au pas 1
  - [x] `test_enter_orb_detected` — orbe `[2.5, 1.8]` avec orb_max=2.0 → `enter_orb`
  - [x] `test_exit_orb_detected` — orbe `[1.8, 2.5]` → `exit_orb`
  - [x] `test_applying_true_on_decreasing_orb` — orbe décroissant → `phase="applying"`
  - [x] `test_separating_true_on_increasing_orb` — orbe croissant → `phase="separating"`
  - [x] `test_moon_ingress_detected` — Moon `sign_code` passe de 1 à 2 → `moon_sign_ingress`
  - [x] `test_asc_change_detected` — Asc `sign_code` change → `asc_sign_change`
  - [x] `test_24_planetary_hours` — journée complète → 24 événements `planetary_hour_change`
  - [x] `test_non_v1_target_ignored` — cible hors V1 dans `natal_positions` → ignorée
  - [x] `test_minor_aspect_ignored` — 150° (quinconce) → aucun événement
  - [x] `test_events_sorted_by_time` — liste retournée triée par `ut_time` croissant

## Dev Notes

### Mise à jour des schémas

`StepAstroState` et `AstroEvent` ont été enrichis pour supporter `local_time` et `metadata`. Les tests existants ont été mis à jour.

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Mise à jour de `schemas.py` pour ajouter `metadata` à `AstroEvent` et `local_time` à `StepAstroState`.
- Mise à jour de `astro_calculator.py` pour passer `local_time` à `compute_step`.
- Mise à jour de `test_astro_calculator.py` pour refléter le changement de signature de `compute_step`.

### Completion Notes List

- `EventDetector` implémenté avec détection d'aspects (enter, exact, exit), ingress lunaire, changement de signe Asc et heures planétaires.
- Tests unitaires complets passant à 100%.
- Régression évitée sur `AstroCalculator` via mise à jour des tests.

### File List

- `backend/app/prediction/event_detector.py` (Nouveau)
- `backend/app/tests/unit/test_event_detector.py` (Nouveau)
- `backend/app/prediction/schemas.py` (Modifié)
- `backend/app/prediction/astro_calculator.py` (Modifié)
- `backend/app/tests/unit/test_astro_calculator.py` (Modifié)
