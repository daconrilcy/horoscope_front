<!-- Registre d'ownership des surfaces CSS legacy frontend. -->

# Legacy Style Surface Registry

Chaque selecteur ou alias legacy actif doit avoir un owner, une cible canonique
et une condition de sortie. Les entrees ambiguës restent migration-only et ne
doivent pas croitre.

| Surface | Type | Status | Owner | Canonical target | Exit condition |
|---|---|---|---|---|---|
| `.chat-layout-legacy*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ChatLayout.css` | migrate chat shell styles |
| `.chat-layout-mobile-action-*` | selector-family | migration-only | `frontend/src/App.css` | chat mobile action component styles | migrate chat shell styles |
| `.chat-layout-panel-legacy*` | selector-family | migration-only | `frontend/src/App.css` | chat panel components | migrate chat shell styles |
| `.conversation-list-legacy*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ConversationList.css` | migrate conversation list styles |
| `.conversation-list-*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ConversationList.css` | migrate conversation list styles |
| `.conversation-item-legacy*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ConversationItem.tsx` styles | migrate conversation item styles |
| `.conversation-item-*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ConversationItem.tsx` styles | migrate conversation item styles |
| `.chat-window-legacy*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ChatWindow.css` | migrate chat window styles |
| `.chat-window-*` | selector-family | migration-only | `frontend/src/App.css` | `features/chat/components/ChatWindow.css` | migrate chat window styles |
| `.chat-composer-legacy*` | selector-family | migration-only | `frontend/src/App.css` | chat composer component styles | migrate composer styles |
| `.chat-composer-*` | selector-family | migration-only | `frontend/src/App.css` | chat composer component styles | migrate composer styles |
| `.astrologer-chip-legacy*` | selector-family | migration-only | `frontend/src/App.css` | astrologer chip component styles | migrate chip styles |
| `.astrologer-chip-*` | selector-family | migration-only | `frontend/src/App.css` | astrologer chip component styles | migrate chip styles |
| `.admin-prompts-legacy*` | selector-family | migration-only | `frontend/src/pages/admin/AdminPromptsPage.css` | admin prompts route components | migrate route-specific legacy screen |
| `.admin-prompts-modal--legacy-rollback` | selector | migration-only | `frontend/src/pages/admin/AdminPromptsPage.css` | admin prompts route modal styles | migrate route-specific legacy screen |
| `--text-*` | token-alias | compatibility | `frontend/src/styles/theme.css` | `--color-text-*` | retire after consumers migrate |
| `--glass*` | token-alias | compatibility | `frontend/src/styles/theme.css` | `--color-glass-*` | retire after consumers migrate |
| `--primary*` | token-alias | compatibility | `frontend/src/styles/theme.css` | `--color-primary*` | retire after consumers migrate |
