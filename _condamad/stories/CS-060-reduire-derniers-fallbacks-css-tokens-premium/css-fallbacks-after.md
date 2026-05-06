# CS-060 - CSS fallbacks after

After capture apres migration.

Remaining scan:

```text
src/App.css:3128: width: calc(var(--usage-progress, 0) * 1%);
src/pages/settings/Settings.css:1052: width: calc(var(--usage-progress, 0) * 1%);
src/pages/admin/AdminEntitlementsPage.css:44: background: var(--glass-heavy, #1a1a1a);
```

Count after: 3 fallbacks.

Decisions:
- `--premium-text-muted` declared in `frontend/src/styles/premium-theme.css`.
- `--premium-glass-border-soft` declared in `frontend/src/styles/premium-theme.css`.
- `--usage-progress` entries kept as dynamic runtime bridges.
- `--glass-heavy` kept because the admin entitlement surface is outside this story's premium/token batch.

Registry sync:
- `frontend/src/styles/css-fallback-allowlist.md` contains the same 3 entries.
- `frontend/src/tests/design-system-allowlist.ts` contains the same 3 executable exceptions.
