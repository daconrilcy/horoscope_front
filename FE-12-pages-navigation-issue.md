# Issue: FE-12 — Pages & Navigation

## Objectif

Implémenter les pages Home et Dashboard avec redirection automatique (Home), cartes Auth, Plan (PlanBanner), quotas (QuotaBadge), et Quick Cards avec logique d'état (Horoscope/Chat/Account) pour un parcours fluide vers les features clés.

## Principes (rappel)

- Aucune logique d'auth dans les pages : tout passe par RouteGuard + useAuthStore
- Routes centralisées (ROUTES.\*), pas de strings en dur
- Chargements propres : Loader (aria-busy), pas de "flash" d'erreur
- Surfaces plan/quotas : PlanBanner + QuotaBadge (déjà vus en FE-9), refetch au mount du Dashboard

## Sous-issues

### 12.1 — Pages / (home) & /app/dashboard

**Objectif** : Accueillir et résumer l'état avec parcours fluide vers features clés.

**Tâches** :

1. **Home (/) — Accueil minimal** :
   - Si `isAuthenticated` → `navigate(ROUTES.APP.DASHBOARD, { replace: true })` (sans flicker, après hydratation)
   - Contenu :
     - h1 court : "Horoscope & Conseils Personnalisés"
     - 2 CTA : "S'inscrire" → `/signup`, "Se connecter" → `/login`
     - Liens discrets vers `/legal/tos` & `/legal/privacy`
   - SEO basique : `useTitle('Accueil')`
   - Accessibilité : `<main>` avec section principale, ordre tab logique

2. **Dashboard (/app/dashboard) — Résumé état + raccourcis** :
   - **Carte Auth** :
     - Afficher `userRef.email` depuis `useAuthStore`
     - CTA "Se déconnecter" utilisant `authStore.logout()`
   - **Plan** :
     - PlanBanner (avec PortalButton + UpgradeButton si free)
     - Hook : `usePlan()` — refetch au mount via `queryClient.invalidateQueries({ queryKey: ['paywall'] })`
   - **Quotas** :
     - QuotaBadge (ex: `FEATURES.CHAT_MSG_PER_DAY`, `FEATURES.HORO_TODAY_PREMIUM`)
     - Si 429 avec retry_after → countdown (déjà prévu FE-9)
   - **Raccourcis — 3 Quick Cards** :
     - **Horoscope** :
       - Si `horoscopeStore.recentCharts.length > 0` → montrer dernier `chartId` + CTA "Voir Today"
       - Sinon → CTA "Créer mon thème natal"
     - **Chat** :
       - Afficher badge "Plus requis" si `usePaywall('chat.messages/day').isAllowed !== true`
       - CTA vers Chat
     - **Account** : Export & Portal (CTA directs)
   - **(Option bonus) Historique récent** : Liste des 1-2 derniers charts avec action "Today"
   - **Comportements UX** :
     - Prefetch paresseux : au survol d'une carte, déclencher `import()` de la page cible (code-splitting)
     - Prefetch idle : au mount Dashboard, `router.prefetch(ROUTES.APP.HOROSCOPE)` & `router.prefetch(ROUTES.APP.CHAT)` en idle
     - Pas de flash : entourer sections Plan/Quota avec Loader compact si hooks en `isLoading`
     - Navigation clavier : chaque carte est un `<button>` / `<a>` accessible (role, aria-label)

3. **Navigation & Layouts** :
   - Home = public (PublicLayout), Dashboard = privé (PrivateLayout)
   - Redirections :
     - `/` (auth) → `/app/dashboard`
     - `/app/*` (non-auth) → `/login` (déjà via RouteGuard FE-1)

4. **Intégrations techniques** :
   - Refetch plan/quotas au mount Dashboard : `queryClient.invalidateQueries({ queryKey: ['paywall'] })`
   - Stores : `useAuthStore` pour `userRef`/email, `horoscopeStore` pour `recentCharts`
   - Titres : Home `useTitle('Accueil')`, Dashboard `useTitle('Tableau de bord')`
   - Erreurs : Cartes utilisent `InlineError` local (pas de toast global)
   - i18n prêt (même si non branché) : isole les labels/CTA dans `src/shared/i18n/strings.ts`

5. **Tests (Vitest + Testing Library)** :
   - `src/pages/home/index.test.tsx` :
     - Non-auth → voit CTA; Auth → redir vers dashboard (sans flicker)
     - Liens fonctionnels
   - `src/pages/app/dashboard/index.test.tsx` :
     - Rendu `userRef.email`
     - Mocks `usePlan` & `usePaywall` → vérifie rendu PlanBanner/QuotaBadge
     - Mocks `horoscopeStore` :
       - Cas 0 chart → "Créer mon thème natal"
       - Cas ≥1 chart → "Voir Today" avec dernier chartId
     - Quick Cards cliquables → `navigate()` appelé avec bonnes routes
     - Loaders visibles quand hooks en `isLoading`
     - Prefetch au survol fonctionne

**AC** :

- [ ] Home : CTA signup/login, redir silencieuse vers dashboard si auth (sans flicker)
- [ ] Dashboard : carte Auth (email), PlanBanner, QuotaBadge, Quick Cards (Horoscope/Chat/Account)
- [ ] Prefetch des pages clés (survol + idle), loaders compacts, no-flash
- [ ] Raccourcis tiennent compte de l'état (ex. "Plus requis" sur Chat si gated, "Voir Today" si chart existe)
- [ ] Tests Home & Dashboard verts (navigation, états charts, mocks plan/quota)
- [ ] Lint/type OK, PR qui close l'issue FE-12

## Critères d'acceptation

- [ ] Home : CTA signup/login, redir silencieuse vers dashboard si auth (sans flicker)
- [ ] Dashboard : carte Auth (email), PlanBanner, QuotaBadge, Quick Cards (Horoscope/Chat/Account)
- [ ] Prefetch des pages clés (survol + idle), loaders compacts, no-flash
- [ ] Raccourcis tiennent compte de l'état (ex. "Plus requis" sur Chat si gated, "Voir Today" si chart existe)
- [ ] Tests Home & Dashboard verts (navigation, états charts, mocks plan/quota)
- [ ] Lint/type OK
- [ ] Pre-commit passe (lint + test)
- [ ] Code fonctionnel, sans bugs, conforme au cahier des charges
- [ ] PR créée et issue FE-12 fermée

## Livrables

- Page Home améliorée avec redirection auto et CTA clairs
- Dashboard complet avec cartes Auth/Plan/Quota et Quick Cards intelligentes
- Prefetch optimisé (survol + idle)
- Tests complets (unitaires)
- Module i18n pour labels/CTA
- Issue et PR complètes

## Labels

`feature`, `navigation`, `milestone-fe-12`
