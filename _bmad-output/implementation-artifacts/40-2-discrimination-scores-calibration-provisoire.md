# Story 40.2 : Discrimination des scores en mode calibration provisoire

Status: done

## Story

En tant que développeur backend de l'application horoscope,
je veux que le moteur de prédiction calcule des scores catégoriels relatifs à la journée quand la calibration historique est absente, et expose un flag `is_provisional` par catégorie dans l'API,
afin que les scores provisoires reflètent de vraies différences relatives entre domaines (travail vs amour vs santé) même sans données historiques, et que le frontend puisse afficher un indicateur de fiabilité per-catégorie plutôt qu'une série uniforme de 10/20.

## Acceptance Criteria

### AC1 — Le calibrateur calcule une distribution relative à la journée en mode provisoire

- [x] `PercentileCalibrator` expose une nouvelle méthode `calibrate_all_provisional_aware(day_aggregation, calibrations)` qui remplace `calibrate_all()` dans `EngineOrchestrator`
- [x] Quand au moins 3 catégories sont considérées provisoires (`calibration is None`, ou `sample_size in {None, 0}`, ou `calibration_label == "provisional"`), la méthode calcule une distribution p05/p25/p50/p75/p95 sur les `raw_day` de ces catégories sur la journée
- [x] Chaque catégorie provisoire est calibrée avec cette distribution jour-relative : une catégorie avec `raw_day` plus haut que la médiane du jour obtient un score > 10, une catégorie plus faible obtient un score < 10
- [x] Les catégories ayant une calibration réelle (`sample_size > 0`) ne sont pas modifiées

### AC2 — La calibration jour-relative est robuste aux cas limites

- [x] Si moins de 3 catégories sont provisoires, on conserve `DEFAULT_CALIBRATION` (fallback actuel)
- [x] Si toutes les `raw_day` provisoires sont identiques (pas de variance), la méthode retombe sur `DEFAULT_CALIBRATION` pour ces catégories (on évite une division par zéro ou une distribution dégénérée)
- [x] La calibration jour-relative interne utilisée pour les catégories provisoires est marquée `calibration_label="day-relative"` et `sample_size=<nb_cats_provisoires>` sans écraser le `run_metadata.calibration_label` global, qui continue à refléter la traçabilité issue du `PredictionContextLoader`

### AC3 — Chaque `DailyPredictionCategoryScore` enregistre son statut provisoire en DB

- [x] La table `daily_prediction_category_scores` possède une nouvelle colonne `is_provisional BOOLEAN NULL DEFAULT NULL`
- [x] Une migration Alembic est créée et appliquée en suivant le pattern réel du repo (`YYYYMMDD_XXXX_add_is_provisional_to_category_scores.py`), avec `down_revision` pointant sur la dernière révision effectivement présente au moment de l'implémentation
- [x] `PredictionPersistenceService._save_scores()` remplit `is_provisional=True` si la calibration de la catégorie était `None` ou `sample_size == 0` au moment du calcul, `False` sinon

### AC4 — L'API `/v1/predictions/daily` expose `is_provisional` par catégorie

- [x] `DailyPredictionCategory` Pydantic (dans `predictions.py`) ajoute `is_provisional: bool | None`
- [x] `DailyPredictionRepository.get_full_run()` inclut `is_provisional` dans le dict `category_scores`
- [x] Le mapping dans l'endpoint `get_daily_prediction()` passe `is_provisional=s.get("is_provisional")` à chaque `DailyPredictionCategory`
- [x] L'endpoint `/daily/debug` (`DailyPredictionDebugCategory`) reçoit également `is_provisional: bool | None`

### AC5 — Le type TypeScript frontend est mis à jour

- [x] `frontend/src/types/dailyPrediction.ts` : `DailyPredictionCategory` ajoute `is_provisional?: boolean | null`
- [x] `DailyPredictionDebugCategory` (si existante dans les types TS) est aussi mise à jour

### AC6 — Disclaimer éditorial quand la calibration est entièrement provisoire

