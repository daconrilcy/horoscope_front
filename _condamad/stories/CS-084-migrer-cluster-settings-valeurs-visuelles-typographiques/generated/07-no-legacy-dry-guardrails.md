# No Legacy / DRY Guardrails

## Canonical Owners

| Responsibility | Canonical owner |
|---|---|
| Global colors, type, spacing, radius, shadow tokens | `frontend/src/styles/design-tokens.css` |
| Settings page semantic roles | `--settings-*` declarations in `frontend/src/pages/settings/Settings.css`, registered in `token-namespace-registry.md` |
| Typography roles | `frontend/src/styles/typography-roles.md` and `--type-*` tokens |
| Runtime progress custom property | `--usage-progress` exact dynamic allowlist |
| Anti-return guards | `frontend/src/tests/design-system-guards.test.ts` |

## Forbidden Patterns

- `legacy`, `Legacy`, `alias`, `compat`, `compatibility`, `shim`, `fallback`, `migration-only` in active touched CSS.
- `var(--token, literal)` except exact `--usage-progress` dynamic property.
- New unregistered token namespace.
- `--settings-*` usage outside `frontend/src/pages/settings/Settings.css`.
- Duplicate page-local visual roles when an existing token or role covers the responsibility.

## Required Negative Evidence

| Pattern | Scope | Expected |
|---|---|---|
| `legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only` | `frontend/src/pages/settings/Settings.css` | zero hits |
| `var\(\s*--[a-zA-Z0-9_-]+\s*,` | `frontend/src/pages/settings/Settings.css` | only allowlisted `--usage-progress` |
| `--settings-` | `frontend/src --glob "*.css"` | page-scoped usage remains in owner CSS only |
| migrated visual literals | `frontend/src/pages/settings/Settings.css` outside owner declarations | zero unclassified hits |

## Exceptions

- `--usage-progress` with literal `0` remains allowed as a runtime custom property bridge, already documented in `frontend/src/styles/css-fallback-allowlist.md`.

## Review Checklist

- No React behavior changed.
- No new dependency or package script.
- No wildcard/folder-wide allowlist.
- Every remaining literal is documented in `hardcoded-values-after.md`.
- Guard test fails on reintroduction of migrated Settings literals.
