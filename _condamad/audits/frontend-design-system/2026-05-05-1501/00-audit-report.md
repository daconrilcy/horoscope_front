# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend/src` design-system and style consumption layer.
- Baseline audits: `_condamad/audits/frontend-design-system/2026-05-04-2238/` and `_condamad/audits/frontend-design-system/2026-05-05-1411/`.
- Audit archetype: custom frontend design-system audit using CONDAMAD DRY, No Legacy, missing canonical owner, duplicate responsibility, missing guard, and test-guard coverage dimensions.
- Read-only mode: application code was not modified.
- Output folder: `_condamad/audits/frontend-design-system/2026-05-05-1501/`.

## Expected Responsibility

The frontend design-system layer should keep visual decisions in governed CSS tokens, utilities, registries, and static guards. Page and component CSS may keep migration debt only when it is explicitly classified, guarded, and attached to an exit condition. Static inline styles remain forbidden by project rule unless they are exact dynamic exceptions.

## Evidence Summary

- Frontend guardrails `RG-044` through `RG-050` are still active in `_condamad/stories/regression-guardrails.md` and cover token namespaces, migrated hardcoded values, typography roles, inline styles, CSS fallbacks, legacy style surfaces, and anti-drift guards (E-001).
- The implemented frontend stories include `CS-026` through `CS-032`, plus follow-up cleanup stories `CS-034` and `CS-035`, so the audit now measures post-refactor state rather than only initial governance convergence (E-002).
- The canonical registries and tests remain present under `frontend/src/styles` and `frontend/src/tests` (E-003, E-004).
- Targeted design-system guards pass: `npm run test -- design-system inline-style css-fallback legacy-style theme-tokens` reports 5 files and 108 tests passed (E-005).
- `npm run lint`, `npm run build`, and the full `npm run test` pass. The build still emits the known Vite chunk-size warning for the main bundle (E-006, E-007, E-008).
- Static counts show improvement on governed debt since the 14:11 audit: inline style attributes dropped from 85 to 68, and CSS fallback usages dropped from 329 to 262. Remaining exceptions are still classified by allowlists (E-009, E-010, E-011).
- The prior full-suite-only `HelpPage.test.tsx` failure was not reproduced in this run: the full suite passed with 113 files, 1234 tests passed, and 8 skipped (E-008).
- Broad hardcoded value debt remains outside the migrated batches, with 1899 color-like hits and 4172 spacing/radius/shadow/typography declaration hits in static scans (E-012, E-013).

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low | 0 |
| Info | 2 |

## Key Findings

- `F-001`: Token ownership and anti-drift governance remain materially remediated.
- `F-002`: Hardcoded visual and typography decisions remain broad outside the migrated batches.
- `F-003`: Inline-style debt is reduced but still preserves static CSS decisions in allowlisted TSX surfaces.
- `F-004`: CSS fallback debt is reduced but still large, especially in shared UI and page-level CSS.
- `F-005`: The previous HelpPage suite flake is not reproduced and should be downgraded to observation unless it returns.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`.
- Applicable invariants:
  - `RG-044` - token namespace ownership for frontend CSS variables.
  - `RG-045` - migrated hardcoded values must not return in the covered batch.
  - `RG-046` - semantic typography roles are canonical for migrated surfaces.
  - `RG-047` - static inline styles are forbidden unless exactly allowlisted.
  - `RG-048` - unclassified CSS variable fallbacks are forbidden.
  - `RG-049` - legacy CSS selectors and aliases must remain classified.
  - `RG-050` - anti-drift design-system guards must remain executable.
- Required regression evidence: E-001 through E-008 cover the active frontend guardrails and executable validation.
- Allowed differences: no application code differences were introduced by this audit.

## Recommendations

1. Keep the current guardrails as the blocking quality gate for any future frontend design-system story.
2. Prioritize one cleanup story for `TurningPointsList.tsx`, because it owns most remaining static inline style debt.
3. Continue CSS fallback reduction by shared UI components first: `Modal`, `Field`, `Card`, `Button`, `Select`, `UserAvatar`, `LockedSection`, `EmptyState`, `Skeleton`, and `UpgradeCTA`.
4. Keep the previous HelpPage flake under observation, but do not treat it as an active finding while `npm run test` passes in full-suite mode.

## Validation Plan

- Validate these audit artifacts with the CONDAMAD validator and lint scripts from the repository root.
- Because repository policy requires Python commands to run inside the venv, validation must be run after `.\.venv\Scripts\Activate.ps1`.
