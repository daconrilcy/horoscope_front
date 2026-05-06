# CS-063 - Legacy style before

Baseline capture.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.admin-prompts-legacy*` | selector-family | external-active | `AdminPromptsPage.css` route legacy | route-specific canonical markup | keep | registry + scan CSS | deletion requires product/user decision |
| `.admin-prompts-modal--legacy-rollback` | selector | external-active | rollback modal styles | route-specific modal markup | keep | registry + scan CSS | deletion requires product/user decision |
| `--text-*` | token-alias | compatibility | `App.css` and theme aliases | `--color-text-*` | keep | broad consumer scan | migration too broad for this story slice |
| `--glass*` | token-alias | compatibility | `App.css` and theme aliases | `--color-glass-*` | keep | broad consumer scan | migration too broad for this story slice |
| `--primary*` | token-alias | compatibility | `App.css` and theme aliases | `--color-primary*` | keep | broad consumer scan | migration too broad for this story slice |
