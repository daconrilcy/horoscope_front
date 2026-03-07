# Story 33-2 — Loader de contexte de prédiction

## Contexte & Périmètre

**Epic 33 / Story 33-2**
**Chapitre 33** — Fondations du moteur de calcul quotidien

Le moteur de calcul a besoin d'un contexte de référence complet et immuable pour chaque run : catégories, profils planètes, profils maisons, matrices de poids, rulerships, profils d'aspects, types d'événements, paramètres et calibrations. Cette story crée le service `PredictionContextLoader` qui charge tout ce référentiel depuis les repositories DB existants et le rend disponible sous la forme d'un objet immutable exploitable par le moteur.

---

## Hypothèses & Dépendances

- **Dépend de 33-1** : le module `backend/app/prediction/` existe, les schémas `EngineInput`, `EngineOutput` sont définis
- `PredictionReferenceRepository` est stable et opérationnel (`backend/app/infra/db/repositories/prediction_reference_repository.py`)
- `PredictionRulesetRepository` est stable et opérationnel (`backend/app/infra/db/repositories/prediction_ruleset_repository.py`)
- Les structures de données `PredictionContext` et `RulesetContext` existent dans `backend/app/infra/db/repositories/prediction_schemas.py` et sont réutilisées telles quelles ou étendues légèrement
- Une calibration absente est tolérée en mode provisoire (le contexte le signale)
- Les données de référence sont immuables une fois chargées pour un run donné

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Créer `PredictionContextLoader` : service qui accepte `(db, reference_version, ruleset_version)` et retourne un contexte complet chargé
- Valider la cohérence du contexte au chargement (versions, composants requis)
- Signaler clairement si les calibrations sont absentes (mode provisoire)
- Rendre le contexte chargé accessible au moteur via `EngineOrchestrator`

**Non-Objectifs :**
- Pas de cache distribué ou Redis dans cette story
- Pas de lazy loading — tout est chargé d'un coup
- Pas de migration DB

---

## Acceptance Criteria

### AC1 — Chargement complet
`PredictionContextLoader.load(db, reference_version, ruleset_version)` retourne un objet `LoadedPredictionContext` contenant :
- `prediction_context` : `PredictionContext` (catégories, profils, matrices, rulerships, points)
- `ruleset_context` : `RulesetContext` (ruleset, paramètres, event types)
- `calibrations` : dict `category_code → CalibrationData | None`
- `is_provisional_calibration` : bool (True si au moins une calibration est absente)

### AC2 — Cohérence des versions
Les catégories chargées appartiennent strictement à la `reference_version` demandée. Si les catégories de la `reference_version` et les profils planètes ne correspondent pas, le loader échoue avec une erreur explicite.

### AC3 — Composants requis
Si l'un des composants suivants est absent, le loader lève une exception nommée `PredictionContextError` avec un message clair :
- catégories (liste vide)
- profils planètes (dict vide)
- profils maisons (dict vide)
- ruleset introuvable pour `ruleset_version`
- paramètres du ruleset absents

### AC4 — Calibration provisoire tolérée
Si les calibrations sont absentes ou partielles, `is_provisional_calibration = True` et le contexte est retourné normalement. Aucune exception n'est levée.

### AC5 — Immutabilité fonctionnelle
Le `LoadedPredictionContext` ne doit pas être modifié après construction. Utiliser `@dataclass(frozen=True)` ou équivalent pour les objets critiques.

### AC6 — Mismatch de version → échec explicite
Si la `reference_version` demandée ne correspond pas à la `reference_version_id` du ruleset chargé, le loader lève `PredictionContextError`.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
├── context_loader.py    ← PredictionContextLoader, LoadedPredictionContext
└── exceptions.py        ← PredictionContextError, PredictionEngineError
```

### `context_loader.py` — extraits clés

```python
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
from app.infra.db.repositories.prediction_schemas import (
    PredictionContext, RulesetContext, CalibrationData
)

@dataclass
class LoadedPredictionContext:
    prediction_context: PredictionContext
    ruleset_context: RulesetContext
    calibrations: dict[str, CalibrationData | None]
    is_provisional_calibration: bool

class PredictionContextLoader:
    def load(
        self,
        db: Session,
        reference_version: str,
        ruleset_version: str,
    ) -> LoadedPredictionContext:
        ref_repo = PredictionReferenceRepository(db)
        ruleset_repo = PredictionRulesetRepository(db)
        # Charger la reference_version → obtenir son id
        # Charger toutes les matrices via ref_repo
        # Charger ruleset + paramètres + event types via ruleset_repo
        # Valider cohérence des versions
        # Charger calibrations (peut être vide)
        # Construire et retourner LoadedPredictionContext
        ...
```

### Intégration dans `EngineOrchestrator`

```python
# Dans engine_orchestrator.py
from app.prediction.context_loader import PredictionContextLoader

class EngineOrchestrator:
    def run(self, engine_input: EngineInput, db: Session) -> EngineOutput:
        loader = PredictionContextLoader()
        ctx = loader.load(db, engine_input.reference_version, engine_input.ruleset_version)
        ...
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_context_loader.py`

| Test | Description |
|------|-------------|
| `test_load_complete_context_ok` | Contexte complet chargé sans erreur, tous les champs présents |
| `test_load_missing_categories_raises` | Catégories vides → `PredictionContextError` |
| `test_load_missing_planet_profiles_raises` | Profils planètes vides → `PredictionContextError` |
| `test_load_missing_ruleset_raises` | Version ruleset inconnue → `PredictionContextError` |
| `test_load_missing_ruleset_params_raises` | Paramètres ruleset absents → `PredictionContextError` |
| `test_version_mismatch_raises` | `reference_version` du ruleset ≠ celle demandée → `PredictionContextError` |
| `test_missing_calibration_provisional` | Calibrations absentes → `is_provisional_calibration=True`, pas d'exception |
| `test_categories_belong_to_correct_version` | Seules les catégories de la bonne version sont retournées |

Ces tests utilisent des mocks des repositories (pas de DB réelle requise).

---

## Nouveaux fichiers

- `backend/app/prediction/context_loader.py` ← CRÉER
- `backend/app/prediction/exceptions.py` ← CRÉER
- `backend/app/tests/unit/test_context_loader.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/infra/db/repositories/prediction_schemas.py` — `PredictionContext`, `RulesetContext`, `CalibrationData`
- `backend/app/infra/db/repositories/prediction_reference_repository.py` — `PredictionReferenceRepository`
- `backend/app/infra/db/repositories/prediction_ruleset_repository.py` — `PredictionRulesetRepository`

---

## Checklist de validation

- [ ] `LoadedPredictionContext` contient tous les composants requis
- [ ] Contexte complet chargé sans exception avec fixtures valides
- [ ] Contexte incomplet (catégories, profils, ruleset) → `PredictionContextError`
- [ ] Mismatch de version → `PredictionContextError` avec message explicite
- [ ] Calibrations absentes → `is_provisional_calibration=True`, pas d'exception
- [ ] Tous les tests unitaires passent (mocks, sans DB)
