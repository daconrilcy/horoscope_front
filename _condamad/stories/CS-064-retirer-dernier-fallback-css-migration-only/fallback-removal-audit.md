<!-- Audit de retrait du fallback CSS migration-only pour CS-064. -->

# Fallback Removal Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `var(--glass-heavy, #1a1a1a)` | CSS fallback | historical-facade | `frontend/src/pages/admin/AdminEntitlementsPage.css` | `--glass-heavy` | delete | `--glass-heavy` est declare dans `frontend/src/styles/design-tokens.css`; le consommateur utilise `var(--glass-heavy)` sans literal | risque limite: le token doit rester declare par `theme-tokens` |
| `var(--usage-progress, 0)` | CSS fallback | canonical-active | `frontend/src/App.css`, `frontend/src/pages/settings/Settings.css` | runtime CSS custom property | keep | pont runtime documente dans `css-fallback-allowlist.md` | aucun risque nouveau |
