# Fixed Stars Runtime Before - CS-189

Baseline capture before implementation:

- `FixedStarData` exposed only `key`, `display_name`, `ecliptic_longitude_deg`.
- `PredictionReferenceRepository.get_fixed_stars()` selected only star and definition rows, losing `visual_magnitude`, keywords and source metadata.
- `PredictionContextLoader._freeze_fixed_star()` preserved only the three original fields.
- `EnrichedAstroEventsBuilder._compute_fixed_star_conjunctions()` used `dist <= 1.0` directly.
- Retained `fixed_star_conjunction` events used `base_weight=0.0` and metadata only carried `star_display_name`.

Impact: fixed stars were visible in `astro_daily_events.fixed_stars`, but had no effective score contribution because `ContributionCalculator` multiplies by `event.base_weight`.
