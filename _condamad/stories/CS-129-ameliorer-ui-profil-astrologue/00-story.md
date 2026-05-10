# Story CS-129 ameliorer-ui-profil-astrologue: Ameliorer l'UI de la page /astrologers/:id

Status: done

## 1. Objective

Ameliorer la page profil astrologue `/astrologers/:id` sans changer son identite visuelle douce,
premium et lumineuse. La story cible la structure, la lisibilite et le responsive:
corriger la cause du scroll horizontal, remonter un CTA primaire, clarifier les avis vides
et equilibrer le hero, les badges, les statistiques, les sections contenu et le mobile.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-10 dans la conversation Codex.
- Reason for change: la page a une direction visuelle valide mais presente des signaux de finition
  insuffisante: scroll horizontal, CTA principal trop bas, avis contradictoire et hero trop dispersif.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/pages/AstrologerProfilePage.tsx` visual and interaction surface for route `/astrologers/:id`
- In scope:
  - composition React de `frontend/src/pages/AstrologerProfilePage.tsx`
  - styles dedies dans `frontend/src/pages/AstrologerProfilePage.css`
  - sections dediees dans `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
  - libelles i18n astrologers pour tout nouveau texte visible
  - tests `frontend/src/tests/AstrologersPage.test.tsx`, `frontend/src/tests/design-system-guards.test.ts`, `frontend/src/tests/visual-smoke.test.tsx`
  - test navigateur `frontend/e2e/astrologer-profile-ui.spec.ts`
  - artefacts before/after et validation dans ce dossier de story
- Out of scope:
  - route liste `/astrologers`, `AstrologersPage`, `AstrologerCard`, `AstrologerGrid`
  - backend, API `/v1/astrologers`, cache local et types de payload
  - flux consultation, chat et natal au-dela des navigations CTA deja existantes
  - settings default astrologer hors repositionnement visuel du bouton existant
  - nouvelle dependance, nouveau systeme de design ou refonte globale des layouts
- Explicit non-goals:
  - ne pas masquer le scroll horizontal par un simple `overflow-x: hidden` sans corriger la cause locale
  - ne pas modifier la route `/astrologers/:id`, les query params CTA ou les appels API
  - ne pas changer l'identite graphique: palette, douceur, glass, premium et luminosite doivent rester coherents
  - ne pas affaiblir `RG-044` a `RG-050`, `RG-064`, `RG-068`, `RG-078`, `RG-079`
  - ne pas introduire de style inline, fallback CSS non classe, alias historique ou style actif dans `frontend/src/App.css`
  - ne pas modifier les credentials de test ni les secrets

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: supported archetypes cover route/API decommissioning, namespace convergence,
  guards, service boundaries and migrations; this is a bounded visual and UX adjustment.
- Custom reason: the work changes visual hierarchy and responsive behavior without changing route ownership or data contracts.
- Additional validation rules:
  - ACs must include CSS overflow evidence, DOM CTA evidence, empty-review behavior evidence, responsive evidence and design-system guard evidence.
  - The implementation must prove the existing CTA navigations still target consultation, chat and natal routes.
  - The implementation must persist before/after evidence because the requested visual adjustment is evidence-driven.
- Behavior change allowed: constrained
- Behavior change constraints:
  - allowed: visual hierarchy, local layout, spacing, CTA placement, review empty-state copy, method step helper copy, mobile sticky CTA if it uses the existing consultation action
  - forbidden: API contract, route registration, loading/error/not-found behavior,
    review submission API, default astrologer mutation semantics and CTA destinations
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the requested UI quality requires a new dependency, backend/API change,
  route change, hidden profile section, or a product decision about `average_rating` without public reviews.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The rendered DOM and computed layout for `/astrologers/:id` are the source for CTA visibility, empty reviews and mobile behavior. |
| Baseline Snapshot | yes | The work is a visual before/after improvement and must prove no horizontal overflow and allowed visual differences. |
| Ownership Routing | yes | Route composition, feature sections and CSS owners must stay in their canonical frontend owners without `App.css` pollution. |
| Allowlist Exception | no | No new derogation, wildcard, fallback or register entry is expected. |
| Contract Shape | no | No API, DTO, OpenAPI, generated client or payload shape is affected. |
| Batch Migration | no | This is one bounded page improvement, not a multi-surface migration. |
| Reintroduction Guard | yes | Guards must prevent horizontal overflow regressions, inline styles and `App.css` profile styling from returning. |
| Persistent Evidence | yes | Visual baseline, after state and validation results must be kept as story artifacts. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - rendered `AstrologerProfilePage` DOM under `MemoryRouter` for `/astrologers/:id`
  - AST guard `frontend/src/tests/design-system-guards.test.ts`
  - rendered DOM artifact from Testing Library for `AstrologerProfilePage`
  - CSS assertions from `frontend/src/pages/AstrologerProfilePage.css`
  - browser/manual viewport evidence for desktop and mobile widths, or a recorded local-run blocker
  - Playwright viewport evidence from `frontend/e2e/astrologer-profile-ui.spec.ts`
