<!-- Registre exact des fallbacks CSS autorises ou migration-only. -->

# CSS Fallback Allowlist

Les tokens canoniques requis doivent etre consommes via `var(--token)` dans les
surfaces migrees. Les fallbacks restants sont des exceptions classees, pas une
deuxieme source de verite.

| File | Token | Literal | Status | Reason | Exit condition |
|---|---|---|---|---|---|
| `frontend/src/styles/app/base.css` | `--usage-progress` | `0` | dynamic | valeur de progression runtime injectee par propriete CSS | permanent tant que la progression reste runtime |
| `frontend/src/pages/settings/Settings.css` | `--usage-progress` | `0` | dynamic | valeur de progression runtime injectee par propriete CSS | permanent tant que la progression reste runtime |
