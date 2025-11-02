# Milestone FE-0 — Bootstrap & Qualité

## Objectif

Créer le squelette frontend avec toutes les fondations nécessaires : structure de dossiers, configuration des outils de qualité, et gestion des variables d'environnement.

## Sous-issues

### 0.1 — Init Vite/React/TS + structure dossiers ✅

**Objectif :** créer le squelette frontend/ avec arborescence proposée.

**Tâches :**
- ✅ npm create vite@latest (React + TS), config TS strict, alias @/*.
- ✅ Créer dossiers src/app, shared/*, entities, features/*, pages/*, widgets, stores, styles.
- ✅ App démarre (npm run dev), page / rendue.
- ✅ Aliases et import paths OK.

**Labels:** `setup`

---

### 0.2 — Tooling DX (ESLint, Prettier, Vitest, Testing Library) ✅

**Objectif :** qualité dev homogène.

**Tâches :**
- ✅ ESLint TS strict, Prettier, hooks pre-commit (lint + test).
- ✅ Vitest + @testing-library/react configurés.
- ✅ npm run lint et npm run test passent.
- ✅ Exemple de test vert (Smoke component).

**Labels:** `setup`, `quality`

---

### 0.3 — Env & config ✅

**Objectif :** variables d'env.

**Tâches :**
- ✅ .env.example avec VITE_API_BASE_URL.
- ✅ shared/config/env.ts (validation Zod).
- ✅ Base URL lue depuis env, fallback interdit (erreur claire).

**Labels:** `setup`, `config`

---

## Critères d'acceptation

- [x] App démarre avec `npm run dev`
- [x] Page `/` rendue correctement
- [x] Aliases `@/*` fonctionnels
- [x] `npm run lint` passe sans erreur
- [x] `npm run test` passe
- [x] Variables d'environnement validées au démarrage
- [x] Structure de dossiers conforme à l'architecture FSD

## Livrables

- Structure complète du projet
- Configuration ESLint + Prettier
- Configuration Vitest + Testing Library
- Hooks Git (Husky + lint-staged)
- Validation Zod des variables d'environnement
- Client API de base

## PR liée

#1