- Secondary evidence:
  - `frontend/src/tests/AstrologersPage.test.tsx`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx` when a rendered DOM smoke is needed
  - targeted `rg` scans for forbidden inline styles, `App.css` pollution and blunt overflow masking
- Static scans alone are not sufficient for this story because:
  - a CSS selector can exist while the rendered route still overflows horizontally, hides the CTA below the first screen or displays contradictory review information.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/profile-ui-before.md`
  - screenshot paths in the same folder, or a blocker note if the local browser/dev server cannot be used
- Comparison after implementation:
  - `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/profile-ui-after.md`
  - `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/validation-evidence.md`
- Expected invariant:
  - same route, data source, profile identity, CTA destinations, rating mutation and premium visual language.
  - only local hierarchy, spacing, empty-state copy, responsive layout and decorative intensity may change.
- Allowed differences:
  - hero order and spacing, CTA placement, badge grouping, metric labels/helpers, mission density,
    method helper text, review empty-state presentation and mobile sticky consultation CTA.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Profile route composition | `frontend/src/pages/AstrologerProfilePage.tsx` | route table, API client, unrelated pages |
| Profile-only visual styling | `frontend/src/pages/AstrologerProfilePage.css` | `frontend/src/App.css`, inline `style=`, shared app CSS modules without owner need |
| Metrics/method/reviews/final CTA sections | `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` | duplicated components in the route file |
| Astrologer profile texts | `frontend/src/i18n/astrologers.ts` for new visible copy | backend payload shape or unrelated i18n namespaces |
| Design tokens | existing global tokens and existing page-local CSS variables in `AstrologerProfilePage.css` | new unclassified token namespace or CSS fallback literal |
| Tests for profile route | `frontend/src/tests/AstrologersPage.test.tsx` and existing design-system/visual-smoke guards | new ad hoc test harness |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable.
- Reason: no new fallback, inline-style derogation, historical-style derogation, page-size derogation or broad register entry is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable.
- Reason: no API, route manifest, DTO, OpenAPI schema, generated client, persisted payload or serialization contract is modified.

## 4g. Batch Migration Plan

- Batch migration: not applicable.
- Reason: the story is a single profile page UI improvement; there is no old-to-new multi-batch migration.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| before profile audit | `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/profile-ui-before.md` | current overflow, hierarchy, reviews, spacing and responsive issues |
| after profile audit | `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/profile-ui-after.md` | resolved issues, allowed visual differences and residual observations |
| validation log | `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/validation-evidence.md` | records exact commands, results, skipped checks and manual viewport evidence |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if these forbidden or required surfaces drift:

- forbidden examples:
  - `overflow-x: hidden` added as the only profile overflow fix without local source correction evidence
  - active `/astrologers/:id` styles added to `frontend/src/App.css`
  - `style=` added to `AstrologerProfilePage.tsx` or `AstrologerProfileSections.tsx`
  - review summary rendering `4.x/5` together with `(0 avis)` as the primary empty public-review state
  - mobile layout collapsing metrics to one column before the smallest breakpoint instead of a readable 2x2 grid
- required examples:
  - hero includes a primary consultation CTA in or immediately after the first-screen content
  - metric cards expose balanced value/label hierarchy
  - empty public reviews show a non-contradictory state such as "Nouvel astrologue" / "Soyez le premier"
  - mobile viewport has a quickly reachable consultation CTA, either in hero or as a sober sticky bottom CTA

Guard evidence:

- Evidence profile: `reintroduction_guard`; architecture guard
  `frontend/src/tests/design-system-guards.test.ts`, `npm run test -- AstrologersPage design-system visual-smoke`
  and targeted scans from the validation plan.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase and user source indicate:

