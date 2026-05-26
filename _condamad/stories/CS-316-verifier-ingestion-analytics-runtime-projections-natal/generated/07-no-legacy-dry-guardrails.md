# No Legacy / DRY Guardrails

## Decisions

- No analytics provider was added.
- No compatibility path, shim, alias, mapper, dashboard-only note, backend
  route, replay path, migration or persistence change was added.
- CS-311 `event-catalog.json` remains the single baseline for event names and
  public fields.
- `ANALYTICS_CONFIG` remains the single provider configuration source.
- `useAnalytics` remains the single frontend provider dispatch and redaction
  boundary.

## Evidence

- Direct provider scan in `frontend/src/features`, `frontend/src/components`
  and `frontend/src/api`: PASS, no matches.
- Sensitive-field evidence scan in CS-316 `evidence/`: PASS, no matches.
- `git diff --check`: PASS.
- RG-047 inline-style policy test: PASS. Contextual `style=` scan returns
  pre-existing dynamic/style-forwarding occurrences outside CS-316 edits.
- RG-071 natal interpretation/component architecture guard: PASS.

## Feedback Loop

`no-propagation`: no reusable correction or new durable invariant was discovered
because CS-316 adds bounded evidence only and does not change runtime code.
