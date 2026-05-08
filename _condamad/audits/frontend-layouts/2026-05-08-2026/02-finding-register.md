<!-- Registre des constats de l'audit CONDAMAD frontend-layouts post-CS-109. -->

# Finding Register - frontend-layouts post-CS-109

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-301 | Medium | High | missing-test-coverage | frontend-layouts | E-005, E-006, E-010, E-011 | `PageLayout` can lose its intended padding because a malformed CSS declaration is active while lint and tests stay green. | Fix the declaration and add a deterministic CSS syntax/design-system guard covering layout CSS primitives. | yes |
| F-302 | Medium | High | legacy-surface | frontend-layouts | E-004, E-005, E-007, E-014 | `TwoColumnLayout` keeps an inline-style exception inside the layout domain despite the repository no-inline-style rule; the exception is guarded but still active. | Replace the inline custom-property write with CSS-owned variants or record a renewed explicit decision; remove the layout exception when remediated. | yes |
| F-303 | Low | High | runtime-contract-drift | frontend-layouts | E-008, E-009 | The CS-109 source story header contradicts the canonical story registry and final evidence, creating ambiguity for future audits. | Align the CS-109 source story status and checklist with the `done` registry/final evidence. | yes |

## Finding Details

### F-301 - `PageLayout.css` contains invalid active CSS

- Severity: Medium
- Confidence: High
- Category: missing-test-coverage
- Domain: frontend-layouts
- Evidence: E-005, E-006, E-010, E-011.
- Expected rule: layout primitive CSS should be syntactically valid and guarded by the frontend quality suite.
- Actual state: `frontend/src/layouts/PageLayout.css` line 6 declares `padding: var(--layout-page-padding));` with an extra closing parenthesis. `npm run lint`, targeted guards, and full `npm run test` still pass.
- Impact: `PageLayout` can lose its intended padding because a malformed CSS declaration is active while lint and tests stay green.
- Recommended action: Fix the declaration and add a deterministic CSS syntax/design-system guard covering layout CSS primitives.
- Story candidate: yes
- Suggested archetype: test-guard-hardening
- Closure classification: closure-ready

### F-302 - `TwoColumnLayout` preserves a layout-owned inline style exception

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-layouts
- Evidence: E-004, E-005, E-007, E-014.
- Expected rule: no inline styles in application UI unless a narrow, current decision explicitly overrides the repository rule.
- Actual state: `frontend/src/layouts/TwoColumnLayout.tsx` sets `--sidebar-width` via an inline `style` prop and the exception is preserved in both design-system and inline-style allowlists.
- Impact: `TwoColumnLayout` keeps an inline-style exception inside the layout domain despite the repository no-inline-style rule; the exception is guarded but still active.
- Recommended action: Replace the inline custom-property write with CSS-owned variants or record a renewed explicit decision; remove the layout exception when remediated.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal
- Closure classification: blocked-if-arbitrary-width-required

### F-303 - CS-109 source story status is stale

- Severity: Low
- Confidence: High
- Category: runtime-contract-drift
- Domain: frontend-layouts
- Evidence: E-008, E-009.
- Expected rule: source story status, global story registry, and final evidence should agree after story closure.
- Actual state: `_condamad/stories/story-status.md` records CS-109 as `done`, while `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` still says `Status: ready-to-dev`.
- Impact: The CS-109 source story header contradicts the canonical story registry and final evidence, creating ambiguity for future audits.
- Recommended action: Align the CS-109 source story status and checklist with the `done` registry/final evidence.
- Story candidate: yes
- Suggested archetype: governance-evidence-alignment
- Closure classification: closure-ready

## Closed Prior Findings

| Prior finding | Closure evidence | Guardrail |
|---|---|---|
| 2026-05-08-1405 F-001 | E-001, E-003, E-010 | RG-068 |
| 2026-05-08-1405 F-002 | E-001, E-003, E-010 | RG-068 |
| 2026-05-08-1405 F-003 | E-001, E-003, E-010 | RG-068 |
| 2026-05-08-1405 F-004 | E-003, E-004, E-010 | RG-064, RG-068 |
| 2026-05-08-1405 F-005 | E-002, E-003, E-013 | RG-068 |
| 2026-05-08-1532 F-101 | E-002, E-008, E-009, E-013 | RG-068 |
| 2026-05-08-1532 F-102 | E-008 | RG-068 |
| 2026-05-08-1914 F-201 | E-001, E-002, E-008, E-009, E-013 | RG-068 |

## Exhaustive Active Surface

Application files:

- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`

Governance/test files:

- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts` or a focused CSS syntax guard
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`

Deferred non-domain context:

- Broader design-system inline-style exceptions outside layout primitives.
- Test-harness warnings unrelated to layout ownership.
