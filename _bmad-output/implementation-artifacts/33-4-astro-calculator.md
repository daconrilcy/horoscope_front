# Story 33.4 : Calculateur astro intraday V1

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `AstroCalculator` qui calcule pour chaque pas de temps les positions planétaires, vitesses, Asc/MC, maisons et la maison natale traversée,
so that le détecteur d'événements (story 33-5) dispose d'un état astro complet et fiable pour chaque instant de la journée.

## Acceptance Criteria

### AC1 — 10 planètes V1 uniquement

`StepAstroState.planets` contient exactement les 10 clés V1 : `Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto`.

### AC2 — Asc et MC à chaque pas

`StepAstroState.ascendant_deg` et `mc_deg` dans `[0, 360)`, calculés via `swe.houses()` avec la latitude/longitude du jour.

### AC3 — Vitesse et statut D/R

`PlanetState.speed_lon` (deg/jour, signé). `PlanetState.is_retrograde = speed_lon < 0`.

### AC4 — Signe courant

`PlanetState.sign_code = floor(longitude / 30)` — entier `[0, 11]`.

### AC5 — Maison natale traversée

`PlanetState.natal_house_transited` (int 1–12) calculé en comparant la longitude de transit aux cuspides natales passées en entrée.

### AC6 — Repli Placidus → Porphyre tracé

Si `swe.houses()` avec `'P'` échoue (retour anormal ou latitude extrême) → tenter `'O'` (Porphyre) → consigner `house_system_effective = "Porphyre"` dans la réponse. Pas d'exception.

### AC7 — Corps hors V1 → exception explicite

Demander un corps non V1 → `PredictionEngineError` claire.

## Tasks / Subtasks

### T1 — `AstroCalculator` (AC1–AC7)

- [x] Créer `backend/app/prediction/astro_calculator.py`
  - [x] Dataclass `PlanetState` (fields: `code`, `longitude`, `speed_lon`, `is_retrograde`, `sign_code`, `natal_house_transited`)
  - [x] Dataclass `StepAstroState` (fields: `ut_jd`, `ascendant_deg`, `mc_deg`, `house_cusps: list[float]`, `house_system_effective: str`, `planets: dict[str, PlanetState]`)
  - [x] Classe `AstroCalculator(natal_cusps: list[float], latitude: float, longitude: float)`
  - [x] `compute_step(ut_jd: float) -> StepAstroState`
    - [x] Calculer les 10 planètes via `swe.calc_ut(jd, swe.SUN, swe.FLG_SPEED)` etc.
    - [x] `_compute_houses(ut_jd)` → `(cusps, asc, mc, effective_system)`
    - [x] `_natal_house_for_longitude(lon)` → int 1–12
    - [x] Construire `PlanetState` pour chaque planète V1
  - [x] `V1_PLANETS: dict[str, int]` = mapping nom → constante `swe.*`
  - [x] Repli Porphyre si Placidus échoue (AC6)

### T2 — Tests unitaires (AC1–AC7)

- [x] Créer `backend/app/tests/unit/test_astro_calculator.py`
  - [x] `test_all_v1_planets_present` — 10 clés exactes dans `StepAstroState.planets`
  - [x] `test_asc_mc_in_range` — `ascendant_deg` et `mc_deg` dans `[0, 360)`
  - [x] `test_longitude_in_range` — toutes longitudes dans `[0, 360)`
  - [x] `test_sign_code_from_longitude` — `sign_code == floor(longitude / 30)` pour le Soleil
  - [x] `test_retrograde_detection` — utiliser JD connu de Mercure rétrograde (ex. 2026-03-15) → `is_retrograde=True`
  - [x] `test_direct_detection` — JD Mercure direct → `is_retrograde=False`
  - [x] `test_natal_house_boundary` — longitude 30.1° avec cuspide maison 2 à 30° → maison 2
  - [x] `test_fallback_porphyre` — latitude 89°N → `house_system_effective` ≠ `"Placidus"`
  - [x] `test_unknown_planet_raises` — demander `"Chiron"` → `PredictionEngineError`

## Dev Notes

### Constantes Swiss Ephemeris V1

```python
import swisseph as swe

V1_PLANETS: dict[str, int] = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}
```

### Calcul position + vitesse

```python
result, flags = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
longitude = result[0]   # degrés écliptiques 0–360
speed_lon = result[3]   # deg/jour (négatif = rétrograde)
```

### Calcul maisons Placidus

```python
cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
# cusps[0] = cuspide maison 1, ..., cusps[11] = cuspide maison 12
# ascmc[0] = Ascendant, ascmc[1] = MC
```

En cas de retour invalide (latitudes extrêmes), `swe.houses` peut retourner des valeurs aberrantes. Détecter via vérification de cohérence des cuspides.

### Maison natale pour une longitude

```python
def _natal_house_for_longitude(self, lon: float) -> int:
    for i in range(11, -1, -1):
        if lon >= self.natal_cusps[i] % 360:
            return i + 1
    return 1  # fallback
```

Note : cette logique simple ignore le cas de cuspides qui traversent 0°/360°. Implémenter la logique correcte pour les cuspides > 330° (signe Poissons → Bélier).

### pyswisseph déjà disponible

`pyswisseph` est dans `backend/pyproject.toml` depuis l'epic 20. Vérifier le chemin des éphémérides avec `swe.set_ephe_path(path)` — le path est configuré dans les settings existants.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/astro_calculator.py` | Créer |
| `backend/app/tests/unit/test_astro_calculator.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/temporal_sampler.py` (lire `SamplePoint` uniquement)
- `backend/app/domain/astrology/` (moteur natal existant — ne pas modifier)

### Références

- [Source: docs/model_de_calcul_journalier.md — Périmètre V1, orbes, Swiss Ephemeris]
- [Source: backend/app/domain/astrology/ — exemples d'utilisation Swiss Ephemeris existants]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-001

### Debug Log References

- [AstroCalculator passed 10 unit tests]
- [Ruff linting passed for all modified files]

### Completion Notes List

- Service `AstroCalculator` implémenté avec support des 10 planètes V1.
- Calcul de l'Ascendant et du MC à chaque pas.
- Détection du statut rétrograde via la vitesse longitudinale.
- Calcul de la maison natale traversée avec gestion du wrap-around (0/360°).
- Repli automatique sur le système de maisons Porphyre en cas d'échec de Placidus (latitudes extrêmes).
- Validation via 10 tests unitaires couvrant les AC1 à AC7.
- Déplacement des dataclasses `PlanetState` et `StepAstroState` vers `schemas.py` pour une meilleure réutilisation.
- Validation finale en pipeline réel via `EngineOrchestrator.run()` sur un `chart_json` canonique et une journée complète (`samples=96`).

### File List

- `backend/app/prediction/astro_calculator.py`
- `backend/app/prediction/schemas.py`
- `backend/app/tests/unit/test_astro_calculator.py`

Status: done
