<!-- Guardrails No Legacy et DRY appliques a CS-111. -->

# No Legacy / DRY Guardrails CS-111

## Forbidden

- `style={{ '--sidebar-width': sidebarWidth }}`
- `sidebarWidth` prop on `TwoColumnLayout`
- `--sidebar-width` generic active token
- allowlist row for `TwoColumnLayout`
- wrapper, alias, shim, fallback, or retained compatibility facade

## Canonical owners

- Two-column sidebar width: `frontend/src/layouts/TwoColumnLayout.css`
- Chat sidebar width: `--chat-sidebar-width` in `frontend/src/pages/ChatPage.css`
- Inline-style policy: `frontend/src/tests/inline-style-allowlist.ts`

## Hit classification

| Pattern | Classification | Action | Status |
|---|---|---|---|
| `sidebarWidth` | active legacy removed | remove prop and inline style | PASS |
| `--sidebar-width` | active generic token removed | replace chat consumer with `--chat-sidebar-width` | PASS |
| `TwoColumnLayout` allowlist | active legacy removed | delete allowlist rows | PASS |
