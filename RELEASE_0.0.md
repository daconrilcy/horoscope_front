# Release 0.0 — Bootstrap & Qualité

## Résumé

Cette release initiale établit le squelette du projet frontend avec toutes les fondations nécessaires pour le développement : structure de dossiers, configuration des outils de qualité, et gestion des variables d'environnement.

## Fonctionnalités

### Structure du projet

Arborescence complète selon l'architecture Feature-Sliced Design :
- `src/app/` - Bootstrapping, Providers, Router
- `src/shared/` - Libs transverses (api, auth, hooks, ui, config, types)
- `src/entities/` - Modèles/Types par domaine
- `src/features/` - Unités fonctionnelles réutilisables (auth, billing, horoscope, chat, account, legal)
- `src/pages/` - Pages route-level composant les features
- `src/widgets/` - Blocs UI composés
- `src/stores/` - Stores Zustand pour state UI éphémère
- `src/styles/` - Styles globaux

### Configuration technique

**Stack principale :**
- Vite 5.x - Build tool ultra-rapide
- React 18.x - Bibliothèque UI
- TypeScript 5.x - Typage statique strict

**Outils de qualité :**
- ESLint 8.x - Linting strict avec règles TypeScript
- Prettier 3.x - Formatage de code automatique
- Vitest 1.x - Framework de tests unitaires/intégration
- @testing-library/react - Tests de composants React

**Git hooks :**
- Husky - Hooks Git
- lint-staged - Lint/format sur fichiers modifiés avant commit
- Pre-commit hook exécute lint + tests

### Variables d'environnement

- Validation Zod stricte des variables d'environnement
- `VITE_API_BASE_URL` obligatoire avec message d'erreur clair si absent
- Fichier `.env.example` comme template

### Scripts npm disponibles

```bash
npm run dev          # Démarrer le serveur de développement
npm run build        # Build de production
npm run lint         # Linter le code
npm run lint:fix     # Auto-fix des erreurs ESLint
npm run format       # Formatter avec Prettier
npm run format:check # Vérifier le formatage
npm run test         # Exécuter les tests
npm run test:watch   # Tests en mode watch
npm run test:ui      # Interface UI pour les tests
npm run preview      # Prévisualiser le build
```

## Issues complétées

### 0.1 — Init Vite/React/TS + structure dossiers ✅
- Projet Vite initialisé avec React + TypeScript
- Configuration TypeScript strict activée
- Alias `@/*` configuré dans Vite et TypeScript
- Arborescence complète créée
- App de base fonctionnelle avec route `/`

### 0.2 — Tooling DX ✅
- ESLint configuré avec règles TypeScript strictes
- Prettier configuré et intégré avec ESLint
- Vitest + Testing Library configurés
- Hooks pre-commit configurés (lint + tests)
- Test smoke créé et passant (`src/app/App.test.tsx`)

### 0.3 — Env & config ✅
- `.env.example` créé avec `VITE_API_BASE_URL`
- `src/shared/config/env.ts` avec validation Zod
- Client API placeholder créé (`src/shared/api/client.ts`)
- Erreur claire si variable d'environnement manquante

## Prochaines étapes

- Implémentation des features (auth, billing, horoscope, chat, account, legal)
- Configuration de React Router
- Mise en place de React Query pour server-state
- Configuration de Zustand pour UI state
- Styles et thème

## Installation

```bash
# Installer les dépendances
npm install

# Créer le fichier .env à partir de l'exemple
cp env.example .env

# Éditer .env avec vos valeurs
# VITE_API_BASE_URL=http://localhost:8000

# Démarrer le serveur de développement
npm run dev
```

