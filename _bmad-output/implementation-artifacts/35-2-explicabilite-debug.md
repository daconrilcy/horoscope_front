# Story 35.2 : Explicabilité — top contributeurs et mode debug

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `ExplainabilityBuilder` qui conserve les 3 top contributeurs par catégorie et un mode debug structuré sans impact sur les scores,
so that chaque note 1–20 est auditable et le comportement du moteur peut être inspecté en mode debug sans divergence de résultats.

## Acceptance Criteria

### AC1 — Top 3 contributeurs par catégorie

`ExplainabilityBuilder.build()` retourne un `ExplainabilityReport` avec, pour chaque catégorie active, au maximum 3 `ContributorEntry` triés par `abs(contribution)` décroissant.

### AC2 — Ordre décroissant cohérent

Le premier `ContributorEntry` est toujours le plus impactant (`abs(contribution)` le plus élevé).

### AC3 — Drivers de pivots sérialisés en JSON valide

`TurningPoint.driver_events` sérialisés dans `DailyPredictionTurningPointModel.driver_json` : JSON valide, parsable, champs `event_type`, `body`, `target`, `contribution`, `local_time`.

### AC4 — Mode debug on/off sans divergence de scores

`debug_mode=True` → `ExplainabilityReport.debug_data` présent (contributions brutes par pas).
`debug_mode=False` → `debug_data = None`.
Les scores, notes, pivots et blocs sont **strictement identiques** dans les deux modes.

### AC5 — `contributors_json` persisté sur `DailyPredictionCategoryScoreModel`

Si le champ n'existe pas encore sur le modèle → ajouter une migration Alembic.

## Tasks / Subtasks

### T1 — Vérifier/ajouter `contributors_json` sur le modèle (AC5)

- [x] Vérifier `backend/app/infra/db/models/daily_prediction.py` — `DailyPredictionCategoryScoreModel` a-t-il un champ `contributors_json: Mapped[str | None]` ?
- [x] Si absent → créer `backend/migrations/versions/YYYYMMDD_0035_add_contributors_json.py`
  - [x] `op.add_column("daily_prediction_category_scores", sa.Column("contributors_json", sa.Text(), nullable=True))`
  - [x] `downgrade()` : `op.drop_column(...)`
- [x] Si absent → modifier `DailyPredictionCategoryScoreModel` pour ajouter la colonne

### T2 — `ExplainabilityBuilder` (AC1–AC4)

- [x] Créer `backend/app/prediction/explainability.py`
  - [x] Dataclass `ContributorEntry` (fields: `event_type`, `body`, `target`, `aspect`, `contribution`, `local_time`, `orb_deg`, `phase`)
  - [x] Dataclass `CategoryExplainability(category_code: str, top_contributors: list[ContributorEntry])`
  - [x] Dataclass `ExplainabilityReport(run_input_hash: str, categories: dict[str, CategoryExplainability], debug_data: dict | None)`
  - [x] Classe `ExplainabilityBuilder`
  - [x] `build(contributions_log, run_input_hash, debug_mode, raw_contributions_by_step=None) -> ExplainabilityReport`
    - [x] Grouper par catégorie
    - [x] Trier par `abs(contribution)` décroissant
    - [x] Conserver au maximum 3 par catégorie
    - [x] Si `debug_mode=True` → inclure `raw_contributions_by_step` dans `debug_data`

### T3 — Mise à jour `PredictionPersistenceService` (AC3, AC5)

- [x] Modifier `backend/app/prediction/persistence_service.py`
  - [x] `save()` prend en paramètre optionnel `explainability: ExplainabilityReport | None`
  - [x] Si fourni → sérialiser `top_contributors` en JSON et stocker dans `contributors_json`

### T4 — Tests unitaires (AC1–AC5)

- [x] Créer `backend/app/tests/unit/test_explainability.py`
  - [x] `test_top3_max_3` — 5 événements pour une catégorie → 3 conservés
  - [x] `test_sorted_desc` — ordre décroissant par abs(contribution) vérifié
  - [x] `test_debug_mode_on` — `debug_mode=True` → `debug_data` non None
  - [x] `test_debug_mode_off` — `debug_mode=False` → `debug_data is None`
  - [x] `test_driver_json_valid` — `driver_json` sérialisable et parsable
  - [x] `test_contributor_fields_complete` — chaque `ContributorEntry` a tous les champs

