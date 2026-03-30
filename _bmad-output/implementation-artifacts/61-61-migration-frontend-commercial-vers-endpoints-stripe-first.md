# Story 61.61 : Migrer le frontend commercial vers les endpoints Stripe-first

Status: done

## Story

En tant qu'utilisateur souscrivant ou modifiant un abonnement payant,
je veux que le frontend me redirige vers la page Stripe officielle (Checkout ou Customer Portal)
au lieu d'appeler des endpoints legacy qui activent mon plan de manière synchrone côté serveur,
afin que mon paiement soit traité directement par Stripe et que le plan commercial
soit piloté exclusivement par la réconciliation webhook canonique.

---

## Contexte

L'audit de l'epic 61 (2026-03-30) a identifié un finding **HIGH bloquant** :

Le frontend appelle encore trois endpoints legacy au lieu des endpoints Stripe-first
déjà opérationnels depuis la story 61.3 / 61.52 :

| Endpoint legacy (actif dans le front) | Ce qu'il fait de problématique |
|---|---|
| `POST /v1/billing/checkout` | Crée un `PaymentAttemptModel` + mute `UserSubscriptionModel.status = "active"` de manière synchrone |
| `POST /v1/billing/retry` | Idem — recrée une tentative locale sans passer par Stripe |
| `POST /v1/billing/plan-change` | Modifie `UserSubscriptionModel.plan_id` localement sans webhook |

Ces trois endpoints maintiennent **deux sources de vérité concurrentes** :
`UserSubscriptionModel` (local) vs `StripeBillingProfileModel` (canonique Stripe).

**Les endpoints Stripe-first déjà opérationnels à utiliser à la place :**

| Endpoint Stripe-first | Réponse | Rôle |
|---|---|---|
| `POST /v1/billing/stripe-checkout-session` | `{ data: { checkout_url: string } }` | Crée une session Checkout Stripe, renvoie l'URL Stripe |
| `POST /v1/billing/stripe-customer-portal-session` | `{ data: { url: string } }` | Crée une session Customer Portal Stripe pour gérer/modifier l'abonnement |

**Composants frontend concernés :**
- `frontend/src/api/billing.ts` (ligne 152–213) : fonctions `postCheckout`, `postRetry`, `postPlanChange` + hooks correspondants
- `frontend/src/pages/settings/SubscriptionSettings.tsx` : composant user-facing principal
- `frontend/src/components/BillingPanel.tsx` : panel admin/debug, utilise aussi les hooks legacy

**Ce qui NE doit PAS être modifié :**
- `BillingSuccessPage.tsx` — gère déjà le retour Stripe, fonctionne correctement
- `BillingCancelPage.tsx` — idem
- `GET /v1/billing/subscription` — déjà Stripe-first depuis story 61.58
- `GET /v1/entitlements/me` — déjà canonique depuis story 61.47
- Le backend Stripe déjà en place

**Clarification essentielle sur les codes de plan :**

- `POST /v1/billing/stripe-checkout-session` attend des codes canoniques Stripe-first: `basic` ou `premium`
- `SubscriptionSettings.tsx` et `BillingPanel.tsx` affichent encore aujourd'hui des codes/comparaisons legacy (`basic-entry`, `premium-unlimited`)
- La story DOIT donc inclure une normalisation frontend explicite vers les codes canoniques envoyés à Stripe, sinon l'implémentation échouera en 422

---

## Acceptance Criteria

**AC1 — Souscription initiale via Stripe Checkout Session**

- [ ] Quand un utilisateur sans abonnement actif choisit un plan et confirme dans `SubscriptionSettings.tsx`,
  le frontend appelle `POST /v1/billing/stripe-checkout-session` avec `{ plan: "basic" | "premium" }`.
- [ ] Le frontend redirige immédiatement vers `checkout_url` reçu dans la réponse (`window.location.href = checkout_url`).
- [ ] `postCheckout` legacy (`/v1/billing/checkout`) n'est plus appelé depuis `SubscriptionSettings.tsx`.
- [ ] Aucune mutation locale de statut côté frontend avant le retour Stripe.

**AC2 — Modification de plan et retry via Customer Portal**

- [ ] Quand un utilisateur avec abonnement actif sélectionne un autre plan dans `SubscriptionSettings.tsx`,
  le frontend appelle `POST /v1/billing/stripe-customer-portal-subscription-update-session` (sans corps de requête).
- [ ] Le frontend redirige vers `url` reçu dans la réponse.
- [ ] Quand un utilisateur a déjà un profil Stripe mais doit simplement gérer son moyen de paiement ou relancer une tentative,
  le frontend appelle `POST /v1/billing/stripe-customer-portal-session`.
