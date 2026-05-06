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
| `--default_dropshadow` | migration-only | legacy app CSS | `--shadow-card` | replace in component migration |
| `--landing-*` | semantic-extension | landing layout and sections | premium landing layer | product decision before global merge |
| `--help-*` | semantic-extension | `frontend/src/pages/HelpPage.css` | help page visual roles | permanent page-scoped semantic layer |
| `--admin-settings-*` | semantic-extension | `frontend/src/pages/admin/AdminSettingsPage.css` | admin settings cluster local visual roles | permanent page-scoped semantic layer |
| `--admin-entitlements-*` | semantic-extension | `frontend/src/pages/admin/AdminEntitlementsPage.css` | admin entitlements cluster local visual roles | permanent page-scoped semantic layer |
| `--calendar-*` | semantic-extension | `frontend/src/index.css` | calendar cell background states | permanent calendar UI role |
| `--consultation-result-*` | semantic-extension | `frontend/src/pages/ConsultationResultPage.css` | consultation result page visual roles | permanent page-scoped semantic layer |
| `--natal-interpretation-*` | semantic-extension | `frontend/src/components/NatalInterpretation.css` | natal interpretation component roles | permanent component-scoped semantic layer |
| `--prediction-timeline-*` | semantic-extension | prediction timeline CSS | prediction timeline layout roles | permanent component-scoped semantic layer |
| `--glass-surface-1` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass surface | migrate with daily premium token layer |
| `--glass-surface-2` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass surface | migrate with daily premium token layer |
| `--glass-surface-3` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass surface | migrate with daily premium token layer |
| `--glass-border` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass border | migrate with daily premium token layer |
| `--glass-border-strong` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium glass border | migrate with daily premium token layer |
| `--text-strong` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-main` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-meta` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-faint` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
