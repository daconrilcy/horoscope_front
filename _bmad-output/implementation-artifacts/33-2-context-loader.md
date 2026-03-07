# Story 33.2 : Loader de contexte de prédiction

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `PredictionContextLoader` qui charge le référentiel complet (catégories, profils planètes, matrices, rulerships, aspects, event types, calibrations) depuis la DB dans un objet immuable,
so that le moteur dispose d'un contexte cohérent et validé dès le début du run, sans requêtes DB en cours d'exécution.

## Contexte métier

Le moteur a besoin d'un contexte de référence complet pour chaque run. Les repositories `PredictionReferenceRepository` et `PredictionRulesetRepository` (epic 31) exposent déjà toutes les données nécessaires. Cette story crée le service de chargement qui valide la cohérence des versions et signale si la calibration est provisoire.

## Acceptance Criteria

### AC1 — `LoadedPredictionContext` complet

`PredictionContextLoader.load(db, reference_version, ruleset_version)` retourne un `LoadedPredictionContext` contenant :
- `prediction_context: PredictionContext` — catégories, profils planètes, profils maisons, matrices, rulerships, points, aspect_profiles
- `ruleset_context: RulesetContext` — ruleset, paramètres, event types
- `calibrations: dict[str, CalibrationData | None]` — par `category_code`
- `is_provisional_calibration: bool`

### AC2 — Catégories appartenant à la bonne version

Les catégories chargées appartiennent strictement à la `reference_version` demandée (filtre par `reference_version_id`).

### AC3 — Composants requis manquants → `PredictionContextError`

Si l'un des éléments suivants est absent/vide, lever `PredictionContextError` avec message explicite :
- liste de catégories vide
- dict profils planètes vide
- dict profils maisons vide
- ruleset non trouvé pour `ruleset_version`
- paramètres du ruleset absents

### AC4 — Calibration provisoire tolérée

Si calibrations absentes ou partielles → `is_provisional_calibration = True`. Aucune exception levée, contexte retourné normalement.

### AC5 — Mismatch de version → `PredictionContextError`

Si la `reference_version_id` du ruleset chargé ne correspond pas à l'ID de la `reference_version` demandée → `PredictionContextError`.

## Tasks / Subtasks

### T1 — `PredictionContextLoader` (AC1, AC2, AC3, AC4, AC5)

- [x] Créer `backend/app/prediction/context_loader.py`
  - [x] Dataclass `LoadedPredictionContext` (fields: `prediction_context`, `ruleset_context`, `calibrations`, `is_provisional_calibration`)
  - [x] Classe `PredictionContextLoader`
  - [x] Méthode `load(db: Session, reference_version: str, ruleset_version: str) -> LoadedPredictionContext`
    - [x] Résoudre `reference_version_id` depuis la DB (table `reference_versions`)
    - [x] Appeler `PredictionReferenceRepository` pour charger toutes les matrices
    - [x] Appeler `PredictionRulesetRepository` pour charger ruleset + paramètres + event types
    - [x] Valider cohérence versions (AC5)
    - [x] Charger calibrations (peut être vide, AC4)
    - [x] Valider composants requis (AC3)
    - [x] Construire et retourner `LoadedPredictionContext`

### T2 — Tests unitaires avec mocks (AC1, AC3, AC4, AC5)

- [x] Créer `backend/app/tests/unit/test_context_loader.py`
  - [x] `test_load_complete_ok` — contexte complet sans erreur
  - [x] `test_missing_categories_raises` — catégories vides → `PredictionContextError`
  - [x] `test_missing_planet_profiles_raises` — profils planètes vides → `PredictionContextError`
  - [x] `test_missing_ruleset_raises` — version ruleset inconnue → `PredictionContextError`
  - [x] `test_missing_params_raises` — paramètres ruleset absents → `PredictionContextError`
  - [x] `test_version_mismatch_raises` — mismatch reference_version → `PredictionContextError`
  - [x] `test_missing_calibration_provisional` — calibrations vides → `is_provisional_calibration=True`, pas d'exception

## Dev Notes

### Repositories existants à utiliser

```python
# backend/app/infra/db/repositories/prediction_reference_repository.py
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository

# Méthodes disponibles (vérifier le fichier réel) :
ref_repo = PredictionReferenceRepository(db)
categories = ref_repo.get_categories(reference_version_id)
planet_profiles = ref_repo.get_planet_profiles(reference_version_id)
# ... etc.
```

```python
# backend/app/infra/db/repositories/prediction_ruleset_repository.py
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
ruleset_repo = PredictionRulesetRepository(db)
```

### Schémas existants à réutiliser

`PredictionContext`, `RulesetContext`, `CalibrationData` sont déjà définis dans `backend/app/infra/db/repositories/prediction_schemas.py`. Ne pas les redéfinir — importer directement.

### Résolution de `reference_version` (string → ID)

La table `reference_versions` est dans `backend/app/infra/db/models/reference.py`. Requête :
```python
from app.infra.db.models.reference import ReferenceVersionModel
rv = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == reference_version))
if rv is None:
    raise PredictionContextError(f"reference_version '{reference_version}' not found")
```

### Pattern mock pour les tests

```python
from unittest.mock import MagicMock, patch

def test_load_complete_ok():
    mock_db = MagicMock()
    mock_ref_repo = MagicMock()
    mock_ref_repo.get_categories.return_value = [MagicMock(code="amour", is_enabled=True)]
    # ... etc.
    with patch("app.prediction.context_loader.PredictionReferenceRepository", return_value=mock_ref_repo):
        loader = PredictionContextLoader()
        ctx = loader.load(mock_db, "V1", "V1")
        assert ctx.is_provisional_calibration is False
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/context_loader.py` | Créer |
| `backend/app/tests/unit/test_context_loader.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_ruleset_repository.py`

### Références

- [Source: backend/app/infra/db/repositories/prediction_schemas.py — PredictionContext, RulesetContext, CalibrationData]
- [Source: backend/app/infra/db/repositories/prediction_reference_repository.py — PredictionReferenceRepository]
- [Source: backend/app/infra/db/repositories/prediction_ruleset_repository.py — PredictionRulesetRepository]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Implementation of PredictionContextLoader with validation of version coherence (AC5).
- Handling of provisional calibrations (AC4).
- Unit tests with 100% coverage for success and error paths.

### Completion Notes List

- Service implemented in `backend/app/prediction/context_loader.py`.
- Tests implemented in `backend/app/tests/unit/test_context_loader.py`.
- Verified with ruff and pytest.

### File List

- backend/app/prediction/context_loader.py
- backend/app/tests/unit/test_context_loader.py
