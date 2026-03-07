# Story 33.1 : Contrat d'entrée/sortie du moteur + orchestrateur de run

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un contrat d'API interne stable (schémas `EngineInput` / `EngineOutput`) et un orchestrateur de run qui enchaîne les étapes du moteur,
so that toutes les stories suivantes (sampler, calculateur, détecteur, scorer) peuvent s'appuyer sur ce contrat sans ambiguïté et que le run est déterministe.

## Contexte métier

L'epic 33 pose les fondations du moteur de prédiction astrologique journalier. Cette première story fige le contrat d'API interne : entrée canonique (`EngineInput`), sortie structurée (`EngineOutput`), calcul du `input_hash` et conversion local → UT. L'orchestrateur créé ici est le point d'entrée unique du moteur ; il a ensuite été branché réellement sur les stories 33-2 à 33-6 et sert désormais de point d'entrée exécutable du pipeline quotidien.

Les repositories DB (epic 31-32) sont déjà stables et peuvent être utilisés.

## Acceptance Criteria

### AC1 — Schéma `EngineInput`

Le dataclass/Pydantic `EngineInput` contient au minimum :
- `natal_chart: dict` — thème natal sérialisé
- `local_date: date`
- `timezone: str` — identifiant IANA
- `latitude: float`
- `longitude: float`
- `reference_version: str`
- `ruleset_version: str`
- `debug_mode: bool = False`

### AC2 — Schéma `EngineOutput`

`EngineOutput` contient :
- `run_metadata: dict` — `run_id` (nullable), `computed_at`, `debug_mode`
- `effective_context: EffectiveContext` — `house_system_requested`, `house_system_effective`, `timezone`, `input_hash`
- `sampling_timeline: list[SamplePoint]` — vide à ce stade
- `detected_events: list[AstroEvent]` — vide à ce stade
- `category_scores: dict` — placeholder vide
- `time_blocks: list` — placeholder vide
- `turning_points: list` — placeholder vide

### AC3 — Hash d'entrée SHA-256 stable

Le `input_hash` est un SHA-256 hex digest sur dict canonique trié contenant au minimum : `natal`, `local_date` (ISO 8601), `timezone`, `latitude`, `longitude`, `reference_version`, `ruleset_version`. Hash identique à entrée identique, différent si un seul champ change.

### AC4 — Conversion local → UT

`EngineOrchestrator` convertit `local_date + timezone` en intervalle UT (début/fin du jour local, en Julian Day Number) avant tout calcul. Utilise `zoneinfo` Python 3.9+.

### AC5 — `house_system_requested` vs `house_system_effective` toujours présents

Les deux champs sont présents dans `EffectiveContext` dès la création. `house_system_effective` peut être identique à `requested` ou indiquer un repli (Porphyre si Placidus échoue).

### AC6 — Déterminisme strict

Deux appels successifs `EngineOrchestrator.run(same_input)` produisent exactement le même `EngineOutput` (même hash, mêmes métadonnées).

## Tasks / Subtasks

### T1 — Créer le module `backend/app/prediction/` (AC1, AC2)

- [x] Créer `backend/app/prediction/__init__.py`
- [x] Créer `backend/app/prediction/schemas.py` avec :
  - [x] `EngineInput` (dataclass)
  - [x] `EffectiveContext` (dataclass)
  - [x] `SamplePoint` (dataclass — `ut_time: float`, `local_time: datetime`)
  - [x] `AstroEvent` (dataclass — tous les champs définis en AC spec)
  - [x] `EngineOutput` (dataclass avec tous les placeholders)
- [x] Créer `backend/app/prediction/exceptions.py` avec `PredictionEngineError`, `PredictionContextError`

### T2 — Implémenter `EngineOrchestrator` (AC3, AC4, AC5, AC6)

