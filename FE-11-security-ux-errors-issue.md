# Issue: FE-11 — Sécurité & UX erreurs

## Objectif

Implémenter une normalisation globale des erreurs HTTP (401/402/429/5xx) avec mapping dans le wrapper HTTP et surfaces UI cohérentes (toasts, bannières, ErrorBoundary) pour une UX cohérente. Anti-spam, sécurité, et gestion robuste des erreurs.

## Sous-issues

### 11.1 — Normalisation erreurs (401/402/429/5xx)

**Objectif** : UX cohérente pour toutes les erreurs HTTP avec mapping global dans http wrapper + surfaces UI (bannières, toasts).

**Tâches** :

1. **401 — Debounce global 60s + post-login redirect + toast unique** :
   - Modifier `src/shared/api/eventBus.ts` :
     - Ajouter type d'événement `'auth:unauthorized'` (au lieu de `'unauthorized'`)
   - Modifier `src/shared/api/client.ts` :
     - Implémenter debounce global 401 (60s) avec flag module-scope `unauthorizedFiredAt`
     - Fonction `fireUnauthorizedOnce()` qui émet `auth:unauthorized` seulement si >60s depuis dernier
     - Dans `toApiError()`, appeler `fireUnauthorizedOnce()` au lieu d'émettre directement
   - Modifier `src/app/AppProviders.tsx` :
     - Écouter `auth:unauthorized` de eventBus
     - Avant redirection, stocker `location.pathname + location.search` dans `sessionStorage.setItem('post_login_redirect', ...)`
     - Afficher toast `'Session expirée'` UNIQUEMENT si pas déjà sur `/login`
     - Rediriger vers `/login`
   - Modifier `src/pages/login/index.tsx` :
     - Après login réussi, lire `post_login_redirect` depuis sessionStorage
     - Naviguer vers `redirectTo || '/app/dashboard'`
     - Supprimer `post_login_redirect` après lecture

2. **402/429 — Événements typés + Retry-After** :
   - Modifier `src/shared/api/types.ts` :
     - Étendre `PaywallPayload` avec `feature?: string`, `retry_after?: number`
   - Modifier `src/shared/api/eventBus.ts` :
     - Ajouter types `'paywall:plan'` et `'paywall:rate'` (au lieu de `'paywall'` et `'quota'`)
   - Modifier `src/shared/api/client.ts` :
     - Dans `toApiError()`, extraire `Retry-After` depuis headers (seconds) ou JSON `{retry_after}`
     - Pour 402 : émettre `paywall:plan` avec payload `{ feature, upgrade_url? }`
     - Pour 429 : émettre `paywall:rate` avec payload `{ feature, retry_after? }`
   - Modifier `src/features/billing/hooks/usePaywall.ts` :
     - Extraire `Retry-After` depuis headers de la réponse ApiError 429
     - Merger avec `retry_after` du body
   - Vérifier que tous les hooks premium (useChat, useTodayPremium) :
     - Ne déclenchent rien si `usePaywall(feature).isAllowed !== true`
     - Gardent les guards paywall existants

