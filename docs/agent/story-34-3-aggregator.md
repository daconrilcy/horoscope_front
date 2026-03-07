# Story 34-3 — Agrégateur temporel `RawStep` / `RawDay`

## Contexte & Périmètre

**Epic 34 / Story 34-3**
**Chapitre 34** — Scoring, notes et timeline UX

L'agrégateur transforme les contributions individuelles par événement en un signal exploitable par journée. Pour chaque pas de temps (15 min) et chaque catégorie, il somme les contributions (`RawStep`), puis calcule les métriques journalières (`Mean`, `Peak90`, `Close`) et produit `RawDay(c)`. Il calcule aussi `Power(c)` et `Vol(c)`.

---

## Hypothèses & Dépendances

- **Dépend de 34-2** : `Contribution(e,c,t)` disponible pour chaque (événement, catégorie, pas de temps)
- Les événements sont associés à un pas de temps via leur `ut_time` (mapping depuis `DayGrid`)
- La grille de 15 min est disponible (`DayGrid.samples` depuis 33-3)
- `Peak90` = maximum sur fenêtre glissante de 90 minutes (6 pas de 15 min)
- `Close` = moyenne des 2 dernières heures de la journée locale (8 pas de 15 min)

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Calculer `RawStep(c,t)` pour chaque pas et chaque catégorie
- Calculer `Mean(c)`, `Peak90(c)`, `Close(c)` sur la journée
- Calculer `RawDay(c) = 0.70×Mean + 0.20×Peak90 + 0.10×Close`
- Calculer `Power(c)` et `Vol(c)`
- Clamp `RawStep ∈ [-3, +3]` et `RawDay ∈ [-2, +2]`

