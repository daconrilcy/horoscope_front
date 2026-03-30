# Story 61.58 : Réconcilier le runtime B2C et le plan commercial sur le snapshot Stripe canonique

Status: done

## Story

En tant que responsable produit et technique,
je veux que le runtime B2C, les entitlements effectifs et le contrat `GET /v1/billing/subscription`
soient réellement pilotés par le snapshot Stripe canonique réconcilié par webhook,
afin que le plan commercial, les accès produit et l'UX billing reflètent le vrai statut Stripe
sans dépendre du legacy `UserSubscriptionModel`.

---

## Contexte

La review complète de l'epic 61 a mis en évidence un défaut structurel bloquant :

- `StripeBillingProfileService.update_from_event_payload()` met bien à jour `stripe_billing_profiles`
  avec `subscription_status`, `stripe_price_id` et `entitlement_plan`.
- Mais `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot()` continue de dériver
  `plan_code` et `billing_status` depuis `BillingService.get_subscription_status_readonly()`,
  lui-même fondé sur `UserSubscriptionModel` legacy.
- Résultat : un utilisateur peut avoir un snapshot Stripe `active/basic` ou `trialing/basic`
  correctement réconcilié, tout en restant exposé côté runtime comme `inactive` / `plan=None`
  si aucun abonnement legacy local n'existe.

Preuve fonctionnelle reproduite pendant la review :

```python
{
  "status": "inactive",
  "subscription_status": "active",
  "plan": None,
  "failure_reason": None,
  "updated_at": None,
}
```

pour un utilisateur ne portant qu'un `StripeBillingProfileModel(active/basic)` sans `UserSubscriptionModel`.

Ce bug invalide la promesse des stories 61.47 à 61.55 :
- webhook Stripe comme source de vérité,
- contrat frontend unique du plan commercial,
- validation end-to-end du plan commercial,
- self-service billing via Customer Portal.

Cette story corrige la cohérence métier réelle.

---

## Acceptance Criteria

**AC1 — Le runtime B2C devient Stripe-first quand un snapshot Stripe existe**

- [x] `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot()` ne dérive plus `plan_code`
  et `billing_status` depuis le seul `UserSubscriptionModel` quand un `StripeBillingProfileModel`
  existe pour l'utilisateur.
- [x] Le resolver utilise en priorité un snapshot canonique issu de `stripe_billing_profiles` :
  - `plan_code` dérivé de `entitlement_plan`
  - `billing_status` dérivé du vrai `subscription_status` Stripe
- [x] Le fallback legacy reste autorisé uniquement si aucun profil Stripe exploitable n'existe.
- [x] Aucun impact régressif sur le scope B2B.

**AC2 — `GET /v1/billing/subscription` reflète le vrai état billing canonique**

- [x] Un utilisateur avec un profil Stripe `subscription_status="active"` et
  `entitlement_plan="basic"` est exposé avec :
  - `status="active"`
  - `subscription_status="active"`
  - `plan.code="basic"`
- [x] Un utilisateur `trialing` est exposé comme `status="active"` avec
  `subscription_status="trialing"`.
- [x] Un utilisateur `incomplete`, `paused`, `canceled` ou `unpaid` n'est jamais exposé comme
  `status="active"`.
- [x] Si le snapshot Stripe est exploitable, le contrat ne retombe pas silencieusement sur
  `plan=None` à cause de l'absence d'abonnement legacy local.

**AC3 — Le mapping métier `subscription_status Stripe -> accès produit` est réellement branché**

- [x] Les entitlements B2C exposés par `GET /v1/entitlements/me` utilisent le plan et le statut
  réellement dérivés du snapshot Stripe canonique.
- [x] `trialing` ouvre l'accès selon le plan mappé.
- [x] `active` ouvre l'accès selon le plan mappé.
- [x] `incomplete`, `incomplete_expired`, `paused`, `canceled`, `unpaid` refusent l'accès payant.
- [x] `past_due` conserve l'accès selon la politique existante.

**AC4 — L'invalidation de cache est cohérente avec les webhooks Stripe**

- [x] Toute mise à jour de `stripe_billing_profiles` via `update_from_event_payload()` invalide
  le cache utilisé par `BillingService` pour l'utilisateur concerné.
- [x] Après traitement d'un webhook Stripe pertinent, un appel suivant à
  `GET /v1/billing/subscription` ou `GET /v1/entitlements/me` ne peut pas servir un statut
  périmé uniquement à cause de la TTL du cache.

**AC5 — Les tests prouvent le branchement réel et ne mockent plus le point critique**

- [x] Ajouter un test d'intégration démontrant qu'un `StripeBillingProfileModel(active/basic)`
  sans `UserSubscriptionModel` legacy donne bien un contrat billing cohérent.
- [x] Ajouter un test d'intégration démontrant qu'un profil Stripe `trialing` ouvre réellement
  l'accès produit via `GET /v1/entitlements/me`.