- [ ] `postPlanChange` legacy (`/v1/billing/plan-change`) n'est plus appelé depuis `SubscriptionSettings.tsx`.
- [ ] `postRetry` legacy (`/v1/billing/retry`) n'est plus appelé depuis `SubscriptionSettings.tsx`.
- [ ] Le choix entre `subscription-update-session` et `portal-session` est explicite dans le code,
  basé sur l'intention utilisateur et sur l'état renvoyé par `GET /v1/billing/subscription`.

**AC3 — `BillingPanel.tsx` migré (panel admin/debug)**

- [ ] `BillingPanel.tsx` n'appelle plus `useCheckoutEntryPlan`, `useRetryPayment`, `useChangePlan` pour ses actions principales.
- [ ] Le panel affiche la souscription courante et un bouton "Ouvrir le portail Stripe" via `useStripePortalSession`.
- [ ] Pour les tests de checkout (uniquement admin), un bouton "Créer session checkout" via `useStripeCheckoutSession` peut rester visible si jugé utile.
- [ ] Les sélecteurs de `paymentToken` (`pm_card_ok`, `pm_fail`) peuvent être retirés car ils n'ont plus de sens avec Stripe réel.

**AC4 — Nouveaux types et hooks dans `billing.ts`**

- [ ] Ajouter le type :
  ```typescript
  export type StripeCheckoutSessionData = { checkout_url: string }
  export type StripePortalSessionData = { url: string }
  ```
- [ ] Ajouter la fonction `postStripeCheckoutSession(plan: "basic" | "premium"): Promise<StripeCheckoutSessionData>` appelant `POST /v1/billing/stripe-checkout-session`.
- [ ] Ajouter la fonction `postStripePortalSession(): Promise<StripePortalSessionData>` appelant `POST /v1/billing/stripe-customer-portal-session`.
- [ ] Ajouter la fonction `postStripePortalSubscriptionUpdateSession(): Promise<StripePortalSessionData>` appelant `POST /v1/billing/stripe-customer-portal-subscription-update-session`.
- [ ] Ajouter les hooks :
  ```typescript
  export function useStripeCheckoutSession(): UseMutationResult<StripeCheckoutSessionData, BillingApiError, "basic" | "premium">
  export function useStripePortalSession(): UseMutationResult<StripePortalSessionData, BillingApiError, void>
  export function useStripePortalSubscriptionUpdateSession(): UseMutationResult<StripePortalSessionData, BillingApiError, void>
  ```
- [ ] Les anciens hooks `useCheckoutEntryPlan`, `useRetryPayment`, `useChangePlan` peuvent rester exportés pour ne pas casser d'autres usages potentiels, mais ne doivent plus être le chemin actif dans les composants user-facing.

**AC4bis — Normalisation stricte des codes de plan côté frontend**

- [ ] Le frontend introduit une fonction centrale de mapping du catalogue UI vers les codes canoniques Stripe:
  `basic-entry -> basic`, `premium-unlimited -> premium`, `null -> null`.
- [ ] Aucun composant user-facing n'envoie `basic-entry` ou `premium-unlimited` à `POST /v1/billing/stripe-checkout-session`.
- [ ] Les comparaisons d'état local peuvent continuer à supporter temporairement les deux familles de codes si nécessaire,
  mais le chemin Stripe-first émet uniquement des codes canoniques.

**AC5 — UX de redirection claire**

- [ ] Pendant le `isPending` de la mutation Stripe, les boutons sont désactivés avec un état de chargement visible.
- [ ] En cas d'erreur de l'API Stripe (502, 503), un message d'erreur utilisateur est affiché (pas de redirection).
- [ ] Le cas spécifique d'erreur `stripe_billing_profile_not_found` (404 sur le portal) est traité : l'utilisateur est invité à contacter le support ou à créer un abonnement d'abord.
- [ ] Le cas spécifique d'erreur `stripe_subscription_not_found` (404 sur `subscription-update-session`) est traité :
  l'utilisateur est redirigé vers le portal générique ou reçoit un message l'invitant à rouvrir son espace billing.

**AC6 — Tests mis à jour**

