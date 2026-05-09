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
| `--letter-spacing-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--type-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--type-admin-*` | canonical | `frontend/src/styles/design-tokens.css` | admin typography roles | none |
| `--space-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--radius-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--radius-admin-*` | canonical | `frontend/src/styles/design-tokens.css` | admin shape roles | none |
| `--shadow-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--shadow-admin-*` | canonical | `frontend/src/styles/design-tokens.css` | admin elevation roles | none |
| `--duration-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--easing-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--layout-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--surface-*` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--glass-heavy` | canonical | `frontend/src/styles/design-tokens.css` | self | none |
| `--glass-surface-*` | semantic-extension | `frontend/src/styles/glass.css` | premium glass surfaces shared by daily and reusable glass cards | permanent shared glass layer |
| `--glass-border*` | semantic-extension | `frontend/src/styles/glass.css` | premium glass borders shared by daily and reusable glass cards | permanent shared glass layer |
| `--glass-base-*` | semantic-extension | `frontend/src/styles/glass.css` | reusable base glass effects | permanent shared glass layer |
| `--glass-card-*` | semantic-extension | `frontend/src/styles/glass.css` | reusable glass card visual roles | permanent shared glass layer |
| `--hero-*` | semantic-extension | `frontend/src/styles/theme.css` | hero composition tokens | product decision before merge into global color tokens |
| `--love-*` | semantic-extension | `frontend/src/styles/theme.css` | thematic mini-card tokens | product decision before merge |
| `--work-*` | semantic-extension | `frontend/src/styles/theme.css` | thematic mini-card tokens | product decision before merge |
| `--energy-*` | semantic-extension | `frontend/src/styles/theme.css` | thematic mini-card tokens | product decision before merge |
| `--premium-*` | semantic-extension | `frontend/src/styles/premium-theme.css` | premium product layer | product decision before merge into globals |
| `--settings-*` | semantic-extension | `frontend/src/pages/settings/Settings.css` | settings page visual roles | permanent page-scoped semantic layer |
| `--profile-*` | semantic-extension | `frontend/src/pages/AstrologerProfilePage.css` | astrologer profile page visual roles | permanent page-scoped semantic layer |
| `--astro-*` | semantic-extension | `frontend/src/App.css` | astrologer card local visual roles | permanent component-scoped semantic layer |
| `--app-*` | semantic-extension | `frontend/src/App.css` | generic App primitives for page, section, stack, grid, card, panel, actions, states, badges, avatars and modals; residual App-owned specific names require exact CS-124 expiry entries | permanent app-scoped semantic layer; mechanical repeated selector names are blocked by CS-087 guard and page-specific names by CS-124 |
| `--usage-*` | dynamic | `frontend/src/pages/settings/Settings.css` | runtime progress value | permanent custom property bridge |
| `--period-accent` | dynamic | prediction timeline components | runtime accent value | permanent custom property bridge |
| `--landing-*` | semantic-extension | `frontend/src/layouts/LandingLayout.css` | landing visual and typography semantic owners consumed by landing sections | permanent landing-scoped semantic layer |
| `--help-*` | semantic-extension | `frontend/src/pages/HelpPage.css` | help page visual roles | permanent page-scoped semantic layer |
| `--chat-*` | semantic-extension | `frontend/src/pages/ChatPage.css` | chat cluster visual and typography roles | permanent chat page-scoped semantic layer |
| `--admin-settings-*` | semantic-extension | `frontend/src/pages/admin/AdminSettingsPage.css` | admin settings cluster local visual roles | permanent page-scoped semantic layer |
| `--admin-entitlements-*` | semantic-extension | `frontend/src/pages/admin/AdminEntitlementsPage.css` | admin entitlements cluster local visual roles | permanent page-scoped semantic layer |
| `--calendar-*` | semantic-extension | `frontend/src/index.css` | calendar cell background states | permanent calendar UI role |
| `--consultation-result-*` | semantic-extension | `frontend/src/pages/ConsultationResultPage.css` | consultation result page visual roles | permanent page-scoped semantic layer |
| `--natal-interpretation-*` | semantic-extension | `frontend/src/features/natal-chart/NatalInterpretation.css` | natal interpretation feature roles | permanent feature-scoped semantic layer |
| `--prediction-timeline-*` | semantic-extension | prediction timeline CSS | prediction timeline layout roles | permanent component-scoped semantic layer |
| `--text-strong` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-main` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-meta` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-faint` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
