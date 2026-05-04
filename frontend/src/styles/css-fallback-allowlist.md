<!-- Registre exact des fallbacks CSS autorises ou migration-only. -->

# CSS Fallback Allowlist

Les tokens canoniques requis doivent etre consommes via `var(--token)` dans les
surfaces migrees. Les fallbacks restants sont des exceptions classees, pas une
deuxieme source de verite.

| File | Token | Literal | Status | Reason | Exit condition |
|---|---|---|---|---|---|
| `frontend/src/layouts/TwoColumnLayout.css` | `--sidebar-width` | `320px` | dynamic | largeur injectee par prop React | permanent |
| `frontend/src/pages/settings/Settings.css` | `--usage-progress` | `0` | dynamic | valeur de progression runtime | permanent |
| `frontend/src/App.css` | `--usage-progress` | `0` | dynamic | valeur de progression runtime | permanent |
| `frontend/src/styles/glass.css` | `--surface-glass-blur` | `14px` | compatibility | utilitaire partage chargeable hors theme complet | retirer apres garantie d'import global |
| `frontend/src/styles/utilities.css` | `--surface-glass-blur` | `14px` | compatibility | utilitaire partage chargeable hors theme complet | retirer apres garantie d'import global |
| `frontend/src/components/ui/Modal/Modal.css` | `--z-index-modal` | `2000` | semantic-extension | z-index applicatif non encore tokenise | migrer vers token layout |
| `frontend/src/components/ui/Select/Select.css` | `--z-index-dropdown` | `1000` | semantic-extension | z-index applicatif non encore tokenise | migrer vers token layout |
| `frontend/src/components/ui/Button/Button.css` | `--duration-fast` | `150ms` | compatibility | composant UI peut etre isole en tests | retirer apres import theme obligatoire |
| `frontend/src/components/ui/Button/Button.css` | `--duration-normal` | `250ms` | compatibility | composant UI peut etre isole en tests | retirer apres import theme obligatoire |
