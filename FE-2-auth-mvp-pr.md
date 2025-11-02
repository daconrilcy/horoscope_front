# PR: FE-2 — Auth (MVP)

## Description

Implémentation complète du système d'authentification (MVP) avec sécurité renforcée : helpers JWT, store Zustand avec hydratation contrôlée, service API avec validation Zod stricte, et pages Login/Signup/Reset fonctionnelles.

## Type de changement

- [x] Nouvelle fonctionnalité (feature)
- [ ] Correction de bug (bugfix)
- [ ] Refactoring
- [ ] Documentation

## Checklist

- [x] J'ai vérifié que mon code suit les conventions du projet
- [x] J'ai auto-reviewé mon code
- [x] Mes commentaires sont utiles et clairs
- [x] J'ai documenté les changements complexes si nécessaire
- [x] Mes tests passent localement
- [x] J'ai mis à jour la documentation si nécessaire

## Résumé des changements

### Nouveaux fichiers

1. `src/shared/auth/token.ts` - Helpers pour gestion token localStorage
2. `src/shared/auth/token.test.ts` - Tests helpers token (11 tests)
3. `src/shared/auth/redirect.ts` - Helper redirection sécurisée
4. `src/shared/auth/redirect.test.ts` - Tests redirection (10 tests)
5. `src/shared/api/auth.service.ts` - Service API d'authentification
6. `src/shared/api/auth.service.test.ts` - Tests service auth (15 tests)
7. `src/pages/reset/request/index.tsx` - Page demande réinitialisation
8. `src/pages/reset/confirm/index.tsx` - Page confirmation réinitialisation
9. `FE-2-auth-mvp-issue.md` - Issue GitHub
10. `FE-2-auth-mvp-pr.md` - Description PR

### Fichiers modifiés

1. `src/stores/authStore.ts` - Refonte complète avec `hasHydrated`, `login()`, `logout()`
2. `src/stores/authStore.test.ts` - Tests mis à jour (9 tests)
3. `src/app/AppProviders.tsx` - Hydratation au boot
4. `src/pages/login/index.tsx` - Page login fonctionnelle complète
5. `src/pages/signup/index.tsx` - Page signup fonctionnelle complète
6. `src/shared/config/routes.ts` - Ajout routes RESET
7. `src/app/router.tsx` - Ajout routes reset, mise à jour RouteGuard
8. `src/app/layouts/PrivateLayout.tsx` - Utilise `logout()` avec QueryClient
9. `src/app/router.test.tsx` - Tests mis à jour pour `hasHydrated`
10. `src/app/layouts/PrivateLayout.test.tsx` - Tests mis à jour pour `logout()`

## Fonctionnalités

### 2.1 — Auth store & helpers

- ✅ Helpers JWT avec clé namespacée `APP_AUTH_TOKEN`
- ✅ Helper redirection sécurisée (`safeInternalRedirect`)
- ✅ Store avec `hasHydrated`, `userRef`, `redirectAfterLogin`
- ✅ Méthodes `hydrateFromStorage()`, `login()`, `logout()`
- ✅ `logout()` purge token + userRef + React Query cache
- ✅ Hydratation au boot via `AppProviders`

### 2.2 — API AuthService

- ✅ Service avec validation Zod stricte (fail-fast)
- ✅ Endpoints : signup, login, requestReset, confirmReset
- ✅ Schémas Zod précis pour toutes les réponses
- ✅ Gestion erreurs 422/400 avec `details` par champ
- ✅ Propagation `ApiError` pour 401

### 2.3 — Pages d'authentification

- ✅ Page Login : formulaire fonctionnel, normalisation email, double-submit empêché, A11y, gestion erreurs, redirection sécurisée
- ✅ Page Signup : validation confirmPassword, gestion erreurs, redirection `/login`
- ✅ Page Reset Request : demande réinitialisation, toast success
- ✅ Page Reset Confirm : confirmation avec token depuis URL, validation, redirection

## Tests

### Tests unitaires

- ✅ **77/77 tests passants**
  - 11 tests helpers token
  - 10 tests redirection
  - 15 tests service auth
  - 9 tests store auth
  - 9 tests router
  - 13 tests AppProviders
  - 4 tests PrivateLayout
  - 3 tests PublicLayout
  - 1 test App
  - 2 tests useTitle

### Couverture

- ✅ Validation Zod fail-fast testée
- ✅ Gestion erreurs avec details testée
- ✅ Hydratation testée
- ✅ Login/logout testés
- ✅ Redirection sécurisée testée

## Qualité

- ✅ **Lint** : 0 erreur / 0 avertissement
- ✅ **Type-check** : TypeScript strict OK
- ✅ **Build** : Compilation réussie
- ✅ **Tests** : 77/77 passants

## Références

- Closes #8

## Instructions de test

### Tests unitaires

```bash
npm run test
```

### Tests manuels (e2e)

1. **Signup → Login → Dashboard** :
   - Aller sur `/signup`
   - Créer un compte avec email/password
   - Vérifier toast "Compte créé, connectez-vous"
   - Redirection vers `/login`
   - Se connecter avec les identifiants créés
   - Vérifier toast "Connexion réussie"
   - Redirection vers `/app/dashboard`

2. **Reset Password** :
   - Aller sur `/reset/request`
   - Entrer un email
   - Vérifier toast "Email envoyé, vérifiez votre boîte mail"
   - Cliquer sur le lien dans l'email (avec token)
   - Entrer nouveau mot de passe
   - Vérifier toast "Mot de passe réinitialisé"
   - Redirection vers `/login`

3. **Gestion erreurs** :
   - Tester login avec identifiants invalides → erreur inline
   - Tester signup avec email existant → erreur inline par champ
   - Tester reset avec token invalide → message d'erreur

4. **Sécurité** :
   - Vérifier que redirection externe est bloquée (`safeInternalRedirect`)
   - Vérifier que token persiste après refresh
   - Vérifier que logout purge tout (token + cache React Query)

## Notes supplémentaires

- Les pages utilisent des styles inline pour l'instant (MVP)
- Les tests des pages avec Testing Library seront ajoutés dans une PR suivante si nécessaire
- Les tests d'intégration e2e complets seront ajoutés dans une PR suivante si nécessaire
