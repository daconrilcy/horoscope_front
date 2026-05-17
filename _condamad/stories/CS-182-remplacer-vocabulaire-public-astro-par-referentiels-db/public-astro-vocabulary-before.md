<!-- Inventaire initial de fermeture CS-182 avant suppression du vocabulaire local. -->

# CS-182 public astro vocabulary before

Closure status: open-before-implementation

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `PublicAstroVocabulary` | classe runtime | historical-facade | `public_projection.py`, `public_astro_daily_events.py`, `astrologer_prompt_builder.py`, tests publics prediction | formateur de labels sans données DB-backed | replace-consumer | scan initial `rg -n "PublicAstroVocabulary" backend/app/domain/prediction backend/app/tests backend/tests -g "*.py"` | conserve `_STAR_DATA` et `_ASPECT_TONES` comme surface runtime |
| `_STAR_DATA` | constante DB-backed | historical-facade | `star()`, `fixed_star_longitudes()`, `fixed_star_display_name()` | `AstralFixedStarModel` + `AstralFixedStarDefinitionModel` via `PredictionContext.fixed_stars` | delete | `backend/app/domain/prediction/public_astro_vocabulary.py` | duplication des longitudes et noms DB |
| `_ASPECT_TONES` | mapping DB-backed | historical-facade | `PublicAstroFoundationPolicy.dominant_aspects[*].tonality` | `AspectProfileData.energy_type` depuis `PredictionContext.aspect_profiles` | delete | `backend/app/domain/prediction/public_astro_vocabulary.py` | divergence avec les profils d'aspects seedés |
| `fixed_star_longitudes()` | helper runtime | historical-facade | `EnrichedAstroEventsBuilder._compute_fixed_star_conjunctions()` | `PredictionContext.fixed_stars` | delete | import direct dans `enriched_astro_events_builder.py` | détection daily déconnectée du référentiel DB |
| `fixed_star_display_name()` | helper runtime | historical-facade | metadata des événements fixed star | `FixedStarData.display_name` | delete | import direct dans `enriched_astro_events_builder.py` | affichage public déconnecté du référentiel DB |

Regression guardrails consulted: `RG-108`, `RG-110`, `RG-112`, `RG-113`.
