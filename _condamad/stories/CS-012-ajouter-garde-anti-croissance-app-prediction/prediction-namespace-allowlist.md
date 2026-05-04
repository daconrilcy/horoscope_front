# Allowlist namespace prediction - CS-012

<!-- Artefact persistant: capture l'etat autorise de `backend/app/prediction` pour la garde anti-croissance. -->

## Objectif

Cette allowlist est la source persistante consultee par
`backend/app/tests/unit/test_daily_prediction_guardrails.py`. Tout nouveau fichier Python
dans `backend/app/prediction` doit etre classe ici avec une justification explicite.

## Fichiers Python autorises

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

## Exceptions d'import autorisees

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

Aucune exception active. Les anciennes exceptions `context_loader.py`,
`persistence_service.py` et `public_projection.py` sont fermees par CS-007 et CS-009.

## Imports interdits

- `from app.api` ou `import app.api`
- `fastapi`
- `from app.core.config` ou symbole `settings`
- `from app.infra` hors owner canonique externe a `app.prediction`
- `from sqlalchemy` ou `import sqlalchemy`
- `AIEngineAdapter`
- `LLMNarrator`

## Condition de mise a jour

Toute modification de cette allowlist doit accompagner un changement de code explicite,
une justification d'ownership et une validation par:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_daily_prediction_guardrails.py
```
