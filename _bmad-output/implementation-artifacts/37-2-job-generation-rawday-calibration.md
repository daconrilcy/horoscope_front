# Story 37.2 : Job offline de génération des RawDay de calibration

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction,
I want un job batch idempotent qui exécute le moteur sur le corpus de calibration et stocke les raw_day par catégorie dans une table dédiée,
so that le dataset brut nécessaire au calcul des percentiles est produit de manière reproductible et reprend proprement après toute interruption.

## Acceptance Criteria

### AC1 — Idempotence garantie (pas de doublons)

Le job ne crée jamais deux lignes pour le même triplet `(profile_label, local_date, category_code, reference_version, ruleset_version)`. Une contrainte unique sur la table et un check avant calcul empêchent tout doublon.

### AC2 — Reprise après interruption

Si le job est interrompu (crash, timeout, Ctrl+C), la prochaine exécution reprend exactement où il s'est arrêté sans recalculer les paires déjà stockées.

### AC3 — Traçabilité des runs

Chaque profil traité émet un log structuré indiquant : label, date, statut (`skipped` / `computed`), durée du calcul.

### AC4 — Dataset exploitable pour le calcul percentile

Pour chaque combinaison `(profil × date)`, les champs `raw_score`, `power`, `volatility`, `pivot_count` sont stockés par catégorie active — suffisant pour calculer P5…P95 dans la story 37.3.

### AC5 — Pas de génération de texte éditorial

Le moteur tourne sans appel LLM. Le job ne configure pas `debug_mode=True` et n'utilise pas la couche éditoriale.

## Tasks / Subtasks

### T1 — Créer le modèle DB `CalibrationRawDayModel`

- [ ] Créer `backend/app/infra/db/models/calibration.py`
  - [ ] Définir `CalibrationRawDayModel` (table `calibration_raw_days`) avec les colonnes :
    - `id` (Integer, PK, autoincrement)
    - `profile_label` (String, not null)
    - `local_date` (Date, not null)
    - `category_code` (String, not null)
    - `raw_score` (Float, not null)
    - `power` (Float, nullable)
    - `volatility` (Float, nullable)
    - `pivot_count` (Integer, default 0)
    - `reference_version` (String, not null)
    - `ruleset_version` (String, not null)
    - `computed_at` (DateTime, default utcnow)
  - [ ] Ajouter `UniqueConstraint("profile_label", "local_date", "category_code", "reference_version", "ruleset_version", name="uq_calibration_raw_day")`
  - [ ] Ajouter l'import du modèle dans `backend/app/infra/db/models/__init__.py` (ou équivalent)

### T2 — Créer la migration Alembic

- [ ] Créer `backend/app/infra/db/migrations/versions/20260308_calibration_raw_days.py`
  - [ ] `upgrade()` : `op.create_table("calibration_raw_days", ...)` avec toutes les colonnes et la contrainte unique
  - [ ] `downgrade()` : `op.drop_table("calibration_raw_days")`

### T3 — Créer le repository `CalibrationRepository`

- [ ] Créer `backend/app/infra/db/repositories/calibration_repository.py`
  - [ ] `exists(profile_label, local_date, category_code, reference_version, ruleset_version) -> bool`
  - [ ] `save(raw_day: CalibrationRawDayModel) -> None`
  - [ ] `count(reference_version, ruleset_version) -> int` (utile pour le rapport de progression)

### T4 — Créer le job principal

- [ ] Créer `backend/app/jobs/generate_daily_calibration_dataset.py`
  - [ ] Bloc `if __name__ == "__main__":` (module `__main__` invocable via `python -m app.jobs.generate_daily_calibration_dataset`)
  - [ ] Charger `CALIBRATION_PROFILES`, `CALIBRATION_DATE_RANGE`, `CALIBRATION_VERSIONS` depuis `calibration/natal_profiles.py`
  - [ ] Générer la liste de toutes les dates de la plage (`date_range`)
  - [ ] Pour chaque `(profil, date)` :
    - [ ] Vérifier via `CalibrationRepository.exists()` pour chaque `category_code` connu — si toutes présentes, `skip`
    - [ ] Construire `EngineInput` avec `debug_mode=False`
    - [ ] Appeler `EngineOrchestrator.run(engine_input, db)`
    - [ ] Itérer sur `engine_output.category_scores.items()` et stocker un `CalibrationRawDayModel` par catégorie
    - [ ] Logger le résultat (`skipped` ou `computed` avec durée)
  - [ ] Afficher un résumé final : total calculés, total skippés, durée globale

### T5 — Tests unitaires