**Non-Objectifs :**
- Pas de calibration (c'est 34-4)
- Pas de persistance

---

## Acceptance Criteria

### AC1 — `RawStep(c,t)` agrège tous les événements du pas
Pour chaque pas de temps `t` et chaque catégorie `c` :
```
RawStep(c,t) = clamp(Σ Contribution(e,c,t) pour tout e actif à t, -3.0, +3.0)
```
Un événement est "actif à t" s'il appartient au pas de temps correspondant (via `ut_time`).

### AC2 — `RawStep` borné
`RawStep(c,t) ∈ [-3.0, +3.0]` strictement après clamp.

### AC3 — `Mean(c)` sur toute la journée
```
Mean(c) = mean(RawStep(c,t) pour tout t de la journée)
```

### AC4 — `Peak90(c)` fenêtre glissante 90 minutes
`Peak90(c)` = valeur maximale de la moyenne glissante sur 6 pas consécutifs (90 min) de la journée :
```
Peak90(c) = max over all windows of size 6 of mean(RawStep(c, t:t+6))
```
Si la journée a moins de 6 pas (cas DST court), prendre la fenêtre disponible.

### AC5 — `Close(c)` 2 dernières heures
```
Close(c) = mean(RawStep(c,t) pour t dans les 8 derniers pas de la journée)
```
(2h = 8 × 15 min)

### AC6 — `RawDay(c)` formule V1
```
RawDay(c) = clamp(0.70 × Mean(c) + 0.20 × Peak90(c) + 0.10 × Close(c), -2.0, +2.0)
```

### AC7 — `Power(c)` et `Vol(c)` non nuls si activité
```
Power(c) = max(abs(RawStep(c,t)) for t in journée)
Vol(c) = std(RawStep(c,t) for t in journée)
```
Si aucun événement ne touche la catégorie, `Power(c) = 0` et `Vol(c) = 0`.

### AC8 — Sortie structurée
`TemporalAggregator.aggregate()` retourne un `DayAggregation` contenant pour chaque catégorie :
- `raw_steps` : list[float] (96 valeurs, une par pas)
- `mean` : float
- `peak90` : float
- `close` : float
- `raw_day` : float (borné)
- `power` : float
- `volatility` : float

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── aggregator.py    ← TemporalAggregator, DayAggregation, CategoryAggregation
```

### `aggregator.py` — extraits clés

```python
import statistics
from dataclasses import dataclass, field

RAW_STEP_MAX = 3.0
RAW_DAY_MAX = 2.0
PEAK90_WINDOW = 6    # 6 × 15min = 90min
CLOSE_WINDOW = 8     # 8 × 15min = 2h

@dataclass
class CategoryAggregation:
    category_code: str
    raw_steps: list[float]
    mean: float
    peak90: float
    close: float
    raw_day: float
    power: float
    volatility: float

@dataclass
class DayAggregation:
    categories: dict[str, CategoryAggregation]  # code → CategoryAggregation

class TemporalAggregator:
    def aggregate(
        self,
        contributions_by_step: list[dict[str, float]],  # [pas → {cat_code: contribution}]
        category_codes: list[str],
    ) -> DayAggregation:
        result = {}
        for code in category_codes:
            steps = [
                max(-RAW_STEP_MAX, min(RAW_STEP_MAX,
                    sum(step_contributions.get(e_code, 0.0) for e_code in [code])))
                for step_contributions in contributions_by_step
            ]
            mean_val = statistics.mean(steps) if steps else 0.0
            peak90_val = self._peak90(steps)
            close_val = statistics.mean(steps[-CLOSE_WINDOW:]) if len(steps) >= CLOSE_WINDOW else mean_val
            raw_day = max(-RAW_DAY_MAX, min(RAW_DAY_MAX,
                0.70 * mean_val + 0.20 * peak90_val + 0.10 * close_val))
            result[code] = CategoryAggregation(
                category_code=code,
                raw_steps=steps,
                mean=mean_val,
                peak90=peak90_val,
                close=close_val,
                raw_day=raw_day,
                power=max(abs(s) for s in steps) if steps else 0.0,
                volatility=statistics.stdev(steps) if len(steps) > 1 else 0.0,
            )
        return DayAggregation(categories=result)

    def _peak90(self, steps: list[float]) -> float:
        if len(steps) < PEAK90_WINDOW:
            return statistics.mean(steps) if steps else 0.0
        return max(
            statistics.mean(steps[i:i+PEAK90_WINDOW])
            for i in range(len(steps) - PEAK90_WINDOW + 1)
        )
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_aggregator.py`

| Test | Description |
|------|-------------|
| `test_raw_step_aggregates_all_events` | 3 événements au même pas → somme correcte |
| `test_raw_step_clamped` | Somme > 3.0 → clamped à 3.0 |
| `test_mean_correct` | Série simple → mean attendu |
| `test_peak90_identified` | Pic de 90min identifié dans une série avec creux |
| `test_close_uses_last_2h` | Close = moyenne des 8 derniers pas |
| `test_raw_day_formula_exact` | `0.70×Mean + 0.20×Peak90 + 0.10×Close` avec valeurs connues |
| `test_raw_day_clamped_max` | RawDay > 2.0 → clamped à 2.0 |
| `test_raw_day_clamped_min` | RawDay < -2.0 → clamped à -2.0 |
| `test_power_is_max_abs` | Power = max des abs(RawStep) |
| `test_volatility_nonzero_with_variance` | Série avec variance → Vol > 0 |
| `test_no_events_zero_scores` | Aucun événement → Power=0, Vol=0, RawDay≈0 |

---

## Nouveaux fichiers

- `backend/app/prediction/aggregator.py` ← CRÉER
- `backend/app/tests/unit/test_aggregator.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/contribution_calculator.py` — sortie `Contribution(e,c,t)` (34-2)
- `backend/app/prediction/temporal_sampler.py` — `DayGrid` (33-3)

---

## Checklist de validation

- [ ] `RawStep` agrège correctement toutes les contributions du pas
- [ ] `RawStep` borné dans `[-3, +3]`
- [ ] `Peak90` calculé sur fenêtre glissante de 6 pas (90 min)
- [ ] `Close` calculé sur les 8 derniers pas (2h)
- [ ] `RawDay` formule exacte `0.70/0.20/0.10`
- [ ] `RawDay` borné dans `[-2, +2]`
- [ ] `Power` et `Vol` calculés et non nuls quand il y a activité
- [ ] Tous les tests unitaires passent
