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

### Variables obligatoires

```env
# URL de base de l'API backend (obligatoire)
VITE_API_BASE_URL=http://localhost:8000
```

### Variables optionnelles (Billing Config)

Ces variables sont utilisées comme **fallback** si l'endpoint `/v1/config` n'est pas disponible. En production, il est recommandé de configurer le backend pour exposer `/v1/config` plutôt que d'utiliser ces variables.

```env
# URL publique de base (pour générer les URLs de retour Stripe)
VITE_PUBLIC_BASE_URL=http://localhost:5173

# Chemins de redirection après checkout Stripe
VITE_CHECKOUT_SUCCESS_PATH=/billing/success
VITE_CHECKOUT_CANCEL_PATH=/billing/cancel

# URL de retour après session Portal Stripe
VITE_PORTAL_RETURN_URL=http://localhost:5173/app/account

# Feature flags billing (true/false)
VITE_CHECKOUT_TRIALS_ENABLED=false
VITE_CHECKOUT_COUPONS_ENABLED=false
VITE_STRIPE_TAX_ENABLED=false
```

### Variables optionnelles (Dev Tools)

```env
# Activer le simulateur Stripe Terminal (dev uniquement)
VITE_DEV_TERMINAL=true
```

### Notes importantes

- **Priorité** : Si `/v1/config` est disponible, ses valeurs prennent priorité sur les variables d'environnement.
- **Production** : Il est recommandé de configurer le backend pour exposer `/v1/config` avec toutes les valeurs nécessaires.
- **Développement** : Les variables d'environnement sont pratiques pour le développement local sans backend.

## 🚀 Quickstart Billing & Terminal

### Configuration Billing

Le système de billing utilise Stripe pour les sessions checkout et portal. La configuration est récupérée depuis l'endpoint `/v1/config` avec fallback sur les variables d'environnement.

#### Étapes de configuration

1. **Configurer le backend** (recommandé pour la production) :
   - Exposer l'endpoint `GET /v1/config` avec la configuration billing
   - Inclure les URLs et feature flags nécessaires

2. **Ou utiliser les variables d'environnement** (pour le développement) :

   ```env
   VITE_PUBLIC_BASE_URL=http://localhost:5173
   VITE_CHECKOUT_SUCCESS_PATH=/billing/success
   VITE_CHECKOUT_CANCEL_PATH=/billing/cancel
   VITE_PORTAL_RETURN_URL=http://localhost:5173/app/account
   VITE_CHECKOUT_TRIALS_ENABLED=false
   VITE_CHECKOUT_COUPONS_ENABLED=false
   VITE_STRIPE_TAX_ENABLED=false
   ```

3. **Tester le checkout** :
   - Utiliser le hook `useCheckout()` pour créer une session checkout
   - L'utilisateur sera redirigé vers Stripe Checkout
   - Après paiement, redirection vers `/billing/success`

4. **Tester le portal** :
   - Utiliser le hook `usePortal()` pour créer une session portal
   - L'utilisateur sera redirigé vers Stripe Customer Portal
   - Après gestion, redirection vers l'URL configurée

### Stripe Terminal Simulator (Dev)

Le simulateur Stripe Terminal est disponible uniquement en mode développement pour tester les flows Terminal.

> 📚 **Guide de test complet** : Consultez [docs/STRIPE_TERMINAL_TESTING.md](docs/STRIPE_TERMINAL_TESTING.md) pour la documentation complète des cartes de test Stripe, des montants de test avec décimales spécifiques, et des scénarios de test recommandés.

#### Accès au simulateur

1. **Activer le mode dev** :

   ```env
   VITE_DEV_TERMINAL=true
   ```

2. **Accéder à la console** :
   - Naviguer vers `/dev/terminal`
   - Ou utiliser le raccourci dans le menu dev (si disponible)

3. **Flow de test** :
   - **Connect** : Se connecter au terminal
   - **Create Payment Intent** : Créer un PI avec montant et devise
   - **Process** : Traiter le paiement
   - **Capture** : Capturer le paiement
   - **Cancel** : Annuler un paiement (si nécessaire)
   - **Refund** : Rembourser un paiement (après capture)