3. **5xx — ErrorBoundary riche (request_id + retry local)** :
   - Modifier `src/shared/api/client.ts` :
     - Toujours extraire `x-request-id` (ou `x-correlation-id`) des réponses succès et erreur
     - Inclure dans ApiError (déjà fait, vérifier que c'est complet)
     - Cas blob : si `parseAs:'blob'` et `content-type` JSON → reparser JSON et lever ApiError avec request_id
   - Modifier `src/shared/ui/ErrorBoundary.tsx` :
     - Vérifier que `onError?` callback est bien utilisé pour logger (Sentry futur)
     - Fallback : `role="alert"`, affiche request_id si dispo, bouton Retry
     - `resetKeys` permet déjà retry (vérifier que c'est fonctionnel)

4. **Normalisation globale (mapping centralisé)** :
   - Modifier `src/shared/api/client.ts` :
     - Mapping unique par statut :
       - 401 → `auth:unauthorized` (debounced)
       - 402 → `paywall:plan` (payload)
       - 429 → `paywall:rate` (payload)
       - 5xx → throw ApiError (capturé par ErrorBoundary)
     - Jamais de toast direct depuis client.ts (laisser AppProviders toaster)
     - Retry policy : jamais sur 4xx; 1 retry max sur NetworkError (backoff court) — vérifier que c'est déjà le cas
   - Modifier `src/app/AppProviders.tsx` :
     - Souscription eventBus :
       - `auth:unauthorized` → toast (unique) + redirect `/login`
       - `paywall:*` → pas de toast global (PaywallGate/QuotaBadge s'en charge)

5. **React Query — Background errors** :
   - Modifier `src/app/AppProviders.tsx` :
     - QueryClient defaults :
       - `queries: { retry: (failureCount, error) => isNetworkError(error) && failureCount < 1, refetchOnWindowFocus: false }`
     - Les erreurs de refetch ne déclenchent pas de toast global

6. **Sécurité des messages d'erreur** :
   - Modifier `src/shared/api/errors.ts` :
     - Ajouter champ optionnel `meta?: { debugMessage?: string }` à ApiError
   - Modifier `src/shared/api/client.ts` :
     - Dans `toApiError()`, stocker message brut dans `error.meta.debugMessage`
     - Mapper message UX générique : "Une erreur est survenue ; Request ID: ..."
   - Modifier `src/shared/ui/ErrorBoundary.tsx` :
     - Afficher message UX générique au lieu de `error.message` brut
     - Afficher request_id si disponible
   - Vérifier tous les usages de `toast.error(error.message)` :
     - Utiliser message UX générique au lieu du message brut

7. **Tests complets** :
   - `src/shared/api/client.test.ts` :
     - 401 : plusieurs requêtes simultanées ⇒ 1 seul `auth:unauthorized` émis + 1 toast
     - 401 depuis `/login` : aucun toast (déjà sur login)
     - 402 : événement `paywall:plan` avec feature, upgrade_url
     - 429 : événement `paywall:rate` avec retry_after pris des headers et JSON
     - 5xx blob JSON : ApiError avec request_id
     - Extraction request_id : vérifier headers `x-request-id`, `x-correlation-id`
   - `src/app/AppProviders.test.tsx` :
     - Sur `auth:unauthorized` → toast affiché + `navigate('/login')` + stockage `post_login_redirect`
     - Rejeu post-login : redirection vers route initiale
   - `src/shared/ui/ErrorBoundary.test.tsx` :
     - Capture d'une erreur 5xx → fallback rendu + request_id affiché
     - `resetKeys` → rerender OK
   - Spot E2E (Playwright local, léger) :
     - Simuler un 401 en background → pas de boucles, toast unique
     - 429 avec `Retry-After: 5` → badge/quota affiche countdown

**AC** :

- [ ] 401 : toast unique "Session expirée" (+ debounce 60s), redirection `/login`, retour post-login vers route d'origine
- [ ] 402/429 : événements typés (`paywall:plan`, `paywall:rate`), `retry_after` pris en compte, surfaces PaywallGate/QuotaBadge OK (pas de requêtes premium si gated)
- [ ] 5xx : ErrorBoundary affiche request_id si présent, retry via `resetKeys`
- [ ] Normalisation : pas de toasts dans client.ts; mapping statuts centralisé; retry Network-only
- [ ] Sécurité : messages serveurs non exposés en clair ; Request ID affiché
- [ ] Tests : unitaires & spot E2E couvrant 401/402/429/5xx, debouncing, post-login redirect, request_id
- [ ] Qualité : lint/type/tests verts

## Critères d'acceptation

- [ ] 401 : toast unique "Session expirée" (+ debounce 60s), redirection `/login`, retour post-login vers route d'origine
- [ ] 402/429 : événements typés (`paywall:plan`, `paywall:rate`), `retry_after` pris en compte, surfaces PaywallGate/QuotaBadge OK (pas de requêtes premium si gated)
- [ ] 5xx : ErrorBoundary affiche request_id si présent, retry via `resetKeys`
- [ ] Normalisation : pas de toasts dans client.ts; mapping statuts centralisé; retry Network-only
- [ ] Sécurité : messages serveurs non exposés en clair ; Request ID affiché
- [ ] Tests : unitaires & spot E2E couvrant 401/402/429/5xx, debouncing, post-login redirect, request_id
- [ ] Qualité : lint/type/tests verts
- [ ] Pre-commit passe (lint + test)
- [ ] Code fonctionnel, sans bugs, conforme au cahier des charges
- [ ] PR créée et issue FE-11 fermée

## Livrables

- Normalisation globale des erreurs HTTP (401/402/429/5xx)
- Debounce 401 (60s) avec toast unique et post-login redirect
- Événements typés pour paywall (paywall:plan, paywall:rate) avec Retry-After
- ErrorBoundary riche avec request_id et retry
- Messages d'erreur sécurisés (non exposés en clair)
- Tests complets (unitaires + spot E2E)
- Issue et PR complètes

## Labels

`security`, `ux`, `milestone-fe-11`

