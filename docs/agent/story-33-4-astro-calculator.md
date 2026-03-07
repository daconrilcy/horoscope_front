# Story 33-4 — Calculateur astro intraday V1

## Contexte & Périmètre

**Epic 33 / Story 33-4**
**Chapitre 33** — Fondations du moteur de calcul quotidien

Pour chaque pas de temps produit par le `TemporalSampler`, le moteur doit calculer les positions et états astrologiques utiles : longitude, vitesse, statut direct/rétrograde, signe courant, Ascendant, MC, cuspides de maisons et maison natale traversée par chaque planète transitante. Cette story crée `AstroCalculator`, wrapper au-dessus de Swiss Ephemeris, limité au périmètre V1 strict.

---

## Hypothèses & Dépendances

- **Dépend de 33-3** : `DayGrid`, `SamplePoint` disponibles
- `pyswisseph` est installé et les fichiers d'éphémérides sont présents (chemin configurable via `SWE_EPHE_PATH`)
- Le périmètre V1 : 10 planètes (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto), Asc, MC
- Positions géocentriques uniquement (flag `swe.FLG_SPEED` activé pour vitesses)
- Système de maisons : Placidus (`'P'`) avec repli Porphyre (`'O'`) si non-convergence Swiss Ephemeris
- Le thème natal est fourni comme dict avec les positions natales déjà calculées

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Calculer pour chaque `SamplePoint` : positions (longitude), vitesses, statut D/R, signe courant pour les 10 planètes V1
- Calculer Asc et MC à chaque pas via `swe_houses`
- Calculer la maison natale traversée par chaque planète transitante (en comparant la longitude de transit aux cuspides natales)
- Tracer explicitement tout repli Placidus → Porphyre dans la sortie
- Fournir un objet `StepAstroState` par pas de temps

**Non-Objectifs :**
- Pas de topocentrique dans cette story (V1 = géocentrique uniquement)
- Pas de calcul d'aspects (c'est la story 33-5)
- Pas d'étoiles fixes, parts arabes, astéroïdes mineurs
- Pas de progressions, révolutions solaires, directions primaires

---

## Acceptance Criteria

### AC1 — Périmètre V1 strict
Seules les 10 planètes V1 sont calculées : `[Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto]`. Aucun autre corps n'est inclus dans la sortie standard.

### AC2 — Asc et MC à chaque pas
`StepAstroState` contient `ascendant_deg` et `mc_deg` (longitude écliptique), calculés via `swe.houses()` à chaque pas, avec la latitude/longitude du jour.

### AC3 — Vitesse et statut D/R
Pour chaque planète : `speed_lon_deg_day` (vitesse en longitude, deg/jour). Une planète est `is_retrograde = True` si et seulement si `speed_lon_deg_day < 0`.

### AC4 — Signe courant
`sign_code` pour chaque planète : le signe tropical (0–11) dérivé de `floor(longitude / 30)`.

### AC5 — Maison natale traversée
Pour chaque planète transitante, `natal_house_transited` (int 1–12) est calculé en comparant sa longitude de transit aux cuspides du thème natal. Utilise les cuspides du thème natal (déjà calculées et passées en entrée).

### AC6 — Repli Placidus → Porphyre tracé
Si `swe.houses()` avec `'P'` échoue (latitude extrême, retour anormal), le calculateur :
1. Tente Porphyre (`'O'`)
2. Consigne `house_system_effective = "Porphyre"` dans l'`EngineOutput.effective_context`
3. Ne lève pas d'exception

### AC7 — Pas de technique exotique
Aucun calcul hors périmètre V1. Le code échoue explicitement si on lui demande un corps non V1.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── astro_calculator.py    ← AstroCalculator, StepAstroState, PlanetState
```

### `astro_calculator.py` — extraits clés

```python
from dataclasses import dataclass
import swisseph as swe

V1_PLANETS = {
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

@dataclass
class PlanetState:
    code: str
    longitude: float       # degrés écliptiques 0–360
    speed_lon: float       # deg/jour (négatif = rétrograde)
    is_retrograde: bool
    sign_code: int         # 0=Aries, 1=Taurus, ..., 11=Pisces
    natal_house_transited: int  # 1–12

@dataclass
class StepAstroState:
    ut_jd: float
    ascendant_deg: float
    mc_deg: float
    house_cusps: list[float]  # 12 cuspides (index 0 = maison 1)
    house_system_effective: str
    planets: dict[str, PlanetState]  # code → PlanetState

class AstroCalculator:
    def __init__(self, natal_cusps: list[float], latitude: float, longitude: float):
        self.natal_cusps = natal_cusps
        self.latitude = latitude
        self.longitude = longitude

    def compute_step(self, ut_jd: float) -> StepAstroState:
        """Calcule l'état astro complet pour un Julian Day UT donné."""
        ...

    def _compute_houses(self, ut_jd: float) -> tuple[list[float], float, float, str]:
        """Retourne (cuspides, asc, mc, house_system_effective)."""
        ...

    def _natal_house_for_longitude(self, lon: float) -> int:
        """Retourne la maison natale (1–12) pour une longitude de transit."""
        ...
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_astro_calculator.py`

| Test | Description |
|------|-------------|
| `test_all_v1_planets_present` | `StepAstroState.planets` contient exactement les 10 clés V1 |
| `test_asc_mc_present` | `ascendant_deg` et `mc_deg` non nuls, dans `[0, 360)` |
| `test_longitude_in_range` | Toutes les longitudes planétaires dans `[0, 360)` |
| `test_sign_code_derived_from_longitude` | `sign_code == floor(longitude / 30)` pour Sun |
| `test_retrograde_when_speed_negative` | Mercure rétrograde connu : `is_retrograde=True` et `speed_lon < 0` |
| `test_direct_when_speed_positive` | Mercure direct : `is_retrograde=False` |
| `test_natal_house_correct` | Longitude 30° avec cuspide maison 1 à 0°, maison 2 à 30° → maison 2 |
| `test_placidus_fallback_traced` | Latitude 89°N → repli, `house_system_effective != "Placidus"` |
| `test_unknown_planet_raises` | Demander corps hors V1 → exception explicite |

Utiliser des Julian Days connus pour des positions vérifiables (ex. éphémérides du 2000-01-01 12:00 UT).

---

## Nouveaux fichiers

- `backend/app/prediction/astro_calculator.py` ← CRÉER
- `backend/app/tests/unit/test_astro_calculator.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `SamplePoint`
- `backend/app/prediction/temporal_sampler.py` — `DayGrid` (33-3)
- `docs/model_de_calcul_journalier.md` — orbes, périmètre V1, conventions Swiss Ephemeris

---

## Checklist de validation

- [ ] 10 planètes V1 calculées à chaque pas
- [ ] Asc et MC présents à chaque pas
- [ ] `sign_code` cohérent avec longitude
- [ ] `is_retrograde` dérivé uniquement du signe de la vitesse
- [ ] `natal_house_transited` calculé correctement pour 2–3 cas types
- [ ] Repli Porphyre tracé si Placidus échoue (test latitude extrême)
- [ ] Corps hors V1 → exception explicite
- [ ] Tous les tests unitaires passent