- [x] Créer `backend/app/prediction/engine_orchestrator.py`
  - [x] Méthode `run(engine_input: EngineInput) -> EngineOutput`
  - [x] `_compute_hash(engine_input) -> str` — SHA-256 sur dict canonique JSON trié
  - [x] `_local_date_to_ut_interval(local_date, timezone) -> tuple[float, float]` — retourne `(jd_start, jd_end)` via `zoneinfo` + conversion JD
  - [x] Construire `EffectiveContext` avec `house_system_requested` depuis ruleset config (valeur par défaut `"Placidus"` pour l'instant), `house_system_effective` identique
  - [x] Stubs vides pour les étapes 33-2 à 33-6 (commentaires `# TODO: story 33-X`)

### T3 — Tests unitaires (AC3, AC4, AC6)

- [x] Créer `backend/app/tests/unit/test_engine_orchestrator.py`
  - [x] `test_hash_stable` — même input × 2 → même hash
  - [x] `test_hash_changes_on_diff` — changer `local_date` → hash différent
  - [x] `test_local_to_ut_paris` — `2026-03-07` + `Europe/Paris` → `jd_start ≈ 2461106.458333` et `jd_end ≈ 2461107.458333`
  - [x] `test_output_has_mandatory_fields` — tous les champs `EngineOutput` présents
  - [x] `test_house_system_fields_present` — `house_system_requested` et `effective` présents
  - [x] `test_determinism` — deux runs identiques → `EngineOutput` identiques
  - [x] `test_debug_mode_propagated` — `debug_mode=True` propagé dans `run_metadata`

## Dev Notes

### Pattern dataclass existant dans le projet

Le projet utilise des `@dataclass` (pas Pydantic) pour les schémas internes du moteur — cf. `backend/app/infra/db/repositories/prediction_schemas.py` ligne 1 à 139 pour le pattern exact.

### Conversion Julian Day

```python
import swisseph as swe
from zoneinfo import ZoneInfo
from datetime import datetime, date, time

def local_date_to_jd(local_date: date, tz_name: str) -> float:
    tz = ZoneInfo(tz_name)
    dt = datetime(local_date.year, local_date.month, local_date.day, 0, 0, 0, tzinfo=tz)
    dt_utc = dt.astimezone(ZoneInfo("UTC"))
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
```

### Calcul du hash SHA-256

```python
import hashlib, json

def _compute_hash(engine_input: EngineInput) -> str:
    canonical = {
        "natal": engine_input.natal_chart,
        "local_date": engine_input.local_date.isoformat(),
        "timezone": engine_input.timezone,
        "latitude": engine_input.latitude,
        "longitude": engine_input.longitude,
        "reference_version": engine_input.reference_version,
        "ruleset_version": engine_input.ruleset_version,
    }
    serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
```

### Structure du module prediction

```
backend/app/prediction/
├── __init__.py
├── schemas.py
├── exceptions.py
└── engine_orchestrator.py
```

### Dépendance pyswisseph

`pyswisseph` est déjà dans `backend/pyproject.toml` (utilisé depuis l'epic 20). Ne pas ajouter de dépendance.

### Fichiers à NE PAS toucher

- Tous les fichiers dans `backend/app/infra/db/`
- Tout fichier frontend
- `backend/app/api/`

### Références

- [Source: docs/model_de_calcul_journalier.md — Hypothèses et conventions / Temps de référence]
- [Source: backend/app/infra/db/repositories/prediction_schemas.py — Pattern dataclass]
- [Source: backend/app/infra/db/repositories/daily_prediction_repository.py — DailyPredictionRepository]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Création du module `backend/app/prediction/` pour centraliser la logique du moteur.
- Implémentation des schémas de données `EngineInput`, `EngineOutput`, etc., via `@dataclass` (frozen=True pour garantir l'immutabilité et le déterminisme).
- Implémentation de `EngineOrchestrator` avec calcul de hash stable (SHA-256) et conversion temporelle locale → UT (Julian Day).
- Correction du calcul de l'intervalle UT pour couvrir exactement 24h (utilisant le début du jour suivant).
- Durcissement post-review : `AstroEvent` aligné sur la spec annexe, résolution du `house_system` depuis un contexte de ruleset injectable, et erreurs métier stables pour timezone/ruleset invalides.
- Durcissement post-review : `computed_at` rendu déterministe à partir du début UTC du jour local évalué, ce qui rend `EngineOutput` strictement reproductible pour une même entrée.
- Validation via tests unitaires renforcés sur le déterminisme complet, la propagation de `debug_mode`, le contrat temporel exact et les erreurs métier.
- Intégration réelle du pipeline `33-2 -> 33-6` dans `EngineOrchestrator.run()` avec production effective de `sampling_timeline`, `detected_events` et `category_scores`.
- Support du format `chart_json` canonique pour `natal_chart` (`planets`, `houses`, `angles`) avec erreur métier explicite si les 12 cuspides ne sont pas disponibles.
- Validation applicative finale via smoke test réel sur DB seedée (`reference_version=2.0.0`, `ruleset_version=1.0.0`) : `RUN OK`, `samples=96`, `events=48`, catégories non vides.
- Correction industrialisée du référentiel prediction via migration de data `20260307_0036` et mise à jour du script de seed `31.3`.

### Senior Developer Review (AI)

- Corrections appliquées pour les écarts relevés en revue : déterminisme strict de `EngineOutput`, contrat `AstroEvent`, source du `house_system_requested`, gestion d'erreurs métier et durcissement des tests.
- Lint `ruff check` et tests unitaires ciblés exécutés dans le venv après corrections.

### File List

- `backend/app/prediction/__init__.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/exceptions.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/scripts/seed_31_prediction_reference_v2.py`
- `backend/migrations/versions/20260307_0036_backfill_prediction_planet_profile_orbs.py`
