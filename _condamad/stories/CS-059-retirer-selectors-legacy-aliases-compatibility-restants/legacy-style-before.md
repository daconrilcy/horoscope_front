# Legacy style before CS-059

Scan command: `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css` from `frontend`.

Initial registry included 17 active rows: 12 chat selector families, 2 admin external-active selector rows, and 3 token alias families.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| chat `*-legacy` selectors in `App.css` | selector-family | dead | no TSX consumers | canonical chat component CSS files | delete | active components use non-legacy classes in `features/chat/components` | low |
| `.admin-prompts-legacy*` | selector-family | external-active | `AdminPromptsPage.tsx` | admin prompts route styles | keep | story blocks deletion without decision | deletion could break active admin route |
| `.admin-prompts-modal--legacy-rollback` | selector | external-active | `AdminPromptsPage.tsx` rollback modal | admin prompts route styles | keep | story blocks deletion without decision | deletion could break active admin route |
| `--text-*`, `--glass*`, `--primary*` | token-alias | compatibility | broad active CSS consumers | `--color-*` tokens | keep | consumers still active outside chat selector lot | broad migration required |