- [x] Ajouter un test d'intégration démontrant qu'un profil Stripe `incomplete` n'ouvre pas
  l'accès payant.
- [x] Ajouter un test d'intégration démontrant qu'un webhook mettant à jour le profil Stripe
  rend immédiatement visible le nouvel état malgré le cache.
- [x] Les tests d'entitlements ne se contentent plus uniquement de monkeypatcher
  `BillingService.get_subscription_status_readonly()` pour couvrir ce parcours.

**AC6 — Documentation de référence réalignée**

- [x] `docs/billing-self-service-mvp.md` est mis à jour pour décrire correctement que
  le webhook Stripe met à jour le snapshot canonique effectivement utilisé par le runtime.
- [x] `docs/billing-trials-and-first-payment.md` est aligné avec le nouveau branchement runtime
  réel.

---

## Tasks / Subtasks

- [x] **Introduire une lecture canonique Stripe-first du statut billing B2C** (AC: 1, 2, 3)
  - [x] Identifier le point d'assemblage le plus sûr :
    - étendre `BillingService`, ou
    - créer un petit adapter/service dédié au snapshot billing canonique B2C
  - [x] Faire dériver `plan_code` depuis `StripeBillingProfileModel.entitlement_plan`
    quand un profil Stripe exploitable existe
  - [x] Faire dériver `billing_status` depuis le vrai `subscription_status` Stripe
  - [x] Préserver un fallback legacy explicite seulement en absence de profil Stripe exploitable

- [x] **Corriger le contrat `GET /v1/billing/subscription`** (AC: 2)
  - [x] Aligner `SubscriptionStatusData` sur le snapshot canonique B2C
  - [x] Ne plus dépendre du seul `UserSubscriptionModel` pour le plan exposé
  - [x] Garder un contrat stable pour le frontend (`status`, `subscription_status`, `plan`,
    `failure_reason`, `updated_at`)

- [x] **Brancher réellement le resolver d'entitlements sur le snapshot canonique** (AC: 1, 3)
  - [x] Mettre à jour `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot()`
  - [x] Vérifier l'absence de régression sur les features B2C existantes
  - [x] Ne rien changer au resolver B2B

- [x] **Invalider le cache billing sur la voie webhook** (AC: 4)
  - [x] Ajouter un point d'invalidation de cache lors des mises à jour Stripe canoniques
  - [x] Vérifier aussi le comportement lors des replays webhook idempotents

- [x] **Créer les tests d'intégration manquants** (AC: 5)
  - [x] Étendre `backend/app/tests/integration/test_billing_api.py`
  - [x] Étendre `backend/app/tests/integration/test_entitlements_me.py`
  - [x] Étendre `backend/app/tests/integration/test_stripe_webhook_api.py`
  - [x] Ajouter si nécessaire un test unitaire ciblé sur l'adapter/service canonique introduit

- [x] **Mettre à jour la documentation métier** (AC: 6)
  - [x] Corriger `docs/billing-self-service-mvp.md`
  - [x] Corriger `docs/billing-trials-and-first-payment.md`

---

## Dev Notes

### Défaut actuel à corriger

Le problème n'est pas le webhook lui-même. Le problème est le branchement runtime :

- `backend/app/services/stripe_billing_profile_service.py`
  - persiste `subscription_status` et `entitlement_plan`
- `backend/app/services/billing_service.py`
  - construit encore le contrat depuis `UserSubscriptionModel`
- `backend/app/services/effective_entitlement_resolver_service.py`
  - lit `sub.plan.code` et `sub.status`

Il faut donc corriger la couche de lecture, pas réécrire le webhook.

### Décision d'architecture attendue

Pour le scope B2C, la source de vérité de lecture doit devenir :

1. `stripe_billing_profiles` si un snapshot Stripe exploitable existe
2. fallback legacy uniquement sinon

Le comportement attendu par statut Stripe :

| `subscription_status` | `status` exposé | `plan_code` exposé | accès produit |
|---|---|---|---|
| `trialing` | `active` | plan mappé | ouvert |
| `active` | `active` | plan mappé | ouvert |
| `past_due` | `inactive` ou statut équivalent non-payé selon contrat choisi, mais avec conservation d'accès produit via politique canonique existante | plan courant | conservé selon politique existante |
| `incomplete` | `inactive` | `free` ou absence de plan payant exposé | refusé |
| `incomplete_expired` | `inactive` | `free` | refusé |
| `paused` | `inactive` | `free` | refusé |
| `canceled` | `inactive` | `free` | refusé |
| `unpaid` | `inactive` | `free` | refusé |

### Contraintes importantes

