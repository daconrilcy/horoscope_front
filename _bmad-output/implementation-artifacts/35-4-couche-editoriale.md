# Story 35.4 : Préparation de la couche éditoriale dérivée

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `EditorialOutputBuilder` qui produit un objet `EditorialOutput` intégralement dérivé des scores et métriques du moteur,
so that la future couche de génération de texte (LLM) dispose d'un contrat d'interface clair sans que le moteur numérique rédige lui-même.

## Acceptance Criteria

### AC1 — Aucun texte libre LLM produit dans ce service

`EditorialOutputBuilder` ne fait aucun appel LLM, ne génère aucun texte libre, aucune chaîne rédigée en dur pour l'utilisateur.

### AC2 — `top3_categories` triées par note décroissante

Liste des 3 catégories avec les meilleures notes. Tiebreak sur `category.sort_order`.

### AC3 — `bottom2_categories` = les 2 notes les plus basses

### AC4 — `top3` et `bottom2` disjoints

Pas de code commun entre les deux listes.

### AC5 — `main_pivot` = `TurningPoint` avec `severity` la plus haute (ou `None`)

### AC6 — `best_window` = fenêtre de 90 min avec `peak90` max sur les top3

Contient `start_local`, `end_local`, `dominant_category`.

### AC7 — Flags prudence santé/argent

`caution_flags["sante"] = True` si note ≤ 7 ou volatilité ≥ 1.5.
`caution_flags["argent"] = True` idem.
Les codes concernés sont configurables via paramètres ruleset (`caution_category_codes`).

### AC8 — Ton global dérivé mécaniquement

- `"positive"` si moyenne top3 ≥ 13
- `"negative"` si ≤ 7
- `"mixed"` si écart max–min top3 ≥ 5
- `"neutral"` sinon

### AC9 — `top3_contributors_per_category` depuis explainability

Champs nécessaires aux templates présents. Depuis `ExplainabilityReport.categories`.

## Tasks / Subtasks

### T1 — `EditorialOutputBuilder` (AC1–AC9)

- [ ] Créer `backend/app/prediction/editorial_builder.py`
  - [ ] Dataclass `BestWindow(start_local: datetime, end_local: datetime, dominant_category: str)`
  - [ ] Dataclass `CategorySummary(code: str, note_20: int, power: float, volatility: float)`
  - [ ] Dataclass `EditorialOutput` (tous les champs AC2–AC9)
  - [ ] Constantes `CAUTION_NOTE_THRESHOLD = 7`, `CAUTION_VOL_THRESHOLD = 1.5`
  - [ ] Classe `EditorialOutputBuilder`
  - [ ] `build(engine_output: EngineOutput, explainability: ExplainabilityReport) -> EditorialOutput`
    - [ ] `_build_top3_bottom2(scores) -> tuple[list[CategorySummary], list[CategorySummary]]`
    - [ ] `_find_main_pivot(turning_points) -> TurningPoint | None`
    - [ ] `_find_best_window(time_blocks, top3) -> BestWindow | None`
    - [ ] `_compute_caution_flags(scores, params) -> dict[str, bool]`
    - [ ] `_derive_tone(top3) -> str`

### T2 — Tests unitaires (AC1–AC9)

- [ ] Créer `backend/app/tests/unit/test_editorial_builder.py`
  - [ ] `test_top3_sorted_desc` — top3 triés par note décroissante
  - [ ] `test_bottom2_lowest` — bottom2 = les deux notes les plus basses
  - [ ] `test_top3_bottom2_disjoint` — pas de code commun
  - [ ] `test_main_pivot_max_severity` — pivot principal = severity max
  - [ ] `test_no_pivot_none` — pas de pivot → `main_pivot=None`
  - [ ] `test_best_window_present` — bloc avec peak90 max → fenêtre retournée
  - [ ] `test_caution_sante_low_note` — santé note ≤ 7 → flagué
  - [ ] `test_caution_argent_high_vol` — argent vol ≥ 1.5 → flagué
  - [ ] `test_no_caution_above_threshold` — note > 7 et vol < 1.5 → pas de flag
  - [ ] `test_tone_positive` — top3 moyenne ≥ 13 → `"positive"`
  - [ ] `test_tone_negative` — top3 moyenne ≤ 7 → `"negative"`
  - [ ] `test_tone_mixed` — écart ≥ 5 → `"mixed"`
  - [ ] `test_no_llm_dependency` — aucun mock LLM requis dans les tests
  - [ ] `test_contributors_from_explainability` — `top3_contributors_per_category` provient de l'explainability

