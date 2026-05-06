<!-- Synthese executive de l'audit frontend design-system apres CS-081. -->

# Executive Summary - frontend-design-system

## Result

The frontend design-system is stable after the implemented audit stories through CS-081. Focused guards, full Vitest, lint and production build pass. The recent compatibility, cross-page token, migration-only namespace, inline-style and CSS fallback surfaces remain bounded by executable tests.

## Findings By Severity

- Critical: 0
- High: 0
- Medium: 2
- Low: 1
- Info: 1

## Main Risks

1. `F-002`: 66 non-test application files still contain hardcoded visual or typography literals outside `frontend/src/styles/**`.
2. `F-003`: one active CSS comment still contains No Legacy vocabulary, and current guards do not scan CSS comments/vocabulary.
3. `F-004`: production build remains above Vite's chunk warning threshold.

## Story Candidates

- `SC-001`: migrate the next coherent hardcoded visual/typography cluster. The report provides the exhaustive 66-file affected inventory.
- `SC-002`: remove or classify the `legacy` CSS comment in `AdminPromptsPage.css` and harden the guard.

## Recommended Next Action

Implement `SC-002` first because it is small and closes a guard gap, then choose one bounded cluster from `SC-001` for the next visual literal migration.

