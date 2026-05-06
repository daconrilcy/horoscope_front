# Hardcoded Values After - CS-081

## Final owner

| Owner | Decision | Evidence |
|---|---|---|
| `.chat-page-container` in `frontend/src/pages/ChatPage.css` | registered-semantic-owner | `--chat-*` contains chat glass, message, scrollbar, elevation, radius, color and typography roles. |
| `frontend/src/styles/token-namespace-registry.md` | registered-semantic-owner | Row `--chat-*` documents the permanent chat page-scoped semantic layer. |
| `frontend/src/tests/design-system-guards.test.ts` | migrated | Guard `bloque le retour des literals chat migres par CS-081` verifies migrated values stay outside consumers. |

## Consumer decisions

| File | Decision |
|---|---|
| `frontend/src/pages/ChatPage.css` | Owner block keeps semantic `--chat-*`; consumer rules use `var(--chat-*)` or existing tokens. |
| `frontend/src/features/chat/components/ChatComposer.css` | migrated |
| `frontend/src/features/chat/components/ChatPageHeader.css` | migrated |
| `frontend/src/features/chat/components/ChatQuotaBanner.css` | migrated |
| `frontend/src/features/chat/components/ChatWindow.css` | migrated |
| `frontend/src/features/chat/components/ConversationItem.css` | migrated |
| `frontend/src/features/chat/components/ConversationList.css` | migrated |

## Scan classification

| Command | Result | Classification |
|---|---|---|
| `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | Hits only in `.chat-page-container` declarations. | registered-semantic-owner |
| `rg -n "font-size:\|font-weight:\|line-height:\|letter-spacing:" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | Consumer declarations use `var(--chat-*)`, `var(--type-*)`, `var(--font-size-*)` or `var(--line-height-*)`. | migrated |
| `rg -n "box-shadow:\|border-radius:\|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | Radius and elevation consumers use tokens or `--chat-*`; no CSS variable literal default found. | migrated |
| Vocabulary scan from the story validation plan | Existing avatar image replacement names and skeleton animation names only. | classified-non-transitional |

## Validation summary

- Guarded style subset: PASS, 6 files and 134 tests.
- `npm run lint`: PASS.
- `npm run build`: PASS, with existing Vite chunk-size warning.
