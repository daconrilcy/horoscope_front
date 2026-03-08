# Story 36.1 : Service applicatif `DailyPredictionService`

Status: done

## Story

As a développeur de l'application horoscope,
I want un service applicatif `DailyPredictionService` qui orchestre la résolution du contexte utilisateur, l'exécution du moteur et la persistance en un seul appel stable,
so that la prédiction quotidienne est calculable ou réutilisable depuis n'importe quel point d'entrée (API, batch, tests) sans dupliquer de logique métier.

## Acceptance Criteria

### AC1 — Prédiction complète pour utilisateur avec natal valide

Un utilisateur avec un `ChartResultModel` existant obtient un `ServiceResult` complet avec `run`, `engine_output` et `was_reused`.

### AC2 — Pas de recalcul inutile en mode `compute_if_missing`

Si un run avec le même `input_hash` existe déjà en DB, le service retourne `was_reused=True` sans déclencher de nouveau calcul moteur.

### AC3 — Interprétation de la date dans le fuseau de l'utilisateur

La `date_local` est interprétée dans le `current_timezone` du profil (ou `birth_timezone` en fallback), jamais en UTC côté service. La conversion UT se fait uniquement dans le moteur via `EngineInput`.

### AC4 — Erreurs métier explicites

Le service lève une exception typée `DailyPredictionServiceError` dans les cas suivants :
- natal absent (aucun `ChartResultModel` pour cet utilisateur)
- timezone absente ou invalide (profil sans `current_timezone` ni `birth_timezone`)
- localisation invalide ou absente (profil sans `current_lat`/`current_lon`)
- version de ruleset absente (`PredictionContextError` convertie)

### AC5 — Interface stable API/batch

Le `ServiceResult` est un dataclass frozen, lisible aussi bien par un endpoint FastAPI que par une tâche batch (`Annotated[Session, Depends(get_db)]`-compatible).

### AC6 — Mode `force_recompute` recalcule et remplace

En mode `force_recompute`, le service calcule systématiquement et passe l'output au `PredictionPersistenceService` même si un hash identique existe. La persistance gère le remplacement.

### AC7 — Mode `read_only` sans recalcul

En mode `read_only`, le service tente uniquement de lire le run existant via repository. Retourne `None` si absent, sans jamais invoquer le moteur.

## Tasks / Subtasks

### T1 — Créer `DailyPredictionService` (AC1–AC7)

- [x] Créer `backend/app/services/daily_prediction_service.py`
  - [x] Enum `ComputeMode` : `compute_if_missing`, `force_recompute`, `read_only`
  - [x] `@dataclass(frozen=True) ServiceResult` :
    - `run: DailyPredictionRunModel`
    - `engine_output: EngineOutput | None`
    - `was_reused: bool`
  - [x] Exception `DailyPredictionServiceError(code: str, message: str)`
  - [x] Classe `DailyPredictionService` avec constructeur injectant :
    - `context_loader: PredictionContextLoader`
    - `persistence_service: PredictionPersistenceService`
  - [x] Méthode principale : `get_or_compute`
  - [x] `_resolve_date` : date_local ou aujourd'hui dans le fuseau
  - [x] `_resolve_timezone` : `timezone_override` > `current_timezone` > `birth_timezone` > erreur AC4
  - [x] `_resolve_location` : override > `current_lat/lon` > erreur AC4
  - [x] `_resolve_natal_chart` : `ChartResultRepository.get_latest_by_user_id()` → `result_payload` ou erreur AC4
  - [x] `_resolve_versions` : IDs via `select(ReferenceVersionModel)` + `PredictionRulesetRepository.get_ruleset()` ou erreur AC4
  - [x] `_build_engine_input` : `EngineInput`
  - [x] Logique de dispatch selon `ComputeMode`

### T2 — Tests unitaires (AC1–AC7)