- Evidence 1: `frontend/src/app/routes.tsx` - route `astrologers/:id` renders `AstrologerProfilePage`; route registration is not part of this story.
- Evidence 2: `frontend/src/pages/AstrologerProfilePage.tsx` - hero renders avatar, badges, name,
  subtitle, metadata, default action and quote before the metrics bar.
- Evidence 3: `frontend/src/pages/AstrologerProfilePage.tsx` - `handleConsultationCta`
  routes to `/consultations/new?astrologerId={id}`.
- Evidence 4: `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` -
  final CTA renders "Commencer avec {first_name}" near the bottom of the page.
- Evidence 5: `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` -
  reviews summary can render `4.7/5` with `0 avis`, matching the reported contradiction.
- Evidence 6: `frontend/src/pages/AstrologerProfilePage.css` - profile page owns hero, metrics,
  about/specialties grid, mission, method, reviews, final CTA and responsive breakpoints.
- Evidence 7: `frontend/src/pages/AstrologerProfilePage.css` - decorative positioned elements
  and fixed hero/avatar values are likely overflow candidates.
- Evidence 8: `frontend/src/tests/AstrologersPage.test.tsx` - existing profile tests cover hero/profile rendering, loading, not-found, error, CTA navigation and reviews flow.
- Evidence 9: `frontend/src/tests/design-system-guards.test.ts` - `pages/AstrologerProfilePage.css` is already part of design-system guard coverage.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - invariants consulted before scope was finalized, especially frontend design-system and layout guardrails.

## 6. Target State

After implementation:

- `/astrologers/:id` has no horizontal scroll at desktop, tablet or mobile widths because the overflowing local element is corrected.
- The first screen communicates photo, name, expertise, quote and primary consultation CTA in a clear reading path.
- Badges are grouped by meaning: positioning/provider first, personal metadata second, default action treated as secondary.
- The metrics bar uses consistent value/label hierarchy and stays readable as a 2x2 grid on mobile.
- About and specialties feel aligned as one content block; the sidebar no longer feels detached.
- Mission appears as a concise note or receives enough copy to justify its height without becoming visually heavier than the main bio.
- Method steps include short helper text under each label, preserving the current premium styling.
- Public reviews empty state is not contradictory: no primary `4.x/5 (0 avis)` claim when there are zero public reviews.
- Mobile users see a consultation CTA quickly without the photo, stats or decorative effects consuming the whole first screen.
- Decorative effects remain present but less competing, with local CSS tokens and no inline styles.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - profile CSS uses token namespaces and existing page-local variables; new namespaces must be classified if introduced.
  - `RG-045` - migrated visual literals must not return as unowned raw CSS values.
  - `RG-047` - no static inline styles may be added to profile route or section components.
  - `RG-048` - no unclassified CSS fallback `var(--token, value)` may be introduced.
  - `RG-049` - no historical selector alias or compatibility styling may be added.
  - `RG-050` - design-system static guards must stay executable.
  - `RG-064` - page architecture guards must remain valid while profile route composition changes locally.
  - `RG-068` - route remains under the existing layout hierarchy; no route ownership change is allowed.
  - `RG-078` - `App.css` must remain bounded and must not receive profile styles.
  - `RG-079` - list route `/astrologers` visual relief must not regress; this story must avoid changing list card owners.
  - `RG-080` - this story establishes the durable invariant for `/astrologers/:id` UI quality.
- Non-applicable invariants:
  - backend API, DB, prompt, billing and script invariants `RG-001` to `RG-043` do not apply because no backend surface is modified.
  - component relocation invariants `RG-069` to `RG-074` are passive unless the implementation tries to move shared components; such move is out of scope.
- Required regression evidence:
  - `npm run test -- AstrologersPage design-system visual-smoke`
  - `npm run test -- inline-style css-fallback page-architecture`
  - `npm run lint`
  - targeted scans for `App.css`, inline styles and blunt overflow masking
  - before/after artifacts in this story folder
- Allowed differences:
  - visual-only differences on `/astrologers/:id` listed in section 4c; no route/data/API differences.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Horizontal scroll is resolved at the local overflowing element. | Evidence profile: `baseline_before_after_diff`; `npm run test -- visual-smoke`; overflow scan. |
