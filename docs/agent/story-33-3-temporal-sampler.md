# Story 33-3 — Sampler temporel journalier

## Contexte & Périmètre

**Epic 33 / Story 33-3**
**Chapitre 33** — Fondations du moteur de calcul quotidien

Le moteur a besoin d'une grille temporelle précise pour parcourir la journée locale et calculer les positions astrologiques à intervalles réguliers. Cette story crée le service `TemporalSampler` qui convertit un jour local en intervalle UT, génère les pas de 15 minutes, intègre les bornes lever/coucher du soleil pour les heures planétaires, et prévoit un mécanisme de raffinement local à 1 minute autour des transitions détectées.

---

## Hypothèses & Dépendances

- **Dépend de 33-1** : `EngineInput`, `SamplePoint` définis dans `backend/app/prediction/schemas.py`
- `pyswisseph` (ou `ephem`) disponible pour les calculs de lever/coucher solaire
- Le timezone utilisateur est un identifiant IANA valide (ex. `"Europe/Paris"`)
- Le jour local peut chevaucher 2 jours UT (fréquent pour les fuseaux UTC+, les 00:00-02:00 locales tombent la veille en UT)
- Le changement d'heure (DST) est géré par `zoneinfo` (Python 3.9+)

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Convertir une date locale + timezone en intervalle UT précis (début/fin)
- Générer 96 pas de 15 minutes couvrant toute la journée locale
- Maintenir un mapping explicite `ut_jd ↔ local_datetime` pour chaque pas
- Calculer les heures de lever/coucher solaires (UT) pour la journée
- Fournir un mécanisme `refine_around(ut_jd, radius_minutes=5)` qui génère des sous-pas à 1 min

**Non-Objectifs :**
- Pas de calcul de positions planétaires dans ce service
- Pas de scoring
- Le raffinement est un utilitaire, pas encore appelé automatiquement

---

## Acceptance Criteria

### AC1 — Grille de base 15 minutes
`TemporalSampler.build_day_grid(local_date, timezone, latitude, longitude)` retourne un `DayGrid` contenant :
- `samples` : liste de `SamplePoint` avec exactement 96 éléments pour une journée standard (pas de changement d'heure)
- `ut_start` : Julian Day UT du début du jour local (00:00:00 local)
- `ut_end` : Julian Day UT de la fin du jour local (23:59:59 local)

### AC2 — Mapping UT ↔ local explicite
Chaque `SamplePoint` stocke :
- `ut_time` : float (Julian Day Number en UT)
- `local_time` : `datetime` timezone-aware en heure locale

La conversion inverse `SamplePoint.local_time → ut_time` doit être cohérente.

### AC3 — Lever/coucher solaire intégré
`DayGrid` contient :
- `sunrise_ut` : float (JD UT du lever du soleil, ou `None` si non calculable)
- `sunset_ut` : float (JD UT du coucher, ou `None`)
- Ces valeurs sont calculées via Swiss Ephemeris (`swe_rise_trans`) ou équivalent

### AC4 — Raffinement autour d'une transition
`TemporalSampler.refine_around(ut_jd, radius_minutes=5)` retourne une liste de `SamplePoint` à pas de 1 minute centré sur `ut_jd` (soit 10 points pour radius=5).

### AC5 — Stabilité sur changement d'heure (DST)
Sur un jour de passage heure d'été → heure d'hiver (23h locales au lieu de 24h) :
- Le nombre de pas est ajusté (92 pas au lieu de 96)
- Aucune exception n'est levée
- Le mapping UT ↔ local reste cohérent

Sur un jour de passage heure d'hiver → heure d'été (25h locales) :
- 100 pas
- Aucune exception

### AC6 — Pas de scoring dans ce service
`TemporalSampler` ne calcule aucun score ni aucune position planétaire.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── temporal_sampler.py    ← TemporalSampler, DayGrid
```

### `temporal_sampler.py` — extraits clés

```python
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import swisseph as swe

from app.prediction.schemas import SamplePoint

STEP_MINUTES = 15
REFINE_STEP_MINUTES = 1

@dataclass
class DayGrid:
    samples: list[SamplePoint]
    ut_start: float
    ut_end: float
    sunrise_ut: float | None
    sunset_ut: float | None
    local_date: date
    timezone: str

class TemporalSampler:
    def build_day_grid(
        self,
        local_date: date,
        timezone: str,
        latitude: float,
        longitude: float,
    ) -> DayGrid:
        ...

    def refine_around(
        self,
        ut_jd: float,
        radius_minutes: int = 5,
    ) -> list[SamplePoint]:
        ...

    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convertit un datetime timezone-aware en Julian Day UT."""
        ...

    def _jd_to_local_datetime(self, jd: float, tz: ZoneInfo) -> datetime:
        """Convertit un Julian Day UT en datetime local."""
        ...
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_temporal_sampler.py`

| Test | Description |
|------|-------------|
| `test_standard_day_has_96_samples` | Journée standard (sans DST) → 96 `SamplePoint` |
| `test_sample_ut_local_coherent` | Pour chaque `SamplePoint`, `local_time` reconverti en UT = `ut_time` (±1s) |
| `test_ut_start_end_covers_full_day` | `ut_start` ≤ premier pas, `ut_end` ≥ dernier pas |
| `test_sunrise_sunset_present` | `DayGrid.sunrise_ut` et `sunset_ut` non nulls pour Paris en journée normale |
| `test_refine_around_yields_1min_steps` | `refine_around(jd, radius=5)` → 10 points espacés de 1 minute |
| `test_dst_spring_forward` | Passage printemps (25h jour) → 100 pas, pas d'exception |
| `test_dst_fall_back` | Passage automne (23h jour) → 92 pas, pas d'exception |
| `test_timezone_coherence` | UTC+9 (Tokyo) : début UT = fin UT - veille, mapping cohérent |

---

## Nouveaux fichiers

- `backend/app/prediction/temporal_sampler.py` ← CRÉER
- `backend/app/tests/unit/test_temporal_sampler.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `SamplePoint` (défini en 33-1)
- `docs/model_de_calcul_journalier.md` — conventions temporelles, UT vs local

---

## Checklist de validation

- [ ] 96 pas sur journée standard sans DST
- [ ] Mapping UT ↔ local cohérent pour chaque point
- [ ] `sunrise_ut` et `sunset_ut` présents pour coordonnées tempérées
- [ ] `refine_around` retourne 2×radius points à 1 minute
- [ ] Stabilité sur les 2 jours DST de l'année
- [ ] Aucun calcul astro ni scoring dans ce service
- [ ] Tous les tests unitaires passent
