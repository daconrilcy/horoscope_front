<!-- Registre d'ownership des surfaces CSS legacy frontend. -->

# Legacy Style Surface Registry

Chaque selecteur ou alias legacy actif doit avoir un owner, une cible canonique
et une condition de sortie. Les entrees ambiguës restent migration-only et ne
doivent pas croitre.

| Surface | Type | Status | Owner | Canonical target | Exit condition |
|---|---|---|---|---|---|
| `.admin-prompts-legacy*` | selector-family | external-active | `frontend/src/pages/admin/AdminPromptsPage.css` | admin prompts route components | deletion blocked while `AdminPromptsPage.tsx` consumes legacy markup; requires product/user decision before route-specific migration |
| `.admin-prompts-modal--legacy-rollback` | selector | external-active | `frontend/src/pages/admin/AdminPromptsPage.css` | admin prompts route modal styles | deletion blocked while rollback modal markup remains active; requires product/user decision before migration |
| `--text-*` | token-alias | compatibility | `frontend/src/styles/theme.css` | `--color-text-*` | retire after consumers migrate |
| `--glass*` | token-alias | compatibility | `frontend/src/styles/theme.css` | `--color-glass-*` | retire after consumers migrate |
| `--primary*` | token-alias | compatibility | `frontend/src/styles/theme.css` | `--color-primary*` | retire after consumers migrate |
