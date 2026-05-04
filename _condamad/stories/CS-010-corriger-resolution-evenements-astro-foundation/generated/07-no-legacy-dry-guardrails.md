# No Legacy / DRY Guardrails

## Applicable invariant

- `RG-030`: `PublicAstroFoundationPolicy` must read canonical event sources `events` and `detected_events`, with support for `aspect_exact_*`.

## DRY stance

- Event resolution is centralized in `resolve_public_astro_events`.
- Exact aspect event types are centralized in `PUBLIC_ASTRO_ASPECT_EVENT_TYPES`.
- `PublicAstroFoundationPolicy` and `PublicAstroDailyEventsPolicy` reuse those shared definitions.

## Forbidden patterns

- New public field replacing `astro_foundation`.
- New event source outside `events`, `detected_events`, or persisted `v3_metrics.detected_events` already used by the public daily events policy.
- Compatibility wrapper, alias, re-export, or fallback to a non-canonical event path.
- Duplicate aspect taxonomy inside `PublicAstroFoundationPolicy`.

## Search evidence

| Pattern | Classification | Action | Status |
|---|---|---|---|
| `aspect_exact_to_angle|aspect_exact_to_luminary|aspect_exact_to_personal|detected_events` in `app/prediction` | canonical runtime taxonomy and event resolution references | Reviewed hits; CS-010 changes are in `public_astro_daily_events.py` and `public_projection.py`. | PASS |
| `legacy|compat|shim|fallback|deprecated|alias` | Broad scan not used as primary evidence because this story does not remove a legacy path; source-specific scan is RG-030. | No new shim, alias, wrapper, or compatibility path introduced. | PASS |

## Reviewer checklist

- Confirm `astro_foundation` still returns the same object shape.
- Confirm exact aspect support is not duplicated in a second active taxonomy.
- Confirm broad backend regression failure is unrelated to this story.
