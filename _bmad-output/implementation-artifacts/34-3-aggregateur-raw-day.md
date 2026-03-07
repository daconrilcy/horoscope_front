# Story 34.3 : Agrégateur temporel `RawStep` / `RawDay`

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `TemporalAggregator` qui agrège les contributions en `RawStep` par pas de temps, puis calcule `RawDay = 0.70×Mean + 0.20×Peak90 + 0.10×Close` avec `Power` et `Vol`,
so that le calibrateur (story 34-4) dispose d'un signal journalier normalisé et borné par catégorie.

## Acceptance Criteria

### AC1 — `RawStep(c,t)` agrège tous les événements du pas et est borné `[-3, +3]`

```
RawStep(c,t) = clamp(Σ Contribution(e,c,t) pour tout e actif à t, -3.0, +3.0)
```

### AC2 — `Mean(c)` = moyenne des RawStep de la journée

### AC3 — `Peak90(c)` = maximum de la moyenne glissante sur 6 pas (90 minutes)

Fenêtre de 6 pas consécutifs. Si moins de 6 pas disponibles, prendre la fenêtre complète disponible.

### AC4 — `Close(c)` = moyenne des 8 derniers pas (2 heures)

### AC5 — `RawDay(c)` formule V1 bornée `[-2, +2]`

```
RawDay(c) = clamp(0.70 × Mean + 0.20 × Peak90 + 0.10 × Close, -2.0, +2.0)
```

### AC6 — `Power(c)` et `Vol(c)`

```
Power(c) = max(abs(RawStep(c,t)) for all t)
Vol(c) = std(RawStep(c,t) for all t)
```
Tous deux = 0.0 si aucun événement.

### AC7 — Sortie `DayAggregation`

`aggregate()` retourne un `DayAggregation` avec un `CategoryAggregation` par catégorie contenant : `raw_steps`, `mean`, `peak90`, `close`, `raw_day`, `power`, `volatility`.

## Tasks / Subtasks

### T1 — `TemporalAggregator` (AC1–AC7)

- [ ] Créer `backend/app/prediction/aggregator.py`
  - [ ] Dataclasses `CategoryAggregation` et `DayAggregation`
  - [ ] Constantes `RAW_STEP_MAX = 3.0`, `RAW_DAY_MAX = 2.0`, `PEAK90_WINDOW = 6`, `CLOSE_WINDOW = 8`
  - [ ] Classe `TemporalAggregator`
  - [ ] `aggregate(contributions_by_step: list[dict[str, float]], category_codes: list[str]) -> DayAggregation`
    - [ ] Pour chaque catégorie, construire la liste des `RawStep` (un par pas, clamped)
    - [ ] Calculer `mean` via `statistics.mean`
    - [ ] Calculer `peak90` via `_peak90(steps)`
    - [ ] Calculer `close` via moyenne des `CLOSE_WINDOW` derniers pas
    - [ ] Calculer `raw_day` avec formule V1, clamp `[-2, +2]`
    - [ ] Calculer `power` et `volatility`
  - [ ] `_peak90(steps: list[float]) -> float`

### T2 — Tests unitaires (AC1–AC7)

- [ ] Créer `backend/app/tests/unit/test_aggregator.py`
  - [ ] `test_raw_step_sum_correct` — 3 contributions au même pas → somme correcte
  - [ ] `test_raw_step_clamped_max` — somme > 3.0 → 3.0
  - [ ] `test_raw_step_clamped_min` — somme < -3.0 → -3.0
  - [ ] `test_mean_correct` — série simple → mean attendu
  - [ ] `test_peak90_identifies_peak` — pic de 6 pas dans une série → identifié
  - [ ] `test_close_last_2h` — `close` = moyenne des 8 derniers pas
  - [ ] `test_raw_day_formula` — valeurs connues Mean/Peak90/Close → `0.70×M + 0.20×P + 0.10×C`
  - [ ] `test_raw_day_clamped_max` — RawDay > 2.0 → 2.0
  - [ ] `test_raw_day_clamped_min` — RawDay < -2.0 → -2.0
  - [ ] `test_power_max_abs` — Power = max(abs(steps))
  - [ ] `test_volatility_nonzero` — série avec variance → Vol > 0
  - [ ] `test_no_events_zero` — aucun événement → Power=0, Vol=0, RawDay≈0

## Dev Notes

### Input `contributions_by_step`

Le format attendu est : `contributions_by_step[step_index][category_code] = total_contribution_for_step`.

Avant d'appeler `aggregate()`, le caller doit construire ce dict en groupant les `Contribution(e,c,t)` par pas de temps (en utilisant le mapping `ut_time → step_index` depuis `DayGrid`).

### Implementation `_peak90`

```python
import statistics

PEAK90_WINDOW = 6

def _peak90(self, steps: list[float]) -> float:
    if not steps:
        return 0.0
    if len(steps) < PEAK90_WINDOW:
        return statistics.mean(steps)
    return max(
        statistics.mean(steps[i:i + PEAK90_WINDOW])
        for i in range(len(steps) - PEAK90_WINDOW + 1)
    )
```

### Calcul de la volatilité

```python
import statistics

volatility = statistics.stdev(steps) if len(steps) > 1 else 0.0
```

`statistics.stdev` lève `StatisticsError` si la liste a moins de 2 éléments — d'où le check.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/aggregator.py` | Créer |
| `backend/app/tests/unit/test_aggregator.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/contribution_calculator.py`
- `backend/app/prediction/temporal_sampler.py`

### Références

- [Source: docs/model_de_calcul_journalier.md — Architecture de scoring, RawDay, Peak90]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
