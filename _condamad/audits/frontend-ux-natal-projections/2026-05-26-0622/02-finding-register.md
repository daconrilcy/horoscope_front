# Finding Register - frontend-ux-natal-projections - 2026-05-26-0622

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | missing-canonical-owner | frontend-ux | E-007, E-010, E-015, E-019, E-020 | Projection layout is readable, but visible projection panel copy is hardcoded in the rendering component, so product wording review and i18n ownership cannot be closed by the UX audit alone. | Route to CS-308 wording story: move or review projection panel copy in canonical app wording owners, keep disclaimers app-owned, and keep backend projection payloads unchanged. | yes |

## F-001 - Projection panel wording is not yet closed by a canonical wording owner

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-ux
- Evidence: E-007, E-010, E-015, E-019, E-020
- Expected rule: App-owned UX copy around `/natal` projections should be auditable through canonical wording owners, with product decisions separated from rendering and backend payloads.
- Actual state: `AstrologyProjectionsPanel` and `ProjectionCard` render French labels and state messages directly in `NatalInterpretationContent.tsx`, while disclaimer copy is already i18n-owned in `natalChart.ts`.
- Impact: Projection layout is readable, but visible projection panel copy is hardcoded in the rendering component, so product wording review and i18n ownership cannot be closed by the UX audit alone.
- Recommended action: Route to CS-308 wording story: move or review projection panel copy in canonical app wording owners, keep disclaimers app-owned, and keep backend projection payloads unchanged.
- Story candidate: yes
- Suggested archetype: frontend-wording-convergence
