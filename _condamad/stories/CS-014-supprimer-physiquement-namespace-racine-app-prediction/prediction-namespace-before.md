# Inventaire avant suppression

## Commandes de baseline

- `git status --short` depuis la racine: workspace deja modifie sur `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md` et capsules CS-014 a CS-018 non suivies.
- `git ls-files backend/app/prediction`: 55 fichiers suivis sous le namespace legacy.
- `(Get-ChildItem backend\app\prediction -Recurse -File | Where-Object { $_.FullName -notmatch '__pycache__' }).Count`: 55 fichiers hors caches Python.
- `rg -l "app\.prediction" backend\app backend\tests -g "*.py"`: consommateurs actifs dans `app`, `app/tests` et `backend/tests`.

## Fichiers suivis avant suppression

- `backend/app/prediction/__init__.py`
- `backend/app/prediction/aggregator.py`
- `backend/app/prediction/astro_calculator.py`
- `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/prediction/block_generator.py`
- `backend/app/prediction/calibrator.py`
- `backend/app/prediction/category_codes.py`
- `backend/app/prediction/context.py`
- `backend/app/prediction/contribution_calculator.py`
- `backend/app/prediction/daily_prediction_evidence_builder.py`
- `backend/app/prediction/decision_window_builder.py`
- `backend/app/prediction/domain_router.py`
- `backend/app/prediction/editorial_builder.py`
- `backend/app/prediction/editorial_service.py`
- `backend/app/prediction/editorial_template_engine.py`
- `backend/app/prediction/editorial_templates/en/*.txt` (8 templates)
- `backend/app/prediction/editorial_templates/fr/*.txt` (8 templates)
- `backend/app/prediction/enriched_astro_events_builder.py`
- `backend/app/prediction/event_detector.py`
- `backend/app/prediction/exceptions.py`
- `backend/app/prediction/explainability.py`
- `backend/app/prediction/impulse_signal_builder.py`
- `backend/app/prediction/input_hash.py`
- `backend/app/prediction/intraday_activation_builder.py`
- `backend/app/prediction/natal_sensitivity.py`
- `backend/app/prediction/persisted_baseline.py`
- `backend/app/prediction/persisted_relative_score.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/prediction/public_astro_daily_events.py`
- `backend/app/prediction/public_astro_vocabulary.py`
- `backend/app/prediction/public_domain_taxonomy.py`
- `backend/app/prediction/public_label_catalog.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/public_score_mapper.py`
- `backend/app/prediction/regime_segmenter.py`
- `backend/app/prediction/relative_scoring_calculator.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/temporal_kernel.py`
- `backend/app/prediction/temporal_sampler.py`
- `backend/app/prediction/transit_signal_builder.py`
- `backend/app/prediction/turning_point_detector.py`

## Consommateurs avant migration

- Services applicatifs: `app/services/prediction/*`, `app/services/user_profile/prediction_baseline_service.py`, `app/services/llm_generation/horoscope_daily/narration_service.py`.
- Repositories infra: `daily_prediction_repository.py`, `prediction_schemas.py`, `user_prediction_baseline_repository.py`.
- Routeurs API: `app/api/v1/routers/public/predictions.py`, `app/api/v1/routers/internal/llm/qa.py`.
- Jobs: `app/jobs/generate_daily_calibration_dataset.py`.
- Tests collectes: `backend/app/tests/**` et `backend/tests/**`.
