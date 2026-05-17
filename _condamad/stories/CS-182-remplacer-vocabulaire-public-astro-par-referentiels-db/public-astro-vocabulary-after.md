<!-- Preuve finale de fermeture CS-182 après suppression du vocabulaire local. -->

# CS-182 public astro vocabulary after

Closure status: closed

| Item | Former surface | Replacement | Evidence | Result |
|---|---|---|---|---|
| Classe legacy | `backend/app/domain/prediction/public_astro_vocabulary.py::PublicAstroVocabulary` | `backend/app/domain/prediction/astro_label_formatter.py::AstroLabelFormatter` sans données DB-backed | fichier legacy supprimé; imports runtime migrés | PASS |
| Étoiles fixes | `_STAR_DATA`, `fixed_star_longitudes()`, `fixed_star_display_name()` | `PredictionContext.fixed_stars` chargé par `PredictionReferenceRepository.get_fixed_stars()` | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py` | PASS |
| Détection fixed star daily | mapping local de longitudes | contrat runtime `fixed_stars` injecté dans `EnrichedAstroEventsBuilder` | `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py` | PASS |
| Noms publics d'étoiles | `PublicAstroVocabulary.star()` | `AstroEvent.metadata["star_display_name"]` produit depuis le référentiel runtime | `pytest -q tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_time_window.py` | PASS |
| Tonalités d'aspects | `_ASPECT_TONES` | `AspectProfileData.energy_type` via `aspect_profiles` injectés à la projection | `pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py` | PASS |
| Garde anti-retour | ancienne exception CS-181 | guards AST/scans `RG-113` | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py` | PASS |
| Correction review | omission de propagation `aspect_profiles` dans l'assembleur | passage explicite à `PublicAstroFoundationPolicy` | `pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py tests/integration/test_v4_scenarios.py` | PASS |

Scans finaux:

- `rg -n "PublicAstroVocabulary|_STAR_DATA|_ASPECT_TONES|fixed_star_longitudes|fixed_star_display_name" app/domain/prediction app/tests tests -g "*.py"`: zéro hit.
- `rg -n '"nuance"|"fluidité"|"ajustement"|"intensification"|"adaptation"' app/domain/prediction -g "*.py"`: zéro hit.

Allowed differences: `dominant_aspects[*].tonality` expose désormais `AspectProfileData.energy_type`, par exemple `friction_activation` au lieu de l'ancienne tonalité locale.
