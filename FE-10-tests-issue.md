# Issue: FE-10 — Tests

## Objectif

Mettre en place une couverture de tests complète avec tests unitaires (services & hooks avec MSW) et tests E2E (Playwright) pour garantir la robustesse de l'application. Environnement déterministe, mocks robustes, et couverture ≥70% sur shared/api & features/*.

## Sous-issues

### 10.1 — Tests unitaires services & hooks

**Objectif** : robustesse I/O avec couverture ≥70% sur shared/api & features/*, environnement déterministe.

**Tâches** :

1. **Configuration environnement déterministe** :
   - Configurer `vite.config.ts` avec coverage v8 (provider: 'v8', reportsDirectory: './coverage', reporter: ['text','html','lcov'])
   - Créer `src/test/setup/vitest.setup.ts` avec TZ='Europe/Paris', MSW server, polyfills
   - Configurer MSW server avec handlers par domaine (auth, billing, paywall, horoscope, chat, account, legal)

2. **Handlers MSW organisés** :
   - Créer `src/test/setup/msw.server.ts` (server MSW centralisé)
   - Créer handlers par domaine dans `src/test/setup/handlers/` : auth.ts, billing.ts, paywall.ts, horoscope.ts, chat.ts, account.ts, legal.ts

3. **Utilitaires de test React Query** :
   - Créer `src/test/utils/render.tsx` avec `renderWithQuery()` (QueryClient retry: false)
   - Créer `src/test/utils/routerRender.tsx` pour tests avec Router (redirections 401)

4. **Tests services complets** :
   - Tests happy path + 401/402/429/404/422/500 + NetworkError + JSON vs blob pour tous les services
   - Vérifier content-type (PDF/ZIP vs JSON erreur), idempotency injecté uniquement quand demandé

5. **Tests hooks manquants** :
   - `src/features/horoscope/hooks/useCreateNatal.test.tsx` (mutation, double-submit, fieldErrors, invalidation)
   - `src/features/horoscope/hooks/useToday.test.tsx` (query enabled conditionnel, retry, staleTime)
   - `src/features/horoscope/hooks/useTodayPremium.test.tsx` (query enabled conditionnel, retry)
   - `src/features/horoscope/hooks/useDownloadPdf.test.tsx` (mutation blob, downloadBlob, erreurs)

6. **Correction tests existants** :
   - Corriger `src/shared/ui/ConfirmModal.test.tsx` (wrapping act)
   - Améliorer `src/shared/ui/InlineError.test.tsx` (ApiError.requestId)
   - Améliorer `src/shared/ui/CopyButton.test.tsx` (Clipboard OK/KO)
   - Améliorer `src/shared/ui/Loader.test.tsx` (aria-busy)
   - Améliorer `src/shared/ui/ErrorBoundary.test.tsx` (resetKeys)

7. **Couverture ≥70% ciblée** :
   - Configurer seuil par répertoire (API + features) dans vite.config.ts
   - Script `test:cov` dans package.json avec `--coverage`
   - Vérifier ≥70% sur `shared/api` et `features/*` (pas global trompeur)

**AC** :
- MSW opérationnel avec handlers organisés par domaine
- Environnement déterministe (TZ Europe/Paris, polyfills)
- Tous les services ont des tests complets (happy path + erreurs + blob)
- Tous les hooks ont des tests complets (mutations, queries, enabled conditionnel)
- Couverture ≥70% sur shared/api et features/*
- Tous les tests passent

### 10.2 — E2E Playwright (local)

**Objectif** : 4 parcours critiques testés localement contre frontend Vite (http://localhost:5173).

**Tâches** :

1. **Configuration Playwright** :
   - Installer @playwright/test
   - Créer `playwright.config.ts` : baseURL `http://localhost:5173` (frontend Vite), trace/screenshot/video on failure, chromium Desktop Chrome

2. **Intercepteurs Stripe Checkout** :
   - Intercepter `/v1/billing/checkout` pour répondre `checkout_url: '/__fake_stripe_success'`
   - Créer route locale `/__fake_stripe_success` qui simule retour Stripe et redirige vers `/app/dashboard`

3. **Scénarios E2E** :
   - `e2e/01_auth.spec.ts` : signup → login → dashboard (assert Dashboard, PlanBanner, storageState)
   - `e2e/02_billing_upgrade.spec.ts` : upgrade Plus → chat débloqué (intercept checkout, assert usePlan=plus, Chat accessible)
   - `e2e/03_horoscope_pdf.spec.ts` : créer natal → today → export PDF (intercept PDF, page.waitForEvent('download'))
   - `e2e/04_reset_password.doc.md` : documentation Mailpit (manuel, pas automatisé)

4. **Storage & auth** :
   - Utiliser `storageState` pour accélérer scénarios enchaînés
   - Premier test fait signup/login puis sauvegarde `storageState.json`

5. **Scripts NPM** :
   - `test:e2e` : playwright test
   - `test:e2e:ui` : playwright test --ui
   - `test:e2e:codegen` : playwright codegen

**AC** :
- 3 scénarios automatisés verts (signup/login, upgrade Plus, natal→today→PDF)
- Reset password documenté (pas automatisé)
- Intercepteurs Stripe locaux fonctionnels
- Tests rapides (<~2–3 min local)

## Critères d'acceptation

- [ ] MSW opérationnel avec handlers organisés par domaine
- [ ] Environnement déterministe (TZ Europe/Paris, polyfills)
- [ ] Tous les services ont des tests complets (happy path + erreurs + blob)
- [ ] Tous les hooks ont des tests complets (mutations, queries, enabled conditionnel)
- [ ] Couverture ≥70% sur shared/api et features/*
- [ ] Tous les tests unitaires passent
- [ ] 3 scénarios E2E automatisés verts
- [ ] Reset password documenté
- [ ] Pre-commit passe (lint + test)
- [ ] Code fonctionnel, sans bugs, conforme au cahier des charges

## Livrables

- Configuration MSW complète avec handlers par domaine
- Tests unitaires pour tous les services et hooks manquants
- Configuration Playwright avec 3 scénarios E2E
- Documentation Mailpit pour reset password
- Rapports de couverture ≥70%
- Issue et PR complètes

## Labels

`tests`, `quality`, `milestone-fe-10`