- [x] Quand `is_provisional_calibration=True` (run-level), `DailyPredictionSummary.overall_summary` inclut une phrase de contexte (générée par le template `intro_du_jour.txt` ou via un nouveau champ `calibration_note: str | None` dans `DailyPredictionSummary`)
- [x] Optionnel mais recommandé : si le spread des `note_20` top3 < 3 (toutes quasi-identiques), `DailyPredictionSummary` expose `low_score_variance: bool = True`

### AC7 — Tests unitaires couvrent le nouveau comportement

- [x] Test `test_calibrate_all_provisional_aware_with_day_relative` : 5 catégories sans calibration, `raw_day` en [-0.3, -0.1, 0.0, 0.2, 0.4] → les scores ne sont plus tous ~10/20, ils reflètent l'ordre relatif (le plus haut `raw_day` donne le score le plus élevé)
- [x] Test `test_calibrate_all_provisional_aware_degenerate` : tous les `raw_day` provisoires = 0.0 → fallback sur `DEFAULT_CALIBRATION`, pas d'erreur
- [x] Test `test_calibrate_all_provisional_aware_mixed` : 2 catégories avec calibration réelle + 4 provisoires → les 2 calibrées utilisent leur calibration, les 4 provisoires utilisent la day-relative
- [x] Test `test_calibrate_all_provisional_aware_less_than_3_provisional` : seulement 2 catégories provisoires → toutes utilisent `DEFAULT_CALIBRATION` (pas de day-relative)
- [x] Non-régression : `test_daily_prediction_service.py` passe sans modification

## Tasks / Subtasks

### T1 — Enrichir `PercentileCalibrator` (AC1, AC2)

- [x] Dans `backend/app/prediction/calibrator.py`, ajouter :
  ```python
  def _compute_day_relative_calibration(
      self, raw_days: list[float]
  ) -> CalibrationData:
      """Calibration jour-relative : p05/p25/p50/p75/p95 sur les raw_day de la journée."""
      if len(raw_days) < 3:
          return DEFAULT_CALIBRATION
      sorted_days = sorted(raw_days)
      # Vérifier la variance : si tous identiques → dégénéré
      if sorted_days[-1] == sorted_days[0]:
          return DEFAULT_CALIBRATION
      n = len(sorted_days)
      def _pct(p: float) -> float:
          idx = (p / 100.0) * (n - 1)
          lo, hi = int(idx), min(int(idx) + 1, n - 1)
          return sorted_days[lo] + (idx - lo) * (sorted_days[hi] - sorted_days[lo])
      return CalibrationData(
          p05=_pct(5), p25=_pct(25), p50=_pct(50), p75=_pct(75), p95=_pct(95),
          sample_size=n,
          calibration_label="day-relative",
      )
  ```
- [x] Ajouter `calibrate_all_provisional_aware(self, day_aggregation, calibrations)` :
  - Identifier les `provisional_cats` : catégories dont `calibrations[cat]` est `None`, ou `sample_size in {None, 0}`, ou `calibration_label == "provisional"`
  - Si `len(provisional_cats) >= 3` : calculer `_compute_day_relative_calibration(raw_days)` et remplacer les calibrations provisoires
  - Sinon : appeler `calibrate_all()` sans modification
  - Retourner le dict de scores calibrés

### T2 — Mettre à jour `EngineOrchestrator` (AC1)

- [x] Dans `backend/app/prediction/engine_orchestrator.py`, méthode `_build_prediction_outputs()` :
  - Remplacer l'appel à `self._percentile_calibrator.calibrate_all(day_aggregation, loaded_context.calibrations)` par `self._percentile_calibrator.calibrate_all_provisional_aware(day_aggregation, loaded_context.calibrations)`
  - Même remplacement pour le calcul de `notes_by_step` (utiliser la méthode per-step déjà existante, pas besoin de changer ici car elle appelle `calibrate()` individuel)
  - Note : `notes_by_step` utilise `self._percentile_calibrator.calibrate(raw_val, calibrations.get(cat))` step par step → appliquer la même logique day-relative ici. Stocker la `day_relative_calibration` calculée une seule fois et la passer aux appels per-step pour les catégories provisoires

### T3 — Migration Alembic (AC3)