- [x] Créer `backend/app/tests/unit/test_daily_prediction_service.py`
  - [x] Setup fixtures : mock `PredictionContextLoader`, mock `PredictionPersistenceService`, mock `ChartResultRepository`, mock `DailyPredictionRepository`, mock `UserBirthProfileRepository`
  - [x] `test_user_without_natal` → `DailyPredictionServiceError(code="natal_missing")`
  - [x] `test_user_missing_profile` → `DailyPredictionServiceError(code="profile_missing")`
  - [x] `test_user_with_natal` → `ServiceResult` complet, `was_reused=False`
  - [x] `test_identical_hash_not_recomputed` → `was_reused=True`, moteur non invoqué
  - [x] `test_force_recompute` → moteur invoqué, ancien run supprimé (`db.delete` asserté)
  - [x] `test_timezone_missing_raises` → erreur si aucun timezone
  - [x] `test_timezone_invalid_raises` → erreur si timezone non reconnue par ZoneInfo
  - [x] `test_location_missing_raises` → erreur si `current_lat/lon` absents et pas d'override
  - [x] `test_version_missing_raises` → erreur si `reference_version` introuvable en DB
  - [x] `test_ruleset_missing_raises` → erreur si `ruleset_version` introuvable en DB
  - [x] `test_read_only_existing` → run retourné sans calcul
  - [x] `test_read_only_missing` → `None` retourné

## Dev Notes

### Architecture : couche de service applicatif

Ce service est une **couche d'orchestration** — il ne doit pas contenir de logique métier astrologique. Sa seule responsabilité est de :
1. résoudre les dépendances (natal, timezone, localisation, versions),
2. construire `EngineInput`,
3. déléguer au moteur,
4. déléguer à la persistance,
5. retourner un `ServiceResult` stable.

### Pattern de résolution des versions

```python
# Reference version → ReferenceVersionModel.id
from sqlalchemy import select
from app.infra.db.models.reference import ReferenceVersionModel

rv_model = db.scalar(select(ReferenceVersionModel.id).where(
    ReferenceVersionModel.version == reference_version
))
if rv_model is None:
    raise DailyPredictionServiceError("version_missing", f"Référence version '{reference_version}' introuvable")
reference_version_id = rv_model.id

# Ruleset version → RulesetData
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
ruleset_repo = PredictionRulesetRepository(db)
ruleset = ruleset_repo.get_ruleset(ruleset_version)
if ruleset is None:
    raise DailyPredictionServiceError("ruleset_missing", f"Ruleset version '{ruleset_version}' introuvable")
ruleset_id = ruleset.id
```

### Pattern de récupération du natal

Le natal est stocké dans `ChartResultModel.result_payload` (dict). Il correspond au format attendu par `EngineInput.natal_chart`.

```python
from app.infra.db.repositories.chart_result_repository import ChartResultRepository

chart_repo = ChartResultRepository(db)
chart = chart_repo.get_latest_by_user_id(user_id)
if chart is None:
    raise DailyPredictionServiceError("natal_missing", "Aucun thème natal trouvé pour cet utilisateur")
natal_chart = chart.result_payload
```

### Pattern de résolution timezone

```python
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def _resolve_timezone(self, profile: UserBirthProfileModel, override: str | None) -> str:
    tz_str = override or profile.current_timezone or profile.birth_timezone
    if not tz_str:
        raise DailyPredictionServiceError("timezone_missing", "Timezone introuvable pour l'utilisateur")
    try:
        ZoneInfo(tz_str)
    except (ZoneInfoNotFoundError, KeyError):
        raise DailyPredictionServiceError("timezone_invalid", f"Timezone invalide : '{tz_str}'")
    return tz_str
```

### Pattern de résolution de la date locale

```python
from datetime import date
from zoneinfo import ZoneInfo
from datetime import datetime

def _resolve_date(self, date_local: date | None, tz_str: str) -> date:
    if date_local is not None:
        return date_local
    # "Aujourd'hui" dans le fuseau de l'utilisateur
    return datetime.now(ZoneInfo(tz_str)).date()
```

