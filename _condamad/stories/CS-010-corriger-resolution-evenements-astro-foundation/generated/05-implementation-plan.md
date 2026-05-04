# Implementation Plan

## Repository findings

- `PublicAstroFoundationPolicy` read `evidence.metadata["astro_events"]` or `core.events`, but not `core.detected_events`.
- `PublicAstroFoundationPolicy` filtered dominant aspects with `event_type == "aspect"`.
- `PublicAstroDailyEventsPolicy` already encoded the audited runtime behavior: `events`, `detected_events`, persisted `v3_metrics.detected_events`, and `aspect_exact_*`.

## Proposed changes

- Extract public event resolution to `resolve_public_astro_events`.
- Extract exact aspect taxonomy to `PUBLIC_ASTRO_ASPECT_EVENT_TYPES`.
- Reuse both from `PublicAstroFoundationPolicy`.
- Add unit tests for `detected_events` and all exact aspect event types.

## Files modified

- `backend/app/prediction/public_astro_daily_events.py`
- `backend/app/prediction/public_projection.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- CONDAMAD evidence files under this story capsule.

## Rollback strategy

- Revert the three backend file changes and generated CS-010 evidence updates.
- No dependency, migration, or schema rollback is required.
