# Fixed Stars Runtime After - CS-189

Runtime state after implementation:

- `FixedStarData` carries `visual_magnitude`, `keywords`, `source_category` and `source_key`.
- `PredictionReferenceRepository.get_fixed_stars()` joins `astral_fixed_star_keywords` and `astral_reference_sources`.
- `PredictionContextLoader._freeze_fixed_star()` preserves the enriched immutable contract.
- `EnrichedAstroEventsBuilder._compute_fixed_star_conjunctions()` reads:
  - `fixed_star_orb_deg`
  - `fixed_star_max_visual_magnitude`
  - `fixed_star_base_weight`
- Retained events expose:
  - `orb_max`
  - `star_key`
  - `star_display_name`
  - `visual_magnitude`
  - `fixed_star_source_category`
  - `fixed_star_source_key`
  - `fixed_star_keywords`
- `DomainRouter` routes `fixed_star_conjunction` via `fixed_star_category_weights`.
- `ContributionCalculator` remains the single contribution engine and produces a non-zero value for a retained event.

Validation summary:

- Builder tests prove runtime reference fields, ruleset orb and magnitude filtering.
- Repository tests prove DB-backed metadata loading.
- Router and contribution tests prove explicit routing and non-zero contribution.
- Public projection test keeps `Lune conjoint à l'étoile Regulus`.
- Seed integration test proves an existing locked V2 ruleset missing the new
  fixed-star parameters is repaired idempotently.
