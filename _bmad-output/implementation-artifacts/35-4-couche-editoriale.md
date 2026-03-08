# Story 35.4 : Préparation de la couche éditoriale dérivée

Status: done

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

- [x] Créer `backend/app/prediction/editorial_builder.py`
  - [x] Dataclass `BestWindow(start_local: datetime, end_local: datetime, dominant_category: str)`
  - [x] Dataclass `CategorySummary(code: str, note_20: int, power: float, volatility: float)`
  - [x] Dataclass `EditorialOutput` (tous les champs AC2–AC9)
  - [x] Constantes `CAUTION_NOTE_THRESHOLD = 7`, `CAUTION_VOL_THRESHOLD = 1.5`
  - [x] Classe `EditorialOutputBuilder`
  - [x] `build(engine_output: EngineOutput, explainability: ExplainabilityReport) -> EditorialOutput`
    - [x] `_build_top3_bottom2(scores) -> tuple[list[CategorySummary], list[CategorySummary]]`
    - [x] `_find_main_pivot(turning_points) -> TurningPoint | None`
    - [x] `_find_best_window(time_blocks, top3) -> BestWindow | None`
    - [x] `_compute_caution_flags(scores, params) -> dict[str, bool]`
    - [x] `_derive_tone(top3) -> str`

### T2 — Tests unitaires (AC1–AC9)

- [x] Créer `backend/app/tests/unit/test_editorial_builder.py`
  - [x] `test_top3_sorted_desc` — top3 triés par note décroissante
  - [x] `test_bottom2_lowest` — bottom2 = les deux notes les plus basses
  - [x] `test_top3_bottom2_disjoint` — pas de code commun
  - [x] `test_main_pivot_max_severity` — pivot principal = severity max
  - [x] `test_no_pivot_none` — pas de pivot → `main_pivot=None`
  - [x] `test_best_window_present` — bloc avec peak90 max → fenêtre retournée
  - [x] `test_caution_sante_low_note` — santé note ≤ 7 → flagué
  - [x] `test_caution_argent_high_vol` — argent vol ≥ 1.5 → flagué
  - [x] `test_no_caution_above_threshold` — note > 7 et vol < 1.5 → pas de flag
  - [x] `test_tone_positive` — top3 moyenne ≥ 13 → `"positive"`
  - [x] `test_tone_negative` — top3 moyenne ≤ 7 → `"negative"`
  - [x] `test_tone_mixed` — écart ≥ 5 → `"mixed"`
  - [x] `test_no_llm_dependency` — aucun mock LLM requis dans les tests
  - [x] `test_contributors_from_explainability` — `top3_contributors_per_category` provient de l'explainability

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

- Implemented `EditorialOutputBuilder` to derive editorial data from engine scores and metrics.
- Added `EditorialOutput` and related dataclasses in `backend/app/prediction/editorial_builder.py`.
- Integrated `EditorialOutputBuilder` into `EngineOrchestrator.run()`.
- Updated `EngineOutput` in `backend/app/prediction/schemas.py` to include the `editorial` field.
- Created comprehensive unit tests in `backend/app/tests/unit/test_editorial_builder.py` covering all ACs.
- Ensured no LLM dependencies were introduced as per AC1.
- Post-review validation: full-day regression snapshots were refreshed so the editorial contract is now locked in non-regression tests.
- Post-release stabilization: local SQLite startup now auto-upgrades missing auth/schema tables in dev, and the chapter-35 migration path no longer breaks login/register on partially drifted local DBs.
- Post-release validation: real local smoke `POST /v1/auth/register` and `POST /v1/auth/login` both return `200` after migration to `20260308_0037`.
- Validation finale exécutée dans le venv sur la suite ciblée chapitre 35 puis sur toute la suite backend sans régression.

### File List

- `backend/app/prediction/editorial_builder.py`
- `backend/app/tests/unit/test_editorial_builder.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/infra/db/bootstrap.py`
- `backend/app/tests/unit/test_db_bootstrap.py`
- `backend/app/tests/integration/test_db_bootstrap.py`
- `backend/app/tests/integration/test_auth_api.py`

## Change Log

- 2026-03-08: Implementation of editorial layer (Story 35.4).
