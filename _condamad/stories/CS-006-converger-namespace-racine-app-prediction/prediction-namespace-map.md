# Prediction Namespace Map - CS-006

## Mapping

| Current baseline file | Responsibility | Target owner | CS-006 action |
|---|---|---|---|
| `backend/app/prediction/__init__.py` | Legacy package marker | none / removable later | Keep marker only, no re-export |
| `backend/app/prediction/aggregator.py` | Pure aggregation/scoring | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/astro_calculator.py` | Astro calculation | `backend/app/domain/prediction/astrology` | Not moved |
| `backend/app/prediction/astrologer_prompt_builder.py` | Horoscope daily LLM facts | `backend/app/services/llm_generation/horoscope_daily` | Not moved |
| `backend/app/prediction/block_generator.py` | Pure block generation | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/calibrator.py` | Pure calibration math | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/category_codes.py` | Pure category normalization | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/context_loader.py` | DB context loading | `backend/app/infra/db` adapter used by `services/prediction` | Not moved |
| `backend/app/prediction/contribution_calculator.py` | Pure scoring contribution | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/daily_prediction_evidence_builder.py` | Pure evidence pack assembly | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/decision_window_builder.py` | Pure decision windows | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/domain_router.py` | Pure domain routing | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/editorial_builder.py` | Deterministic editorial assembly | `backend/app/services/prediction/editorial` | Not moved |
| `backend/app/prediction/editorial_service.py` | Deterministic editorial service | `backend/app/services/prediction/editorial` | Not moved |
| `backend/app/prediction/editorial_template_engine.py` | Editorial template engine | `backend/app/services/prediction/editorial` | Not moved |
| `backend/app/prediction/editorial_templates/en/intro_du_jour.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/intro_du_jour.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/meilleure_fenetre.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/meilleure_fenetre.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/phrase_pivot.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/phrase_pivot.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/prudence_argent.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/prudence_argent.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/prudence_sante.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/prudence_sante.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/resume_bloc_horaire.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/resume_bloc_horaire.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/resume_categorie.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/resume_categorie.txt` | Not moved |
| `backend/app/prediction/editorial_templates/en/resume_turning_point.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/en/resume_turning_point.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/intro_du_jour.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/intro_du_jour.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/meilleure_fenetre.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/meilleure_fenetre.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/phrase_pivot.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/phrase_pivot.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/prudence_argent.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/prudence_argent.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/prudence_sante.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/prudence_sante.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/resume_bloc_horaire.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/resume_bloc_horaire.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/resume_categorie.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/resume_categorie.txt` | Not moved |
| `backend/app/prediction/editorial_templates/fr/resume_turning_point.txt` | Localized editorial template | `backend/app/services/prediction/editorial/templates/fr/resume_turning_point.txt` | Not moved |
| `backend/app/prediction/enriched_astro_events_builder.py` | Astro event enrichment | `backend/app/domain/prediction/astrology` | Not moved |
| `backend/app/prediction/engine_orchestrator.py` | Application orchestration | `backend/app/services/prediction/engine_orchestrator.py` | Moved |
| `backend/app/prediction/event_detector.py` | Pure event detection | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/exceptions.py` | Prediction domain errors | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/explainability.py` | Pure explainability assembly | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/impulse_signal_builder.py` | Pure signal builder | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/input_hash.py` | Pure input hashing | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/intraday_activation_builder.py` | Pure signal builder | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/natal_sensitivity.py` | Pure sensitivity scoring | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/persisted_baseline.py` | Persistence read model | `backend/app/infra/db` or `services/prediction/types` | Not moved |
| `backend/app/prediction/persisted_relative_score.py` | Persistence read model | `backend/app/infra/db` or `services/prediction/types` | Not moved |
| `backend/app/prediction/persisted_snapshot.py` | Persistence read model | `backend/app/infra/db` or `services/prediction/types` | Not moved |
| `backend/app/prediction/persistence_service.py` | Persistence adapter/service | `backend/app/infra/db` adapter or `services/prediction` | Not moved |
| `backend/app/prediction/public_astro_daily_events.py` | Public deterministic taxonomy | `backend/app/domain/prediction/public` | Not moved |
| `backend/app/prediction/public_astro_vocabulary.py` | Public deterministic taxonomy | `backend/app/domain/prediction/public` | Not moved |
| `backend/app/prediction/public_domain_taxonomy.py` | Public deterministic taxonomy | `backend/app/domain/prediction/public` | Not moved |
| `backend/app/prediction/public_label_catalog.py` | Public deterministic taxonomy | `backend/app/domain/prediction/public` | Not moved |
| `backend/app/prediction/public_projection.py` | Public projection assembly | `backend/app/services/prediction` | Not moved |
| `backend/app/prediction/public_score_mapper.py` | Public score mapping | `backend/app/domain/prediction/public` | Not moved |
| `backend/app/prediction/regime_segmenter.py` | Pure regime segmentation | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/relative_scoring_calculator.py` | Pure relative scoring | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/schemas.py` | Internal engine contracts | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/temporal_kernel.py` | Pure temporal math | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/temporal_sampler.py` | Pure temporal sampling | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/transit_signal_builder.py` | Pure signal builder | `backend/app/domain/prediction` | Not moved |
| `backend/app/prediction/turning_point_detector.py` | Pure turning point detection | `backend/app/domain/prediction` | Not moved |
