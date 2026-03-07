# Story 34.4 : Calibrateur percentile → note 1–20

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `PercentileCalibrator` qui convertit `RawDay(c)` en note entière 1–20 via interpolation piecewise linéaire sur 5 percentiles,
so that les scores sont stables, comparables et calibrés sur la distribution réelle des signaux.

## Acceptance Criteria

### AC1 — Interpolation piecewise linéaire sur 4 segments

Points d'ancrage : `(P5→2, P25→6, P50→10, P75→14, P95→19)`.
Entre deux points, interpolation linéaire.

### AC2 — Saturation basse : `raw_day ≤ P5 → note 1`

### AC3 — Saturation haute : `raw_day ≥ P95 → note 20`

### AC4 — Note entière `[1, 20]`

`round()` + `max(1, min(20, ...))`.

### AC5 — Calibration par catégorie

Chaque catégorie utilise ses propres percentiles. Deux catégories avec même `raw_day` peuvent avoir des notes différentes.

### AC6 — Calibration provisoire fonctionnelle

Si `CalibrationData is None` → utiliser calibration par défaut synthétique :
```python
DEFAULT_CALIBRATION = CalibrationData(p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5, sample_size=0)
```
Pas d'exception, pas de note absurde.

### AC7 — Déterminisme

Même input → même note (pas d'aléatoire).

## Tasks / Subtasks

### T1 — `PercentileCalibrator` (AC1–AC7)

- [ ] Créer `backend/app/prediction/calibrator.py`
  - [ ] Constante `DEFAULT_CALIBRATION: CalibrationData`
  - [ ] Constante `PERCENTILE_TARGETS = [(p05, 2), (p25, 6), (p50, 10), (p75, 14), (p95, 19)]`
  - [ ] Classe `PercentileCalibrator`
  - [ ] `calibrate(raw_day: float, calibration: CalibrationData | None) -> int`
    - [ ] Si `None` → utiliser `DEFAULT_CALIBRATION`
    - [ ] Si `raw_day ≤ p05` → retourner `1`
    - [ ] Si `raw_day ≥ p95` → retourner `20`
    - [ ] Sinon interpoler sur le bon segment
    - [ ] `round()` + clamp `[1, 20]`
  - [ ] Méthode `calibrate_all(day_aggregation: DayAggregation, calibrations: dict[str, CalibrationData | None]) -> dict[str, int]`

### T2 — Tests unitaires (AC1–AC7)

- [ ] Créer `backend/app/tests/unit/test_calibrator.py`
  - [ ] `test_at_p5_returns_2` — `raw_day = P5` → note = 2
  - [ ] `test_below_p5_returns_1` — `raw_day < P5` → note = 1
  - [ ] `test_at_p95_returns_19` — `raw_day = P95` → note = 19
  - [ ] `test_above_p95_returns_20` — `raw_day > P95` → note = 20
  - [ ] `test_midpoint_p5_p25` — `raw_day = (P5+P25)/2` → note = 4
  - [ ] `test_midpoint_p50_p75` — `raw_day = (P50+P75)/2` → note = 12
  - [ ] `test_all_4_segments` — tester un point dans chacun des 4 segments
  - [ ] `test_none_calibration_uses_default` — `None` → calibration par défaut, pas d'exception
  - [ ] `test_note_range` — pour tout `raw_day ∈ [-3, +3]` → note ∈ `[1, 20]` (100 valeurs)
  - [ ] `test_deterministic` — même input × 10 → même note

## Dev Notes

### Implementation piecewise linéaire

```python
from app.infra.db.repositories.prediction_schemas import CalibrationData

DEFAULT_CALIBRATION = CalibrationData(
    p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5, sample_size=0
)

def calibrate(self, raw_day: float, calibration: CalibrationData | None) -> int:
    cal = calibration or DEFAULT_CALIBRATION
    p5  = cal.p05 if cal.p05 is not None else DEFAULT_CALIBRATION.p05
    p25 = cal.p25 if cal.p25 is not None else DEFAULT_CALIBRATION.p25
    p50 = cal.p50 if cal.p50 is not None else DEFAULT_CALIBRATION.p50
    p75 = cal.p75 if cal.p75 is not None else DEFAULT_CALIBRATION.p75
    p95 = cal.p95 if cal.p95 is not None else DEFAULT_CALIBRATION.p95

    if raw_day <= p5:
        return 1
    if raw_day >= p95:
        return 20

    segments = [
        (p5, 2.0, p25, 6.0),
        (p25, 6.0, p50, 10.0),
        (p50, 10.0, p75, 14.0),
        (p75, 14.0, p95, 19.0),
    ]
    for x0, y0, x1, y1 in segments:
        if x0 <= raw_day <= x1 and x1 > x0:
            t = (raw_day - x0) / (x1 - x0)
            return max(1, min(20, round(y0 + t * (y1 - y0))))

    return 10  # fallback (ne devrait jamais être atteint)
```

### `CalibrationData` déjà défini

`backend/app/infra/db/repositories/prediction_schemas.py` — ligne ~111 à 118. Importer directement, ne pas redéfinir.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/calibrator.py` | Créer |
| `backend/app/tests/unit/test_calibrator.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/aggregator.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`

### Références

- [Source: backend/app/infra/db/repositories/prediction_schemas.py — CalibrationData]
- [Source: docs/model_de_calcul_journalier.md — Calibration percentile]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
