# Story 61.59 : UX de retour billing — états erreur, empty et retry explicites

Status: ready-for-dev

## Story

En tant qu'utilisateur revenant d'un checkout ou du portail Stripe,
je veux que la page de retour billing distingue clairement l'attente de réconciliation,
l'erreur API et l'absence temporaire d'état exploitable,
afin de ne jamais confondre un incident backend avec un simple délai webhook.

---

## Contexte

La review de l'epic 61 a montré que `BillingSuccessPage.tsx` ne traite aujourd'hui que :

- `isLoading`
- `subscription_status === "trialing"`
- `subscription_status === "active"`
- `subscription_status === "incomplete"`
- sinon : fallback vers "waiting for webhook"

Or `useBillingSubscription()` propage une `BillingApiError` sur toute réponse non-200.
La page ignore ce signal et transforme donc des cas comme `401`, `403`, `500` ou `503`
en faux état "Paiement en cours de confirmation...".

Cette story ne change pas la source de vérité. Elle corrige la robustesse UX du retour billing.

---

## Acceptance Criteria

**AC1 — Les états loading, error et empty sont distincts**

- [ ] La page distingue explicitement :
  - `loading`
  - `error`
  - `empty/pending`
  - `success trialing`
  - `success active`
  - `activation pending/incomplete`
- [ ] Un échec API n'est jamais rendu comme une attente webhook.

**AC2 — L'état d'erreur est actionnable**

- [ ] Si `GET /v1/billing/subscription` échoue, l'UI affiche un message explicite de vérification
  impossible de l'état billing.
- [ ] L'utilisateur dispose d'une action claire pour réessayer la récupération du statut.
- [ ] Les CTA de navigation restent disponibles (`dashboard`, `subscription settings`).

**AC3 — L'état empty/pending reste neutre**

- [ ] Si la requête réussit mais que le statut retourné ne permet pas encore de conclure
  (`null`, absence de `subscription_status`, autre statut non mappé), l'UI reste sur un wording
  neutre d'attente de réconciliation.
- [ ] L'UI ne prétend jamais qu'un paiement est réussi sans confirmation backend explicite.

**AC4 — Aucun style inline et aucun contournement URL**

- [ ] Tous les ajustements de rendu passent par `billing-return.css`.
- [ ] L'UI ne dépend pas d'un flag URL du type `is_trial`.
- [ ] Le `session_id` reste purement informatif.

**AC5 — Tests frontend complets**

- [ ] Ajouter les tests couvrant :
  - erreur API
  - état empty/pending après réponse 200
  - retry manuel
  - non-régression des cas `trialing`, `active`, `incomplete`
- [ ] Le test existant garantissant que `is_trial` dans l'URL est ignoré reste vert.

---

## Tasks / Subtasks

- [ ] **Étendre le composant `BillingSuccessPage`** (AC: 1, 2, 3, 4)
  - [ ] Lire explicitement `error`, `isError` et `refetch` depuis `useBillingSubscription()`
  - [ ] Introduire un état d'erreur explicite
  - [ ] Introduire un état empty/pending explicite
  - [ ] Préserver les cas `trialing`, `active`, `incomplete`

- [ ] **Étendre les traductions billing** (AC: 1, 2, 3)
  - [ ] Ajouter les clés nécessaires dans `frontend/src/i18n/billing.ts`
  - [ ] Conserver un wording neutre et non trompeur

- [ ] **Ajuster le style CSS dédié** (AC: 4)
  - [ ] Ajouter si nécessaire les classes de variation dans `frontend/src/pages/billing/billing-return.css`
  - [ ] Réutiliser les variables CSS existantes

- [ ] **Créer/mettre à jour les tests frontend** (AC: 5)
  - [ ] Étendre `frontend/src/tests/BillingSuccessPage.test.tsx`
  - [ ] Vérifier le retry manuel via le `refetch` mocké

---

## Dev Notes

### Défaut actuel

Aujourd'hui :

- `frontend/src/api/billing.ts` lève une `BillingApiError` en cas de réponse non-OK
- `BillingSuccessPage.tsx` ignore `error` / `isError`
- le fallback final réutilise le message `waitingForWebhook`

La correction attendue est purement UX/comportement frontend.

### Mapping UI attendu

| Situation | UI attendue |
|---|---|
| `isLoading=true` | attente de réconciliation |
| `isError=true` | erreur explicite + action retry |
| `subscription_status="trialing"` | essai démarré |
| `subscription_status="active"` | abonnement activé |
| `subscription_status="incomplete"` | activation en attente |
| `subscription_status` vide / inconnu | attente neutre |

### Contraintes

- Ne pas introduire de polling agressif dans cette story.
- Ne pas modifier le contrat API backend.
- Ne pas réécrire le hook `useBillingSubscription()` si un simple usage correct du hook suffit.
- Respecter `AGENTS.md` : aucun style inline.

### Fichiers probablement concernés

- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/billing-return.css`
- `frontend/src/i18n/billing.ts`
- `frontend/src/tests/BillingSuccessPage.test.tsx`

### Tests attendus

- `npm test -- --run src/tests/BillingSuccessPage.test.tsx`

### References

- [Source: `frontend/src/pages/billing/BillingSuccessPage.tsx`] — composant actuel
- [Source: `frontend/src/api/billing.ts`] — propagation de `BillingApiError`
- [Source: `frontend/src/i18n/billing.ts`] — wording billing existant

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- Story créée à partir de la review complète Epic 61 workspace actuel.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `_bmad-output/implementation-artifacts/61-59-ux-retour-billing-etats-erreur-empty-et-retry.md`

