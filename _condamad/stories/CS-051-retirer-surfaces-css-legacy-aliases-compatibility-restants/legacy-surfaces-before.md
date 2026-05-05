<!-- Inventaire before des surfaces legacy CS-051. -->

# CS-051 Legacy Surfaces Before

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.chat-layout-mobile-action-legacy` | selector | dead | zero TSX consumer | `.chat-layout-mobile-action` in `ChatPage.css` | delete | `rg` TSX only finds canonical class | none |
| `.admin-prompts-legacy*` | selector-family | external-active | active route tab | admin prompts legacy tab | keep | active TSX consumers | product scope |
| `.admin-prompts-modal--legacy-rollback` | selector | external-active | active rollback modal | admin prompts modal | keep | active TSX consumer | product scope |
| `--text-*`, `--glass*`, `--primary*` | token-alias | external-active | broad CSS consumers | `--color-*` tokens | keep | broad scan hits | requires separate migration |

