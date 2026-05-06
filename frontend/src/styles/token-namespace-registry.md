<!-- Registre canonique des namespaces de tokens CSS frontend. -->

# Token Namespace Registry

`frontend/src/styles/design-tokens.css` est la source de verite des tokens globaux.
Les autres fichiers ne peuvent ajouter qu'une extension semantique durable et
sourcee dans ce registre.

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
| `--settings-*` | semantic-extension | `frontend/src/pages/settings/Settings.css` | settings page visual roles | permanent page-scoped semantic layer |
| `--profile-*` | semantic-extension | `frontend/src/pages/AstrologerProfilePage.css` | astrologer profile page visual roles | permanent page-scoped semantic layer |
| `--astro-*` | semantic-extension | `frontend/src/App.css` | astrologer card local visual roles | permanent component-scoped semantic layer |
| `--app-*` | semantic-extension | `frontend/src/App.css` | app shell, catalogue and dashboard summary visual roles | permanent app-scoped semantic layer |
| `--usage-*` | dynamic | `frontend/src/pages/settings/Settings.css` | runtime progress value | permanent custom property bridge |
| `--sidebar-width` | dynamic | layout components | runtime layout value | permanent custom property bridge |
| `--period-accent` | dynamic | prediction timeline components | runtime accent value | permanent custom property bridge |
| `--landing-*` | semantic-extension | landing layout and sections | premium landing layer | product decision before global merge |
| `--help-*` | semantic-extension | `frontend/src/pages/HelpPage.css` | help page visual roles | permanent page-scoped semantic layer |
| `--chat-*` | semantic-extension | `frontend/src/pages/ChatPage.css` | chat cluster visual and typography roles | permanent chat page-scoped semantic layer |
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
