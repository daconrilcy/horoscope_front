# Story 33.3 : Sampler temporel journalier

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `TemporalSampler` qui convertit un jour local en grille de 96 pas de 15 minutes avec mapping UT ↔ local, lever/coucher solaire et raffinement à 1 minute,
so that le calculateur astro peut recevoir une séquence temporelle précise et cohérente pour chaque run.

## Acceptance Criteria

### AC1 — 96 pas de 15 minutes sur journée standard

`TemporalSampler.build_day_grid(local_date, timezone, latitude, longitude)` retourne un `DayGrid` avec `samples: list[SamplePoint]` de 96 éléments pour une journée sans DST.

### AC2 — Mapping UT ↔ local explicite

Chaque `SamplePoint.ut_time` (Julian Day float) et `SamplePoint.local_time` (datetime timezone-aware) sont cohérents : reconvertir `local_time` → `ut_time` donne la même valeur (±1 seconde).

### AC3 — Lever/coucher solaire intégrés

`DayGrid.sunrise_ut` et `DayGrid.sunset_ut` (float JD UT ou `None`) calculés via `swe.rise_trans()`.

### AC4 — Raffinement à 1 minute

`TemporalSampler.refine_around(ut_jd, radius_minutes=5)` retourne `2 × radius_minutes` `SamplePoint` à pas de 1 minute centrés sur `ut_jd`.

### AC5 — Stabilité sur DST

- Passage printemps (23h locales) → 92 pas, pas d'exception
- Passage automne (25h locales) → 100 pas, pas d'exception
- Mapping UT ↔ local cohérent dans les deux cas

## Tasks / Subtasks

### T1 — `TemporalSampler` et `DayGrid` (AC1, AC2, AC3, AC4, AC5)

- [x] Créer `backend/app/prediction/temporal_sampler.py`
  - [x] Dataclass `DayGrid` (fields: `samples`, `ut_start`, `ut_end`, `sunrise_ut`, `sunset_ut`, `local_date`, `timezone`)
  - [x] Classe `TemporalSampler`
  - [x] `build_day_grid(local_date, timezone, latitude, longitude) -> DayGrid`
    - [x] Convertir `00:00:00 local` → JD UT via `zoneinfo` + `swe.julday()`
    - [x] Convertir `23:59:59 local` → JD UT
    - [x] Générer les pas de 15 min entre `ut_start` et `ut_end`
    - [x] Pour chaque pas, calculer `local_time` (JD UT → UTC datetime → local datetime)
    - [x] Calculer lever/coucher via `swe.rise_trans(jd, swe.SUN, lon, lat, ...)`
  - [x] `refine_around(ut_jd, radius_minutes=5) -> list[SamplePoint]`
    - [x] Générer `2 × radius` pas à 1 min autour de `ut_jd`
  - [x] `_jd_to_local_datetime(jd, tz_name) -> datetime`
  - [x] `_datetime_to_jd(dt: datetime) -> float`

### T2 — Tests unitaires (AC1, AC2, AC3, AC4, AC5)

- [x] Créer `backend/app/tests/unit/test_temporal_sampler.py`
  - [x] `test_standard_day_96_samples` — Paris 2026-03-07 → 96 SamplePoint
  - [x] `test_ut_local_coherent` — tous les SamplePoint cohérents (reconversion ±1s)
  - [x] `test_sunrise_sunset_present` — Paris latitude → sunrise/sunset non null
  - [x] `test_refine_around_10_points` — `refine_around(jd, 5)` → 10 points
  - [x] `test_refine_step_is_1min` — pas entre points refine_around = 1/1440 JD (1 minute)
  - [x] `test_ut_start_end_covers_full_day` — `ut_start`/`ut_end` couvrent bien 00:00:00 → 23:59:59 local
  - [x] `test_dst_spring_forward_has_92_samples_and_stays_in_day` — 2026-03-29 Europe/Paris → 92 pas et aucun sample hors jour local
  - [x] `test_dst_fall_back_has_100_samples_and_stays_in_day` — 2026-10-25 Europe/Paris → 100 pas et aucun sample hors jour local
  - [x] `test_dst_days_keep_local_15_minute_spacing` — les transitions DST conservent une grille locale cohérente