| AC2 | A primary consultation CTA appears in the first-screen hero area. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage`; DOM assertion. |
| AC3 | Hero hierarchy is tightened without data changes. | Evidence profile: `baseline_before_after_diff`; `npm run test -- AstrologersPage visual-smoke`; after artifact. |
| AC4 | Default action is secondary to identity badges. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage design-system`. |
| AC5 | Metrics keep balanced value-label hierarchy. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system visual-smoke`; CSS guard. |
| AC6 | Content spacing uses one local grid rhythm. | Evidence profile: `baseline_before_after_diff`; `rg -n "profile-main-grid" src/pages/AstrologerProfilePage.css`. |
| AC7 | Method steps include short helper copy for each step. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage`; helper text assertion. |
| AC8 | Empty public reviews no longer pair a non-zero score with `0 avis`. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage`. |
| AC9 | Review stats simplify when public reviews are empty. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage`; both review states. |
| AC10 | Mobile CTA stays quickly reachable. | Evidence profile: `baseline_before_after_diff`; `npm run test -- visual-smoke`; mobile CSS scan. |
| AC11 | Design-system guardrails remain intact. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system inline-style css-fallback visual-smoke`; scans. |
| AC12 | Existing profile behaviors still pass. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run test -- AstrologersPage`; `npm run lint`. |

Acceptance evidence details:

- AC1 overflow scan: `rg -n "overflow-x:\\s*hidden" frontend/src/pages/AstrologerProfilePage.css`.
- AC2 navigation assertion must target `/consultations/new?astrologerId={id}`.
- AC4 must prove provider/positioning badges remain separate from personal metadata and default action.
- AC5 must prove metric labels are balanced and mobile keeps two columns at the tablet/mobile breakpoint.
- AC6 CSS scan: `rg -n "profile-main-grid|specialties-card|profile-mission-card" frontend/src/pages/AstrologerProfilePage.css`.
- AC10 must prove the mobile CTA is present before the final CTA, or sticky without overlap.
- AC10 mobile CSS scan: `rg -n "@media \\(max-width: 768px\\)|profile-hero|profile-mobile" frontend/src/pages/AstrologerProfilePage.css`.
- Browser evidence: `npm run test:e2e -- astrologer-profile-ui.spec.ts` must assert `scrollWidth <= clientWidth`
  at 390px and a desktop width.

## 8. Implementation Tasks

- [x] Task 1 - Capture current baseline and overflow source. (AC: AC1, AC3, AC6, AC10)
  - [x] Create `profile-ui-before.md` with desktop/mobile observations, suspected overflow element, current CTA position, review empty-state behavior and responsive issues.
  - [x] If live verification is used, authenticate with the provided test user only in local/dev context and record no secrets in artifacts.
  - [x] Identify the overflowing local selector before applying any `overflow-x` containment.

- [x] Task 2 - Tighten hero and CTA hierarchy. (AC: AC2, AC3, AC4, AC10, AC12)
  - [x] Add a primary consultation CTA near the name/quote using the existing consultation handler.
  - [x] Keep the final CTA section but avoid creating two competing primary actions on desktop.
  - [x] Rebalance avatar/decorative circle size and hero grid spacing using existing page CSS variables and tokens.
  - [x] Reorganize badge rows so provider/positioning metadata and personal metadata do not visually compete with the default action.

- [x] Task 3 - Normalize metrics and content section rhythm. (AC: AC5, AC6)
  - [x] Adjust metric label text or helper structure so values and labels are comparable across cards.
  - [x] Keep mobile metrics in a readable 2x2 grid until the smallest breakpoint.
  - [x] Align about/specialties top edges and tune sidebar width/gap without changing route data.
  - [x] Reduce mission card visual weight; do not invent copy beyond existing profile fields or i18n labels.

- [x] Task 4 - Clarify method and review sections. (AC: AC7, AC8, AC9)
  - [x] Extend `AstrologerProfileMethodSection` to accept helper copy for each step without duplicating step rendering logic.
  - [x] Add i18n labels for the four method helper texts.
  - [x] Split review rendering between zero-public-review and non-zero-review states.
  - [x] In zero-review state, avoid primary display of non-zero average rating as public-review proof; keep rating input usable.

- [x] Task 5 - Add responsive and design-system guards. (AC: AC1, AC5, AC10, AC11)
  - [x] Update or add tests for hero CTA, empty reviews, method helpers and mobile/profile CSS invariants.
  - [x] Add guard coverage for no profile styles in `App.css`, no inline styles in touched TSX files and no blunt overflow-only fix.
  - [x] Mock auth, profile and user settings API responses in Playwright from existing frontend contracts.
  - [x] Add Playwright coverage for desktop/mobile horizontal overflow and mobile CTA reachability.
  - [x] Ensure `/astrologers` list tests and `RG-079` guard evidence still pass.