#### Debug Tools (Dev)

Plusieurs outils de debug sont disponibles en mode développement :

- **Billing Debug Panel** : Affiche la configuration billing actuelle, les flags, et les warnings (visible en bas-droite)
- **Debug Drawer** : Affiche les breadcrumbs de toutes les requêtes API avec `request_id` et latence (accessible via `Ctrl+Shift+D`)
- **Admin Tools** : Bouton pour clear le cache `price_lookup` dans le Billing Debug Panel

### Headers de corrélation

Toutes les requêtes HTTP incluent automatiquement :

- `X-Client-Version` : Version du client (hash de dev ou version définie)
- `X-Request-Source` : Source de la requête (`frontend`)

Ces headers permettent au backend de corréler les logs et de tracer les requêtes.

## 📚 Documentation

- [RELEASE_0.5.md](./RELEASE_0.5.md) - Détails complets de la release 0.5
- [RELEASE_0.0.md](./RELEASE_0.0.md) - Release initiale (bootstrap)

## 🔧 Troubleshooting

### Problèmes de configuration Billing

**Problème** : Les URLs de redirection Stripe ne fonctionnent pas

- **Solution** : Vérifier que `VITE_PUBLIC_BASE_URL` correspond à l'URL réelle de l'application
- **Solution** : Vérifier que les chemins `/billing/success` et `/billing/cancel` sont bien configurés dans le backend Stripe
- **Solution** : Vérifier que l'endpoint `/v1/config` retourne les bonnes valeurs

**Problème** : Le Billing Debug Panel n'apparaît pas

- **Solution** : Vérifier que vous êtes en mode développement (`npm run dev`)
- **Solution** : Vérifier que le panel n'est pas masqué par d'autres éléments (z-index)

**Problème** : Les événements billing/terminal ne s'affichent pas dans le Debug Drawer

- **Solution** : Vérifier que le Debug Drawer est ouvert (`Ctrl+Shift+D`)
- **Solution** : Vérifier que les requêtes sont bien effectuées (vérifier la console)
- **Solution** : Vérifier que `import.meta.env.DEV` est `true`

### Problèmes de Terminal Simulator

**Problème** : La page `/dev/terminal` redirige vers le dashboard

- **Solution** : Vérifier que `VITE_DEV_TERMINAL=true` dans `.env`
- **Solution** : Vérifier que vous êtes en mode développement

**Problème** : Les appels Terminal échouent

- **Solution** : Vérifier que le backend expose les endpoints `/v1/terminal/*`
- **Solution** : Vérifier que vous êtes authentifié (JWT valide)
- **Solution** : Vérifier les logs du backend pour plus de détails

### Problèmes généraux

**Problème** : Erreur "Configuration d'environnement invalide"

- **Solution** : Vérifier que `VITE_API_BASE_URL` est définie dans `.env`
- **Solution** : Vérifier que l'URL est valide (commence par `http://` ou `https://`)
- **Solution** : Redémarrer le serveur de développement après modification de `.env`

**Problème** : Les requêtes API échouent avec 401

- **Solution** : Vérifier que vous êtes connecté (JWT valide)
- **Solution** : Vérifier que le token n'a pas expiré
- **Solution** : Se reconnecter si nécessaire

**Problème** : Les requêtes API échouent avec 402/429

- **Solution** : Vérifier votre plan d'abonnement
- **Solution** : Vérifier vos quotas (pour 429)
- **Solution** : Utiliser le bouton "Upgrade" si nécessaire

## 🔄 Roadmap

- Amélioration UI/UX avec styles et responsive design
- Optimisations performance (lazy loading images, code splitting fin)
- Tests E2E supplémentaires pour flows critiques
- Intégration monitoring (Sentry, analytics)
- Internationalisation (i18n) si nécessaire

## 📄 Licence

(À définir)
