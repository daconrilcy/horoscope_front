# Audit FE-13 — Billing config awareness & dev debug panel

## ✅ Éléments implémentés

### 1. Service de configuration ✅
- [x] `billingConfigService.getConfig()` qui lit `/v1/config` avec fallback sur `import.meta.env`
- [x] Cache mémoire (5 minutes TTL)
- [x] Validation Zod stricte avec `BillingConfigSchema`
- [x] Normalisation des URLs (retrait trailing slash)
- [x] Méthode `validateOrigin()` pour vérifier le match d'origin

### 2. Variables exposées ✅
- [x] `publicBaseUrl` (PUBLIC_BASE_URL)
- [x] `checkoutSuccessPath` (BILLING_CHECKOUT_SUCCESS_PATH)
- [x] `checkoutCancelPath` (BILLING_CHECKOUT_CANCEL_PATH)
- [x] `portalReturnUrl` (optionnel)
- [x] `checkoutTrialsEnabled` (CHECKOUT_TRIALS_ENABLED)
- [x] `checkoutCouponsEnabled` (CHECKOUT_COUPONS_ENABLED)
- [x] `stripeTaxEnabled` (STRIPE_TAX_ENABLED)
- [x] `priceLookupHash` et `priceLookupLength` (optionnels)

### 3. Hook React Query ✅
- [x] `useBillingConfig()` avec cache React Query
- [x] `refetchOnWindowFocus` en dev uniquement
- [x] `staleTime` de 5 minutes

### 4. Billing Debug Panel ✅
- [x] Composant `BillingDebugPanel.tsx` créé
- [x] Masqué en production (`import.meta.env.DEV` check)
- [x] Affiche tous les flags (Trials, Coupons, Tax)
- [x] Affiche les URLs (Base URL, Success Path, Cancel Path, Portal Return URL)
- [x] Badge d'environnement ("development")
- [x] Warning si origin mismatch (current ≠ expected)
- [x] Style fixe en bas-droite

### 5. Headers de corrélation ✅
- [x] `version.ts` avec `CLIENT_VERSION` et `REQUEST_SOURCE`
- [x] Headers `X-Client-Version` et `X-Request-Source` dans `client.ts`

### 6. Tests unitaires ✅
- [x] 8 tests unitaires dans `billingConfig.service.test.ts`
- [x] Tests pour API fetch, fallback env, normalisation URL, cache, validation origin

### 7. Variables d'environnement ✅
- [x] Extension de `env.ts` avec schémas Zod pour variables billing
- [x] Variables optionnelles avec fallback

## ⚠️ Éléments manquants ou incomplets

### 1. Intégration dans le router ❌
- [ ] `BillingDebugPanel` n'est **PAS** intégré dans `router.tsx` dans le commit FE-13
- Le panel existe mais n'est jamais rendu !
- **Action requise** : Ajouter l'import lazy et le rendre dans `AppShell` (comme fait dans main)

### 2. Tests E2E ❌
- [ ] Aucun test E2E Playwright pour vérifier :
  - Le panel apparaît en dev
  - Le panel est masqué en prod
  - Les badges reflètent les flags

### 3. EventBus pour request_id ⚠️
- [ ] L'observabilité avec EventBus est mentionnée dans FE-13 mais implémentée dans FE-19
- Pas critique, mais à noter

### 4. Badge d'environnement ⚠️
- [ ] Le badge affiche toujours "development" en dur
- Devrait détecter dynamiquement dev/prod

## 📋 Actions correctives nécessaires

### Priorité HAUTE
1. **Ajouter BillingDebugPanel au router** (bloquant pour l'AC)
   ```tsx
   // Dans src/app/router.tsx
   const BillingDebugPanel = lazy(() =>
     import('@/features/billing/BillingDebugPanel').then((module) => ({
       default: module.BillingDebugPanel,
     }))
   );
   
   // Dans AppShell
   {import.meta.env.DEV && (
     <Suspense fallback={null}>
       <BillingDebugPanel />
     </Suspense>
   )}
   ```

### Priorité MOYENNE
2. **Corriger le badge d'environnement** (affichage dynamique)
3. **Ajouter tests E2E** (comme demandé dans le cahier des charges)

## ✅ Critères d'acceptation (AC)

- [x] Le panneau dev affiche correctement les flags
- [x] Avertissement si mismatch d'URL ✅
- [ ] **Aucun rendu en production (build)** → ❌ **À VÉRIFIER** (code présent mais pas intégré)
- [ ] Tests E2E → ❌ **MANQUANT**

## 📊 Score de complétude

**Implémentation : 85%**
- Code : ✅ 100%
- Intégration router : ❌ 0%
- Tests E2E : ❌ 0%
- Badge dynamique : ⚠️ 50%

**Action immédiate : Intégrer BillingDebugPanel dans router.tsx**
