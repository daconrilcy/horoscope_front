# Story 34.5 : Détecteur de points de bascule + générateur de blocs UX

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want des services `TurningPointDetector` et `BlockGenerator` qui structurent la journée en pivots et blocs horaires lisibles,
so that la couche de persistance (story 35-1) et la future interface utilisateur disposent d'une timeline enrichie et traçable.

## Acceptance Criteria

### AC1 — Pivot règle 1 : `ΔNote ≥ 2`

Créé si une catégorie varie d'au moins 2 points entre deux pas consécutifs (notes calibrées).

### AC2 — Pivot règle 2 : changement top 3

Créé si la composition des 3 catégories ayant les meilleures notes change entre deux pas.

### AC3 — Pivot règle 3 : événement priorité ≥ 65

Créé si un `AstroEvent.priority ≥ 65` est associé au pas courant.

### AC4 — Structure `TurningPoint`

Chaque pivot contient : `local_time`, `reason` (`"delta_note"` | `"top3_change"` | `"high_priority_event"`), `categories_impacted: list[str]`, `trigger_event: AstroEvent | None`, `severity: float`.

### AC5 — Blocs standard d'1h (4 pas de 15 min)

Sans pivot : 24 blocs sur 96 pas. Chaque bloc contient `block_index`, `start_local`, `end_local`.

### AC6 — Blocs adaptatifs autour des pivots

Un pivot découpe le bloc courant en deux sous-blocs. Durée minimale : 1 pas (15 min).

### AC7 — Structure `TimeBlock`

Chaque bloc contient : `block_index`, `start_local`, `end_local`, `dominant_categories: list[str]` (top 3 sur le bloc), `tone_code: str`, `driver_events: list[AstroEvent]` (top 3 contributeurs).

### AC8 — Ton dérivé mécaniquement

- `"positive"` si note moyenne top 3 du bloc ≥ 13
- `"negative"` si ≤ 7
- `"mixed"` si écart entre meilleure et pire note top 3 ≥ 5
- `"neutral"` sinon

### AC9 — Traçabilité driver → bloc

Les `driver_events` d'un bloc sont les `AstroEvent` avec le plus fort `abs(contribution)` moyen sur la fenêtre du bloc.

## Tasks / Subtasks

### T1 — `TurningPointDetector` (AC1–AC4)

- [ ] Créer `backend/app/prediction/turning_point_detector.py`
  - [ ] Dataclass `TurningPoint` (fields: `local_time`, `reason`, `categories_impacted`, `trigger_event`, `severity`)
  - [ ] Constante `PRIORITY_PIVOT_THRESHOLD = 65`
  - [ ] Classe `TurningPointDetector`
  - [ ] `detect(notes_by_step, events_by_step, step_times) -> list[TurningPoint]`
    - [ ] Règle 1 : boucle sur pas t, comparer notes[t] vs notes[t-1], ΔNote ≥ 2
    - [ ] Règle 2 : calculer top3(notes[t]) vs top3(notes[t-1]), détecter changement
    - [ ] Règle 3 : vérifier `event.priority ≥ 65` pour chaque événement du pas
    - [ ] Éviter les doublons (un seul pivot par pas même si plusieurs règles déclenchent)

### T2 — `BlockGenerator` (AC5–AC9)

- [ ] Créer `backend/app/prediction/block_generator.py`
  - [ ] Dataclass `TimeBlock`
  - [ ] Classe `BlockGenerator`
  - [ ] `generate(pivots, notes_by_step, events_by_step, step_times, contributions_by_step) -> list[TimeBlock]`
    - [ ] Construire les frontières de blocs : découpage régulier 4 pas, puis adapter autour des pivots
    - [ ] Pour chaque bloc : calculer `dominant_categories`, `tone_code`, `driver_events`
    - [ ] `_dominant_categories(notes_slice) -> list[str]` — top 3 catégories par note
    - [ ] `_tone_code(notes_slice) -> str` — règles AC8
    - [ ] `_driver_events(events_slice, contribs_slice) -> list[AstroEvent]` — top 3 par abs(contrib)

### T3 — Tests unitaires (AC1–AC9)

- [ ] Créer `backend/app/tests/unit/test_turning_points.py`
  - [ ] `test_pivot_delta_note_2` — ΔNote=2 → pivot `delta_note`
  - [ ] `test_no_pivot_delta_note_1` — ΔNote=1 → aucun pivot
  - [ ] `test_pivot_top3_change` — top3 change → pivot `top3_change`
  - [ ] `test_pivot_high_priority` — événement priorité 70 → pivot `high_priority_event`
  - [ ] `test_24_blocks_no_pivot` — 96 pas sans pivot → 24 blocs
  - [ ] `test_adaptive_split` — pivot en milieu de bloc → 2 sous-blocs
  - [ ] `test_min_block_1_step` — sous-bloc minimum = 1 pas
  - [ ] `test_tone_positive` — notes top3 moyenne ≥ 13 → `"positive"`
  - [ ] `test_tone_negative` — notes top3 moyenne ≤ 7 → `"negative"`
  - [ ] `test_driver_traceable` — drivers retrouvables dans la liste des événements

## Dev Notes

### `top3` helper

```python
def _top3_codes(notes: dict[str, int]) -> frozenset[str]:
    sorted_cats = sorted(notes.items(), key=lambda x: -x[1])
    return frozenset(c for c, _ in sorted_cats[:3])
```

### Fusion de doublons de pivots

Si plusieurs règles déclenchent sur le même pas : créer un seul `TurningPoint` avec `reason` de la règle la plus sévère (ordre : `high_priority_event` > `delta_note` > `top3_change`). Mettre tous les `categories_impacted` dans la liste.

### Découpage adaptatif des blocs

```
Pas standard : [0–3], [4–7], ..., [92–95]  → 24 blocs
Pivot au pas 5 → découp [4, 5) et [5, 7]   → blocs de taille 1 et 3
```

L'index `block_index` est séquentiel dans l'ordre chronologique.

### Modèles DB existants pour référence

Les structures `TurningPoint` et `TimeBlock` correspondent à `DailyPredictionTurningPointModel` et `DailyPredictionTimeBlockModel` dans `backend/app/infra/db/models/daily_prediction.py`. Les dataclasses Python ici sont les objets en mémoire avant persistance.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/turning_point_detector.py` | Créer |
| `backend/app/prediction/block_generator.py` | Créer |
| `backend/app/tests/unit/test_turning_points.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/prediction/aggregator.py`
- `backend/app/prediction/calibrator.py`

### Références

- [Source: backend/app/infra/db/models/daily_prediction.py — DailyPredictionTurningPointModel, DailyPredictionTimeBlockModel]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