- Ne pas supprimer `UserSubscriptionModel` dans cette story.
- Ne pas casser les endpoints legacy `/v1/billing/checkout`, `/v1/billing/retry`, `/v1/billing/plan-change`.
- Ne pas réintroduire de booléen simpliste `is_paid`.
- Ne pas utiliser le frontend comme source de vérité.
- Ne pas muter le runtime depuis les endpoints portail ; le webhook reste la voie de réconciliation.

### Fichiers probablement concernés

- `backend/app/services/billing_service.py`
- `backend/app/services/effective_entitlement_resolver_service.py`
- `backend/app/services/stripe_billing_profile_service.py`
- `backend/app/api/v1/routers/billing.py`
- `backend/app/tests/integration/test_billing_api.py`
- `backend/app/tests/integration/test_entitlements_me.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `docs/billing-self-service-mvp.md`
- `docs/billing-trials-and-first-payment.md`

### Tests attendus

- `pytest -q app/tests/integration/test_billing_api.py`
- `pytest -q app/tests/integration/test_entitlements_me.py`
- `pytest -q app/tests/integration/test_stripe_webhook_api.py`
- Ajouter tout test unitaire utile sur le nouvel adapter/service

### References

- [Source: `backend/app/services/effective_entitlement_resolver_service.py`] — branchement runtime actuel
- [Source: `backend/app/services/billing_service.py`] — contrat billing actuel et cache
- [Source: `backend/app/services/stripe_billing_profile_service.py`] — snapshot Stripe canonique
- [Source: `backend/app/api/v1/routers/entitlements.py`] — exposition du snapshot effectif au frontend
- [Source: `docs/billing-self-service-mvp.md`] — doc actuellement trop optimiste sur la réconciliation runtime
- [Source: `docs/billing-trials-and-first-payment.md`] — mapping métier annoncé

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- Story créée à partir de la review complète Epic 61 workspace actuel.
- Implémentation Story 61.58 : Stripe-first runtime, mapping canonique, cache webhook.
- Validations exécutées dans le venv :
  - `ruff check ...`
  - `pytest -q app/tests/integration/test_billing_api.py app/tests/integration/test_entitlements_me.py app/tests/integration/test_stripe_webhook_api.py app/tests/unit/test_billing_service.py app/tests/unit/test_effective_entitlement_resolver_service.py`
  - `pytest -q`

### Completion Notes List

- Runtime B2C branché sur un snapshot Stripe exploitable même sans `UserSubscriptionModel` legacy ni `stripe_subscription_id`.
- `BillingService` expose désormais un contrat Stripe-first cohérent pour `trialing`, `active`, `incomplete`, `paused`, `canceled`, `unpaid` et conserve le plan courant en `past_due`.
- `EffectiveEntitlementResolverService` dérive `plan_code` runtime depuis le mapping canonique Stripe et conserve `past_due` comme accès produit autorisé selon la politique existante.
- Ajout d'un fallback DTO déterministe sur les plans par défaut pour éviter un `plan=None` en lecture seule si le `BillingPlanModel` n'est pas encore seedé.
- Ajout de tests d'intégration prouvant le branchement réel billing, entitlements et webhook cache invalidation, plus alignement des tests de régression existants.
- Documentation billing Stripe réalignée sur la lecture runtime réelle.
- Correctif de stabilisation post-implémentation : un `checkout.session.completed` plus récent n'empêche plus les événements `customer.subscription.*` du même flow d'enrichir le snapshot Stripe local quand le profil n'a pas encore de `subscription_status`.
- Validation locale réelle via Stripe Checkout + Stripe CLI confirmée : la réconciliation webhook alimente désormais correctement `stripe_subscription_id`, `stripe_price_id`, `subscription_status` et `entitlement_plan` après paiement sandbox.

### File List

- `_bmad-output/implementation-artifacts/61-58-reconciliation-runtime-b2c-plan-commercial-snapshot-stripe-canonique.md`
- `backend/app/services/billing_service.py`
- `backend/app/services/effective_entitlement_resolver_service.py`
- `backend/app/services/stripe_billing_profile_service.py`
- `backend/app/tests/integration/test_billing_api.py`
- `backend/app/tests/integration/test_entitlements_me.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `backend/app/tests/integration/test_entitlements_e2e_matrix.py`
- `backend/app/tests/integration/test_support_api.py`
- `backend/app/tests/unit/test_billing_service.py`
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py`
- `backend/app/tests/test_story_61_58_full.py`
- `docs/billing-self-service-mvp.md`
- `docs/billing-trials-and-first-payment.md`

### Change Log

- 2026-03-30 : Implémentation complète de la story 61.58 avec lecture Stripe-first du billing B2C, mapping runtime canonique des entitlements, invalidation de cache sur webhooks Stripe et couverture de tests de régression étendue.
- 2026-03-30 : Stabilisation post-QA locale du flux Stripe réel pour tolérer l'ordre effectif des événements `checkout.session.completed` puis `customer.subscription.*` observé via Stripe CLI.
