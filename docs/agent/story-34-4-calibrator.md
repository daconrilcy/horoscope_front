# Story 34-4 — Calibrateur percentile → note 1–20

## Contexte & Périmètre

**Epic 34 / Story 34-4**
**Chapitre 34** — Scoring, notes et timeline UX

La note 1–20 est le signal final livré à l'utilisateur. Elle est obtenue en convertissant `RawDay(c)` via une interpolation piecewise linéaire sur 5 percentiles de référence. Cette calibration par catégorie assure que les notes sont stables, comparables dans le temps et correctement étalonnées sur la distribution réelle des scores.

---

## Hypothèses & Dépendances

- **Dépend de 34-3** : `DayAggregation` avec `raw_day` par catégorie disponible
- Les percentiles `P5, P25, P50, P75, P95` sont chargés via `LoadedPredictionContext.calibrations` (par catégorie)
- En mode provisoire (`is_provisional_calibration=True`), les percentiles peuvent être des valeurs par défaut synthétiques
- Politique P5 figée : note `1` si `raw_day ≤ P5`
- Politique P95 : note `20` si `raw_day ≥ P95`
- Les cibles d'interpolation sont : `P5→2`, `P25→6`, `P50→10`, `P75→14`, `P95→19`

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Implémenter `PercentileCalibrator.calibrate(raw_day, category_code, calibration)` → `int` (note 1–20)
- Interpolation piecewise linéaire sur les 4 segments `[P5–P25]`, `[P25–P50]`, `[P50–P75]`, `[P75–P95]`
- Saturation à `1` (sous P5) et `20` (au-dessus de P95)
- Mode provisoire : si calibration absente, utiliser des percentiles synthétiques par défaut

**Non-Objectifs :**
- Pas de recalcul des percentiles (ils viennent du contexte)
- Pas de persistance

---

## Acceptance Criteria

### AC1 — Interpolation piecewise linéaire
La fonction de calibration est définie par les points :
```
(P5,  note=2)
(P25, note=6)
(P50, note=10)
(P75, note=14)
(P95, note=19)
```
Entre deux points, l'interpolation est linéaire. Exemple : si `raw_day = P50 + (P75-P50)/2`, la note = `(10+14)/2 = 12`.

### AC2 — Saturation basse
Si `raw_day ≤ P5`, la note retournée est `1`.

### AC3 — Saturation haute
Si `raw_day ≥ P95`, la note retournée est `20`.

### AC4 — Note entière
La note est arrondie à l'entier le plus proche (`round()`). Toujours dans `[1, 20]`.

### AC5 — Calibration par catégorie
Chaque catégorie utilise ses propres percentiles. Deux catégories avec le même `raw_day` peuvent avoir des notes différentes si leurs distributions historiques diffèrent.

### AC6 — Mode provisoire fonctionnel
Si `CalibrationData` est `None` (calibration provisoire), le calibrateur utilise des percentiles synthétiques par défaut :
```python
DEFAULT_CALIBRATION = CalibrationData(p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5, sample_size=0)
```
Le calibrateur signale l'usage de la calibration provisoire via un flag ou un log.

### AC7 — Comportement stable
À entrée identique (même `raw_day`, mêmes percentiles), la note est toujours la même. Pas d'aléatoire.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── calibrator.py    ← PercentileCalibrator
```

### `calibrator.py` — extraits clés

```python
from app.infra.db.repositories.prediction_schemas import CalibrationData

PERCENTILE_TARGETS = [
    # (percentile_attr, note_cible)
    ("p05", 2),
    ("p25", 6),
    ("p50", 10),
    ("p75", 14),
    ("p95", 19),
]

DEFAULT_CALIBRATION = CalibrationData(
    p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5, sample_size=0
)

class PercentileCalibrator:
    def calibrate(
        self,
        raw_day: float,
        calibration: CalibrationData | None,
    ) -> int:
        if calibration is None:
            calibration = DEFAULT_CALIBRATION

        p5 = calibration.p05 or DEFAULT_CALIBRATION.p05
        p25 = calibration.p25 or DEFAULT_CALIBRATION.p25
        p50 = calibration.p50 or DEFAULT_CALIBRATION.p50
        p75 = calibration.p75 or DEFAULT_CALIBRATION.p75
        p95 = calibration.p95 or DEFAULT_CALIBRATION.p95

        if raw_day <= p5:
            return 1
        if raw_day >= p95:
            return 20

        # Interpolation piecewise linéaire
        segments = [
            (p5, 2, p25, 6),
            (p25, 6, p50, 10),
            (p50, 10, p75, 14),
            (p75, 14, p95, 19),
        ]
        for x0, y0, x1, y1 in segments:
            if x0 <= raw_day <= x1:
                t = (raw_day - x0) / (x1 - x0)
                raw_note = y0 + t * (y1 - y0)
                return max(1, min(20, round(raw_note)))

        return 10  # fallback (ne devrait jamais être atteint)
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_calibrator.py`

| Test | Description |
|------|-------------|
| `test_at_p5_returns_2` | `raw_day = P5` → note = 2 |
| `test_below_p5_returns_1` | `raw_day < P5` → note = 1 |
| `test_at_p95_returns_19` | `raw_day = P95` → note = 19 |
| `test_above_p95_returns_20` | `raw_day > P95` → note = 20 |
| `test_midpoint_p5_p25` | `raw_day = (P5+P25)/2` → note = 4 |
| `test_midpoint_p50_p75` | `raw_day = (P50+P75)/2` → note = 12 |
| `test_midpoint_p75_p95` | `raw_day = (P75+P95)/2` → note = 16 ou 17 (arrondi) |
| `test_interpolation_all_segments` | Test des 4 segments complets avec valeurs intermédiaires |
| `test_none_calibration_uses_default` | `calibration=None` → calibration par défaut, pas d'exception |
| `test_note_always_1_to_20` | Pour tout `raw_day ∈ [-3, +3]`, note ∈ `[1, 20]` |
| `test_deterministic` | Même input → même note (×10 appels) |

---

## Nouveaux fichiers

- `backend/app/prediction/calibrator.py` ← CRÉER
- `backend/app/tests/unit/test_calibrator.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/aggregator.py` — `DayAggregation` (34-3)
- `backend/app/infra/db/repositories/prediction_schemas.py` — `CalibrationData`
- `backend/app/prediction/context_loader.py` — `LoadedPredictionContext.calibrations`

---

## Checklist de validation

- [ ] Note `1` si `raw_day ≤ P5`
- [ ] Note `20` si `raw_day ≥ P95`
- [ ] Note `2` exactement à `P5`
- [ ] Note `19` exactement à `P95`
- [ ] Interpolation correcte sur les 4 segments
- [ ] Note toujours entière dans `[1, 20]`
- [ ] Calibration `None` → calibration par défaut sans exception
- [ ] Déterminisme : même input → même note
- [ ] Tous les tests unitaires passent
