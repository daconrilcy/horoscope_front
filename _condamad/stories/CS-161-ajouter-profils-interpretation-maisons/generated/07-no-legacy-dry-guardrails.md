# No Legacy / DRY Guardrails

## Canonical destination

- `house_interpretation_profiles` is the only editorial house interpretation table introduced by this story.
- `astral_houses` remains the stable minimal house vocabulary.
- `astral_prediction_daily_house_profiles` remains the technical prediction profile table.
- `astral_house_category_weights` remains the product category routing table.

## Forbidden patterns

- Adding interpretation keywords to `astral_houses`.
- Reusing `astral_prediction_daily_house_profiles` for editorial prompt vocabulary.
- Creating a generic `astro_characteristics` replacement.
- Importing `HouseInterpretationProfileModel` from `backend/app/domain/astrology`.
- Adding compatibility aliases for old `houses` / `house_profiles` names.

## Required negative evidence

- `rg -n "house_interpretation_profiles|HouseInterpretationProfileModel" app/domain/astrology -g "*.py"` must be zero-hit.
- `rg -n "AstroCharacteristicModel|astro_characteristics" app tests -g "*.py"` must not show active model/table reintroduction.
- Existing table-name tests must continue to prove `astral_houses`, `astral_prediction_daily_house_profiles`, and `astral_house_category_weights`.

## Exceptions

- None.

## Review checklist

- Table name is dedicated and editorial.
- JSON fields are not split into a keyword row table.
- Unique constraint prevents duplicate profile rows per version/house/language/tradition.
- No runtime, API, frontend, or prediction scoring consumer was added.
