<!-- Matrice de risques de l'audit CONDAMAD frontend components. -->

# Risk Matrix - frontend-components

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | Shared components, admin, enterprise, auth, layout and dashboard consumers | High, because future shared component edits can change API workflow ownership without a guard | Medium | P1 |
| F-002 | High | Medium | Ops, enterprise and shared Form primitive typing | High, because TypeScript and lint can pass while suppressed files keep unsafe changes invisible | Low | P1 |
| F-003 | Medium | High | Natal chart interpretation flow, PDF actions, persona selection and evidence rendering | Medium, because a large mixed owner is difficult to change safely | Medium | P2 |
| F-004 | Info | Low | Component CSS and UI primitive styling | Low, current guards are active and passing | None | Observe |
| F-005 | Medium | Medium | Shared component inventory, B2B and ops panels, prediction display components and barrels | Medium, because dead or barrel-only components can retain stale API and UI behavior without runtime coverage | Low | P2 |

## Notes

- `F-001` and `F-002` should be handled before broad component refactors because they define the guardrails that prevent recurrence.
- `F-003` can be implemented as a bounded decomposition after the component architecture guard exists, or as a first slice if natal chart work is already prioritized.
- `F-005` should be closed with an exact symbol/import-aware usage inventory before removing any component, because some low-reference files may be intentionally hidden, library-exported, or affected by same-name symbol collisions.
