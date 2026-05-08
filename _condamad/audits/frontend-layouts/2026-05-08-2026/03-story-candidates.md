<!-- Candidats de stories issus de l'audit CONDAMAD frontend-layouts post-CS-109. -->

# Story Candidates - frontend-layouts post-CS-109

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-301 | F-301 | Corriger et garder la validite CSS des primitives layout | test-guard-hardening | frontend-layouts | None. |
| SC-302 | F-302 | Retirer ou redecider l'exception inline style de TwoColumnLayout | legacy-facade-removal | frontend-layouts | User/technical decision required only if arbitrary runtime sidebar width must remain supported. |
| SC-303 | F-303 | Aligner le statut source de CS-109 avec sa cloture | governance-evidence-alignment | frontend-layouts | None. |

## SC-301 - Corriger et garder la validite CSS des primitives layout

- Candidate ID: SC-301
- Source finding: F-301
- Suggested story title: Corriger et garder la validite CSS des primitives layout
- Suggested archetype: test-guard-hardening
- Primary domain: frontend-layouts
- Required contracts: `report-output-contract`, `no-legacy-dry-audit-contract`, existing guardrails `RG-050` and `RG-068`.
- Draft objective: restore valid `PageLayout.css` padding and add deterministic coverage so active layout CSS syntax regressions fail.
- Closure intent: `full-closure`
- Must include:
  - Correct `frontend/src/layouts/PageLayout.css` so `padding` uses the existing token without malformed punctuation.
  - Add or extend a guard that parses or validates active `frontend/src/layouts/**/*.css`.
  - Keep existing CSS variables; do not create duplicate spacing tokens.
  - Do not alter route hierarchy or page ownership classifications.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture layout`
  - `npm run test -- design-system`
  - Targeted scan: `rg -n "padding: var\\(--layout-page-padding\\)\\);" frontend/src/layouts`
- Blockers: none.

## Exhaustive Files To Modify - SC-301

Application files:

- `frontend/src/layouts/PageLayout.css`

Governance/test files:

- `frontend/src/tests/design-system-guards.test.ts` or a new focused frontend test file under `frontend/src/tests/`.

## Before / After Evidence Required - SC-301

- Before: scan proving the malformed declaration exists.
- After: scan proving it is absent.
- After: guard test proving layout CSS syntax is validated.
- Guard: no wildcard allowlist for layout CSS parse failures.

## Stop Condition - SC-301

`PageLayout.css` has no malformed active declaration and the frontend test suite contains a deterministic guard that fails if an equivalent layout CSS syntax issue is introduced.

## SC-302 - Retirer ou redecider l'exception inline style de TwoColumnLayout

- Candidate ID: SC-302
- Source finding: F-302
- Suggested story title: Retirer ou redecider l'exception inline style de TwoColumnLayout
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, existing guardrails `RG-047` and `RG-050`.
- Draft objective: remove the layout-owned inline style exception when a CSS-owned variant can satisfy current callers, or record a renewed explicit decision if arbitrary runtime width is required.
- Closure intent: `blocked`
- Must include:
  - Inspect all `TwoColumnLayout` consumers and confirm whether non-default `sidebarWidth` is used.
  - If finite widths are enough, replace the inline custom property with CSS classes or data attributes and remove allowlist entries.
  - If arbitrary width remains required, document the owner, exit condition, and why the repository no-inline-style rule is intentionally overridden.
  - Do not create another broad inline-style allowlist entry.
- Validation hints:
  - `npm run test -- inline-style design-system`
  - `rg -n "TwoColumnLayout|sidebarWidth|--sidebar-width|style=" frontend/src`
  - `npm run lint`
- Blockers:
  - Decide whether `TwoColumnLayout.sidebarWidth` must support arbitrary runtime values or can be reduced to CSS-owned variants.

## Exhaustive Files To Modify - SC-302

Application files:

- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`
- Exact consumer files returned by `rg -n "TwoColumnLayout|sidebarWidth" frontend/src`.

Governance/test files:

- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-allowlist.ts`
- Existing or new tests covering `TwoColumnLayout` layout behavior.

## Before / After Evidence Required - SC-302

- Before: current inline-style allowlist entry and source hit.
- After, if remediated: no inline `style=` in `TwoColumnLayout.tsx`, no `--sidebar-width` allowlist entry, and tests passing.
- After, if retained by decision: exact decision artifact with owner, reason, and expiry/exit condition.
- Guard: no wildcard exception, no folder-wide exception, no additional layout inline style.

## Stop Condition - SC-302

Either the inline style exception is removed and guards pass, or the exception is explicitly re-decided with a named owner and no hidden follow-up inside `frontend-layouts`.

## SC-303 - Aligner le statut source de CS-109 avec sa cloture

- Candidate ID: SC-303
- Source finding: F-303
- Suggested story title: Aligner le statut source de CS-109 avec sa cloture
- Suggested archetype: governance-evidence-alignment
- Primary domain: frontend-layouts
- Required contracts: `report-output-contract`.
- Draft objective: make the CS-109 source story header and checklist agree with `story-status.md`, closure evidence, and audit `1914`.
- Closure intent: `full-closure`
- Must include:
  - Update `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` status from `ready-to-dev` to the canonical completed state.
  - Mark implementation tasks consistently with final evidence, or explicitly add a note that the checklist is historical if the project convention prefers immutable stories.
  - Do not alter runtime code.
- Validation hints:
  - `rg -n "Status: ready-to-dev" _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
  - `rg -n "CS-109" _condamad/stories/story-status.md _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
  - Story lint/validate if the story-writer scripts are available, with venv active for Python commands.
- Blockers: none.

## Exhaustive Files To Modify - SC-303

Application files:

- none.

Governance/test files:

- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`

## Before / After Evidence Required - SC-303

- Before: source story header says `Status: ready-to-dev`; registry says `done`.
- After: both sources agree or the source story explicitly records a historical immutable status convention.
- Guard: no active contradiction in future `frontend-layouts` audit sources.

## Stop Condition - SC-303

CS-109 source story status no longer contradicts the canonical registry and final evidence.

## Deferred Non-Domain Context

- Broader inline-style exceptions outside `frontend/src/layouts/**` belong to `frontend-design-system`, not this `frontend-layouts` audit.
- React Router future-flag warnings and jsdom limitations are test-harness concerns, not layout ownership findings.
- External Stripe dashboard configuration remains outside repository scope.
