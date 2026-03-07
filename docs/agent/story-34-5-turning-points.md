# Story 34-5 — Détecteur de points de bascule + générateur de blocs UX

## Contexte & Périmètre

**Epic 34 / Story 34-5**
**Chapitre 34** — Scoring, notes et timeline UX

Les points de bascule (pivots) et les blocs horaires sont la couche UX du moteur : ils structurent la journée en fenêtres lisibles pour l'utilisateur. Un pivot marque un changement significatif dans le signal (note, composition des top catégories, événement fort). Les blocs sont des fenêtres d'1 heure découpées de manière adaptative autour des pivots.

---

## Hypothèses & Dépendances

- **Dépend de 34-4** : notes 1–20 par catégorie et par pas de temps calculées (via calibration de `RawStep`)
- Les événements détectés (33-5) sont disponibles avec leur priorité
- `DayAggregation.raw_steps` contient le signal brut par pas, par catégorie
- La grille temporelle (`DayGrid`) est disponible pour le mapping pas → heure locale
- Les règles de pivot sont figées : `ΔNote ≥ 2`, ou top 3 change, ou événement priorité ≥ 65

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Détecter les pivots selon les 3 règles V1
- Construire les blocs d'1 heure, découpés autour des pivots
- Enrichir chaque pivot (heure locale, raison, catégories impactées, événement responsable)
- Enrichir chaque bloc (catégories dominantes, ton, drivers principaux)

