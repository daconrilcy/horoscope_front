# No Legacy / DRY Guardrails

## Canonical Ownership

- DB-backed signs, planets, aspects and houses: `AstrologyTranslationResolver`.
- Prediction display adapter: `PublicAstroVocabulary`, consuming an injected label contract only.
- Service/API layers own DB-backed resolver construction because they have the SQLAlchemy session.

## Forbidden Active Surfaces

- Local FR mappings for signs, planets, aspects, houses, effects under `backend/app/domain/prediction`.
- Old helper names listed in the story.
- Any `app.services` import from `backend/app/domain/prediction`.
- Compatibility aliases, re-exports, wrappers, or renamed equivalents of the removed mappings.

## Required Negative Evidence

- Forbidden-symbol scans under `backend/app/domain/prediction`.
- Guard test for RG-110.
- Boundary scan proving no resolver/service import inside prediction.

## Exceptions

- Fixed-star proper names remain non DB-backed technical display data.
- Existing editorial strings outside DB-backed labels remain outside this story unless they recreate the forbidden mappings.
