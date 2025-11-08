# Horoscope Frontend

Frontend Vite + React + TypeScript qui expose toute l’expérience web de l’application Horoscope. La branche `main` reflète l’état de la **release 0.5.1** : authentification complète, modules billing Stripe (checkout, portal, terminal), horoscopes (natal, today, premium), chat assisté, flows RGPD et observabilité.

## 🧭 Sommaire

1. [Release 0.5.1 – résumé](#release-051--résumé)
2. [Prérequis](#prérequis)
3. [Mise en route](#mise-en-route)
4. [Scripts npm](#scripts-npm)
5. [Structure](#structure)
6. [Fonctionnalités clés](#fonctionnalités-clés)
7. [Variables d’environnement](#variables-denvironnement)
8. [Qualité & tests](#qualité--tests)
9. [Roadmap & licence](#roadmap--licence)

## Release 0.5.1 – résumé

- Authentification : signup/login, reset password, gestion JWT, pages publiques/privées.
- Billing Stripe : checkout & portal, pages success/cancel, Billing Debug Panel, simulateur terminal (dev).
- Horoscopes : saisie natal, cartes today/premium, export PDF, toasts d’erreurs.
- Chat RAG : historique persisté, quotas et messages adaptés au plan.
- RGPD : export ZIP, suppression compte, pages légales sanitizées.
- Observabilité : Debug Drawer (Ctrl+Shift+D), logs request_id, monitoring terminal/billing.

> Voir `RELEASE_0.5.md` et `RELEASE_0.0.md` pour l’historique détaillé.

## Prérequis

- Node.js **18.x** ou supérieur
- npm (ou pnpm/yarn)
- API backend disponible (par défaut `http://localhost:8000`)

## Mise en route

```bash
git clone https://github.com/daconrilcy/horoscope_front.git
cd horoscope_front

npm install
cp .env.example .env       # puis éditer vos valeurs

npm run dev                # http://localhost:5173
```

Build & preview :

```bash
npm run build
npm run preview
```

## Scripts npm

| Commande               | Description                          |
| ---------------------- | ------------------------------------ |
| `npm run dev`          | Serveur Vite de développement        |
| `npm run build`        | Build production                     |
| `npm run preview`      | Prévisualisation du build            |
| `npm run lint`         | ESLint                               |
| `npm run lint:fix`     | ESLint + auto-fix                    |
| `npm run format`       | Formatage Prettier                   |
| `npm run format:check` | Vérification formatage               |
| `npm run test`         | Tests Vitest (unitaires/intégration) |
| `npm run test:watch`   | Vitest en mode watch                 |
| `npm run test:ui`      | Interface UI Vitest                  |
| `npm run test:cov`     | Tests avec couverture                |
| `npm run test:e2e`     | Tests Playwright                     |
| `npm run test:e2e:ui`  | Runner Playwright UI                 |

## Structure

```
src/
├── app/        # providers, router, layouts
├── shared/     # API clients, configs, hooks, UI, utils
├── features/   # unités fonctionnelles (checkout, chat, terminal…)
├── pages/      # routes finales (home, dashboard, billing, legal…)
├── widgets/    # composants composites (QuotaBadge, DebugDrawer…)
├── stores/     # stores Zustand
├── styles/     # styles globaux
└── test/       # configuration tests (MSW, setup Vitest/Playwright)
```

## Fonctionnalités clés

- **Billing & Terminal**
  - Hooks `useCheckout`, `usePortal`, `useClearPriceLookupCache` et simulateur `/dev/terminal`.
  - Billing Debug Panel affichant configuration et flags Stripe (dev-only).
- **Horoscope**
  - Flow natal + horoscopes jour/premium, export PDF, toasts, sanitisation HTML.
- **Chat RAG**
  - Historique persisté, quotas, messages contextualisés.
- **RGPD**
  - Export ZIP, suppression compte, navigation sécurisée (redirects whitelistés).
- **Observabilité**
  - Debug Drawer avec latence, `request_id`, headers de corrélation (`X-Client-Version`, `X-Request-Source`).

## Variables d’environnement

Copiez `.env.example` puis renseignez :

```env
VITE_API_BASE_URL=http://localhost:8000

# Fallback Billing (si /v1/config indisponible côté backend)
VITE_PUBLIC_BASE_URL=http://localhost:5173
VITE_CHECKOUT_SUCCESS_PATH=/billing/success
VITE_CHECKOUT_CANCEL_PATH=/billing/cancel
VITE_PORTAL_RETURN_URL=http://localhost:5173/app/account
VITE_CHECKOUT_TRIALS_ENABLED=false
VITE_CHECKOUT_COUPONS_ENABLED=false
VITE_STRIPE_TAX_ENABLED=false

# Outils développeur
VITE_DEV_TERMINAL=true
```

Notes :

- Si le backend expose `/v1/config`, ses valeurs priment sur `.env`.
- Préférez la configuration serveur en production ; `.env` reste pratique pour le dev local.

## Qualité & tests

- Vitest couvre API clients, hooks, stores, widgets (`npm test`).
- Playwright rejoue les scénarios critiques (auth, billing success/cancel, terminal…).
- Les répertoires générés (`coverage`, `dist`, `playwright-report`, `test-results`) sont exclus du dépôt.
- Après nettoyage, exécuter `npm test` pour dresser l’état des échecs et planifier leur correction.

## Roadmap & licence

- Optimisations responsive/performance.
- Nouveaux scénarios Playwright (chat multi-compte, flows premium complexes).
- Intégration monitoring (Sentry, analytics) & i18n.

Licence : à définir (voir équipe produit avant toute diffusion externe).
