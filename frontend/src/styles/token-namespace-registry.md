<!-- Registre canonique des namespaces de tokens CSS frontend. -->

# Token Namespace Registry

`frontend/src/styles/design-tokens.css` est la source de verite des tokens globaux.
Les autres fichiers ne peuvent ajouter qu'une extension semantique, un alias de
compatibility cible ou une dette migration-only documentee.

| Namespace | Status | Owner | Canonical target | Exit condition |
|---|---|---|---|---|
| `--color-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--font-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--line-height-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--type-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--space-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--radius-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--shadow-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--duration-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--easing-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--layout-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--surface-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--glass-heavy` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--bg-*` | compatibility | `frontend/src/styles/theme.css` | `--color-bg-*` | retire after all consumers use `--color-bg-*` |
| `--cta-*` | compatibility | `frontend/src/styles/theme.css` | `--color-cta-*` | retire after all consumers use `--color-cta-*` |
| `--badge-*` | compatibility | `frontend/src/styles/theme.css` | `--color-badge-*` | retire after all consumers use `--color-badge-*` |
| `--hero-*` | semantic-extension | `frontend/src/styles/theme.css` | hero composition tokens | product decision before merge into global color tokens |
| `--love-*` | semantic-extension | `frontend/src/styles/theme.css` | thematic mini-card tokens | product decision before merge |
| `--work-*` | semantic-extension | `frontend/src/styles/theme.css` | thematic mini-card tokens | product decision before merge |
| `--energy-*` | semantic-extension | `frontend/src/styles/theme.css` | thematic mini-card tokens | product decision before merge |
| `--premium-*` | semantic-extension | `frontend/src/styles/premium-theme.css` | premium product layer | product decision before merge into globals |
| `--settings-*` | migration-only | `frontend/src/pages/settings/Settings.css` | settings page tokens | migrate when shared settings/profile tokens exist |
| `--profile-*` | migration-only | `frontend/src/pages/AstrologerProfilePage.css` | profile page tokens | migrate when shared profile tokens exist |
| `--astro-*` | migration-only | `frontend/src/App.css` | astrologer card local theme | migrate after card design-system story |
| `--usage-*` | dynamic | `frontend/src/pages/settings/Settings.css` | runtime progress value | permanent custom property bridge |
| `--sidebar-width` | dynamic | layout components | runtime layout value | permanent custom property bridge |
| `--period-accent` | dynamic | prediction timeline components | runtime accent value | permanent custom property bridge |
| `--nav-*` | compatibility | `frontend/src/styles/theme.css` | `--color-nav-*` | retire after all consumers migrate |
| `--line` | compatibility | `frontend/src/styles/theme.css` | `--color-line` | retire after all consumers migrate |
| `--success` | compatibility | `frontend/src/styles/theme.css` | `--color-success` | retire after all consumers migrate |
| `--danger` | compatibility | page/admin legacy styles | `--color-danger` | retire after all consumers migrate |
| `--btn-text` | compatibility | `frontend/src/styles/theme.css` | `--color-btn-text` | retire after all consumers migrate |
| `--purple_base` | migration-only | `frontend/src/App.css` | `--color-primary` as RGB token | replace with canonical RGB token |
| `--default_dropshadow` | migration-only | legacy app CSS | `--shadow-card` | replace in component migration |
| `--background-*` | migration-only | legacy calendar CSS | semantic state background tokens | migrate calendar styles |
| `--ni-*` | migration-only | `frontend/src/components/NatalInterpretation.css` | natal interpretation component tokens | migrate component styles |
| `--landing-*` | semantic-extension | landing layout and sections | premium landing layer | product decision before global merge |
| `--result-*` | migration-only | result pages | result page token layer | migrate to shared result tokens |
| `--timeline-*` | migration-only | prediction timeline CSS | prediction component tokens | migrate timeline design-system |
| `--page-*` | migration-only | page local CSS | global background tokens | migrate page local surfaces |
| `--inner-light` | migration-only | premium card local CSS | `--premium-inner-light` | replace in premium migration |
| `--accent-purple*` | migration-only | legacy/premium local CSS | `--premium-accent-purple*` or `--color-primary*` | migrate consumers |
| `--glass-surface-1` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass surface | migrate with daily premium token layer |
| `--glass-surface-2` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass surface | migrate with daily premium token layer |
| `--glass-surface-3` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass surface | migrate with daily premium token layer |
| `--glass-border` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass border | migrate with daily premium token layer |
| `--glass-border-strong` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass border | migrate with daily premium token layer |
| `--text-strong` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-main` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-meta` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-faint` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