### Dispatch ComputeMode — CRITIQUE : hash calculé AVANT le moteur (AC2)

Le hash d'entrée doit être calculé dès la construction de `EngineInput`, **avant tout appel à l'orchestrateur**. La vérification via `get_run_by_hash()` court-circuite le moteur si le run existe déjà. Déléguer cette vérification à `PredictionPersistenceService.save()` est trop tard : le moteur aurait déjà tourné.

```python
import hashlib, json

def _compute_input_hash(self, engine_input: EngineInput) -> str:
    """Reproduit le hash utilisé par EngineOrchestrator pour cohérence."""
    payload = {
        "natal": engine_input.natal_chart,
        "local_date": engine_input.local_date.isoformat(),
        "timezone": engine_input.timezone,
        "latitude": engine_input.latitude,
        "longitude": engine_input.longitude,
        "reference_version": engine_input.reference_version,
        "ruleset_version": engine_input.ruleset_version,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()

def get_or_compute(self, ..., mode: ComputeMode = ComputeMode.compute_if_missing) -> ServiceResult | None:
    # 1. Résoudre toutes les dépendances
    profile = self._resolve_profile(db, user_id)
    tz_str = self._resolve_timezone(profile, timezone_override)
    lat, lon = self._resolve_location(profile, location_override)
    resolved_date = self._resolve_date(date_local, tz_str)
    natal_chart = self._resolve_natal_chart(db, user_id)
    reference_version_id, ruleset_id = self._resolve_versions(db, reference_version, ruleset_version)

    # 2. Mode read_only : lecture seule, aucun calcul
    if mode == ComputeMode.read_only:
        run = DailyPredictionRepository(db).get_run(
            user_id, resolved_date, reference_version_id, ruleset_id
        )
        if run is None:
            return None
        return ServiceResult(run=run, engine_output=None, was_reused=True)

    # 3. Construire EngineInput et calculer le hash AVANT le moteur
    engine_input = self._build_engine_input(
        natal_chart, resolved_date, tz_str, lat, lon, reference_version, ruleset_version
    )
    input_hash = self._compute_input_hash(engine_input)

    # 4. Mode compute_if_missing : court-circuit AVANT le moteur si hash existant (AC2)
    if mode == ComputeMode.compute_if_missing:
        existing_run = DailyPredictionRepository(db).get_run_by_hash(user_id, input_hash)
        if existing_run:
            return ServiceResult(run=existing_run, engine_output=None, was_reused=True)

    # 5. Mode force_recompute : supprimer l'ancien run (contrainte unique uq_daily_prediction_runs_user_date_ruleset)
    if mode == ComputeMode.force_recompute:
        old_run = DailyPredictionRepository(db).get_run(
            user_id, resolved_date, reference_version_id, ruleset_id
        )
        if old_run:
            db.delete(old_run)
            db.flush()

    # 6. Calcul moteur (uniquement si pas de court-circuit)
    ctx = self.context_loader.load(db, reference_version, ruleset_version)
    engine_output = EngineOrchestrator().run(engine_input, ctx)
    save_result = self.persistence_service.save(
        engine_output=engine_output,
        user_id=user_id,
        local_date=resolved_date,
        reference_version_id=reference_version_id,
        ruleset_id=ruleset_id,
        db=db,
    )
    return ServiceResult(
        run=save_result.run,
        engine_output=engine_output,
        was_reused=False,  # Toujours False ici : on vient de calculer
    )
```

**Attention** : `_compute_input_hash()` doit produire le même hash que `EngineOrchestrator` interne. Vérifier dans `engine_orchestrator.py` comment le hash est calculé et le reproduire exactement.

### Lecture du profil utilisateur

```python
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository

profile_repo = UserBirthProfileRepository(db)
profile = profile_repo.get_by_user_id(user_id)
if profile is None:
    raise DailyPredictionServiceError("profile_missing", "Profil de naissance introuvable")
```

### `EngineInput` : champs requis