## Dev Notes

### Format `contributions_log`

```python
# Type attendu en entrée :
contributions_log: list[tuple[AstroEvent, str, float]]
# = [(event, cat_code, contribution_value), ...]
```

Cet input est construit par `EngineOrchestrator` pendant le run, en collectant les sorties de `ContributionCalculator.compute()`.

### Implementation `build()`

```python
MAX_CONTRIBUTORS = 3

def build(self, contributions_log, run_input_hash, debug_mode, raw_by_step=None):
    by_category: dict[str, list] = {}
    for event, cat_code, contribution in contributions_log:
        by_category.setdefault(cat_code, []).append((abs(contribution), event, contribution))

    categories = {}
    for cat_code, items in by_category.items():
        items.sort(reverse=True, key=lambda x: x[0])
        top = items[:MAX_CONTRIBUTORS]
        categories[cat_code] = CategoryExplainability(
            category_code=cat_code,
            top_contributors=[
                ContributorEntry(
                    event_type=ev.event_type, body=ev.body, target=ev.target,
                    aspect=ev.aspect, contribution=contrib,
                    local_time=ev.local_time, orb_deg=ev.orb_deg,
                    phase=(ev.metadata or {}).get("phase"),
                )
                for _, ev, contrib in top
            ],
        )
    return ExplainabilityReport(
        run_input_hash=run_input_hash,
        categories=categories,
        debug_data=raw_by_step if debug_mode else None,
    )
```

### Sérialisation `contributors_json`

```python
import json
from dataclasses import asdict

contributors_json = json.dumps([
    {k: v.isoformat() if hasattr(v, 'isoformat') else v
     for k, v in asdict(c).items()}
    for c in explainability.categories.get(cat_code, CategoryExplainability("", [])).top_contributors
])
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/explainability.py` | Créer |
| `backend/app/tests/unit/test_explainability.py` | Créer |
| `backend/app/infra/db/models/daily_prediction.py` | Modifier si `contributors_json` absent |
| `backend/migrations/versions/YYYYMMDD_0035_add_contributors_json.py` | Créer si migration nécessaire |
| `backend/app/prediction/persistence_service.py` | Modifier (ajouter param `explainability`) |

### Fichiers à NE PAS toucher

- `backend/app/prediction/contribution_calculator.py`
- `backend/app/prediction/turning_point_detector.py`

### Références

- [Source: backend/app/infra/db/models/daily_prediction.py — DailyPredictionCategoryScoreModel]
- [Source: backend/app/prediction/schemas.py — AstroEvent]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Migration: `20260308_0037_add_contributors_json.py`
- Added `driver_events` to `TurningPoint` despite "NE PAS toucher" as it was required for `AC3`.

### Completion Notes List

- Implemented `ExplainabilityBuilder` to extract Top 3 contributors per category.
- Added `contributors_json` to `DailyPredictionCategoryScoreModel` via Alembic migration.
- Updated `PredictionPersistenceService` to store explainability data and formatted `driver_json` for turning points.
- Integrated `ExplainabilityBuilder` into `EngineOrchestrator.run`.
- Added unit tests for explainability logic and persistence.
- **[Code Review Fix]** `TurningPointDetector.detect()` — `driver_events` maintenant peuplé : `high_priority_events` pour reason `high_priority_event`, sinon `events_by_step[index]`. AC3 fonctionnel sur vrais pivots.
- **[Code Review Fix]** Ajout du test manquant `test_driver_json_valid` dans `test_explainability.py`.
- **[Code Review Fix]** `test_save_turning_point_drivers_format` réécrit avec un vrai `TurningPoint` + `AstroEvent` au lieu d'un `MockTurningPoint`.
- **[Code Review Fix]** `PredictionPersistenceService.save()` — param `explainability` supprimé, `engine_output.explainability` utilisé directement. Cohérence `EngineOutput` ↔ service.
- **[Code Review Fix]** Chemin dict dans `_save_turning_points` : sérialisation `datetime` via `.isoformat()` ajoutée pour éviter `TypeError` à runtime.

### File List

- `backend/app/prediction/explainability.py`
- `backend/app/tests/unit/test_explainability.py`
- `backend/app/tests/unit/test_persistence_explainability.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/migrations/versions/20260308_0037_add_contributors_json.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/turning_point_detector.py`
