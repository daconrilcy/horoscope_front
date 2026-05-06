# Hardcoded Values Before - CS-081

## Scope

- `frontend/src/pages/ChatPage.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`

## Baseline commands

```powershell
Push-Location frontend
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"
Pop-Location
```

## Baseline summary

| Category | Initial evidence summary | Files impacted |
|---|---|---|
| Colors and gradients | Many `rgba(...)`, hex values and gradients in page, shell, header, composer, message bubbles, list items and scrollbars. | `ChatPage.css`, `ChatComposer.css`, `ChatPageHeader.css`, `ChatWindow.css`, `ConversationItem.css`, `ConversationList.css` |
| Typography | Pixel sizes, numeric weights, line-heights and tracking values repeated across header, composer, window and list surfaces. | `ChatPage.css`, `ChatComposer.css`, `ChatPageHeader.css`, `ChatWindow.css`, `ConversationItem.css`, `ConversationList.css` |
| Radius and elevation | Local radius and shadow literals across panels, controls, avatars, bubbles, popups and scrollbars. | `ChatPage.css`, `ChatComposer.css`, `ChatPageHeader.css`, `ChatQuotaBanner.css`, `ChatWindow.css`, `ConversationItem.css`, `ConversationList.css` |

## Initial decision

The cluster requires one documented semantic owner for chat composition values.
Repeated visual and typographic values should be migrated to tokens or
`--chat-*`; no runtime behavior is in scope.
