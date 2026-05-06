# No Legacy / DRY Guardrails - CS-081

## Canonical owners

| Surface | Owner |
|---|---|
| Chat visual values | `.chat-page-container` semantic `--chat-*` variables |
| Global color/radius/shadow/space/type tokens | `frontend/src/styles/design-tokens.css` |
| Premium product layer tokens | `frontend/src/styles/premium-theme.css` |
| Token namespace documentation | `frontend/src/styles/token-namespace-registry.md` |
| Reintroduction guard | `frontend/src/tests/design-system-guards.test.ts` |

## Forbidden active patterns

- New wildcard exception in design-system allowlists.
- CSS variable fallback with a literal value.
- Duplicated local visual literal outside `--chat-*` owner.
- Runtime or API behavior changes in chat hooks and TSX components.
- New dependency or alternate styling system.

## Required evidence

- `hardcoded-values-before.md` records the initial cluster inventory.
- `hardcoded-values-after.md` records final decisions and scan classification.
- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`.
- Scans for colors, typography, radius/elevation and forbidden vocabulary.

## Classification notes

- Existing avatar fallback class names are UI image replacement names and not
  compatibility code.
- Existing `premium-shimmer` names are animation names and not runtime
  transitional behavior.
- No CSS variable fallback expression is introduced.
