# No Legacy / DRY Guardrails - CS-189

## Decisions

- No local fixed-star catalog was introduced.
- No `_STAR_DATA`, `fixed_star_longitudes`, `fixed_star_display_name` or
  `FIXED_STAR_` symbol remains in active prediction/runtime/tests.
- No direct DB access was added to `domain/prediction`.
- `domain/astrology` remains independent from `domain/prediction`.
- Scoring continues through `DomainRouter` and `ContributionCalculator`.

## Guards run

- `rg -n "_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"`: zero hit.
- `rg -n "dist.*1\.0" app/domain/prediction/enriched_astro_events_builder.py`: zero hit.
- `rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"`: zero hit.
- `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py`: PASS.

## DRY check

- `FixedStarData` is the single DTO for fixed-star runtime data.
- `PredictionReferenceRepository.get_fixed_stars()` remains the single DB-backed
  loading point.
- The builder only detects events; routing and contribution stay in their
  existing owners.