- [x] Créer une migration dans `backend/migrations/versions/` avec un nom conforme au pattern Alembic actuel du repo (identifiant séquentiel `YYYYMMDD_XXXX`) :
  ```python
  """Add is_provisional to daily_prediction_category_scores
  Revision ID: <generated_revision_id>
  ...
  """
  def upgrade():
      op.add_column(
          "daily_prediction_category_scores",
          sa.Column("is_provisional", sa.Boolean(), nullable=True),
      )
  def downgrade():
      op.drop_column("daily_prediction_category_scores", "is_provisional")
  ```
- [x] Vérifier que la migration enchaîne correctement après la dernière révision réellement présente dans `backend/migrations/versions/`

### T4 — Mettre à jour `DailyPredictionCategoryScoreModel` et persistance (AC3)

- [x] Dans `backend/app/infra/db/models/daily_prediction.py` : ajouter à `DailyPredictionCategoryScoreModel` :
  ```python
  is_provisional: Mapped[bool | None] = mapped_column(nullable=True)
  ```
- [x] Dans `backend/app/prediction/persistence_service.py`, méthode `_save_scores()` :
  - Accéder à `loaded_context.calibrations` → non disponible ici directement. Solution : accepter un paramètre optionnel `provisional_categories: set[str] | None = None` dans `_save_scores()` et le passer depuis `save()`
  - Ou plus simple : dans `engine_output.category_scores`, inclure un flag `is_provisional` par catégorie (stocker dans le dict `editorial_category_scores` dans `EngineOrchestrator`)
  - **Approche recommandée** : ajouter `"is_provisional": True/False` dans chaque entrée du dict `editorial_category_scores` construit dans `EngineOrchestrator._build_prediction_outputs()`, puis lire `score_data.get("is_provisional")` dans `_save_scores()`

### T5 — Enrichir `get_full_run()` et l'API (AC4)

- [x] Dans `backend/app/infra/db/repositories/daily_prediction_repository.py`, méthode `get_full_run()` :
  - Dans la liste `category_scores`, ajouter `"is_provisional": s.is_provisional`
- [x] Dans `backend/app/api/v1/routers/predictions.py` :
  - `DailyPredictionCategory` : ajouter `is_provisional: bool | None`
  - `DailyPredictionDebugCategory` : ajouter `is_provisional: bool | None`
  - Dans `get_daily_prediction()`, mapping : `is_provisional=s.get("is_provisional")`
  - Dans `debug_daily_prediction()`, mapping : `is_provisional=s.get("is_provisional")`

### T6 — Mettre à jour le type TypeScript (AC5)

- [x] Dans `frontend/src/types/dailyPrediction.ts` :
  ```typescript
  export interface DailyPredictionCategory {
    // ... champs existants ...
    is_provisional?: boolean | null;
  }
  ```

### T7 — Disclaimer éditorial (AC6)

- [x] Dans `backend/app/api/v1/routers/predictions.py`, méthode `_build_summary()` :
  - Si `full_run.get("is_provisional_calibration")` est `True` et que le spread des `note_20` top3 est < 3 → ajouter `low_score_variance: bool = True` dans `DailyPredictionSummary` et le peupler
  - Ajouter `low_score_variance: bool = False` au Pydantic model `DailyPredictionSummary`
- [x] Dans `frontend/src/types/dailyPrediction.ts` : ajouter `low_score_variance?: boolean` à `DailyPredictionSummary`

### T8 — Tests (AC7)

- [x] Créer `backend/app/tests/unit/test_percentile_calibrator_provisional.py` :
  - `test_day_relative_gives_spread` : 5 catégories provisoires avec raw_days variés → scores dans [2, 18], pas 5x 10
  - `test_degenerate_day_fallback` : tous raw_days = 0.0 → scores = 10 (DEFAULT), pas d'erreur
  - `test_mixed_calibration` : 2 calibrées + 4 provisoires → les 2 calibrées non affectées
  - `test_too_few_provisional` : < 3 provisoires → DEFAULT_CALIBRATION utilisée
- [x] Relancer `backend/app/tests/unit/test_daily_prediction_service.py` — doit passer sans modification

## Dev Notes

### Diagnostic de la cause racine

Le problème "notes à 10/20 partout" vient de deux facteurs cumulatifs :

