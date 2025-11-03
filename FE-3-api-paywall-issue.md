# Issue: FE-3 — Couche API & Paywall

## Objectif

Implémenter la couche API transverse et le système paywall avec client HTTP robuste (Idempotency-Key sur mutations), PaywallService avec schémas Zod discriminés, hook usePaywall avec React Query, composants PaywallGate et QuotaMessage, et tests complets.

## Tâches

### 3.1 — HTTP client transverse (+ Idempotency-Key)

- [x] Modifier `src/shared/api/client.ts` :
  - [x] Idempotency-Key sur mutations uniquement (POST/PUT/PATCH/DELETE)
  - [x] Warning en dev si idempotency: true sur GET
  - [x] Pas de retry sur mutations (même avec Idempotency)
  - [x] Retry limité (≤2) uniquement sur GET/HEAD et NetworkError
  - [x] Timeout (15s) avec AbortController
  - [x] Distingue NetworkError('timeout') vs ApiError(5xx)
  - [x] Parsing défensif : gère 204 No Content
  - [x] Détecte Content-Type : JSON vs HTML vs Blob (PDF/ZIP)
  - [x] Si JSON invalide avec Content-Type application/json → ApiError "invalid-json"
  - [x] request_id extrait depuis headers puis body
  - [x] Mapping erreurs 401 → événement unauthorized
  - [x] Mapping erreurs 402 → événement paywall avec payload
  - [x] Mapping erreurs 429 → événement quota avec payload
  - [x] 401 sur /login → pas de redirection (éviter boucles)

**AC** :

- [x] Headers Authorization injecté quand auth !== false
- [x] Idempotency-Key injecté quand idempotency: true sur mutation (POST/PUT/PATCH/DELETE)
- [x] Idempotency-Key non injecté sur GET même si idempotency: true
- [x] Warning en dev si idempotency: true sur GET
- [x] Pas de retry sur mutations
- [x] Retry uniquement sur GET/HEAD et NetworkError (max 2)
- [x] Timeout → NetworkError('timeout')
- [x] JSON invalide → ApiError avec message "invalid-json"
- [x] 204 No Content → retourne undefined
- [x] Content-Type detection (JSON/HTML/Blob)
- [x] request_id extrait depuis headers puis body
- [x] 401/402/429 mappés correctement (événements)

### 3.2 — PaywallService + hook usePaywall(feature)

- [x] Créer `src/shared/config/features.ts` :
  - [x] Clés centralisées : CHAT_MSG_PER_DAY, HORO_TODAY_PREMIUM, etc.
  - [x] Helper assertValidFeatureKey (no-op en prod)
- [x] Créer `src/shared/api/paywall.service.ts` :
  - [x] Schémas Zod discriminés (union PaywallAllowed/PaywallBlocked)
  - [x] Méthode decision(feature: string) : POST /v1/paywall/decision
  - [x] Validation Zod stricte (fail-fast)
- [x] Créer `src/features/billing/hooks/usePaywall.ts` :
  - [x] Hook React Query avec retry: false
  - [x] refetchOnWindowFocus: false
  - [x] staleTime: 5000 (5 secondes)
  - [x] gcTime: 60000 (60 secondes)
  - [x] Key : ['paywall', feature]
  - [x] Gestion Retry-After (429)

**AC** :

- [x] Feature keys centralisées dans config/features.ts
- [x] PaywallService retourne union discriminée (allowed/blocked)
- [x] Hook usePaywall expose isAllowed, reason, upgradeUrl, retryAfter
- [x] Cache court (5s) avec React Query
- [x] Pas de retry sur 402/429
- [x] Pas de refetch sur window focus

### 3.3 — PaywallGate component & UpgradeBanner

- [x] Créer `src/features/billing/PaywallGate.tsx` :
  - [x] Props : feature, children, fallback?, onUpgrade?
  - [x] Utilise usePaywall(feature)
  - [x] Ne déclenche pas lui-même de navigation/checkout
  - [x] Si isAllowed → rend children
  - [x] Si reason === 'plan' (402) → rend UpgradeBanner
  - [x] Si reason === 'rate' (429) → rend QuotaMessage
  - [x] Pendant isLoading → rend fallback ou rien
  - [x] A11y : role="alert" pour messages bloquants
- [x] Créer `src/widgets/QuotaMessage/QuotaMessage.tsx` :
  - [x] Affiche message quota (429) avec retryAfter
  - [x] CTA upgrade avec callback onUpgrade
- [x] Améliorer `src/widgets/UpgradeBanner/UpgradeBanner.tsx` :
  - [x] Accepter onUpgrade callback en props
  - [x] Message correct pour 402 ("Plan insuffisant")

**AC** :

- [x] PaywallGate rend children si allowed
- [x] PaywallGate rend UpgradeBanner si 402 (plan)
- [x] PaywallGate rend QuotaMessage si 429 (rate)
- [x] PaywallGate ne déclenche pas de navigation automatique
- [x] onUpgrade délégué via callback
- [x] A11y : role="alert" pour messages bloquants
- [x] UpgradeBanner accepte onUpgrade callback

## Tests

- [x] `src/shared/api/client.test.ts` : tests pour client HTTP (22 tests)
  - [x] Headers Authorization/Idempotency-Key
  - [x] Mapping erreurs 401/402/429
  - [x] Timeout, JSON invalide, 204, request_id
- [x] `src/shared/config/features.test.ts` : tests pour helper assertValidFeatureKey
- [x] `src/shared/api/paywall.service.test.ts` : tests pour PaywallService
  - [x] Validation Zod union discriminée
  - [x] allowed: true, allowed: false avec reason, retry_after
- [ ] `src/features/billing/hooks/usePaywall.test.ts` : tests pour hook usePaywall
  - [ ] 402 sans upgrade_url
  - [ ] 429 avec Retry-After
  - [ ] Réponses mal formées → ZodError
- [ ] `src/features/billing/PaywallGate.test.tsx` : tests pour PaywallGate
  - [ ] allowed → rend children
  - [ ] 402 → rend UpgradeBanner
  - [ ] 429 → rend QuotaMessage
  - [ ] loading → rend fallback

## Check-list AC finale

- [x] Client : headers Authorization/Idempotency-Key corrects, timeout + abort, retry seulement GET réseau, parsing 204/JSON/Blob, request_id propagé
- [x] PaywallService : Zod union (allowed/blocked), retry: false, refetchOnWindowFocus: false, feature keys centralisées
- [x] PaywallGate : responsibilities clean (no nav), onUpgrade délégué, A11y, gestion 402/429
