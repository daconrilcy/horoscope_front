# CS-130 - Inventaire largeur avant

## Tokens layout

| Surface | Valeur avant |
|---|---|
| `--layout-page-max-width` | `900px` dans `frontend/src/styles/design-tokens.css` |
| `--layout-page-padding` | `var(--space-6)` |
| `--layout-sidebar-width` | `320px` |
| `--layout-admin-max-width` | `1680px` |

## Owners layout avant convergence

| Fichier | Selecteur | Declaration avant | Classification |
|---|---|---|---|
| `frontend/src/styles/backgrounds.css` | `.app-bg-container` desktop | `max-width: 1100px` | owner concurrent non-admin |
| `frontend/src/styles/backgrounds.css` | `.app-bg-container--admin` | `max-width: min(1880px, calc(100vw - 2 * var(--space-6)))` | admin exclu |
| `frontend/src/layouts/PageLayout.css` | `.page-layout` | `max-width: var(--layout-page-max-width)` | owner canonique mais token trop etroit |
| `frontend/src/styles/app/layout.css` | `.activities-catalogue-section` | `max-width: 1000px` | largeur locale historique |
| `frontend/src/styles/app/layout.css` | `.activities-page` | `max-width: 900px` | largeur locale historique |

## Overrides page-level non-admin avant convergence

| Fichier | Selecteur | Declaration avant | Decision |
|---|---|---|---|
| `frontend/src/pages/ChatPage.css` | `body:has(.is-chat-page)` | `overflow-x: hidden` | supprime, masquait le defaut de largeur |
| `frontend/src/pages/ChatPage.css` | `.app-bg-container:has(.is-chat-page)` | `max-width: none` | supprime, bypass du container canonique |
| `frontend/src/pages/ChatPage.css` | `.is-chat-page` | `max-width: none !important` | supprime, bypass du PageLayout |
| `frontend/src/pages/ChatPage.css` | `.chat-page-container` | `--chat-layout-max-width: 1740px`, `max-width: var(--chat-layout-max-width) !important` | supprime comme largeur page-level |
| `frontend/src/pages/DashboardPage.css` | `.dashboard-container` | `--layout-max-width`, `max-width: var(--layout-max-width)` | supprime, PageLayout devient owner |
| `frontend/src/pages/DashboardPage.css` | `.dashboard-container` desktop | `--layout-max-width: 1020px` | supprime |
| `frontend/src/pages/DailyHoroscopePage.css` | `.daily-layout` | `--layout-max-width`, `max-width: var(--layout-max-width)` | supprime, PageLayout devient owner |
| `frontend/src/pages/NatalChartPage.css` | `.natal-page-container` | `--layout-page-max-width: 1200px` | supprime |
| `frontend/src/pages/settings/Settings.css` | `.is-settings-page` | `max-width: none !important` | supprime |
| `frontend/src/pages/settings/Settings.css` | `.settings-container` | `max-width: var(--settings-page-max-width)` | supprime comme cap de corps central |
| `frontend/src/pages/HelpPage.css` | `.page-layout.is-settings-page` | `max-width: none` | supprime |
| `frontend/src/pages/HelpPage.css` | `.help-page` | `max-width: 1280px` | supprime comme cap de corps central |
| `frontend/src/pages/AstrologerProfilePage.css` | `.astrologer-profile-container` | `--layout-max-width: 1140px`, `max-width: var(--layout-max-width)` | supprime |
| `frontend/src/pages/ConsultationResultPage.css` | `.is-consultation-result-page` | `max-width: none !important` | supprime |

## Exceptions admin exclues

- `frontend/src/layouts/AdminLayout.css` garde `.admin-container` avec `max-width: var(--layout-admin-max-width)`.
- `frontend/src/styles/backgrounds.css` garde `.app-bg-container--admin`.
- `frontend/src/pages/admin/**` reste hors migration CS-130.

## Largeurs internes conservees

Largeurs de lecture, cartes, CTA, avatars, colonnes et media queries restent hors cible quand elles ne redefinissent pas le corps central: exemples `max-width: 76ch`, `max-width: 820px` sur `.result-container`, CTA `380px`, textes `12ch/34ch/62ch`, avatars et composants internes.
