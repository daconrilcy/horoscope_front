# Execution Brief

## Story

- Key: `CS-219-chart-object-motion-visibility-payloads`
- Status at start: `ready-to-dev`
- Scope: backend astrology runtime contract only.

## Objective

Attach already computed planetary motion and visibility facts to
`NatalResult.chart_objects` through `ChartObjectRuntimeData.payloads.motion` and
`payloads.visibility`, with strict `ChartObjectCapabilities` coherence.

## Boundaries

- In scope: `backend/app/domain/astrology/runtime`, `builders`, minimal natal
  wiring, backend unit tests, CS-219 evidence.
- Out of scope: frontend, API, OpenAPI public schema, DB, migrations, JSON
  public projection, new calculators, threshold changes.

## Guardrails

- Reuse CS-209 to CS-214 contracts and results.
- Do not recalculate retrograde, station, cazimi, combustion, under beams,
  oriental/occidental relation or visibility in the chart-object builder.
- Do not add local magic thresholds.
- Do not add compatibility shim, alias, fallback or broad allowlist.

## Done Conditions

- AC1 to AC14 have code and validation evidence.
- `RG-146` is present and verified.
- Final evidence exists under `evidence/validation.md` and
  `generated/10-final-evidence.md`.
- `_condamad/stories/story-status.md` is synchronized.