**Non-Objectifs :**
- Pas de texte libre LLM dans ce service
- Pas de persistance (c'est 35-1)

---

## Acceptance Criteria

### AC1 — Règle pivot 1 : `ΔNote ≥ 2`
Un pivot est créé si la note d'une catégorie varie de ≥ 2 points entre deux pas consécutifs de 15 min (comparaison note calibrée du pas `t` vs `t-1`).

### AC2 — Règle pivot 2 : changement top 3
Un pivot est créé si la composition des 3 catégories ayant les meilleures notes change entre deux pas consécutifs.

### AC3 — Règle pivot 3 : événement priorité ≥ 65
Un pivot est créé si un événement `AstroEvent.priority ≥ 65` est associé au pas courant.

### AC4 — Structure d'un pivot
Chaque `TurningPoint` contient :
- `local_time` : heure locale du pivot (début du pas déclencheur)
- `reason` : `"delta_note"` | `"top3_change"` | `"high_priority_event"`
- `categories_impacted` : list[str] (codes des catégories concernées)
- `trigger_event` : `AstroEvent | None` (événement responsable pour règle 3)
- `severity` : float (`ΔNote` pour règle 1, ou priorité normalisée pour règle 3)

### AC5 — Blocs standard d'1 heure
En l'absence de pivot, les blocs sont des fenêtres de 4 pas (1h) couvrant toute la journée. Une journée de 96 pas produit 24 blocs standard.

### AC6 — Blocs adaptatifs autour des pivots
Quand un pivot tombe dans un bloc, ce bloc est découpé en deux blocs plus courts (avant et après le pivot). La durée minimale d'un bloc est de 15 min (1 pas).

### AC7 — Structure d'un bloc
Chaque `TimeBlock` contient :
- `block_index` : int (ordre chronologique, 0-indexé)
- `start_local` : `datetime` (heure locale de début)
- `end_local` : `datetime` (heure locale de fin)
- `dominant_categories` : list[str] (top 3 catégories par note sur ce bloc)
- `tone_code` : str (`"positive"` | `"negative"` | `"mixed"` | `"neutral"`)
- `driver_events` : list[`AstroEvent`] (top 3 événements contributeurs du bloc)

### AC8 — Ton du bloc dérivé des scores
Le `tone_code` est dérivé mécaniquement des notes du bloc :
- `positive` si la note moyenne des catégories top 3 ≥ 13
- `negative` si ≤ 7
- `mixed` si l'écart entre la meilleure et la pire note top 3 ≥ 5
- `neutral` sinon

### AC9 — Traçabilité driver → bloc
Chaque `driver_event` d'un bloc doit être retrouvable dans la liste des `AstroEvent` détectés (33-5). Les drivers sont les événements avec le plus fort `abs(Contribution)` moyen sur la fenêtre du bloc.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
├── turning_point_detector.py    ← TurningPointDetector, TurningPoint
└── block_generator.py           ← BlockGenerator, TimeBlock
```

### `turning_point_detector.py` — extraits clés

```python
from dataclasses import dataclass
from datetime import datetime
from app.prediction.schemas import AstroEvent

PRIORITY_PIVOT_THRESHOLD = 65

@dataclass
class TurningPoint:
    local_time: datetime
    reason: str   # "delta_note" | "top3_change" | "high_priority_event"
    categories_impacted: list[str]
    trigger_event: AstroEvent | None
    severity: float

class TurningPointDetector:
    def detect(
        self,
        notes_by_step: list[dict[str, int]],   # [pas → {cat_code: note}]
        events_by_step: list[list[AstroEvent]], # [pas → [événements]]
        step_times: list[datetime],             # [pas → heure locale]
    ) -> list[TurningPoint]:
        pivots = []
        for t in range(1, len(notes_by_step)):
            prev = notes_by_step[t - 1]
            curr = notes_by_step[t]
            # Règle 1 : ΔNote ≥ 2
            for cat_code, note in curr.items():
                if abs(note - prev.get(cat_code, note)) >= 2:
                    pivots.append(TurningPoint(
                        local_time=step_times[t],
                        reason="delta_note",
                        categories_impacted=[cat_code],
                        trigger_event=None,
                        severity=abs(note - prev.get(cat_code, note)),
                    ))
            # Règle 2 : top3 change
            ...
            # Règle 3 : high priority event
            for event in events_by_step[t]:
                if event.priority >= PRIORITY_PIVOT_THRESHOLD:
                    pivots.append(TurningPoint(...))
        return pivots
```

### `block_generator.py` — extraits clés

```python
@dataclass
class TimeBlock:
    block_index: int
    start_local: datetime
    end_local: datetime
    dominant_categories: list[str]
    tone_code: str
    driver_events: list[AstroEvent]

class BlockGenerator:
    BLOCK_SIZE_STEPS = 4  # 4 × 15min = 1h

    def generate(
        self,
        pivots: list[TurningPoint],
        notes_by_step: list[dict[str, int]],
        events_by_step: list[list[AstroEvent]],
        step_times: list[datetime],
        contributions_by_step: list[dict[str, float]],
    ) -> list[TimeBlock]:
        ...
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_turning_points.py`

| Test | Description |
|------|-------------|
| `test_pivot_on_exact_high_priority` | Événement avec priorité 70 → pivot `high_priority_event` |
| `test_pivot_on_delta_note_2` | Note passe de 8 à 10 → pivot `delta_note` (ΔNote=2) |
| `test_pivot_on_delta_note_1_no_pivot` | Note passe de 8 à 9 → aucun pivot |
| `test_pivot_on_top3_change` | Top 3 change entre deux pas → pivot `top3_change` |
| `test_standard_blocks_24_without_pivot` | Journée sans pivot → 24 blocs d'1h |
| `test_adaptive_split_around_pivot` | Pivot en milieu de bloc → 2 sous-blocs |
| `test_block_min_size_1_step` | Bloc après split ≥ 1 pas (15 min) |
| `test_tone_positive_high_notes` | Top 3 note moyenne ≥ 13 → tone `positive` |
| `test_tone_negative_low_notes` | Top 3 note moyenne ≤ 7 → tone `negative` |
| `test_driver_traceable` | Drivers du bloc retrouvables dans la liste des événements détectés |
| `test_pivot_reason_stored` | Chaque pivot a `reason` et `categories_impacted` renseignés |

---

## Nouveaux fichiers

- `backend/app/prediction/turning_point_detector.py` ← CRÉER
- `backend/app/prediction/block_generator.py` ← CRÉER
- `backend/app/tests/unit/test_turning_points.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `AstroEvent` (33-1)
- `backend/app/prediction/aggregator.py` — `DayAggregation` (34-3)
- `backend/app/prediction/calibrator.py` — notes 1–20 (34-4)
- `backend/app/infra/db/models/daily_prediction.py` — `DailyPredictionTurningPointModel`, `DailyPredictionTimeBlockModel`

---

## Checklist de validation

- [ ] Pivot sur `ΔNote ≥ 2` (mais pas sur `ΔNote = 1`)
- [ ] Pivot sur changement du top 3 catégories
- [ ] Pivot sur événement priorité ≥ 65
- [ ] Blocs standard d'1h sans pivot → 24 blocs sur journée de 96 pas
- [ ] Découpage adaptatif autour d'un pivot → sous-blocs cohérents
- [ ] Ton du bloc dérivé mécaniquement des notes (pas de texte libre)
- [ ] Drivers traçables vers événements détectés
- [ ] Tous les tests unitaires passent