- [x] Task 6 - Validate and persist after evidence. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12)
  - [x] Create `profile-ui-after.md` with allowed differences, before/after summary and residual risks.
  - [x] Create `validation-evidence.md` with exact commands, results and skipped manual checks.
  - [x] Run the validation plan and fix failures before marking ready-to-review.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - existing handlers `handleConsultationCta`, `handleChatCta`, `handleNatalCta` in `AstrologerProfilePage.tsx`
  - existing `Button` component and lucide icons already imported in the profile route
  - existing `AstrologerProfileMetricsBar`, `AstrologerProfileMethodSection`, `AstrologerProfileReviewsSection`, `AstrologerProfileFinalCta`
  - existing page-local variables in `AstrologerProfilePage.css` and global design tokens from `design-tokens.css`, `glass.css`, `backgrounds.css`
  - existing tests in `AstrologersPage.test.tsx` before adding a new test file
- Do not recreate:
  - a second profile page component
  - a duplicate CTA navigation function
  - separate review/stat card implementation when `AstrologerProfileReviewsSection` can own the branch
  - raw hardcoded visual literals when a token or page-local variable exists
  - route aliases or compatibility wrappers
- Shared abstraction allowed only if:
  - at least two profile subsections in this story reuse it immediately and no existing component or CSS utility already owns the responsibility.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- broad registers or wildcard derogations
- new dependencies
- active CSS additions in `frontend/src/App.css`
- inline `style=` additions in profile TSX files
- API/data contract changes for profile metrics, reviews or action state
- global overflow masking as the only fix

Specific forbidden symbols / paths:

- `frontend/src/App.css` profile-specific styles
- `style=` in `frontend/src/pages/AstrologerProfilePage.tsx`
- `style=` in `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
- `overflow-x: hidden` as an unexplained standalone fix in `frontend/src/pages/AstrologerProfilePage.css`
- new CSS selectors under `.astrologer-card` or `.astrologer-grid`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| `/astrologers/:id` route composition | `frontend/src/pages/AstrologerProfilePage.tsx` | route table, API client, unrelated page files |
| Profile visual styling | `frontend/src/pages/AstrologerProfilePage.css` | `frontend/src/App.css`, inline styles, list page CSS |
| Profile section rendering | `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` | duplicated section markup in ad hoc components |
| Profile route tests | `frontend/src/tests/AstrologersPage.test.tsx` | unrelated test suites unless existing guards require update |
| Design-system guards | `frontend/src/tests/design-system-guards.test.ts` | broad manual-only review |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/api/astrologers.ts`
- `frontend/src/api/userSettings.ts`
- `frontend/src/types/astrologer.ts`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/playwright.config.ts`
- `frontend/src/app/routes.tsx`
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/AstrologerProfilePage.tsx` - add hero CTA, pass method helper data and review state props.
- `frontend/src/pages/AstrologerProfilePage.css` - fix overflow source, rebalance hero/spacing/badges/metrics/reviews/mobile sticky CTA and decorative intensity.
- `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` - support method helper text and zero-review rendering without duplicating sections.
- `frontend/src/i18n/astrologers.ts` - add new CTA, helper and empty-review labels.
- `frontend/src/tests/AstrologersPage.test.tsx` - cover hero CTA, empty reviews, method helpers and unchanged navigation.
- `frontend/src/tests/design-system-guards.test.ts` - add or adjust profile CSS guardrails for overflow,
  `App.css`, inline-style and review empty-state CSS when static coverage is appropriate.
- `frontend/src/tests/visual-smoke.test.tsx` - add profile smoke coverage for mobile/visual constraints.
- `frontend/e2e/astrologer-profile-ui.spec.ts` - assert desktop/mobile viewport overflow and CTA reachability.
- `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/profile-ui-before.md` - before evidence.
- `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/profile-ui-after.md` - after evidence.
- `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/validation-evidence.md` - command evidence.

Likely tests:

- `frontend/src/tests/AstrologersPage.test.tsx` - primary behavior coverage for profile route.
- `frontend/src/tests/design-system-guards.test.ts` - static design-system regression coverage.
- `frontend/src/tests/visual-smoke.test.tsx` - rendered layout smoke coverage.
- `frontend/e2e/astrologer-profile-ui.spec.ts` - browser viewport coverage.

Files not expected to change:

- `frontend/src/App.css` - must remain free of profile-specific active styles.
- `frontend/src/app/routes.tsx` - route registration is out of scope.
- `frontend/src/api/astrologers.ts` - API/data contract is out of scope.
- `frontend/src/types/astrologer.ts` - payload shape is out of scope.
- `frontend/src/pages/AstrologersPage.tsx` - list route is out of scope.
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - list card is out of scope.
- `backend/**` - backend is out of scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

No dependency change is allowed for this story.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- AstrologersPage design-system visual-smoke
npm run test -- inline-style css-fallback page-architecture
npm run test:e2e -- astrologer-profile-ui.spec.ts
npm run lint
npm run build
rg -n "AstrologerProfile|profile-" src/App.css
rg -n "style=" src/pages/AstrologerProfilePage.tsx src/features/astrologers/components/AstrologerProfileSections.tsx
rg -n "overflow-x:\\s*hidden" src/pages/AstrologerProfilePage.css
rg -n "profile-main-grid|specialties-card|profile-mission-card" src/pages/AstrologerProfilePage.css
rg -n "@media \\(max-width: 768px\\)|profile-hero|profile-mobile" src/pages/AstrologerProfilePage.css
rg -n "astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim" `
  src/pages/AstrologerProfilePage.css `
  src/features/astrologers/components/AstrologerProfileSections.tsx `
  src/pages/AstrologerProfilePage.tsx
Pop-Location
```

Expected scan results:

- `rg -n "AstrologerProfile|profile-" src/App.css` must return zero hit.
- `rg -n "style="` scan on the listed files must return zero hit.
- `rg -n "overflow-x:\s*hidden" src/pages/AstrologerProfilePage.css` must return zero hit.
  Any hit must be paired with before/after evidence identifying the corrected overflowing selector.
- bounded historical-surface scan must return zero active hit; historical comments in evidence files are outside this scan scope.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md
```

Manual visual check when the dev server can run:

- Open `/astrologers/{id}` on desktop, tablet and mobile.
- Verify no horizontal scrollbar is visible.
- Verify the hero reads photo, then name, then expertise, then CTA.
- Verify metrics are balanced and mobile layout remains readable.
- Verify zero-review profile does not display a public-review score contradiction.
- Verify sticky/mobile CTA, if implemented, does not overlap footer, modal or bottom navigation.

## 22. Regression Risks

- Risk: hiding overflow globally instead of fixing the local decorative or fixed-width source.
  - Guardrail: AC1 before/after artifact, scan for `overflow-x: hidden`, visual smoke/manual viewport check.
- Risk: adding a second CTA changes navigation semantics.
  - Guardrail: reuse `handleConsultationCta`; `AstrologersPage.test.tsx` navigation assertion.
- Risk: review empty-state simplification hides legitimate public reviews.
  - Guardrail: tests cover both `review_count: 0` and positive `review_count`.
- Risk: visual tuning adds raw literals, fallbacks or inline styles.
  - Guardrail: `RG-044` to `RG-050`, `inline-style`, `css-fallback`, `design-system`.
- Risk: profile CSS changes regress `/astrologers` list relief from CS-128.
  - Guardrail: `RG-079`, `npm run test -- AstrologersPage visual-smoke`.
- Risk: mobile sticky CTA overlaps modal or review composer.
  - Guardrail: manual mobile check and CSS constraints in after evidence.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback,
  compatibility, legacy, migration-only, shim, alias, TODO, or hidden residual in-domain work.
- Start by identifying the actual horizontal overflow source in `AstrologerProfilePage.css`.
- Prefer changing local profile CSS and existing profile section props over moving code or adding components.
- Keep `frontend/src/App.css` untouched for active profile styles.
- Keep all new or modified comments/docstrings in French when comments are necessary.
- If a live check uses the supplied test credentials, do not persist credentials in repository files or evidence artifacts.

## 24. References

- User brief in conversation - prioritized UI improvement list for `/astrologers/:id`.
- `frontend/src/pages/AstrologerProfilePage.tsx` - current profile route composition and CTA handlers.
- `frontend/src/pages/AstrologerProfilePage.css` - current profile visual owner and responsive rules.
- `frontend/src/features/astrologers/components/AstrologerProfileSections.tsx` - current metrics, method, reviews and final CTA section owners.
- `frontend/src/tests/AstrologersPage.test.tsx` - current profile behavior tests.
- `frontend/src/tests/design-system-guards.test.ts` - design-system guard owner.
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` - adjacent `/astrologers` list guardrail context.
- `_condamad/stories/regression-guardrails.md` - shared regression invariants.
