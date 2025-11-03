<!-- ea443f71-fa9a-408d-bdba-01e445dc7abb d3216984-d09a-4c90-a3ca-99061c6be34c -->
# Milestone FE-10 — Tests

## Objectif

Mettre en place une couverture de tests complète avec tests unitaires (services & hooks avec MSW) et tests E2E (Playwright) pour garantir la robustesse de l'application.

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
   - `src/features/horoscope/hooks/useCreateNatal.test.tsx` (mutation, double-submit, fieldErrors)
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

### To-dos

- [ ] Créer le fichier FE-10-tests-issue.md avec la structure complète de l'issue
- [ ] Installer MSW (msw) et configurer les handlers pour tous les services API
- [ ] Corriger le test ConfirmModal.test.tsx en échec (wrapping act)
- [ ] Créer les tests manquants pour useCreateNatal, useToday, useTodayPremium, useDownloadPdf
- [ ] Configurer Vitest pour générer le rapport de couverture et vérifier ≥70%
- [ ] Installer Playwright et configurer pour http://localhost:8000
- [ ] Implémenter les 4 scénarios E2E Playwright (signup-login, upgrade-chat, natal-export, reset-password)
- [ ] Documenter Mailpit pour le scénario reset password
- [ ] Vérifier que tous les tests passent (unitaires et E2E)
- [ ] Exécuter pre-commit (lint + test) et s'assurer qu'il passe
- [ ] Créer FE-10-tests-pr.md, commiter et pusher la branche avec PR qui clos l'issue