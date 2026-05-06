# Audit Report - frontend-design-system

## Scope

- Domain key: `frontend-design-system`
- Target: `frontend/src` design-system governance after the refactors linked to audits `2026-05-04-2238`, `2026-05-05-1411`, `2026-05-05-1501`, `2026-05-05-1748`, `2026-05-05-1831`, `2026-05-05-1942`, `2026-05-05-2053`, and `2026-05-06-0016`.
- Archetype used: legacy-surface / test-guard-coverage / No Legacy + DRY audit adapted to the frontend design-system layer.
- Read-only mode: application code was not modified; only audit artifacts were written under this folder.

## Executive Result

The refactors are in a healthy state. Targeted design-system guards pass, the full frontend test suite passes, lint passes, and production build passes. The remaining findings are controlled design-system debt, not failing runtime behavior.

Compared with audit `2026-05-06-0108`:

- CSS fallback exceptions dropped from 10 to 3.
- Inline style exceptions dropped from 9 to 6.
- Missing premium tokens `--premium-text-muted` and `--premium-glass-border-soft` are now declared in `premium-theme.css`.
- Legacy admin prompt selectors and compatibility token aliases remain active and classified.
- Broad hardcoded visual scan remains large at 113 files and should be handled by bounded clusters.

## Evidence Summary

- `E-003`: targeted design-system guard suite PASS, 126 tests.
- `E-004`: full frontend tests PASS, 114 files, 1238 tests passed, 8 skipped.
- `E-005`: lint PASS.
- `E-006`: build PASS with existing Vite chunk-size warning.
- `E-009`: CSS fallback scan FAIL by design because 3 classified exceptions remain.
- `E-010`: inline style scan FAIL by design because 6 classified exceptions remain.
- `E-011`: broad hardcoded visual scan FAIL because 113 files still match literal visual/typography signals.
- `E-013`: legacy surface scan FAIL because active classified legacy surfaces remain.
- `E-014`: premium token scan PASS.

## Findings

- `F-001` Info: executable guard layer is present and passing.
- `F-002` Medium: 3 CSS fallback exceptions remain; only `AdminEntitlementsPage.css` is migration-only.
- `F-003` Medium: 6 inline style exceptions remain and need continued reduction or explicit API ownership.
- `F-004` Medium: 113 files still contain broad literal visual/typography signals outside the main token sources.
- `F-005` Medium: admin prompt legacy selectors and compatibility aliases remain active.
- `F-006` Info: build chunk-size warning remains a performance observation.
- `F-007` Info: premium token ownership issue from prior audit is resolved.

## Exhaustive Files To Modify

The exhaustive per-story file lists are in `03-story-candidates.md`:

- `SC-001`: CSS fallback debt, 4 files.
- `SC-002`: inline style debt, 13 files.
- `SC-003`: hardcoded visual cluster candidates, 113 scanned files plus conditional registries/tests.
- `SC-004`: legacy style surface extinction, 9 files.

Do not implement `SC-003` as a single repository-wide cleanup. Use that exhaustive list as the candidate inventory, then choose one coherent cluster and update only the files in that cluster plus required registries/tests.

## No Legacy / DRY Assessment

- No unclassified CSS fallback growth was found; remaining fallbacks are listed in `css-fallback-allowlist.md` and `design-system-allowlist.ts`.
- No unclassified inline style growth was found; remaining entries are listed in `inline-style-allowlist.ts` and `design-system-allowlist.ts`.
- Legacy style surfaces are not gone: `.admin-prompts-legacy*`, `.admin-prompts-modal--legacy-rollback`, `--text-*`, `--glass*`, and `--primary*` remain active and classified.
- DRY/token convergence is incomplete because local visual literals still compete with semantic tokens across 113 broad-scan files.

## Recommended Order

1. `SC-001`: remove the last migration-only CSS fallback. Smallest delta.
2. `SC-002`: reduce inline style exceptions where the component API is clear.
3. `SC-004`: migrate admin prompts legacy selectors or retire compatibility aliases after explicit decision.
4. `SC-003`: run only as a bounded cluster story after picking the product surface.
