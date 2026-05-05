# CS-040 CSS fallback contract before

## Baseline

- Markdown registry rows: 7 documented exceptions in `frontend/src/styles/css-fallback-allowlist.md`.
- Executable allowlist entries: 165 entries in `CSS_FALLBACK_EXCEPTIONS`.
- Delta: 158 executable entries were not represented by the markdown registry.

## Finding source

- `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-002`.
- `RG-048` and `RG-050` require exact, executable exceptions.
