# Issue: FE-0.4 — Client HTTP et erreurs normalisées

## Objectif

Implémenter un wrapper HTTP unique (fetch) avec injection automatique du token JWT, ajout d'Idempotency-Key pour `/v1/billing/checkout`, et gestion centralisée des erreurs HTTP (401→callback unauthorized, 402/429→eventBus paywall, 5xx→ErrorBoundary). Architecture découplée via eventBus pour éviter les redirs infinies et garder le client agnostique de l'UI.

## Tâches

- [x] Installer les dépendances (zustand, react-router-dom, uuid, @types/uuid, msw)
- [x] Créer eventBus.ts (pub/sub léger)
- [x] Créer errors.ts (ApiError, NetworkError, extractRequestId)
- [x] Créer authStore.ts (mémoire + localStorage, hydratation)
- [x] Créer paywallStore.ts (souscription eventBus)
- [x] Créer client.ts (configureHttp, timeouts, parsing, mapping erreurs)
- [x] Créer ErrorBoundary.tsx
- [x] Créer UpgradeBanner.tsx
- [x] Créer AppProviders.tsx (config http + onUnauthorized)
- [x] Configurer router.tsx avec RouteGuard
- [x] Intégrer dans App.tsx
- [x] Écrire tests unitaires (28 tests couvrant tous les cas critiques)
- [x] Vérifier lint/typecheck/tests

## Critères d'acceptation

- [x] 401 redirige via callback (pas d'appel router dans le client), pas depuis `/login`
- [x] Timeout/abort gérés, erreurs NetworkError distinctes des 5xx
- [x] Idempotency-Key uniquement sur `/v1/billing/checkout`
- [x] 204 / Content-Type / Blob gérés correctement
- [x] request_id propagé (headers et body)
- [x] Stores découplés, bannière paywall déclenchée via eventBus
- [x] Tests couvrent les 28 cas (token, idempotency, timeout, 204, blob, 401/402/429/5xx, request_id, retry)
- [x] Token stocké en mémoire (source de vérité), localStorage sync en arrière-plan
- [x] Pas de retry sur POST/DELETE ou `/v1/billing/checkout`
- [x] Retry uniquement GET/HEAD sur NetworkError (max 2)

## Livrables

- Client HTTP avec toutes les fonctionnalités demandées
- EventBus pour découplage UI/client HTTP
- Stores Zustand (auth, paywall)
- ErrorBoundary et UpgradeBanner
- Router avec RouteGuard
- 28 tests unitaires passants
- Architecture conforme au plan révisé

## Fichiers créés/modifiés

- `src/shared/api/eventBus.ts` - Pub/sub léger
- `src/shared/api/errors.ts` - Types d'erreurs API
- `src/shared/api/types.ts` - Types partagés
- `src/shared/api/client.ts` - Client HTTP complet
- `src/stores/authStore.ts` - Store JWT
- `src/stores/paywallStore.ts` - Store paywall
- `src/shared/ui/ErrorBoundary.tsx` - ErrorBoundary React
- `src/widgets/UpgradeBanner/UpgradeBanner.tsx` - Bannière upgrade
- `src/app/AppProviders.tsx` - Providers avec config HTTP
- `src/app/router.tsx` - Router avec RouteGuard
- `src/app/App.tsx` - Intégration
- `src/shared/api/client.test.ts` - 28 tests unitaires

## Labels

`feature`, `http`, `auth`, `paywall`