- [ ] `frontend/src/tests/BillingPanel.test.tsx` : mocke les nouveaux hooks Stripe et non plus les hooks legacy.
- [ ] Ajouter un test vérifiant que `SubscriptionSettings.tsx` appelle `useStripeCheckoutSession` pour un utilisateur sans plan.
- [ ] Ajouter un test vérifiant que `SubscriptionSettings.tsx` appelle `useStripePortalSubscriptionUpdateSession` pour un utilisateur avec plan actif qui change de plan.
- [ ] Ajouter un test vérifiant que `SubscriptionSettings.tsx` n'envoie jamais `basic-entry` ou `premium-unlimited` au hook checkout Stripe, mais bien `basic` ou `premium`.
- [ ] Les tests ne doivent pas tester `window.location.href` directement (impossible dans jsdom) mais vérifier que la mutation est appelée avec les bons arguments.

**AC7 — Aucune régression fonctionnelle**

- [ ] `BillingSuccessPage.tsx` n'est pas modifié.
- [ ] `GET /v1/billing/subscription` n'est pas modifié.
- [ ] Aucun endpoint backend n'est modifié ou supprimé.
- [ ] `useBillingSubscription` et `useChatEntitlementUsage` continuent de fonctionner.

---

## Tasks / Subtasks

- [x] **Étendre `frontend/src/api/billing.ts` avec les fonctions et hooks Stripe-first** (AC: 4)
  - [x] Ajouter les types `StripeCheckoutSessionData` et `StripePortalSessionData`
  - [x] Implémenter `postStripeCheckoutSession(plan: "basic" | "premium")` → `POST /v1/billing/stripe-checkout-session`
  - [x] Implémenter `postStripePortalSession()` → `POST /v1/billing/stripe-customer-portal-session`
  - [x] Implémenter `postStripePortalSubscriptionUpdateSession()` → `POST /v1/billing/stripe-customer-portal-subscription-update-session`
  - [x] Ajouter un helper central de normalisation des codes de plan UI -> Stripe canonique
  - [x] Exporter `useStripeCheckoutSession()`, `useStripePortalSession()` et `useStripePortalSubscriptionUpdateSession()`

- [x] **Migrer `SubscriptionSettings.tsx`** (AC: 1, 2, 5)
  - [x] Remplacer `useCheckoutEntryPlan` + `useChangePlan` par les nouveaux hooks Stripe
  - [x] Implémenter la logique de redirection : `window.location.href = checkout_url` / `url`
  - [x] Utiliser le mapping central vers `basic` / `premium` avant l'appel checkout Stripe
  - [x] Utiliser `useStripePortalSubscriptionUpdateSession` pour un changement de plan actif
  - [x] Utiliser `useStripePortalSession` pour la gestion générique du billing / retry paiement
  - [x] Gérer l'état loading et les cas d'erreur
  - [x] Retirer la dépendance à `useQueryClient().invalidateQueries` post-mutation
    (la réconciliation se fait via webhook, pas besoin d'invalider le cache immédiatement)

- [x] **Migrer `BillingPanel.tsx`** (AC: 3)
  - [x] Remplacer les hooks legacy par `useStripeCheckoutSession` et `useStripePortalSession`
  - [x] Retirer le sélecteur `paymentToken`
  - [x] Adapter l'UI admin pour refléter le nouveau flux de redirection

- [x] **Mettre à jour les tests** (AC: 6)
  - [x] Mettre à jour `frontend/src/tests/BillingPanel.test.tsx`
  - [x] Ajouter des tests pour `SubscriptionSettings.tsx` si le fichier de test existe,
    sinon créer `frontend/src/tests/SubscriptionSettings.test.tsx`

---

## Dev Notes

### Architecture du nouveau flux

```
Utilisateur clique "Valider"
        │
        ▼
[Appel API backend]
POST /v1/billing/stripe-checkout-session  ← nouveau abonnement
POST /v1/billing/stripe-customer-portal-subscription-update-session  ← changement de plan actif
POST /v1/billing/stripe-customer-portal-session  ← gestion/réessai paiement
        │
        ▼ { checkout_url | url }
window.location.href = url  ← redirection vers Stripe
        │
        ▼ (l'utilisateur paie sur Stripe)
Stripe → webhook → backend réconcilie stripe_billing_profiles
        │
        ▼
Utilisateur redirigé vers BillingSuccessPage
(déjà implémenté en story 61.59)
```

### Contrat des nouveaux endpoints

**POST `/v1/billing/stripe-checkout-session`**
```
Requête : { "plan": "basic" }  // ou "premium"
Réponse OK : { "data": { "checkout_url": "https://checkout.stripe.com/..." }, "meta": {...} }
Erreurs : 401, 403, 422 (plan invalide), 502 (Stripe API error), 503 (Stripe unavailable)
```

**POST `/v1/billing/stripe-customer-portal-session`**
```
Requête : (aucun corps)
Réponse OK : { "data": { "url": "https://billing.stripe.com/..." }, "meta": {...} }
Erreurs : 401, 403, 404 (stripe_billing_profile_not_found — pas encore de profil Stripe), 502, 503
```

**POST `/v1/billing/stripe-customer-portal-subscription-update-session`**
```
Requête : (aucun corps)
Réponse OK : { "data": { "url": "https://billing.stripe.com/..." }, "meta": {...} }
Erreurs : 401, 403, 404 (stripe_subscription_not_found), 502, 503
```

### Cas 404 sur le portal

L'endpoint portal retourne 404 avec code `stripe_billing_profile_not_found` si l'utilisateur
n'a pas encore de profil Stripe (pas d'abonnement Stripe créé). Dans ce cas,
l'interface doit diriger l'utilisateur vers le checkout (pas le portal).

