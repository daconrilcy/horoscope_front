# Implementation Plan

## Architecture Finding

`ChartObjectPayloads.motion` and `.visibility` already exist but motion is
minimal and visibility is not wired. `AdvancedPlanetaryConditionsResult`
already owns the calculated facts needed for CS-219.

## Approach

1. Extend runtime payload dataclasses with typed fields and stricter
   capability/payload validation.
2. Add pure mapping helpers in the chart-object builder that consume
   `PlanetaryConditionsBundle`.
3. Pass `advanced_planetary_conditions` to chart-object projection after the
   existing advanced-condition runtime is computed.
4. Add targeted tests for payloads, builder projection, natal integration and
   architecture guards.
5. Record validation evidence and synchronize story status.

## No Legacy Stance

No compatibility alias, fallback, duplicate calculator or public schema change
is allowed.

## Rollback Strategy

Revert CS-219 changed files only, preserving pre-existing dirty files outside
the story.
