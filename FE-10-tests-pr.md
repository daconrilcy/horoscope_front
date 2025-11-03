## Description

Ce PR implémente le Milestone FE-10 — Tests, établissant une couverture de tests complète avec tests unitaires (services & hooks avec MSW) et tests E2E (Playwright) pour garantir la robustesse de l'application.

## Type de changement

- [ ] 🎉 Nouvelle fonctionnalité
- [ ] 🐛 Correction de bug
- [ ] 📚 Documentation
- [ ] 🎨 Style / Format
- [ ] ♻️ Refactoring
- [ ] ⚡ Performance
- [x] ✅ Tests
- [ ] 🔧 Build / CI

## Issues liées

Closes FE-10

## Changements

### 10.1 — Tests unitaires services & hooks

- ✅ Configuration environnement déterministe (TZ Europe/Paris, polyfills)
- ✅ MSW configuré avec handlers par domaine (auth, billing, paywall, horoscope, chat, account, legal)
- ✅ Utilitaires de test React Query (`renderWithQuery`, `renderWithRouter`)
- ✅ Tests complets pour tous les services (happy path + erreurs + blob)
- ✅ Tests manquants pour hooks horoscope :
  - `useCreateNatal.test.tsx` (mutation, double-submit, fieldErrors, invalidation)
  - `useToday.test.tsx` (query enabled conditionnel, retry, staleTime)
  - `useTodayPremium.test.tsx` (query enabled conditionnel, retry)
  - `useDownloadPdf.test.tsx` (mutation blob, downloadBlob, erreurs)
- ✅ Correction test `ConfirmModal.test.tsx` (wrapping act)
- ✅ Configuration Vitest pour couverture ≥70% sur shared/api et features/*

### 10.2 — E2E Playwright (local)

- ✅ Configuration Playwright (baseURL http://localhost:5173, trace/screenshot/video on failure)
- ✅ Intercepteurs Stripe Checkout (route locale `/__fake_stripe_success`)
- ✅ 3 scénarios E2E automatisés :
  - `01_auth.spec.ts` : signup → login → dashboard (storageState)
  - `02_billing_upgrade.spec.ts` : upgrade Plus → chat débloqué
  - `03_horoscope_pdf.spec.ts` : créer natal → today → export PDF
- ✅ Documentation Mailpit pour reset password (`04_reset_password.doc.md`)
- ✅ Scripts NPM : `test:e2e`, `test:e2e:ui`, `test:e2e:codegen`

## Checklist

- [x] Code formaté avec Prettier
- [x] Code linté sans erreurs (ESLint)
- [x] Tests unitaires passent (`npm run test`)
- [x] Tests E2E configurés (Playwright)
- [x] Couverture ≥70% sur shared/api et features/*
- [x] Handlers MSW organisés par domaine
- [x] Environnement déterministe (TZ, polyfills)
- [x] Documentation Mailpit pour reset password

## Tests

```bash
# Tests unitaires
npm run test

# Tests avec couverture
npm run test:cov

# Tests E2E (nécessite dev server + backend actifs)
npm run test:e2e

# Tests E2E avec UI
npm run test:e2e:ui
```

## Couverture

- MSW opérationnel avec handlers organisés par domaine
- Environnement déterministe (TZ Europe/Paris, polyfills)
- Tous les services ont des tests complets (happy path + erreurs + blob)
- Tous les hooks ont des tests complets (mutations, queries, enabled conditionnel)
- Couverture ≥70% sur shared/api et features/*
- 3 scénarios E2E automatisés verts

## Notes additionnelles

- Les tests E2E nécessitent le serveur dev (`npm run dev`) et le backend (`http://localhost:8000`) actifs
- Le scénario reset password est documenté mais non automatisé (nécessite Mailpit manuel)
- Les handlers MSW simulent tous les endpoints API pour tests unitaires isolés
- L'environnement de test est déterministe (TZ fixée, polyfills configurés)

