<!-- Preuve runtime des référentiels DB utilisés par CS-182. -->

# CS-182 runtime reference evidence

Closure status: closed

## Evidence

| Commande | Résultat | Détail |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | PASS | 1 fichier reformaté après correction de review. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | PASS | Aucun problème après correction des imports. |
| `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py` | PASS | 50 passed. |
| `pytest -q app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py` | PASS | 10 passed. |
| `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_time_window.py` | PASS | 36 passed. |
| `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py` | PASS | 4 passed. |
| `pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py tests/integration/test_v4_scenarios.py` | PASS | 26 passed, 4 deselected; validation de review après correction de propagation `aspect_profiles`. |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py tests/unit/prediction/test_enriched_astro_events_builder.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_time_window.py tests/unit/prediction/test_astrologer_prompt_builder.py` | PASS | 101 passed. |
| Scan symboles legacy | PASS | Zéro hit sur les symboles `RG-113`. |
| Scan anciennes tonalités locales | PASS | Zéro hit sous `app/domain/prediction`. |
| `git diff --check` | PASS | Aucun whitespace error. |
| Démarrage local backend | PASS | `uvicorn app.main:app` a répondu `200` sur `http://127.0.0.1:8765/health`, puis le processus a été arrêté. |
| `pytest -q` | FAIL HORS PERIMETRE | 2610 passed, 1 skipped, 1175 deselected, 3 failures restantes après correction de l'allowlist SQL: `test_engine_output_has_calibration_metadata`, `test_compute_v3_with_factors`, `test_compute_v3_aspects_can_lower_structural_score`. Les échecs concernent les règles d'orbe/profils natal hors fichiers CS-182. |

## Runtime source of truth

- `PredictionReferenceRepository.get_fixed_stars()` joint `astral_fixed_stars` et `astral_fixed_star_definitions`, filtre `is_active`, puis retourne des `FixedStarData` typés.
- `PredictionContext.fixed_stars` transporte ce contrat jusqu'au domaine prediction.
- `EnrichedAstroEventsBuilder` consomme uniquement `loaded_context.prediction_context.fixed_stars` pour détecter les conjonctions fixed star.
- `PublicAstroFoundationPolicy` lit `AspectProfileData.energy_type` depuis les profils d'aspects injectés; l'absence de profil déclenche une erreur explicite.
- `PublicPredictionAssembler` propage les profils d'aspects chargés par les routes API jusqu'à `PublicAstroFoundationPolicy`; `app/tests/unit/test_public_projection.py::test_assembler_propagates_aspect_profiles_to_astro_foundation` couvre ce contrat.

## Review fix evidence

- Issue 1 corrigée: `PublicPredictionAssembler` transmettait `aspect_profiles` à `PublicTimeWindowPolicy.build()`, qui ne l'accepte pas, cassant les parcours assembleur existants.
- Issue 2 corrigée: `aspect_profiles` était chargé côté API mais non transmis à `PublicAstroFoundationPolicy`, ce qui empêchait `dominant_aspects[*].tonality` de provenir du profil DB-backed dans le chemin assembleur.
- Issue 3 corrigée: les imports ajoutés dans les routeurs API déplaçaient les lignes exactes de la garde SQL routeur; l'allowlist `harden-api-adapter-boundary-guards/router-sql-allowlist.md` a été réalignée sans nouvelle dette détectée.
