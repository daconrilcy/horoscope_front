# Acceptance Traceability - CS-189

| AC | Statut | Preuve code | Preuve validation |
|---|---|---|---|
| AC1 Runtime DTO fields | PASS | `FixedStarData` enrichi, `get_fixed_stars()` charge magnitude/keywords/source, `_freeze_fixed_star()` preserve les champs. | `pytest -q app/tests/unit/test_prediction_reference_repository.py` via suite ciblee: PASS. |
| AC2 Orbe non hardcodee | PASS | `EnrichedAstroEventsBuilder._compute_fixed_star_conjunctions()` lit `fixed_star_orb_deg`. | Builder pytest multi-orbes: PASS; scan `rg -n "dist.*1\.0" ...`: zero hit. |
| AC3 Filtrage magnitude explicite | PASS | `fixed_star_max_visual_magnitude` filtre les magnitudes trop faibles, conserve magnitude absente. | `test_compute_fixed_star_conjunctions_filters_visual_magnitude`: PASS. |
| AC4 Metadata explicite | PASS | Metadata `orb_max`, `star_key`, `star_display_name`, `visual_magnitude`, source et keywords. | Builder pytest + projection publique existante: PASS. |
| AC5 Contribution poids positif | PASS | `fixed_star_base_weight` alimente `base_weight`; `DomainRouter` route via `fixed_star_category_weights`; `ContributionCalculator` reste le calculateur. | `test_fixed_star_event_routes_with_explicit_ruleset_weights` et `test_fixed_star_conjunction_contributes_with_runtime_metadata`: PASS. |
| AC6 No local fixed-star catalog | PASS | Aucun catalogue local ajoute; seed ruleset ajoute seulement des parametres runtime. | Scan `_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_`: zero hit. |
| AC7 Validation backend ciblee | PASS | Tests et lint executes dans venv. | `ruff format .`, `ruff check .`, pytests cibles et story lint/validate: PASS. |

## Integration evidence

- `pytest --long -q app/tests/integration/test_seed_31_prediction_v2.py`: PASS,
  7 passed. La commande `--long` est requise car `backend/conftest.py`
  deselectionne les tests integration/slow dans la suite rapide.
