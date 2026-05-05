# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend/src` design-system and style consumption layer.
- Baseline audit: `_condamad/audits/frontend-design-system/2026-05-04-2238/`.
- Audit archetype: custom frontend design-system audit using CONDAMAD DRY, No Legacy, missing canonical owner, duplicate responsibility, missing guard, and test-guard coverage dimensions.
- Read-only mode: application code was not modified.
- Output folder: `_condamad/audits/frontend-design-system/2026-05-05-1411/`.

## Expected Responsibility

The frontend design-system layer should keep visual decisions in governed CSS tokens, utilities, registries, and static guards. Page and component CSS may keep migration debt only when it is explicitly classified, guarded, and attached to an exit condition.

## Evidence Summary

- The seven follow-up stories from the previous audit are present: `CS-026` through `CS-032` (E-001).
- Regression guardrails now include frontend invariants `RG-044` through `RG-050`, covering token namespaces, hardcoded values, typography, inline styles, CSS fallbacks, legacy style surfaces, and anti-drift guards (E-002).
- New registries and guards exist under `frontend/src/styles` and `frontend/src/tests`, including token namespace, typography role, fallback, legacy style, inline-style, and design-system guard artifacts (E-003, E-004).
- Targeted design-system tests pass: `npm run test -- design-system inline-style css-fallback legacy-style theme-tokens` reported 5 files and 108 tests passed (E-005).
- `npm run lint` and `npm run build` pass. Build emits the existing Vite chunk-size warning for the main bundle (E-006, E-007).
- Raw scans still show large governed migration debt: 1890 color-like literals outside core token files, 2627 non-tokenized spacing/radius/shadow declarations, 1533 non-tokenized typography declarations, 85 TSX inline style attributes, and 329 CSS fallback usages (E-008 through E-012).
- A full `npm run test` run failed once in `HelpPage.test.tsx`, while `npm run test -- HelpPage` passed immediately after. This indicates suite-level flakiness or parallel isolation risk, not a deterministic HelpPage unit failure (E-013).

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low | 1 |
| Info | 1 |

## Key Findings

- `F-001`: The previous canonical-token High finding is materially remediated by registries and guards.
- `F-002`: Hardcoded visual and typography values remain broad outside the migrated first batch.
- `F-003`: Inline-style policy blocks unclassified growth, but its exact allowlist still preserves static style debt.
- `F-004`: CSS fallback policy blocks unclassified growth, but the current fallback allowlist is still large and should be reduced.
- `F-005`: The full frontend test suite showed a non-deterministic failure, lowering confidence in whole-suite validation.

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
- Required regression evidence: E-002 through E-007 cover the active frontend guardrails.
- Allowed differences: no application code differences were introduced by this audit.

## Recommendations

1. Treat `CS-026` through `CS-032` as successful governance convergence: no new High design-system ownership finding remains.
2. Continue with smaller cleanup stories that reduce existing allowlists instead of expanding guard strictness immediately.
3. Prioritize static inline cleanup in `TurningPointsList.tsx`, `PrivacyPolicyPage.tsx`, `AccountSettings.tsx`, and `AstrologerProfilePage.tsx`.
4. Reduce CSS fallback exceptions by shared UI component first, especially `Select`, `UserMenu`, `NatalChartPage`, `App.css`, and `HelpPage.css`.
5. Investigate full Vitest suite isolation after the observed `HelpPage.test.tsx` full-run-only failure.

## Validation Plan

- Validate these audit artifacts with the CONDAMAD validator and lint scripts from the repository root.
- Because repository policy requires Python commands to run inside the venv, validation must be run after `.\.venv\Scripts\Activate.ps1`.