L'endpoint `subscription-update-session` retourne 404 avec code `stripe_subscription_not_found`
si le profil Stripe existe mais qu'aucune subscription exploitable n'est rattachée. Dans ce cas,
l'interface doit retomber vers le portal générique, pas vers l'ancien `/plan-change`.

Règle UX :
- Pas d'abonnement Stripe exploitable (`status !== "active"` ou `subscription_status` absent) → Checkout Session
- Abonnement Stripe exploitable + intention "changer de plan" → Subscription Update Session
- Abonnement Stripe exploitable + intention "gérer/régler un problème de paiement" → Customer Portal générique

La logique actuelle de `SubscriptionSettings.tsx` doit être remplacée par une variante Stripe-first explicite :
```typescript
if (!currentPlanCode || subscription?.status !== "active") {
  // → useStripeCheckoutSession(toStripePlanCode(selectedPlanCode))
} else if (intent === "change-plan") {
  // → useStripePortalSubscriptionUpdateSession()
} else {
  // → useStripePortalSession()
}
```

### Pattern d'implémentation `postStripeCheckoutSession`

```typescript
// À ajouter dans billing.ts
export type StripeCheckoutSessionData = { checkout_url: string }

async function postStripeCheckoutSession(plan: "basic" | "premium"): Promise<StripeCheckoutSessionData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-checkout-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify({ plan }),
  })
  if (!response.ok) {
    return parseError(response)  // réutiliser la fonction existante
  }
  const body = (await response.json()) as { data: StripeCheckoutSessionData }
  return body.data
}

export function useStripeCheckoutSession() {
  return useMutation({
    mutationFn: postStripeCheckoutSession,
  })
}
```

### Pattern d'implémentation `postStripePortalSession`

```typescript
export type StripePortalSessionData = { url: string }

async function postStripePortalSession(): Promise<StripePortalSessionData> {
  const response = await fetch(`${API_BASE_URL}/v1/billing/stripe-customer-portal-session`, {
    method: "POST",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as { data: StripePortalSessionData }
  return body.data
}

export function useStripePortalSession() {
  return useMutation({
    mutationFn: postStripePortalSession,
  })
}
```

### Gestion de la redirection

La redirection doit se faire dans le `onSuccess` de la mutation, pas dans la fonction API :

```typescript
// Dans SubscriptionSettings.tsx
const checkoutSession = useStripeCheckoutSession()
const portalSession = useStripePortalSession()
const portalUpdateSession = useStripePortalSubscriptionUpdateSession()

const handleValidate = () => {
  if (!selectedPlanCode) return
  if (subscription?.status !== "active") {
    checkoutSession.mutate(toStripePlanCode(selectedPlanCode), {
      onSuccess: (data) => {
        window.location.href = data.checkout_url
      },
      onError: (err) => {
        // afficher l'erreur
      },
    })
  } else {
    portalUpdateSession.mutate(undefined, {
      onSuccess: (data) => {
        window.location.href = data.url
      },
      onError: (err) => {
        // afficher l'erreur
      },
    })
  }
}
```

### Invalidation de cache après retour

Ne pas invalider `billing-subscription` dans le `onSuccess` de la mutation Stripe
(l'utilisateur quitte la page pour aller sur Stripe — il n'y a pas de "retour synchrone").
L'invalidation de cache se fait automatiquement si l'utilisateur revient sur `BillingSuccessPage.tsx`,
qui appelle `useBillingSubscription()` et dispose d'un bouton retry.

### Ce qui NE change PAS

