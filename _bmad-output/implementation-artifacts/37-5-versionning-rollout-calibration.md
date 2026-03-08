# Story 37.5 : Versionning et rollout de calibration

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction,
I want que le moteur expose toujours la calibration utilisée dans ses métadonnées de run et qu'une politique de rollout documentée régisse le passage de calibration provisoire à calibration réelle,
so that les runs historiques restent interprétables, les changements de calibration sont traçables, et le payload API reflète l'état de la calibration active.

## Acceptance Criteria

### AC1 — Le moteur expose la calibration utilisée dans `run_metadata`

`EngineOutput.run_metadata` contient `is_provisional_calibration` (booléen) et `calibration_label` (chaîne, ex. `"provisional"`, `"v1"`, `"v2"`), reflétant la calibration effective au moment du calcul.

### AC2 — Les runs historiques restent interprétables

Aucun run historique n'est recalculé silencieusement lors d'un changement de calibration. Les scores persistés dans `DailyPredictionRunModel` sont immuables ; seuls les nouveaux runs utilisent la nouvelle calibration.

### AC3 — Le changement de calibration est traçable dans les métadonnées

Lors d'un changement de calibration, les nouveaux runs ont un `calibration_label` différent des runs précédents, permettant de distinguer les runs calculés sous chaque version de calibration.

### AC4 — La politique de rollout est documentée

Un fichier `docs/calibration/rollout-policy.md` documente la politique complète : calibration provisoire → calibration réelle v1, conditions de promotion, interdiction de recalcul silencieux.

### AC5 — `is_provisional_calibration` présent dans le payload de réponse API

Le champ `is_provisional_calibration` est inclus dans le bloc `meta` du payload retourné par l'endpoint `GET /v1/predictions/daily` (story 36-2).

## Tasks / Subtasks

### T1 — Propager `is_provisional_calibration` et `calibration_label` jusqu'à `EngineOutput.run_metadata` ET les persister en DB

- [ ] Lire `LoadedPredictionContext.is_provisional_calibration` dans `EngineOrchestrator.run()`
- [ ] Ajouter `is_provisional_calibration` et `calibration_label` dans la construction de `run_metadata`
- [ ] **Persister `is_provisional_calibration` ET `calibration_label` dans `DailyPredictionRunModel`** :
  - Ajouter colonne `is_provisional_calibration: bool | None` (nullable, compatibilité avec runs anciens)
  - Ajouter colonne `calibration_label: str | None` (nullable, valeur ex. `"provisional"`, `"v1"`) — **requis pour AC3** : distinguer les runs par label de calibration dans les historiques
  - Migration Alembic requise pour les deux colonnes
  - Les remplir dans `PredictionPersistenceService.save()` depuis `engine_output.run_metadata`
- [ ] **Pour les runs réutilisés** (`was_reused=True`, `engine_output=None`) : lire les deux valeurs depuis `DailyPredictionRunModel` (colonnes DB) — garantit leur survie aux runs réutilisés et leur disponibilité pour l'API
- [ ] Vérifier que `DailyPredictionMeta` est alimenté depuis les colonnes DB, pas depuis `engine_output` (qui peut être `None`)

### T2 — Ajouter `calibration_label` dans `CategoryCalibrationModel`

- [ ] Vérifier la présence du champ `calibration_label: str` dans `CategoryCalibrationModel`
- [ ] Si absent : ajouter le champ avec valeur par défaut `"provisional"`
- [ ] Générer une migration Alembic si la colonne est absente en base
- [ ] Vérifier que `PercentileCalibrator` lit et propage le `calibration_label`

### T3 — Créer `docs/calibration/rollout-policy.md`

- [ ] Décrire les états de calibration : `provisional` (sortie du job de calcul percentile), `v1` (après validation métier story 37-4), `vN` (incréments suivants)
- [ ] Documenter la règle d'immuabilité : les runs existants ne sont jamais recalculés
- [ ] Documenter la procédure de promotion : conditions, vérifications, mise à jour du `calibration_label` en DB
- [ ] Documenter la procédure de rollback : retour à la calibration précédente sans altérer les runs existants

### T4 — Mettre à jour le payload endpoint 36-2

