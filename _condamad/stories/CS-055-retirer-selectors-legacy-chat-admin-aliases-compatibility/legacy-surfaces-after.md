# CS-055 legacy surfaces after

Final capture for the bounded frontend batch focused on
`frontend/src/pages/admin/AdminPromptsPage.css`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `--glass`, `--glass-2`, `--glass-border` in `AdminPromptsPage.css` | token-alias | remove-now | zero local alias consumers after migration | `--color-glass-bg`, `--color-glass-bg-2`, `--color-glass-border` from `design-tokens.css` | replace-consumer | `rg -n -e "--glass" frontend/src/pages/admin/AdminPromptsPage.css` returns only selector/comment-free canonical misses; `rg -n -e "var\\(--color-glass" frontend/src/pages/admin/AdminPromptsPage.css` shows canonical replacements. | Low: global aliases remain for other active consumers, but this route no longer depends on them. |
| `--success` in `AdminPromptsPage.css` | token-alias | remove-now | zero local alias consumers after migration | `--color-success` from `design-tokens.css` | replace-consumer | `rg -n -e "--success" frontend/src/pages/admin/AdminPromptsPage.css` has no alias-token hits after migration. | Low: global alias remains for other active consumers. |
| `--danger` in `AdminPromptsPage.css` | token-alias | remove-now | zero local alias consumers after migration | `--color-danger` from `design-tokens.css` | replace-consumer | `rg -n -e "--danger" frontend/src/pages/admin/AdminPromptsPage.css` has no alias-token hits after migration. | Low: global alias remains for other active consumers. |
| `--warning` in `AdminPromptsPage.css` | token-alias | remove-now | zero local alias consumers after migration | `--color-admin-warning-ink`, `--color-admin-warning-border`, `--color-admin-warning-surface` from `design-tokens.css` | replace-consumer | `rg -n -e "--warning" frontend/src/pages/admin/AdminPromptsPage.css` only matches class names such as `.admin-prompts-resolved__state--warning`; token usage migrated. | Medium: no global warning token was introduced. |
| `.admin-prompts-legacy*` | selector-family | external-active | active TSX consumers remain in `AdminPromptsPage.tsx` | admin prompts route styles | needs-user-decision | `rg -n "admin-prompts-legacy|admin-prompts-modal--legacy-rollback" frontend/src/pages/admin/AdminPromptsPage.tsx` still shows active route markup. | High: deletion remains blocked without product/user decision. |
| `.admin-prompts-modal--legacy-rollback` | selector | external-active | active TSX consumer remains in `AdminPromptsPage.tsx` | admin prompts route modal styles | needs-user-decision | `rg -n "admin-prompts-modal--legacy-rollback" frontend/src/pages/admin/AdminPromptsPage.tsx` still shows active modal markup. | High: deletion remains blocked without product/user decision. |
| Chat shell legacy selectors in `App.css` | selector-family | needs-user-decision | active scan hits remain in `App.css` | chat component CSS owners listed in registry | needs-user-decision | `rg -n "chat-.*legacy|conversation-.*legacy|astrologer-chip-.*legacy" frontend/src/App.css` remains non-zero and unchanged by this batch. | High: broad chat shell migration remains out of scope. |

## Registry decision

`legacy-style-surface-registry.md` now persists the active admin blocker:
`.admin-prompts-legacy*` and `.admin-prompts-modal--legacy-rollback` are
classified `external-active` because `AdminPromptsPage.tsx` still consumes the
legacy markup. `token-namespace-registry.md` remains unchanged because the
global compatibility aliases are still consumed outside this bounded
`AdminPromptsPage.css` batch.