- La logique de display des plans dans `SubscriptionSettings.tsx` (grille de plans, sélection, état `isCurrent`, etc.)
- La structure CSS — pas d'inline styles à introduire, tout est dans `Settings.css`
- Le composant `BillingSuccessPage.tsx` — déjà branché sur le retour Stripe
- L'endpoint `GET /v1/billing/subscription` et le hook `useBillingSubscription`
- Le hook `useChatEntitlementUsage`

### Fichiers probablement concernés

- `frontend/src/api/billing.ts`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/components/BillingPanel.tsx`
- `frontend/src/tests/BillingPanel.test.tsx`
- `frontend/src/tests/SubscriptionSettings.test.tsx` (à créer si inexistant)

### Commandes de test

```bash
npm test -- --run src/tests/BillingPanel.test.tsx
npm test -- --run src/tests/SubscriptionSettings.test.tsx
```

### Contexte de style

Ce projet utilise un système de CSS custom (pas Tailwind). Voir [Project CSS Notes](#project-css).
- Toute nouvelle classe CSS → dans `frontend/src/pages/settings/Settings.css` ou `App.css`
- Aucun style inline — utiliser les classes existantes
- Variables CSS disponibles : `var(--primary)`, `var(--danger)`, `var(--success)`, `var(--text-1)`, `var(--glass)`, etc.

### References

- [Source: `frontend/src/api/billing.ts`] — fonctions et hooks à migrer
- [Source: `frontend/src/pages/settings/SubscriptionSettings.tsx`] — composant user-facing principal
- [Source: `frontend/src/components/BillingPanel.tsx`] — panel admin
- [Source: `backend/app/api/v1/routers/billing.py#L882`] — endpoint `stripe-checkout-session`
- [Source: `backend/app/api/v1/routers/billing.py#L1021`] — endpoint `stripe-customer-portal-session`
- [Source: `backend/app/api/v1/routers/billing.py#L1113`] — endpoint `stripe-customer-portal-subscription-update-session`
- [Source: `_bmad-output/implementation-artifacts/61-59-ux-retour-billing-etats-erreur-empty-et-retry.md`] — BillingSuccessPage déjà implémentée
- [Source: `_bmad-output/implementation-artifacts/61-58-reconciliation-runtime-b2c-plan-commercial-snapshot-stripe-canonique.md`] — runtime Stripe-first branché
- [Source: `docs/billing-self-service-mvp.md`] — contrat billing MVP

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

(aucun blocage)

### Completion Notes List

- `billing.ts` : ajout de `StripeCheckoutSessionData`, `StripePortalSessionData`, `toStripePlanCode()`, `postStripeCheckoutSession`, `postStripePortalSession`, `postStripePortalSubscriptionUpdateSession`, `useStripeCheckoutSession`, `useStripePortalSession`, `useStripePortalSubscriptionUpdateSession`. Les anciens hooks (`useCheckoutEntryPlan`, `useRetryPayment`, `useChangePlan`) sont conservés exportés pour compatibilité mais ne sont plus le chemin actif.
- `SubscriptionSettings.tsx` : migré entièrement vers les endpoints Stripe-first. Suppression de `useQueryClient`/`invalidateQueries` (réconciliation via webhook). Gestion des codes d'erreur `stripe_billing_profile_not_found` et `stripe_subscription_not_found`. Affichage d'un message d'erreur utilisateur au lieu d'un `alert()`.
- `BillingPanel.tsx` : simplifié — utilise `useStripeCheckoutSession` (checkout basic) et `useStripePortalSession` (portail). Suppression de `paymentToken`, `useRetryPayment`, `useChangePlan`, `useCheckoutEntryPlan`.
- `admin.ts` i18n : ajout des clés `openPortal`, `openCheckout`, `errorPortal` pour les 3 langues (fr, en, es).
- Tests : `BillingPanel.test.tsx` entièrement réécrit pour les nouveaux hooks. `SubscriptionSettings.test.tsx` créé avec 3 tests (checkout sans plan, codes canoniques, portal update avec plan actif). 1101 tests passent, 0 régression.

### File List

- `frontend/src/api/billing.ts`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/components/BillingPanel.tsx`
- `frontend/src/i18n/admin.ts`
- `frontend/src/tests/BillingPanel.test.tsx`
- `frontend/src/tests/SubscriptionSettings.test.tsx` (créé)

### Change Log

- 2026-03-30 : Implémentation story 61-61 — migration frontend vers endpoints Stripe-first (`stripe-checkout-session`, `stripe-customer-portal-session`, `stripe-customer-portal-subscription-update-session`). Suppression des appels legacy `checkout`, `retry`, `plan-change` des composants user-facing. 6 nouveaux tests, 0 régression sur 1101 tests.
