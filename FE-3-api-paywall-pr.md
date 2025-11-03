# PR: FE-3 — Couche API & Paywall

## Description

Implémentation de la couche API transverse et du système paywall avec client HTTP robuste (Idempotency-Key sur mutations), PaywallService avec schémas Zod discriminés, hook usePaywall avec React Query, et composants PaywallGate et QuotaMessage.

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

1. `src/shared/api/client.test.ts` - Tests pour client HTTP (22 tests)
2. `src/shared/config/features.ts` - Clés centralisées pour features paywall
3. `src/shared/config/features.test.ts` - Tests pour helper assertValidFeatureKey
4. `src/shared/api/paywall.service.ts` - Service Paywall avec schémas Zod discriminés
5. `src/shared/api/paywall.service.test.ts` - Tests pour PaywallService
6. `src/features/billing/hooks/usePaywall.ts` - Hook React Query pour paywall
7. `src/widgets/QuotaMessage/QuotaMessage.tsx` - Composant message quota (429)
8. `src/features/billing/PaywallGate.tsx` - Composant passe-plat pour paywall
9. `FE-3-api-paywall-issue.md` - Issue GitHub
10. `FE-3-api-paywall-pr.md` - Description PR

### Fichiers modifiés

1. `src/shared/api/client.ts` - Améliorations Idempotency-Key, parsing défensif, mapping erreurs
2. `src/widgets/UpgradeBanner/UpgradeBanner.tsx` - Support callback onUpgrade en props

## Endpoints utilisés

- `POST /v1/paywall/decision` - Vérification autorisation feature
  - Body : `{ feature: string }`
  - Réponse : `{ allowed: boolean, reason?: 'plan' | 'rate', upgrade_url?: string, retry_after?: number }`

## Fonctionnalités

### 3.1 — HTTP client transverse

- ✅ Idempotency-Key sur mutations uniquement (POST/PUT/PATCH/DELETE)
- ✅ Warning en dev si idempotency: true sur GET
- ✅ Pas de retry sur mutations (même avec Idempotency)
- ✅ Retry limité (≤2) uniquement sur GET/HEAD et NetworkError
- ✅ Timeout (15s) avec AbortController
- ✅ Distingue NetworkError('timeout') vs ApiError(5xx)
- ✅ Parsing défensif : gère 204 No Content
- ✅ Détecte Content-Type : JSON vs HTML vs Blob (PDF/ZIP)
- ✅ JSON invalide avec Content-Type application/json → ApiError "invalid-json"
- ✅ request_id extrait depuis headers puis body
- ✅ Mapping erreurs 401 → événement unauthorized
- ✅ Mapping erreurs 402 → événement paywall avec payload
- ✅ Mapping erreurs 429 → événement quota avec payload
- ✅ 401 sur /login → pas de redirection (éviter boucles)

### 3.2 — PaywallService + hook usePaywall

- ✅ Feature keys centralisées dans config/features.ts
- ✅ Schémas Zod discriminés (union PaywallAllowed/PaywallBlocked)
- ✅ PaywallService avec méthode decision(feature)
- ✅ Hook usePaywall avec React Query
- ✅ Cache court (5s) avec gcTime (60s)
- ✅ retry: false (402/429 ne doivent pas retenter)
- ✅ refetchOnWindowFocus: false
- ✅ Gestion Retry-After (429)

### 3.3 — PaywallGate component & UpgradeBanner

- ✅ Composant PaywallGate avec responsabilités nettes
- ✅ Ne déclenche pas lui-même de navigation/checkout
- ✅ Délègue la navigation via callback onUpgrade
- ✅ A11y : role="alert" pour messages bloquants
- ✅ Composant QuotaMessage pour afficher message quota (429)
- ✅ UpgradeBanner accepte onUpgrade callback en props

## Tests

- ✅ Tests client HTTP (22 tests)
  - Headers Authorization/Idempotency-Key
  - Mapping erreurs 401/402/429
  - Timeout, JSON invalide, 204, request_id
- ✅ Tests features config (5 tests)
- ✅ Tests PaywallService (6 tests)
- ⏳ Tests usePaywall hook (à faire)
- ⏳ Tests PaywallGate component (à faire)

## Contraintes respectées

- ✅ Idempotency-Key uniquement sur mutations (POST/PUT/PATCH/DELETE)
- ✅ Pas de retry sur mutations
- ✅ Retry uniquement sur GET/HEAD et NetworkError (max 2)
- ✅ Timeout avec AbortController (15s par défaut)
- ✅ Parsing défensif (204, Content-Type detection, JSON invalide)
- ✅ request_id extrait depuis headers puis body
- ✅ Mapping erreurs 401/402/429 centralisé via eventBus
- ✅ 401 sur /login → pas de redirection (éviter boucles)
- ✅ Schémas Zod discriminés pour paywall (union allowed/blocked)
- ✅ Cache court React Query (5s staleTime, 60s gcTime)
- ✅ retry: false pour usePaywall
- ✅ refetchOnWindowFocus: false pour usePaywall
- ✅ PaywallGate ne déclenche pas de navigation automatique
- ✅ onUpgrade délégué via callback
- ✅ A11y : role="alert" pour messages bloquants

## Commandes de test

```bash
# Tests unitaires
npm run test

# Linter
npm run lint

# Format
npm run format:check

# Type-check
npm run build
```

## Notes additionnelles

- Les tests pour usePaywall et PaywallGate sont en cours de développement
- La fonctionnalité de pré-chauffe cache sur dashboard est optionnelle
- Les tests finaux (usePaywall, PaywallGate) seront ajoutés dans une prochaine itération
