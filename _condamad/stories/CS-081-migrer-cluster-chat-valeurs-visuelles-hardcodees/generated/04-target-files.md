# Target Files - CS-081

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/00-story.md`
- `frontend/package.json`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`

## Required searches

- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"`
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"`
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"`
- `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/ChatPage.css src/features/chat/components`

## Modified files

- `frontend/src/pages/ChatPage.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`

## Forbidden unless justified

- `frontend/src/features/chat/hooks/**`
- `frontend/src/features/chat/index.ts`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/package.json`
- `backend/**`