## Dev Notes

### `_build_top3_bottom2`

```python
def _build_top3_bottom2(self, scores: dict[str, Any]) -> tuple[list[CategorySummary], list[CategorySummary]]:
    sorted_scores = sorted(
        [(code, s) for code, s in scores.items()],
        key=lambda x: (-x[1].note_20, x[1].sort_order)
    )
    top3 = [CategorySummary(code=c, note_20=s.note_20, power=s.power, volatility=s.volatility)
            for c, s in sorted_scores[:3]]
    # bottom2 : les 2 derniers (par note croissante)
    bottom2_raw = sorted_scores[-2:]
    bottom2 = [CategorySummary(code=c, note_20=s.note_20, power=s.power, volatility=s.volatility)
               for c, s in bottom2_raw]
    # Garantir disjonction
    top3_codes = {c.code for c in top3}
    bottom2 = [c for c in bottom2 if c.code not in top3_codes]
    if len(bottom2) < 2:
        # Chercher le suivant non-top3
        for code, s in reversed(sorted_scores):
            if code not in top3_codes and not any(c.code == code for c in bottom2):
                bottom2.append(CategorySummary(code=code, note_20=s.note_20, power=s.power, volatility=s.volatility))
                if len(bottom2) == 2:
                    break
    return top3, bottom2
```

### `_derive_tone`

```python
def _derive_tone(self, top3: list[CategorySummary]) -> str:
    if not top3:
        return "neutral"
    notes = [c.note_20 for c in top3]
    avg = sum(notes) / len(notes)
    spread = max(notes) - min(notes)
    if avg >= 13:
        return "positive"
    if avg <= 7:
        return "negative"
    if spread >= 5:
        return "mixed"
    return "neutral"
```

### `_find_best_window` depuis `time_blocks`

Le `peak90` par bloc n'est pas directement dans `TimeBlock`. Le builder doit soit :
- Recevoir le `DayAggregation` en paramètre supplémentaire pour accéder aux `raw_steps`
- Ou utiliser les notes moyennes par bloc comme proxy

Choisir l'approche la plus simple : utiliser la note moyenne des catégories top3 sur le bloc comme proxy du `peak90`.

### Codes de catégories prudence

```python
DEFAULT_CAUTION_CODES = {"sante", "argent"}

def _compute_caution_flags(self, scores, params=None) -> dict[str, bool]:
    caution_codes = set(
        (params or {}).get("caution_category_codes", list(DEFAULT_CAUTION_CODES))
    )
    flags = {}
    for code in caution_codes:
        s = scores.get(code)
        if s and (s.note_20 <= CAUTION_NOTE_THRESHOLD or s.volatility >= CAUTION_VOL_THRESHOLD):
            flags[code] = True
        elif code in scores:
            flags[code] = False
    return flags
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/editorial_builder.py` | Créer |
| `backend/app/tests/unit/test_editorial_builder.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/explainability.py`
- `backend/app/prediction/persistence_service.py`
- Tout endpoint API ou service LLM existant

### Références

- [Source: backend/app/prediction/explainability.py — ExplainabilityReport (story 35-2)]
- [Source: backend/app/prediction/turning_point_detector.py — TurningPoint (story 34-5)]
- [Source: backend/app/prediction/block_generator.py — TimeBlock (story 34-5)]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
