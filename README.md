# Horoscope Frontend

Application frontend React/TypeScript pour horoscope personnalisé avec authentification, système de paywall, chat RAG, et gestion compte RGPD.

## 🚀 Release 0.5

Cette version implémente l'ensemble des fonctionnalités principales du frontend :

- ✅ **Authentification complète** (signup, login, reset password)
- ✅ **Système de paywall** avec décisions en temps réel
- ✅ **Checkout & Portal Billing** (Stripe) avec hooks sécurisés
- ✅ **Horoscopes** (natal, today, premium) avec export PDF
- ✅ **Chat RAG** avec historique persisté
- ✅ **Gestion compte RGPD** (export ZIP, suppression compte)
- ✅ **Pages légales** (TOS, Privacy) avec sanitization HTML
- ✅ **Widgets partagés** (QuotaBadge, PlanBanner, etc.)
- ✅ **Tests complets** (500+ tests unitaires, tests E2E Playwright)
- ✅ **Gestion sécurisée des erreurs** (401, 402, 429, 5xx)
- ✅ **Navigation** (Home, Dashboard) avec Quick Cards

Voir [RELEASE_0.5.md](./RELEASE_0.5.md) pour les détails complets.

## 📋 Prérequis

- Node.js 18+
- npm ou yarn
- Backend API actif (par défaut `http://localhost:8000`)

## 🔧 Installation

```bash
# Installer les dépendances
npm install

# Créer le fichier .env à partir de l'exemple
cp .env.example .env

# Éditer .env avec vos valeurs
# VITE_API_BASE_URL=http://localhost:8000

# Démarrer le serveur de développement
npm run dev
```

## 📦 Scripts disponibles

```bash
npm run dev          # Démarrer le serveur de développement
npm run build        # Build de production
npm run preview      # Prévisualiser le build

npm run lint         # Linter le code
npm run lint:fix     # Auto-fix des erreurs ESLint
npm run format       # Formatter avec Prettier
npm run format:check # Vérifier le formatage

npm run test         # Exécuter les tests unitaires
npm run test:watch   # Tests en mode watch
npm run test:ui      # Interface UI pour les tests
npm run test:cov     # Tests avec couverture
npm run test:e2e     # Tests E2E Playwright
npm run test:e2e:ui  # Tests E2E avec UI
```

## 🏗️ Architecture

Le projet suit l'architecture **Feature-Sliced Design** :

```
src/
├── app/          # Bootstrapping, Providers, Router
├── shared/       # Libs transverses (api, auth, hooks, ui, config, types)
├── entities/     # Modèles/Types par domaine
├── features/     # Unités fonctionnelles réutilisables
├── pages/        # Pages route-level composant les features
├── widgets/      # Blocs UI composés
├── stores/       # Stores Zustand pour state UI éphémère
└── styles/       # Styles globaux
```

## 🛠️ Stack technique

- **Vite 5.x** - Build tool ultra-rapide
- **React 18.x** - Bibliothèque UI
- **TypeScript 5.x** - Typage statique strict
- **React Router 7.x** - Data Router
- **React Query 5.x** - Server state management
- **Zustand 5.x** - UI state management
- **Zod 3.x** - Validation schémas stricte
- **Vitest 1.x** - Framework de tests
- **Playwright 1.x** - Tests E2E
- **MSW 2.x** - Mock Service Worker pour tests

## 🔐 Sécurité

- **Open-redirect bloqué** : Helper safeInternalRedirect avec whitelist
- **Sanitization HTML** : Pages légales protégées contre injection XSS
- **JWT storage** : Clé namespacée, helpers persist/clear sécurisés
- **Idempotency-Key** : UUID v4 générée côté client pour mutations
- **Messages erreurs** : Messages UX génériques, request_id pour debugging

## ♿ Accessibilité

Tous les composants sont accessibles avec :

- Attributs ARIA complets (aria-\*, roles, labels)
- Navigation clavier (focus trap dans modals, Tab navigation)
- Messages d'erreur accessibles (aria-invalid, aria-describedby)
- Loading states annoncés (aria-busy, aria-live)
- Liens externes sécurisés (rel="noopener")

## 📊 Tests

- **500+ tests unitaires** avec couverture ≥70% sur shared/api et features/\*
- **Tests E2E Playwright** : 3 scénarios automatisés
- **MSW** : Handlers organisés par domaine pour tests isolés
- **Environnement déterministe** : TZ Europe/Paris, polyfills configurés

## 📝 Variables d'environnement

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📚 Documentation

- [RELEASE_0.5.md](./RELEASE_0.5.md) - Détails complets de la release 0.5
- [RELEASE_0.0.md](./RELEASE_0.0.md) - Release initiale (bootstrap)

## 🔄 Roadmap

- Amélioration UI/UX avec styles et responsive design
- Optimisations performance (lazy loading images, code splitting fin)
- Tests E2E supplémentaires pour flows critiques
- Intégration monitoring (Sentry, analytics)
- Internationalisation (i18n) si nécessaire

## 📄 Licence

(À définir)