```python
from app.prediction.schemas import EngineInput

EngineInput(
    natal_chart=natal_chart,        # dict depuis ChartResultModel.result_payload
    local_date=local_date,          # date dans le fuseau utilisateur
    timezone=tz_str,                # str IANA
    latitude=lat,                   # float
    longitude=lon,                  # float
    reference_version=reference_version,  # str (ex: "1.0.0")
    ruleset_version=ruleset_version,      # str (ex: "1.0.0")
    debug_mode=False,
)
```

### `PredictionContextLoader` : usage

Le `context_loader` doit être instancié ou injecté. Pour l'API il sera fourni via injection de dépendances FastAPI. Pour les tests il sera mocké.

```python
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.engine_orchestrator import EngineOrchestrator

ctx = self.context_loader.load(db, reference_version, ruleset_version)
engine_output = EngineOrchestrator().run(engine_input, ctx)
```

### Project Structure Notes

- Fichier créé : `backend/app/services/daily_prediction_service.py`
- Fichier de tests créé : `backend/app/tests/unit/test_daily_prediction_service.py`
- Le service s'intègre en parallèle des services existants.

### Convention de nommage

Suivre exactement les patterns des services existants dans `backend/app/services/` :
- Nom de classe : `DailyPredictionService`
- Nom d'exception : `DailyPredictionServiceError`
- Injecter les dépendances par constructeur, pas par paramètre de méthode

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Hash consistency with `EngineOrchestrator._compute_hash` verified (key "natal").
- Mocking issues with `ZoneInfo` and `sqlalchemy.select` fixed in tests.
- Ruff E501 (line too long) fixed.

### Completion Notes List

- Implemented `DailyPredictionService` with `get_or_compute` orchestrating everything.
- Implemented `ComputeMode` (compute_if_missing, force_recompute, read_only).
- Added typed exception `DailyPredictionServiceError`.
- Verified hash consistency with the engine.
- Created 9 unit tests covering all ACs and edge cases.
- All tests pass, linting is clean.

### File List

- `backend/app/services/daily_prediction_service.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`

### Note : `_resolve_versions` → deux méthodes séparées (M5)

La story spécifiait `_resolve_versions` (une seule méthode). L'implémentation utilise deux méthodes distinctes — `_resolve_reference_version_id` et `_resolve_ruleset_id` — ce qui est architecturalement meilleur (SRP). Les stories suivantes doivent référencer ces deux noms.

### Note : `was_reused` en mode `read_only` (L2)

En mode `read_only`, le service retourne `was_reused=True`. Sémantiquement, cela signifie "aucun calcul moteur n'a été déclenché", ce qui est cohérent avec l'usage de ce champ par les endpoints (éviter de re-calculer). Si un jour il faut distinguer les modes, ajouter un champ `mode_used: ComputeMode` à `ServiceResult`.

### Note : `EngineOrchestrator` — injection pour la production (H3)

Pour éviter de recréer les 9 sous-composants à chaque appel en production, injecter un `EngineOrchestrator` pré-construit via le constructeur. La méthode `with_context_loader(loader)` permet de lier le `db` per-request sans recréer les sous-composants stateless :

```python
# Dans la DI FastAPI (ex: dependencies.py)
_shared_orchestrator = EngineOrchestrator()  # créé une fois

def get_daily_prediction_service(db: Session = Depends(get_db)) -> DailyPredictionService:
    return DailyPredictionService(
        context_loader=PredictionContextLoader(),
        persistence_service=PredictionPersistenceService(),
        orchestrator=_shared_orchestrator,
    )
```

## Change Log

- 2026-03-08: Story créée pour l'Epic 36 — Productisation V1.
- 2026-03-08: Implémentation complète de `DailyPredictionService` et tests unitaires associés.
- 2026-03-08: Code review — corrections appliquées (H1 PredictionContextError, H3 orchestrator proto, M1/L1 hash, H2/M3 tests manquants, M2 assert delete, M4 patch manquant).