## Dev Notes

### Conversion JD ↔ datetime

```python
import swisseph as swe
from zoneinfo import ZoneInfo
from datetime import datetime, timezone as dt_tz

STEP_MINUTES = 15
JD_STEP = STEP_MINUTES / (24 * 60)  # 0.010416...

def _datetime_to_jd(dt: datetime) -> float:
    """datetime timezone-aware → Julian Day UT."""
    utc = dt.astimezone(dt_tz.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute/60.0 + utc.second/3600.0)

def _jd_to_local_datetime(jd: float, tz_name: str) -> datetime:
    """Julian Day UT → datetime local timezone-aware."""
    y, m, d, h = swe.revjul(jd)
    hour_int = int(h)
    min_frac = (h - hour_int) * 60
    min_int = int(min_frac)
    sec_int = int((min_frac - min_int) * 60)
    dt_utc = datetime(y, m, d, hour_int, min_int, sec_int, tzinfo=dt_tz.utc)
    return dt_utc.astimezone(ZoneInfo(tz_name))
```

### Lever/coucher solaire Swiss Ephemeris

```python
SEFLG_SPEED = swe.FLG_SPEED
rsmi = swe.CALC_RISE  # ou swe.CALC_SET

result, flag = swe.rise_trans(
    tjdut=jd_noon,  # JD UT midi local approximatif
    body=swe.SUN,
    lon=longitude,
    lat=latitude,
    alt=0.0,
    rsmi=swe.CALC_RISE,
)
sunrise_ut = result[1] if flag == 0 else None
```

### Génération des pas

```python
samples = []
t = ut_start
while t < ut_end:
    local_dt = _jd_to_local_datetime(t, timezone)
    samples.append(SamplePoint(ut_time=t, local_time=local_dt))
    t += JD_STEP
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/temporal_sampler.py` | Créer |
| `backend/app/tests/unit/test_temporal_sampler.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/schemas.py` (utiliser `SamplePoint` tel quel)
- Tout fichier infra/db/

### Références

- [Source: docs/model_de_calcul_journalier.md — Hypothèses / Temps de référence]
- [Source: backend/app/prediction/schemas.py — SamplePoint (story 33-1)]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Fixed `_jd_to_local_datetime` and `_datetime_to_jd` precision issues by adding microsecond support.
- Fixed `swe.rise_trans` signature (it requires 7 arguments in `pyswisseph`).
- Fixed `rise_trans` search start point (using `ut_start` instead of `jd_noon` to ensure today's sunrise is found).
- Reworked day-grid generation to iterate in UTC and convert back to local time, eliminating DST boundary drift.
- Aligned `ut_end` with the documented `23:59:59 local` contract.
- Centered `refine_around()` symmetrically around the target JD and expanded tests for DST/local-date coverage.

### Completion Notes List

- `TemporalSampler` implemented with 15-min grid generation.
- Correctly handles DST (Spring/Fall) with variable number of steps (92/100) and no samples leaking to the previous local day.
- `DayGrid` includes sunrise and sunset UT times via Swiss Ephemeris.
- `refine_around` provides centered 1-min precision samples.
- Unit tests cover the acceptance criteria with 8 passing tests.

### File List

- `backend/app/prediction/temporal_sampler.py`
- `backend/app/tests/unit/test_temporal_sampler.py`
- `backend/app/prediction/schemas.py` (read-only)

## Senior Developer Review (AI)

### Reviewer

Cyril

### Date

2026-03-07

### Outcome

Approved after fixes.

### Review Notes

- The day grid now iterates on UTC boundaries and converts each sample back to the requested timezone, which removes the DST fall-back leak to the previous local day.
- `ut_end` now matches the documented `23:59:59 local` boundary instead of using the next midnight as the public contract.
- `refine_around()` is now centered symmetrically around the target Julian Day, and the tests verify both spacing and centering.
- DST coverage now validates the real Europe/Paris transitions on 2026-03-29 and 2026-10-25, including the guarantee that every sample remains on the requested local date.

## Change Log

- 2026-03-07: Fixed code review findings on DST boundaries, `ut_end` contract, refine centering, and missing test coverage.
