# CS-130 - Inventaire largeur apres

## Contrat canonique non-admin

| Surface | Valeur apres | Evidence |
|---|---|---|
| Token canonique | `--layout-page-max-width: min(1440px, calc(100vw - 2 * var(--space-6)))` | `frontend/src/styles/design-tokens.css` |
| Container racine non-admin | `max-width: var(--layout-page-max-width)` | `frontend/src/styles/backgrounds.css` |
| Wrapper page generique | `max-width: var(--layout-page-max-width)` | `frontend/src/layouts/PageLayout.css` |
| Shell applicatif | `min-width: 0` sur `.app-shell-main` | `frontend/src/styles/app/layout.css` |

## Surfaces convergees

| Surface | Resultat |
|---|---|
| `ChatPage.css` | suppression du bypass `.app-bg-container:has(.is-chat-page)`, de `max-width: none !important`, de `--chat-layout-max-width` et des `overflow-x: hidden` de compensation |
| `DashboardPage.css` | fichier supprime: ses selecteurs `.dashboard-*` n'etaient plus consommes par `DashboardPage.tsx`; le runtime utilise `PageLayout.summary-container` |
| `DailyHoroscopePage.css` | suppression du `max-width` local du layout quotidien |
| `NatalChartPage.css` | suppression de l'override `--layout-page-max-width: 1200px` |
| `Settings.css` | suppression du cap page-level `--settings-page-max-width` et du `max-width: none !important` du wrapper |
| `HelpPage.css` | suppression des bypass `max-width: none` sur `PageLayout` et du cap `.help-page` |
| `AstrologerProfilePage.css` | suppression de `--layout-max-width` et du `max-width` du container page |
| `ConsultationResultPage.css` | suppression du `max-width: none !important` du wrapper |
| `styles/app/layout.css` | les anciennes largeurs activities utilisent le token canonique ou heritent du layout |
| `styles/app/cards.css` | suppression du cap actif `.page-layout.people-page { max-width: 600px; }` sur `/astrologers` |
| `pages/billing/billing-return.css` | deplacement du cap `600px` du wrapper page vers la carte interne `.billing-return-card` |

## Exceptions conservees et classees

| Fichier | Selecteur | Raison |
|---|---|---|
| `frontend/src/layouts/AdminLayout.css` | `.admin-container` | owner canonique admin, hors scope |
| `frontend/src/styles/backgrounds.css` | `.app-bg-container--admin` | cap admin separe conserve |
| `frontend/src/layouts/LandingLayout.css` | `--landing-page-max-width` | layout public landing, hors migration non-admin applicative |
| `frontend/src/pages/landing/sections/TestimonialsSection.css` | `.testimonials-section` | section landing publique, hors scope CS-130 |
| `frontend/src/pages/ConsultationResultPage.css` | `.result-container`, `.result-chat-btn` | largeur interne de lecture/action, pas wrapper page |
| `frontend/src/pages/AstrologerProfilePage.css` | textes, CTA, avatar, colonnes internes | largeurs internes de composition |
| `frontend/src/pages/HelpPage.css` | textes, cards, media queries | largeurs internes et breakpoints |
| `frontend/src/pages/settings/Settings.css` | textes, boutons, avatar, progress | largeurs internes de composants |
| `frontend/src/pages/billing/billing-return.css` | `.billing-return-card` | largeur interne de carte de retour paiement, pas wrapper page |

## Guards et scans

- `frontend/src/tests/design-system-guards.test.ts` ajoute `garde la largeur centrale non-admin sous ownership layout CS-130`.
- Le guard scanne les modules CSS actifs de `App.css`, `PageLayout.css`, `backgrounds.css`, `design-tokens.css` et les CSS de pages non-admin.
- Le guard refuse les `--layout-max-width`, overrides `--layout-page-max-width` hors token, `.app-bg-container:has`, `max-width: none !important`, `overflow-x: hidden`, caps `900px/1100px/1200px` et `max-width` sur `.page-layout*` hors owner canonique.
- Scan brut restant attendu: media queries `max-width` et surfaces landing hors scope, plus admin via scan dedie.
