## Description

Ce PR implémente le Milestone FE-0 — Bootstrap & Qualité, établissant toutes les fondations nécessaires pour le projet frontend.

## Type de changement

- [x] 🎉 Nouvelle fonctionnalité (milestone initial)
- [ ] 🐛 Correction de bug
- [ ] 📚 Documentation
- [ ] 🎨 Style / Format
- [ ] ♻️ Refactoring
- [ ] ⚡ Performance
- [ ] ✅ Tests
- [ ] 🔧 Build / CI

## Issues liées

Closes #1

## Changements

### 0.1 — Init Vite/React/TS + structure dossiers
- ✅ Initialisation du projet Vite avec React + TypeScript
- ✅ Configuration TypeScript strict
- ✅ Configuration des alias `@/*`
- ✅ Création de l'arborescence complète (FSD)
- ✅ App de base fonctionnelle

### 0.2 — Tooling DX
- ✅ Configuration ESLint avec règles TypeScript strictes
- ✅ Configuration Prettier avec intégration ESLint
- ✅ Configuration Vitest + Testing Library
- ✅ Setup de tests avec jsdom
- ✅ Test smoke (`App.test.tsx`)
- ✅ Configuration Husky + lint-staged
- ✅ Hook pre-commit (lint + tests)

### 0.3 — Env & config
- ✅ `.env.example` avec `VITE_API_BASE_URL`
- ✅ Validation Zod des variables d'environnement
- ✅ Client API de base (`shared/api/client.ts`)

## Checklist

- [x] Code formaté avec Prettier
- [x] Code linté sans erreurs (ESLint)
- [x] Tests passent (`npm run test`)
- [x] Structure de dossiers conforme
- [x] Variables d'environnement documentées
- [x] README mis à jour si nécessaire

## Tests

```bash
# Tests passent
npm run test

# Lint passe
npm run lint

# Format vérifié
npm run format:check
```

## Captures d'écran

N/A - Milestone de bootstrap

## Notes additionnelles

- Le projet démarre avec `npm run dev`
- Les variables d'environnement doivent être définies dans `.env` (copier depuis `.env.example`)
- Les hooks Git sont automatiquement installés via `npm install` (script `prepare`)

