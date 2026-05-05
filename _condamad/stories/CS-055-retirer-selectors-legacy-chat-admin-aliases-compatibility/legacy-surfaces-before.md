# CS-055 legacy surfaces before

Baseline capture for the bounded frontend batch focused on
`frontend/src/pages/admin/AdminPromptsPage.css`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `--glass`, `--glass-2`, `--glass-border` in `AdminPromptsPage.css` | token-alias | migrate | 56 local matches before migration | `--color-glass-bg`, `--color-glass-bg-2`, `--color-glass-border` from `design-tokens.css` | replace-consumer | `rg -n -e "--glass" frontend/src/pages/admin/AdminPromptsPage.css` | Low: direct canonical token owner exists. |
| `--success` in `AdminPromptsPage.css` | token-alias | migrate | 5 local matches before migration | `--color-success` from `design-tokens.css` | replace-consumer | `rg -n -e "--success" frontend/src/pages/admin/AdminPromptsPage.css` | Low: status semantic is unchanged. |
| `--danger` in `AdminPromptsPage.css` | token-alias | migrate | 5 local matches before migration | `--color-danger` from `design-tokens.css` | replace-consumer | `rg -n -e "--danger" frontend/src/pages/admin/AdminPromptsPage.css` | Low: status semantic is unchanged. |
| `--warning` in `AdminPromptsPage.css` | token-alias | migrate | 7 local matches before migration | `--color-admin-warning-ink`, `--color-admin-warning-border`, `--color-admin-warning-surface` from `design-tokens.css` | replace-consumer | `rg -n -e "--warning" frontend/src/pages/admin/AdminPromptsPage.css` | Medium: no global `--color-warning`; admin warning tokens are the route-local canonical target. |
| `.admin-prompts-legacy*` | selector-family | external-active | active TSX consumers in `AdminPromptsPage.tsx` | admin prompts route styles | needs-user-decision | `rg -n "admin-prompts-legacy|admin-prompts-modal--legacy-rollback" frontend/src/pages/admin/AdminPromptsPage.tsx` | High: selector deletion would break the active legacy investigation route. |
| `.admin-prompts-modal--legacy-rollback` | selector | external-active | active TSX consumer in `AdminPromptsPage.tsx` | admin prompts route modal styles | needs-user-decision | `rg -n "admin-prompts-modal--legacy-rollback" frontend/src/pages/admin/AdminPromptsPage.tsx` | High: selector deletion would break rollback modal styling. |
| Chat shell legacy selectors in `App.css` | selector-family | needs-user-decision | active scan hits in `App.css`; migration intentionally out of this batch | chat component CSS owners listed in registry | needs-user-decision | `rg -n "chat-.*legacy|conversation-.*legacy|astrologer-chip-.*legacy" frontend/src/App.css` | High: broad chat shell migration is explicitly out of scope. |
