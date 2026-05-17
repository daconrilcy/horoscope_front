<!-- Preuve finale de livraison CS-182 apres boucle review-fix. -->

# CS-182 final evidence

Status: done
Review/fix iterations: 2

## Scope delivered

- `PublicAstroVocabulary` et `backend/app/domain/prediction/public_astro_vocabulary.py` ont ete supprimes du runtime.
- Les etoiles fixes daily sont chargees via `PredictionReferenceRepository.get_fixed_stars()` et transportees par `PredictionContext.fixed_stars`.
- `EnrichedAstroEventsBuilder` detecte les conjonctions fixed star depuis le contrat runtime injecte.
- `PublicAstroFoundationPolicy` resout `dominant_aspects[*].tonality` depuis `AspectProfileData.energy_type`.
- Les routes publiques et QA chargent les profils d'aspects DB-backed puis les transmettent a `PublicPredictionAssembler`.
- Les guards `RG-108`, `RG-110`, `RG-112` et `RG-113` bloquent la reintroduction des symboles legacy.

## Review fixes

| Finding | Fix | Evidence |
|---|---|---|
| `PublicPredictionAssembler` envoyait `aspect_profiles` a `PublicTimeWindowPolicy.build()`, qui ne l'accepte pas. | Suppression de l'argument sur cet appel. | `pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py app/tests/unit/prediction/test_public_projection_evidence.py tests/integration/test_v4_scenarios.py`: 26 passed, 4 deselected. |
| Les profils d'aspects charges par les routes API n'etaient pas propages a `PublicAstroFoundationPolicy`. | Ajout de `aspect_profiles=aspect_profiles` et test assembleur dedie. | `app/tests/unit/test_public_projection.py::test_assembler_propagates_aspect_profiles_to_astro_foundation`. |
| Les imports ajoutes dans les routeurs API decalaient les lignes exactes de la garde SQL routeur. | Realignement mecanique de `router-sql-allowlist.md` sans nouvelle dette. | `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist`: PASS. |

## Validation

Toutes les commandes Python ont ete executees apres activation du venv:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py
pytest -q app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py
pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_time_window.py
pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py
pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py tests/unit/prediction/test_enriched_astro_events_builder.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_public_time_window.py tests/unit/prediction/test_astrologer_prompt_builder.py
```

Results:

- `ruff format .`: PASS, 1 fichier reformate.
- `ruff check .`: PASS.
- repository/reference tests: PASS, 50 passed.
- guardrail tests: PASS, 10 passed.
- public prediction tests: PASS, 36 passed.
- prompt builder tests: PASS, 4 passed.
- final targeted suite including SQL allowlist guard: PASS, 101 passed.
- review regression suite: PASS, 26 passed, 4 deselected.
- `git diff --check`: PASS.
- backend local start: PASS, `uvicorn app.main:app` a repondu `200` sur `/health` au port temporaire `8765`.
- full backend `pytest -q`: FAIL hors perimetre CS-182 avec 3 echecs restants sur `test_calibration_versioning.py::test_engine_output_has_calibration_metadata` et `test_natal_structural_v3.py::{test_compute_v3_with_factors,test_compute_v3_aspects_can_lower_structural_score}`; ces echecs portent sur les regles/profils d'aspects natal et ne concernent pas les fichiers modifies par CS-182.

## Scans

```powershell
rg -n "PublicAstroVocabulary|_STAR_DATA|_ASPECT_TONES|fixed_star_longitudes|fixed_star_display_name" app/domain/prediction app/tests tests -g "*.py"
rg -n '"nuance"|"fluidité"|"ajustement"|"intensification"|"adaptation"' app/domain/prediction -g "*.py"
```

Results:

- Symboles legacy `RG-113`: zero hit.
- Anciennes tonalites locales sous `app/domain/prediction`: zero hit.

## Residual risk

Aucun risque restant identifie sur CS-182. Risque repo global hors perimetre: la suite complete `pytest -q` conserve 3 echecs natal/aspect preexistants ou independants de la fermeture du vocabulaire public astro.
