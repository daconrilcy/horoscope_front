# Implementation Plan - CS-202

## Initial findings

- `/natal` renders through `frontend/src/pages/NatalChartPage.tsx`.
- The latest chart hook and manual payload types live in
  `frontend/src/api/natal-chart/index.ts`.
- No existing `NatalExpertPanel` was found under `frontend/src`.
- The current page renders positions, houses, aspects, guide and
  interpretation, but ignores the advanced CS-201 blocks.

## Proposed changes

- Extend manual `LatestNatalChart.result` types with optional public CS-201
  blocks.
- Add `NatalExpertPanel` under `frontend/src/features/natal-chart/`.
- Add CSS beside the component and import it from the component.
- Integrate the panel into `NatalChartPage` after core chart facts and before
  the guide/interpretation.
- Add focused Vitest component tests and page reachability coverage.

## Frontend subagent assignment

- Worker ownership: `frontend/**`.
- Main session ownership: CONDAMAD capsule, evidence, final validation, review
  triage and status synchronization.

## Tests to add or update

- `frontend/src/tests/NatalExpertPanel.test.tsx`.
- `frontend/src/tests/NatalChartPage.test.tsx` if page integration needs
  explicit coverage.

## Rollback strategy

- Remove the panel component/import and revert API type additions. Backend data
  and API contracts remain untouched.
