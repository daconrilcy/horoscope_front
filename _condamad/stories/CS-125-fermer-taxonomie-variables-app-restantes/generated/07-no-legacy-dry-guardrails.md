<!-- Garde No Legacy et DRY pour CS-125. -->

# CS-125 No Legacy / DRY Guardrails

## Forbidden

- Wildcard `--app-*` allowlists.
- Broad folder exceptions.
- Compatibility selectors, aliases, wrappers, shims, or silent fallbacks.
- Unclassified `--app-*` prefixes in `frontend/src/App.css`.
- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`,
  `migration-only` in active `App.css`.

## Required Evidence

- Before and after taxonomy artifacts.
- Positive prefix registry in `design-system-guards.test.ts` or exact
  allowlist source.
- No stale App prefix exceptions.
- Validation scans from `generated/06-validation-plan.md`.
