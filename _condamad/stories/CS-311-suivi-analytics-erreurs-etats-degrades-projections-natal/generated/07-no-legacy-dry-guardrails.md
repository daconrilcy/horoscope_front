# No Legacy / DRY Guardrails - CS-311

## Canonical Owners Preserved

- Analytics tracking and redaction: `frontend/src/hooks/useAnalytics.ts`.
- Projection HTTP/query ownership: `frontend/src/api/astrologyProjections.ts`.
- Projection orchestration: `frontend/src/features/natal-chart/NatalInterpretation.tsx`.
- Projection rendering: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`.

## Forbidden Paths Checked

- No new analytics vendor, dependency, shim, alias, wrapper, or compatibility adapter.
- No direct Plausible, Matomo, `console.debug`, `fetch`, or `axios` call from projection UI/API surfaces outside existing owners.
- No backend route, entitlement, prompt, provider, migration, DB, or generated client change.
- No inline style added in touched natal TSX surfaces.
- No CSS/style file change.

## Guard Results

- Direct analytics provider scan: PASS, no matches in `frontend/src/features`, `frontend/src/components`, or `frontend/src/api`.
- Projection HTTP direct-call scan: PASS, no matches.
- Inline style scan for `RG-047`: PASS, no matches.
- Sensitive key scan: PASS_WITH_CONTEXT; broad repository hits are existing or the redaction allowlist, and runtime tests prove emitted payload redaction.

## Reviewer Focus

Review `NatalInterpretation.tsx` event emission keys and dedupe behavior: events are intentionally public and scoped to `/natal` projection state transitions.
