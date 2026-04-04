# Story 64.5 — Hook `useEntitlementSnapshot` + types upgrade hints côté frontend

Status: done

## Story

En tant que développeur frontend,
je veux un hook React `useEntitlementSnapshot` qui expose le snapshot complet des droits de l'utilisateur (plan, features, upgrade hints) depuis `/v1/entitlements/me`,
afin que toutes les pages stratégiques puissent consommer les droits et hints sans contenir aucune logique métier de plan.

## Context

Dépend de **Story 64.4** (upgrade_hints disponibles dans `/v1/entitlements/me`).

`billing.ts` contient déjà `useChatEntitlementUsage` et des types billings. Cette story étend ce fichier avec les types `UpgradeHint` et crée un hook généraliste `useEntitlementSnapshot` que les stories 64.7, 64.8 et 64.9 utiliseront.

**Règle fondamentale (FR64-11) :** Le frontend ne contient aucune logique de décision métier sur les plans — il consomme le snapshot et en déduit quoi afficher.

## Acceptance Criteria

- [x] **AC1 — Type UpgradeHint et EntitlementSnapshot définis** : types TypeScript complets ajoutés dans `billing.ts`.
- [x] **AC2 — Hook `useEntitlementSnapshot` retourne les données du snapshot** : implémenté via TanStack Query.
- [x] **AC3 — Sélecteur `useUpgradeHint(featureCode)` disponible** : permet de récupérer un hint par code feature.
- [x] **AC4 — Sélecteur `useFeatureAccess(featureCode)` disponible** : permet de récupérer l'accès effectif par code feature.
- [x] **AC5 — Cache TanStack Query — staleTime approprié** : configuré à 2 minutes.
- [x] **AC6 — Tests unitaires** : couverture des hooks et sélecteurs avec mocks API.

## Tasks / Subtasks

- [x] T1 — Ajouter `UpgradeHint` et mettre à jour les types dans `billing.ts` (AC1)
  - [x] T1.1 Mettre à jour `frontend/src/api/billing.ts` avec les nouveaux types et l'export de `fetchEntitlementsSnapshot`

- [x] T2 — Créer `frontend/src/hooks/useEntitlementSnapshot.ts` (AC2, AC3, AC4, AC5)
  - [x] T2.1 Implémenter `useEntitlementsSnapshot` avec cache partagé
  - [x] T2.2 Implémenter les sélecteurs `useUpgradeHint` et `useFeatureAccess`
  - [x] T2.3 Déplacer `useEntitlementsSnapshot` depuis `billing.ts` vers le nouveau hook généraliste
  - [x] T2.4 Mettre à jour les imports dans `SubscriptionGuidePage.tsx`

- [x] T3 — Tests (AC6)
  - [x] T3.1 Créer `frontend/src/tests/useEntitlementSnapshot.test.tsx`
  - [x] T3.2 Valider le comportement des hooks avec Vitest

## Dev Agent Record

### File List
- `frontend/src/api/billing.ts`: Mise à jour des types et exposition de la fonction de fetch brute.
- `frontend/src/hooks/useEntitlementSnapshot.ts`: Nouveau hook centralisé pour les droits et hints d'upgrade.
- `frontend/src/pages/SubscriptionGuidePage.tsx`: Mise à jour des imports suite au déplacement du hook.
- `frontend/src/tests/useEntitlementSnapshot.test.tsx`: Tests unitaires du nouveau hook.

### Change Log
- Définition du contrat TypeScript pour les hints d'upgrade backend.
- Centralisation de l'accès aux droits effectifs via un hook unique et performant (cache Query).
- Isolation des sélecteurs de données pour simplifier la consommation dans les futurs composants UI (CTA upgrade).
- Correction des erreurs de type TypeScript (verbatimModuleSyntax) lors de la création du hook.
- Stabilisation post-intégration :
  - la clé de cache Query inclut désormais le sujet authentifié pour éviter les fuites de snapshot entre sessions/tests.
