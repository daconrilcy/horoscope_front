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
| `--starfield-*` | semantic-extension | `frontend/src/styles/premium-theme.css` | dark astral background star, milky-way and shooting-star roles | permanent CS-138 background layer |
| `--settings-*` | semantic-extension | `frontend/src/pages/settings/Settings.css` | settings page visual roles | permanent page-scoped semantic layer |
| `--profile-*` | semantic-extension | `frontend/src/pages/AstrologerProfilePage.css` | astrologer profile page visual roles | permanent page-scoped semantic layer |
| `--astro-*` | semantic-extension | `frontend/src/App.css` | astrologer card local visual roles | permanent component-scoped semantic layer |
| `--app-account-*` | semantic-extension | `frontend/src/App.css` | account controls in App.css | retained by CS-125 positive prefix registry |
| `--app-activities-*` | semantic-extension | `frontend/src/App.css` | activities page states in App.css | retained by CS-125 positive prefix registry |
| `--app-activity-*` | semantic-extension | `frontend/src/App.css` | activity flow and premium cards in App.css | retained by CS-125 positive prefix registry |
| `--app-admin-*` | semantic-extension | `frontend/src/App.css` | admin layout typography retained in App.css | retained by CS-125 positive prefix registry |
| `--app-astro-*` | semantic-extension | `frontend/src/App.css` | astro catalog local roles in App.css | retained by CS-125 positive prefix registry |
| `--app-banner-*` | semantic-extension | `frontend/src/App.css` | activity banner text roles in App.css | retained by CS-125 positive prefix registry |
| `--app-bg-*` | semantic-extension | `frontend/src/styles/backgrounds.css` | canonical application background route intensity controls | permanent RG-084/RG-085 background layer |
| `--app-bottom-*` | semantic-extension | `frontend/src/App.css` | bottom navigation primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-btn-*` | semantic-extension | `frontend/src/App.css` | button danger variant in App.css | retained by CS-125 positive prefix registry |
| `--app-button-*` | semantic-extension | `frontend/src/App.css` | global button primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-card-*` | semantic-extension | `frontend/src/App.css` | card primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-chat-*` | semantic-extension | `frontend/src/App.css` | chat shells still styled by App.css | retained by CS-125 positive prefix registry |
| `--app-checkbox-*` | semantic-extension | `frontend/src/App.css` | checkbox labels in App.css | retained by CS-125 positive prefix registry |
| `--app-control-*` | semantic-extension | `frontend/src/App.css` | control panel roles in App.css | retained by CS-125 positive prefix registry |
| `--app-danger-*` | semantic-extension | `frontend/src/App.css` | danger action roles in App.css | retained by CS-125 positive prefix registry |
| `--app-day-*` | semantic-extension | `frontend/src/App.css` | day shell role in App.css | retained by CS-125 positive prefix registry |
| `--app-degraded-*` | semantic-extension | `frontend/src/App.css` | degraded warning role in App.css | retained by CS-125 positive prefix registry |
| `--app-drawing-*` | semantic-extension | `frontend/src/App.css` | drawing option cards in App.css | retained by CS-125 positive prefix registry |
| `--app-error-*` | semantic-extension | `frontend/src/App.css` | error message primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-flow-*` | semantic-extension | `frontend/src/App.css` | consultation flow states in App.css | retained by CS-125 positive prefix registry |
| `--app-form-*` | semantic-extension | `frontend/src/App.css` | form primitives in App.css | retained by CS-125 positive prefix registry |
| `--app-interaction-*` | semantic-extension | `frontend/src/App.css` | interaction toggle section in App.css | retained by CS-125 positive prefix registry |
| `--app-message-*` | semantic-extension | `frontend/src/App.css` | message bubble roles in App.css | retained by CS-125 positive prefix registry |
| `--app-mobile-*` | semantic-extension | `frontend/src/App.css` | mobile navigation roles in App.css | retained by CS-125 positive prefix registry |
| `--app-modal-*` | semantic-extension | `frontend/src/App.css` | modal primitives in App.css | retained by CS-125 positive prefix registry |
| `--app-nickname-*` | semantic-extension | `frontend/src/App.css` | nickname input group in App.css | retained by CS-125 positive prefix registry |
| `--app-nothing-*` | semantic-extension | `frontend/src/App.css` | empty collection notice in App.css | retained by CS-125 positive prefix registry |
| `--app-other-*` | semantic-extension | `frontend/src/App.css` | other-person form roles in App.css | retained by CS-125 positive prefix registry |
| `--app-panel-*` | semantic-extension | `frontend/src/App.css` | panel primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-people-*` | semantic-extension | `frontend/src/App.css` | people page header and error states in App.css | retained by CS-125 positive prefix registry |
| `--app-person-*` | semantic-extension | `frontend/src/App.css` | person cards, picker, profile and options in App.css | retained by CS-125 positive prefix registry |
| `--app-premium-*` | semantic-extension | `frontend/src/App.css` | premium page roles in App.css | retained by CS-125 positive prefix registry |
| `--app-section-*` | semantic-extension | `frontend/src/App.css` | section header primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-shell-*` | semantic-extension | `frontend/src/App.css` | application shell roles in App.css | retained by CS-125 positive prefix registry |
| `--app-skeleton-*` | semantic-extension | `frontend/src/App.css` | skeleton loading primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-state-*` | semantic-extension | `frontend/src/App.css` | application state primitives in App.css | retained by CS-125 positive prefix registry |
| `--app-summary-*` | semantic-extension | `frontend/src/App.css` | summary details and panel roles in App.css | retained by CS-125 positive prefix registry |
| `--app-type-*` | semantic-extension | `frontend/src/App.css` | type pill roles in App.css | retained by CS-125 positive prefix registry |
| `--app-typing-*` | semantic-extension | `frontend/src/App.css` | typing indicator primitive in App.css | retained by CS-125 positive prefix registry |
| `--app-usage-*` | semantic-extension | `frontend/src/App.css` | usage metrics and progress roles in App.css | retained by CS-125 positive prefix registry |
| `--app-user-*` | semantic-extension | `frontend/src/App.css` | user data missing notice in App.css | retained by CS-125 positive prefix registry |
| `--app-validation-*` | semantic-extension | `frontend/src/App.css` | validation summary and fields in App.css | retained by CS-125 positive prefix registry |
| `--usage-*` | dynamic | `frontend/src/pages/settings/Settings.css` | runtime progress value | permanent custom property bridge |
| `--period-accent` | dynamic | prediction timeline components | runtime accent value | permanent custom property bridge |
| `--landing-*` | semantic-extension | `frontend/src/layouts/LandingLayout.css` | landing visual and typography semantic owners consumed by landing sections | permanent landing-scoped semantic layer |
| `--help-*` | semantic-extension | `frontend/src/pages/HelpPage.css` | help page visual roles | permanent page-scoped semantic layer |
| `--chat-*` | semantic-extension | `frontend/src/pages/ChatPage.css` | chat cluster visual and typography roles | permanent chat page-scoped semantic layer |
| `--admin-settings-*` | semantic-extension | `frontend/src/pages/admin/AdminSettingsPage.css` | admin settings cluster local visual roles | permanent page-scoped semantic layer |
| `--admin-entitlements-*` | semantic-extension | `frontend/src/pages/admin/AdminEntitlementsPage.css` | admin entitlements cluster local visual roles | permanent page-scoped semantic layer |
| `--calendar-*` | semantic-extension | `frontend/src/index.css` | calendar cell background states | permanent calendar UI role |
| `--consultation-result-*` | semantic-extension | `frontend/src/pages/ConsultationResultPage.css` | consultation result page visual roles | permanent page-scoped semantic layer |
| `--consultation-precision-*` | semantic-extension | `frontend/src/features/consultations/components/ConsultationPrecisionBadge.css` | consultation precision badge visual roles | permanent feature-scoped semantic layer |
| `--natal-interpretation-*` | semantic-extension | `frontend/src/features/natal-chart/NatalInterpretation.css` | natal interpretation feature roles | permanent feature-scoped semantic layer |
| `--prediction-timeline-*` | semantic-extension | prediction timeline CSS | prediction timeline layout roles | permanent component-scoped semantic layer |
| `--text-strong` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-main` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-meta` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
| `--text-faint` | semantic-extension | `frontend/src/pages/DailyHoroscopePage.css` | daily premium text role | migrate with daily premium token layer |
