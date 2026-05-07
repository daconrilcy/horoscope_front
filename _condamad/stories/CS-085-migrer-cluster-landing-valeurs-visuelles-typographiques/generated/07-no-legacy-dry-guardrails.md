# No Legacy / DRY Guardrails - CS-085

## Canonical owners

- Global design values: `frontend/src/styles/design-tokens.css`, `theme.css`, `premium-theme.css`.
- Landing semantic extension: documented `--landing-*` namespace in `frontend/src/styles/token-namespace-registry.md`.
- Landing typography: roles or final decisions in `frontend/src/styles/typography-roles.md`.
- Reintroduction guard: `frontend/src/tests/design-system-guards.test.ts`.

## Forbidden active patterns

- `legacy`, `Legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` in touched active CSS.
- `var(--token, literal)` in landing CSS unless exactly classified by an existing allowlist, which this story does not expect.
- New folder-wide landing exceptions.
- Consumption of `--settings-*`, `--help-*`, `--chat-*`, `--app-*` from landing CSS.
- Duplicate local variables for roles already covered by existing tokens or `--landing-*`.

## Required negative evidence

- No Legacy vocabulary scan over `src/layouts/LandingLayout.css` and `src/pages/landing/**/*.css`.
- Page-scoped namespace scan over the same cluster.
- CSS fallback guard and scan.
- No unresolved limitation markers in this story capsule before closure.

## Review checklist

- Every remaining literal in after evidence is `registered-semantic-owner`, `runtime-custom-property` or `kept-one-off-final`.
- Repeated visual values have a documented owner.
- No allowlist was widened to hide landing debt.
- RG-044 to RG-060 are preserved.
