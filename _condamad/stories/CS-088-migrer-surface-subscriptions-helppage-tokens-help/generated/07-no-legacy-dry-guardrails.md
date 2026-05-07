# No Legacy / DRY Guardrails

## Canonical owners

- Help subscriptions styles: `frontend/src/pages/HelpPage.css`
- Help page-scoped tokens: `--help-*` declared in `:where(.help-page, .help-bg-halo)`
- Global tokens: `frontend/src/styles/design-tokens.css`
- Typography documentation: `frontend/src/styles/typography-roles.md`
- Anti-return guard: `frontend/src/tests/design-system-guards.test.ts`

## Forbidden for this story

- New compatibility layer, shim, alias, fallback, migration-only namespace or broad exception.
- `var(--token, literal)` in `HelpPage.css`.
- Consumption of page-scoped namespaces other than `--help-*` from `HelpPage.css`.
- React extraction, route changes, API changes, dependency changes.
- `PASS with limitation`, TODO or unclassified legacy vocabulary in touched active CSS.

## Required negative evidence

- `rg -n -- "--settings-|--app-|--chat-|--landing-|--admin-" src/pages/HelpPage.css`
- `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/HelpPage.css`
- Targeted design-system guard proving subscriptions literals migrated from the section do not return outside the owner block.

## Review checklist

- No duplicated subscriptions CSS path was created.
- Every migrated literal has a final decision in `hardcoded-values-after.md`.
- No allowlist was broadened.
- `RG-044` through `RG-052` and `RG-060` remain respected for the Help surface.