- [ ] Ajouter `is_provisional_calibration: bool | None` dans le schéma Pydantic `DailyPredictionMeta` (story 36-2)
- [ ] Ajouter `calibration_label: str | None` dans `DailyPredictionMeta` — permet au front d'afficher ou logguer le label de calibration actif
- [ ] Vérifier que le mapping lit depuis `DailyPredictionRunModel` (colonnes DB), pas depuis `engine_output.run_metadata` (peut être `None` sur runs réutilisés)
- [ ] Vérifier que `is_provisional_calibration` est `False` pour une calibration promue et `True` pour une provisoire

### T5 — Tests `backend/app/tests/unit/test_calibration_versioning.py`

- [ ] `test_engine_output_has_provisional_flag` — `EngineOutput.run_metadata` contient `is_provisional_calibration`
- [ ] `test_calibration_label_in_db` — `CategoryCalibrationModel` possède le champ `calibration_label`
- [ ] `test_calibration_label_persisted_in_run` — après `PredictionPersistenceService.save()`, `DailyPredictionRunModel.calibration_label` est rempli depuis `engine_output.run_metadata`
- [ ] `test_calibration_label_survives_reuse` — sur un run réutilisé (`was_reused=True`, `engine_output=None`), `DailyPredictionRunModel.calibration_label` est lisible depuis la DB
- [ ] `test_historical_runs_unchanged_after_calibration_change` — les runs persistés avant un changement de calibration conservent leurs scores et leur `calibration_label` d'origine

## Dev Notes

### Propagation depuis `LoadedPredictionContext`

`LoadedPredictionContext.is_provisional_calibration: bool` existe déjà dans `backend/app/prediction/context_loader.py`. Le passer dans `run_metadata` lors de la construction dans `EngineOrchestrator.run()` :

```python
# Dans EngineOrchestrator.run():
run_metadata = {
    ...existing fields...,
    "is_provisional_calibration": loaded_ctx.is_provisional_calibration,
    "calibration_label": loaded_ctx.calibration_label,  # à ajouter dans LoadedPredictionContext
}
```

### Règle d'immuabilité des runs historiques

Ne jamais recalculer silencieusement. Si une calibration change :

- Les anciens runs gardent leurs `note_20` et `raw_score` persistés tels quels.
- Seuls les nouveaux runs (calculés après la promotion) utilisent la nouvelle calibration.
- Le `calibration_label` dans `run_metadata` permet de savoir quelle calibration a produit chaque run.

### États de calibration

```
provisional  →  (après validation 37-4)  →  v1
v1           →  (après recalibrage)      →  v2
```

La valeur `provisional` est la valeur par défaut à la sortie du job de calcul percentile (story 37-2/37-3). La promotion vers `v1` est manuelle et documentée dans `rollout-policy.md`.

### Migrations Alembic requises

Deux tables à migrer :

```python
# 1. DailyPredictionRunModel — colonnes de traçabilité run par run
op.add_column(
    "daily_prediction_runs",
    sa.Column("is_provisional_calibration", sa.Boolean(), nullable=True),
)
op.add_column(
    "daily_prediction_runs",
    sa.Column("calibration_label", sa.String(length=64), nullable=True),
    # nullable=True pour compatibilité avec les runs historiques antérieurs à cette story
)

# 2. CategoryCalibrationModel — label de calibration associé aux percentiles
op.add_column(
    "category_calibration",
    sa.Column("calibration_label", sa.String(length=64), nullable=False, server_default="provisional"),
)
```

## References

- [Source: backend/app/prediction/context_loader.py — LoadedPredictionContext, is_provisional_calibration]
- [Source: backend/app/prediction/engine_orchestrator.py — EngineOrchestrator.run(), run_metadata]
- [Source: _bmad-output/implementation-artifacts/36-2-endpoint-api-daily-prediction.md — DailyPredictionMeta, payload API]
- [Source: _bmad-output/implementation-artifacts/37-1-specification-dataset-calibration.md — CategoryCalibrationModel]
- [Source: backend/app/prediction/calibrator.py — PercentileCalibrator]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/context_loader.py`
- `backend/app/infra/db/models/calibration.py`
- `backend/app/api/v1/routers/predictions.py`
- `backend/app/tests/unit/test_calibration_versioning.py`
- `docs/calibration/rollout-policy.md`

## Change Log

- 2026-03-08: Story créée pour Epic 37.
