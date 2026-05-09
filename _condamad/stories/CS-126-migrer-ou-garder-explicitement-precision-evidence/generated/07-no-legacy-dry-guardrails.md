<!-- Garde No Legacy et DRY pour CS-126. -->

# CS-126 No Legacy / DRY Guardrails

## Forbidden

- Wildcard `precision-*` or `evidence-*` allowlists.
- Duplicate active styles in `App.css` and feature CSS.
- `.precision-badge*` or `.evidence-*` App.css selectors retained as aliases
  after migration.
- `--app-precision-*` or `--app-evidence-*` retained without exact owner
  decision.
- `OLD`, `legacy`, `alias`, `compat`, `compatibility`, `shim`,
  `migration-only`.

## Required Evidence

- Before and after precision/evidence scans.
- Guard that fails on unclassified `precision/evidence` in `App.css`.
- Targeted consumer tests or exact documented skips.
- No stale CS-125 prefix registry entries after migration.