- [ ] Créer `backend/app/tests/unit/test_calibration_job.py`
  - [ ] `test_job_skips_existing_entry` — si `exists()` retourne `True`, `EngineOrchestrator.run` n'est pas appelé
  - [ ] `test_job_stores_raw_day` — après un run, `CalibrationRawDayModel` est bien persisté avec les bons champs
  - [ ] `test_job_resume_after_interruption` — simuler un dataset partiel en DB, vérifier que seules les paires manquantes sont calculées

## Dev Notes

### Modèle DB

```python
# backend/app/infra/db/models/calibration.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, UniqueConstraint
)
from app.infra.db.base import Base

class CalibrationRawDayModel(Base):
    __tablename__ = "calibration_raw_days"
    __table_args__ = (
        UniqueConstraint(
            "profile_label", "local_date", "category_code",
            "reference_version", "ruleset_version",
            name="uq_calibration_raw_day",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_label = Column(String, nullable=False)
    local_date = Column(Date, nullable=False)
    category_code = Column(String, nullable=False)
    raw_score = Column(Float, nullable=False)
    power = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    pivot_count = Column(Integer, default=0)
    reference_version = Column(String, nullable=False)
    ruleset_version = Column(String, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)
```

### Pattern de check avant calcul (idempotence)

```python
from app.infra.db.repositories.calibration_repository import CalibrationRepository

repo = CalibrationRepository(db)

# Vérifie si toutes les catégories sont déjà calculées pour ce (profil, date)
already_done = all(
    repo.exists(profile["label"], local_date, cat, ref_version, ruleset_version)
    for cat in ACTIVE_CATEGORIES
)
if already_done:
    logger.info("skipped", profile=profile["label"], date=local_date)
    continue
```

### Construction de l'EngineInput

```python
from app.prediction.engine_input import EngineInput

engine_input = EngineInput(
    natal_chart=profile["natal_chart"],
    local_date=local_date,
    timezone=profile["timezone"],
    latitude=profile["latitude"],
    longitude=profile["longitude"],
    reference_version=CALIBRATION_VERSIONS["reference_version"],  # depuis settings, pas "1.0.0" en dur
    ruleset_version=CALIBRATION_VERSIONS["ruleset_version"],  # depuis settings, pas "1.0.0" en dur
    debug_mode=False,
)
```

### Stockage des scores par catégorie

```python
engine_output = orchestrator.run(engine_input, db)

pivot_count = len(engine_output.turning_points) if engine_output.turning_points else 0

for category_code, score in engine_output.category_scores.items():
    raw_day = CalibrationRawDayModel(
        profile_label=profile["label"],
        local_date=local_date,
        category_code=category_code,
        raw_score=score["raw_score"],
        power=score.get("power"),
        volatility=score.get("volatility"),
        pivot_count=pivot_count,
        reference_version=CALIBRATION_VERSIONS["reference_version"],
        ruleset_version=CALIBRATION_VERSIONS["ruleset_version"],
    )
    repo.save(raw_day)
```

### Invocation du job

```bash
# Depuis la racine du projet, venv activé
python -m app.jobs.generate_daily_calibration_dataset

# Avec des paramètres optionnels (si implémentés)
python -m app.jobs.generate_daily_calibration_dataset --dry-run
```

### Fichiers à créer

| Fichier | Action |
|---------|--------|
| `backend/app/infra/db/models/calibration.py` | Créer |
| `backend/app/infra/db/migrations/versions/20260308_calibration_raw_days.py` | Créer |
| `backend/app/infra/db/repositories/calibration_repository.py` | Créer |
| `backend/app/jobs/generate_daily_calibration_dataset.py` | Créer |
| `backend/app/tests/unit/test_calibration_job.py` | Créer |

### Fichiers à NE PAS toucher

- Tous les fichiers `backend/app/prediction/*.py`
- `backend/app/jobs/calibration/natal_profiles.py` (story 37.1)

## References

- [Source: backend/app/prediction/ — EngineOrchestrator, EngineInput, EngineOutput, category_scores]
- [Source: _bmad-output/implementation-artifacts/37-1-specification-dataset-calibration.md — CALIBRATION_PROFILES, CALIBRATION_DATE_RANGE]
- [Source: backend/app/infra/db/models/prediction_ruleset.py — CategoryCalibrationModel (pattern de modèle existant)]
- [Source: backend/app/tests/regression/helpers.py — pattern create_session() pour tests unitaires]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

- `backend/app/infra/db/models/calibration.py`
- `backend/app/infra/db/migrations/versions/20260308_calibration_raw_days.py`
- `backend/app/infra/db/repositories/calibration_repository.py`
- `backend/app/jobs/generate_daily_calibration_dataset.py`
- `backend/app/tests/unit/test_calibration_job.py`

## Change Log

- 2026-03-08: Story créée pour Epic 37.
