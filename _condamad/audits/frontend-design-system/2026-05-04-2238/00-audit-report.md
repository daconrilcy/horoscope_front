# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend/src` design-system and style consumption layer.
- Audit archetype: custom frontend design-system audit using CONDAMAD DRY, No Legacy, missing canonical owner, duplicate responsibility, and missing guard dimensions.
- Read-only mode: application code was not modified.
- Output folder: `_condamad/audits/frontend-design-system/2026-05-04-2238/`.

## Expected Responsibility

The frontend design-system layer should provide one governed source of truth for colors, backgrounds, surfaces, typography, spacing, margins, padding, borders, border radius, shadows, focus states, and component-level visual semantics. Page and component CSS should consume those tokens rather than redefining approximate values.

## Evidence Summary

- Token foundations exist in `frontend/src/styles/design-tokens.css`, with compatibility mappings in `theme.css` and a separate premium layer in `premium-theme.css` (E-002).
- Existing guardrails in `_condamad/stories/regression-guardrails.md` are backend/documentation oriented and do not currently protect frontend design-token usage (E-010).
- Static scans found 1696 color literals outside the main token files, 2823 non-tokenized spacing/radius-related declarations, 1393 non-tokenized typography declarations, 90 TSX inline style attributes, and 329 CSS variable fallbacks (E-003 through E-007).
- Large CSS files concentrate risk: `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css`, and `AstrologerProfilePage.css` are the largest style surfaces (E-009).

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 4 |
| Low | 1 |
| Info | 0 |

## Key Findings

- `F-001`: Token ownership is not canonical. Several namespaces and compatibility layers can make equivalent design decisions.
- `F-002`: Repeated hardcoded design values duplicate token responsibilities across major surfaces.
- `F-003`: Typography roles are not centralized, so hierarchy is encoded repeatedly in local CSS.
- `F-004`: Static inline styles bypass the stylesheet-only rule and need classification.
- `F-005`: `var(--token, fallback)` usage preserves hidden approximations.
- `F-006`: Legacy style surfaces and aliases remain active without a migration registry.
- `F-007`: Existing tests validate token values but not token consumption discipline.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`.
- Applicable invariants: none directly applicable; current active invariants protect backend API, DB, LLM, docs, scripts, and prediction backend surfaces (E-010).
- Non-applicable invariants: RG-001 through RG-043 are outside the audited frontend design-system surface for this audit.
- Required regression evidence: future stories should add frontend-specific guards for token ownership, hardcoded values, inline styles, CSS fallbacks, and legacy selectors.
- Allowed differences: no application code differences were introduced by this audit.

## Recommendations

1. Run `SC-001` first to define token ownership, compatibility aliases, and import-layer status.
2. Run `SC-002` next to centralize repeated colors, glass surfaces, status values, spacing, radius, and shadows.
3. Add `SC-007` guards early, after the first allowlists exist, so new drift is blocked.
4. Handle `SC-003`, `SC-004`, `SC-005`, and `SC-006` as focused cleanup stories rather than one broad refactor.

## Validation Plan

- Validate the audit artifacts with the CONDAMAD validator and lint scripts from the repository root.
- Because repository policy requires Python commands to run inside the venv, validation must be run after `.\.venv\Scripts\Activate.ps1`.
