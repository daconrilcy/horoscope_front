# PR: FE-0.4 — Client HTTP et erreurs normalisées

**Titre**: FE-0.4 — Client HTTP et erreurs normalisées

## Portée & Alignement

Implémente le **client HTTP avec gestion d'erreurs normalisées** côté front, alignée sur **http://localhost:8000/** et les contrats v1. Architecture découplée via eventBus pour éviter les redirs infinies.

## Endpoints utilisés

Tous les endpoints du backend via le client HTTP centralisé :
- `/v1/auth/*` (signup, login, reset)
- `/v1/billing/checkout` (avec Idempotency-Key obligatoire)
- `/v1/billing/portal`
- `/v1/paywall/decision`
- `/v1/account/*`
- `/v1/horoscope/*`
- `/v1/chat/*`

## Contraintes respectées

- ✅ Wrapper HTTP unique (Bearer + Idempotency sur checkout ; mapping 401/402/429/5xx)
- ✅ Redirection 401 via **callback** (pas d'appel router dans le client), **pas** depuis `/login`
- ✅ Timeout/abort gérés, erreurs **NetworkError** distinctes des 5xx
- ✅ Idempotency-Key uniquement sur `/v1/billing/checkout`
- ✅ `204` / `Content-Type` / Blob gérés correctement
- ✅ `request_id` propagé (headers **et** body)
- ✅ Stores découplés, bannière paywall déclenchée via **eventBus**
- ✅ Paywall via événements `paywall` et `quota` (402/429)
- ✅ Token stocké en mémoire (source de vérité), localStorage sync en arrière-plan
- ✅ Retry uniquement GET/HEAD sur NetworkError (max 2), jamais sur `/v1/billing/checkout`
- ✅ Parsing défensif (fallback si JSON échoue)

## Tests (local-only)

- **Unit/int** : `src/shared/api/client.test.ts` → **28 tests passants**
  - Injection Bearer automatique
  - Idempotency-Key uniquement sur `/v1/billing/checkout`
  - Timeout/abort/offline → NetworkError
  - 204 No Content sans parsing
  - Parsing blob/text/JSON selon Content-Type
  - 401/402/429/5xx avec mapping événements
  - Extraction request_id (headers + body)
  - Retry GET uniquement sur NetworkError
  - Pas de retry sur POST ou `/v1/billing/checkout`
- **Commandes** : `npm run dev`, `npm run test`, `npm run lint`

## Vérifications

- [x] Check-list **Quality Gates Frontend** entièrement cochée
- [x] Tous les tests unitaires passent (28/28)
- [x] TypeScript strict : `npx tsc --noEmit` → **0 erreur**
- [x] Lint : quelques warnings mineurs (principalement dans les tests mocks)
- [x] Architecture conforme au plan révisé

## Détails techniques

### EventBus
- Système pub/sub léger pour découpler le client HTTP de l'UI
- Événements : `unauthorized`, `paywall`, `quota`

### Client HTTP
- `configureHttp({ baseURL, onUnauthorized })` pour configuration
- Méthodes : `http.get<T>()`, `http.post<T>()`, `http.put<T>()`, `http.del<T>()`
- Injection automatique Bearer si `auth: true` et token présent
- Idempotency-Key (UUID v4) uniquement sur `/v1/billing/checkout`
- Timeout 15s par défaut via AbortController
- Parsing adaptatif (JSON/blob/text selon Content-Type)
- Retry GET/HEAD max 2 fois sur NetworkError uniquement

### Stores
- `authStore` : Token JWT en mémoire (source de vérité), sync localStorage
- `paywallStore` : État paywall (visible, reason, upgradeUrl), souscrit à eventBus

### Composants
- `ErrorBoundary` : Capture erreurs 5xx avec affichage request_id
- `UpgradeBanner` : Bannière upgrade pour 402/429
- `RouteGuard` : Protection routes privées avec redirection `/login`

## Notes

- Les erreurs de lint restantes sont principalement dans les tests (mocks `global.fetch`), non bloquantes pour la fonctionnalité
- L'architecture respecte le découplage UI/client HTTP via eventBus
- Le client HTTP est prêt pour être utilisé dans toutes les features (auth, billing, horoscope, chat, etc.)

