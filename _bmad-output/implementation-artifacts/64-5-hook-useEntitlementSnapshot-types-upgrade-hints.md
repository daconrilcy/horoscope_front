# Story 64.5 — Hook `useEntitlementSnapshot` + types upgrade hints côté frontend

Status: todo

## Story

En tant que développeur frontend,
je veux un hook React `useEntitlementSnapshot` qui expose le snapshot complet des droits de l'utilisateur (plan, features, upgrade hints) depuis `/v1/entitlements/me`,
afin que toutes les pages stratégiques puissent consommer les droits et hints sans contenir aucune logique métier de plan.

## Context

Dépend de **Story 64.4** (upgrade_hints disponibles dans `/v1/entitlements/me`).

`billing.ts` contient déjà `useChatEntitlementUsage` et des types billings. Cette story étend ce fichier avec les types `UpgradeHint` et crée un hook généraliste `useEntitlementSnapshot` que les stories 64.7, 64.8 et 64.9 utiliseront.

**Règle fondamentale (FR64-11) :** Le frontend ne contient aucune logique de décision métier sur les plans — il consomme le snapshot et en déduit quoi afficher.

## Acceptance Criteria

**AC1 — Type UpgradeHint et EntitlementSnapshot définis**
**Given** `frontend/src/api/billing.ts`  
**When** le fichier est inspecté  
**Then** `UpgradeHint` est un type TypeScript avec :
`feature_code`, `current_plan_code`, `target_plan_code`, `benefit_key`, `cta_variant`, `priority`  
**And** `EntitlementsMeData` (ou type équivalent) contient `upgrade_hints: UpgradeHint[]`

**AC2 — Hook `useEntitlementSnapshot` retourne les données du snapshot**
**Given** un composant React authentifié  
**When** `useEntitlementSnapshot()` est appelé  
**Then** le hook retourne `{ data, isLoading, isError }` avec `data.plan_code`, `data.features`, et `data.upgrade_hints`

**AC3 — Sélecteur `useUpgradeHint(featureCode)` disponible**
**Given** `useEntitlementSnapshot()`  
**When** `useUpgradeHint("horoscope_daily")` est appelé  
**Then** le hint correspondant est retourné s'il existe dans `upgrade_hints`, ou `undefined` sinon

**AC4 — Sélecteur `useFeatureAccess(featureCode)` disponible**
**Given** `useEntitlementSnapshot()`  
**When** `useFeatureAccess("horoscope_daily")` est appelé  
**Then** l'objet `FeatureEntitlementResponse` correspondant est retourné ou `undefined`

**AC5 — Cache TanStack Query — staleTime approprié**
**Given** le hook `useEntitlementSnapshot`  
**When** plusieurs composants le consomment simultanément  
**Then** une seule requête HTTP est effectuée (partage du cache Query)  
**And** `staleTime` est configuré à au moins 2 minutes (les droits ne changent pas à chaque render)

**AC6 — Tests unitaires**
**Given** `frontend/src/tests/useEntitlementSnapshot.test.ts`  
**When** les tests sont exécutés  
**Then** les cas suivants sont couverts :
- snapshot free avec upgrade_hints non vide
- snapshot premium avec upgrade_hints vide
- `useUpgradeHint("horoscope_daily")` retourne le bon hint
- `useFeatureAccess("natal_chart_long")` retourne le bon accès

## Tasks / Subtasks

- [ ] T1 — Ajouter `UpgradeHint` et mettre à jour les types dans `billing.ts` (AC1)
  - [ ] T1.1 Lire `frontend/src/api/billing.ts`
  - [ ] T1.2 Ajouter le type :
    ```ts
    export type UpgradeHint = {
      feature_code: string
      current_plan_code: string
      target_plan_code: string
      benefit_key: string
      cta_variant: 'banner' | 'inline' | 'modal'
      priority: number
    }
    ```
  - [ ] T1.3 Ajouter `upgrade_hints: UpgradeHint[]` dans le type `EntitlementsMeData` (ou créer ce type s'il n'existe pas)

- [ ] T2 — Créer `frontend/src/hooks/useEntitlementSnapshot.ts` (AC2, AC3, AC4, AC5)
  - [ ] T2.1 Créer le répertoire `frontend/src/hooks/` si nécessaire (vérifier s'il existe)
  - [ ] T2.2 Implémenter :
    ```ts
    export function useEntitlementSnapshot() {
      return useQuery({
        queryKey: ['entitlements', 'me'],
        queryFn: () => fetchEntitlementsMe(token),
        staleTime: 2 * 60 * 1000, // 2 minutes
        enabled: !!token,
      })
    }

    export function useUpgradeHint(featureCode: string): UpgradeHint | undefined {
      const { data } = useEntitlementSnapshot()
      return data?.upgrade_hints.find(h => h.feature_code === featureCode)
    }

    export function useFeatureAccess(featureCode: string): FeatureEntitlementResponse | undefined {
      const { data } = useEntitlementSnapshot()
      return data?.features.find(f => f.feature_code === featureCode)
    }
    ```
  - [ ] T2.3 Ajouter `fetchEntitlementsMe(token)` dans `billing.ts` si absent (GET `/v1/entitlements/me`)
  - [ ] T2.4 Utiliser `useAccessTokenSnapshot()` pour le token

- [ ] T3 — Tests (AC6)
  - [ ] T3.1 Créer `frontend/src/tests/useEntitlementSnapshot.test.ts`
  - [ ] T3.2 Mocker `fetchEntitlementsMe` avec des snapshots free / premium
  - [ ] T3.3 Tester `useUpgradeHint` et `useFeatureAccess`
  - [ ] T3.4 Tester le partage de cache (staleTime)

## Dev Notes

### Répertoire hooks

Vérifier si `frontend/src/hooks/` existe. Sinon, le créer. Placer `useEntitlementSnapshot.ts` dedans. Les hooks existants spécifiques aux features (ex: `useChatEntitlementUsage`) restent dans `billing.ts` pour l'instant — ne pas les déplacer.

### queryKey

Utiliser `['entitlements', 'me']` comme queryKey pour pouvoir invalider le cache depuis n'importe quel composant après un changement de plan (ex: retour de la page billing).

### fetchEntitlementsMe

L'endpoint existant est `/v1/entitlements/me` (déjà implémenté backend). Vérifier dans `billing.ts` si une fonction le consomme déjà — si oui, l'utiliser directement dans le hook plutôt que d'en créer une nouvelle.

### Pas de logique métier dans le hook

Le hook ne doit pas contenir de conditions du type `if plan_code === 'free' then ...`. Il expose les données brutes. La logique d'affichage est dans les composants (64.6, 64.7, 64.8, 64.9) qui consomment `granted`, `variant_code`, et `upgrade_hints`.