1. **Raw days proches de zéro** : les contributions cumulées (`raw_day`) de chaque catégorie tendent vers 0.0 quand il n'y a pas d'événement astrologique majeur ciblant spécifiquement une catégorie. L'`TemporalAggregator` somme des contributions qui sont souvent petites et se compensent.

2. **`DEFAULT_CALIBRATION` fixe et symétrique** : quand tous les `raw_day` sont dans [-0.1, +0.1], la calibration par défaut `(p05=-1.5, p25=-0.5, p50=0.0, p75=0.5, p95=1.5)` les mappe dans [9, 11] — un score quasi-identique pour toutes les catégories.

La calibration day-relative résout le problème 2 en permettant la discrimination relative : si catégorie A a `raw_day=0.1` et catégorie B a `raw_day=-0.1`, A obtient ~14 et B obtient ~6 sur la journée, même si les deux valeurs absolues sont faibles.

### Architecture établie — points d'attention

- **`editorial_category_scores`** : dans `EngineOrchestrator._build_prediction_outputs()`, ce dict est construit avec `{"note_20": ..., "raw_score": ..., "power": ..., "volatility": ..., "sort_order": ...}`. C'est là qu'on ajoute `"is_provisional": bool` pour chaque catégorie, sans toucher aux interfaces externes. Voir [Source: backend/app/prediction/engine_orchestrator.py#L426-L445]
- **Définition de "provisoire" à réutiliser partout** : ne pas se limiter à `sample_size == 0`. Le runtime existant considère aussi l'absence de calibration et le label `"provisional"` comme des marqueurs de provisoire. La story doit rester cohérente avec `PredictionContextLoader`.

- **`calibrate_all_provisional_aware` appliqué aux `notes_by_step`** : attention, `notes_by_step` est calculé via des appels individuels à `self._percentile_calibrator.calibrate(raw_step_val, calibrations.get(cat))` (lignes ~446-455). Pour cohérence, les catégories provisoires dans `notes_by_step` doivent aussi utiliser la day-relative calibration — sinon les `time_blocks` et `turning_points` resteraient basés sur les scores par step non-discriminés. Stocker la `day_relative_calibration` comme variable locale dans `_build_prediction_outputs()` et la passer dans les appels per-step pour les catégories provisoires.

- **Impact sur `BlockGenerator` et `TurningPointDetector`** : ces composants utilisent `notes_by_step` calibrés. Avec la day-relative calibration, les notes par step auront plus de variance → meilleurs `tone_code` des blocs, plus de `TurningPoint` détectés. C'est l'effet souhaité.

- **Compatibilité ascendante DB** : la colonne `is_provisional` est nullable. Les runs existants auront `NULL` (pas `False`) → `DailyPredictionCategory.is_provisional=None` en API, que le front doit traiter comme "inconnu" (pas comme "non-provisoire").
- **Ne pas détourner `run_metadata.calibration_label`** : le label global de run reste un signal de traçabilité dataset/ruleset (`provisional`, `mixed`, `vX`). Le `day-relative` introduit ici est un mécanisme interne de secours pour certaines catégories, pas un remplacement du label global du run.

### Pattern de migration Alembic

Le repo courant utilise des identifiants **séquentiels** au format `YYYYMMDD_XXXX` pour toutes les migrations récentes (depuis `20260307_0031`). Les anciennes migrations antérieures à cette série utilisaient des hashes hexadécimaux (ex: `fd1d41d35808_...`), mais le pattern actif depuis Epic 39 est séquentiel. La nouvelle migration doit suivre ce format et calculer son `down_revision` depuis l'état courant du dossier `backend/migrations/versions/`.

### Fichiers à toucher

| Fichier | Opération |
|---------|-----------|
| `backend/app/prediction/calibrator.py` | Ajouter `_compute_day_relative_calibration()` + `calibrate_all_provisional_aware()` |
| `backend/app/prediction/engine_orchestrator.py` | Utiliser `calibrate_all_provisional_aware()` + stocker day_cal pour notes_by_step + injecter `is_provisional` dans `editorial_category_scores` |
| `backend/app/infra/db/models/daily_prediction.py` | Ajouter `is_provisional` à `DailyPredictionCategoryScoreModel` |
| `backend/migrations/versions/20260308_0042_add_is_provisional_to_category_scores.py` | Créer |
| `backend/app/prediction/persistence_service.py` | Lire `score_data.get("is_provisional")` dans `_save_scores()` |
| `backend/app/infra/db/repositories/daily_prediction_repository.py` | Inclure `is_provisional` dans `get_full_run()` category_scores |
| `backend/app/api/v1/routers/predictions.py` | `DailyPredictionCategory` + `DailyPredictionDebugCategory` + `DailyPredictionSummary.low_score_variance` + mappings |
| `frontend/src/types/dailyPrediction.ts` | `is_provisional?: boolean | null` + `low_score_variance?: boolean` |
| `backend/app/tests/unit/test_percentile_calibrator_provisional.py` | Créer |

### Source hints

- Calibrateur actuel : [Source: backend/app/prediction/calibrator.py#L1-L103]
- `calibrate_all()` appelé dans orchestrator : [Source: backend/app/prediction/engine_orchestrator.py#L422-L425]
- `notes_by_step` calcul : [Source: backend/app/prediction/engine_orchestrator.py#L446-L455]
- `editorial_category_scores` construction : [Source: backend/app/prediction/engine_orchestrator.py#L426-L445]
- `get_full_run()` category_scores dict : [Source: backend/app/infra/db/repositories/daily_prediction_repository.py#L216-L228]
- `DailyPredictionCategory` Pydantic : [Source: backend/app/api/v1/routers/predictions.py#L38-L46]
- Type TS frontend : [Source: frontend/src/types/dailyPrediction.ts#L13-L21]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/calibrator.py` — `calibrate_all_provisional_aware()` avec kwargs optionnels + `get_provisional_categories()` + `compute_day_relative_calibration()`
- `backend/app/prediction/engine_orchestrator.py` — utilise `calibrate_all_provisional_aware()`, calcule provisional_cats/day_relative_cal une seule fois, injecte `is_provisional` dans `editorial_category_scores`
- `backend/app/infra/db/models/daily_prediction.py` — champ `is_provisional` sur `DailyPredictionCategoryScoreModel`
- `backend/migrations/versions/20260308_0042_add_is_provisional_to_category_scores.py` — migration Alembic
- `backend/app/prediction/persistence_service.py` — `_save_scores()` lit `score_data.get("is_provisional")`
- `backend/app/infra/db/repositories/daily_prediction_repository.py` — `get_full_run()` inclut `is_provisional`
- `backend/app/api/v1/routers/predictions.py` — `DailyPredictionCategory.is_provisional`, `DailyPredictionDebugCategory.is_provisional`, `DailyPredictionSummary.calibration_note` + `low_score_variance`, logique AC6 dans `_build_summary()`
- `frontend/src/types/dailyPrediction.ts` — `is_provisional`, `low_score_variance`, `calibration_note` sur les interfaces TS
- `backend/app/tests/unit/test_percentile_calibrator_provisional.py` — 4 tests unitaires calibrateur
- `backend/app/tests/integration/test_daily_prediction_api.py` — 3 tests AC4/AC6 : `is_provisional` par catégorie, `calibration_note`, `low_score_variance`

### Completion Notes List

- AC6 : `calibration_note: str | None` ajouté à `DailyPredictionSummary` (backend + TS) — peuplé avec un disclaimer textuel quand `is_provisional_calibration=True`. C'est la livraison de la condition principale d'AC6 ; `low_score_variance` est le signal optionnel complémentaire.
- DRY fix : `provisional_cats` et `day_relative_cal` calculés une seule fois dans `_build_prediction_outputs()`, passés via kwargs à `calibrate_all_provisional_aware()`.
- Type fix : `get_provisional_categories(category_codes: Iterable[str], ...)` — annotation corrigée de `list[str]` vers `Iterable[str]`.

## Change Log

- 2026-03-08 : Story créée pour Epic 40 — discrimination scores calibration provisoire.
- 2026-03-09 : Implémentation complète. Code review : AC6 complété (calibration_note), DRY fix orchestrator, type annotation calibrator, 3 tests d'intégration ajoutés.
