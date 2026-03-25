# Story 61.6 : Sélection canonique des événements Stripe webhook pour SaaS abonnement

Status: done

## Contexte dans l'Epic 61

```text
61-1 (done) : table DB + StripeBillingProfileService + derive_entitlement_plan()
61-2 (done) : SDK stripe==14.4.1 + get_stripe_client() + secrets + STRIPE_PRICE_ENTITLEMENT_MAP
61-3 (done) : POST /v1/billing/stripe-checkout-session
61-4 (done) : socle webhook Stripe signé + dispatch checkout/subscription.* + pages retour navigateur
61-5 (done) : extension aux événements invoice.payment_succeeded + invoice.payment_failed + doc dev/prod
61-6 (cette story) : audit et sélection canonique des événements — remplacement invoice.payment_succeeded
                     par invoice.paid + ajout invoice.payment_action_required + documentation rationale
```

**Pré-requis critique** : lire 61-4 et 61-5 avant toute modification.
Cette story **ne recrée pas** le webhook Stripe.
Le endpoint signé, la vérification de signature et le dispatch existent déjà dans `StripeWebhookService`.

## Story

En tant que système backend,
je veux remplacer `invoice.payment_succeeded` par `invoice.paid` dans le webhook Stripe et ajouter `invoice.payment_action_required`,
afin que la sélection des événements webhook reflète la stratégie recommandée par Stripe pour le suivi d'un abonnement SaaS : réconciliation via Checkout, état d'abonnement via `customer.subscription.*`, et événements de facturation via `invoice.*`, avec une documentation expliquant explicitement les choix et les exclusions.

## Acceptance Criteria

### Backend — Remplacement `invoice.payment_succeeded` → `invoice.paid`

1. `invoice.payment_succeeded` est **retiré** du tuple de dispatch dans `handle_event()` et de `_resolve_user_id()`.
2. `invoice.paid` est **ajouté** au tuple de dispatch et à `_resolve_user_id()` avec la même logique de résolution que l'ancien `invoice.payment_succeeded` (champ `customer` de l'objet invoice).
3. La logique `update_from_event_payload` est appelée pour `invoice.paid` avec l'événement Stripe sérialisé complet — le comportement est identique à l'ancien `invoice.payment_succeeded`.

### Backend — Ajout `invoice.payment_action_required`

4. `invoice.payment_action_required` est **ajouté** au tuple de dispatch dans `handle_event()`.
5. `_resolve_user_id()` résout le `user_id` pour `invoice.payment_action_required` via `customer_id = event.data.object.customer` → lookup `StripeBillingProfileService.get_by_stripe_customer_id()`.
6. `update_from_event_payload` est appelé pour `invoice.payment_action_required` — l'événement est enregistré dans `last_stripe_event_type` et les champs d'idempotence sont mis à jour.

### Tests unitaires

7. `backend/app/tests/unit/test_stripe_webhook_service.py` est mis à jour :
   - Le test `test_handle_invoice_payment_succeeded` est **renommé** en `test_handle_invoice_paid` et utilise le type `invoice.paid`.
   - Ajout : `invoice.paid` avec user non résolu → `"user_not_resolved"`.
   - Ajout : `invoice.payment_action_required` avec user résolu → `"processed"`.
   - Ajout : `invoice.payment_action_required` avec user non résolu → `"user_not_resolved"`.
   - Le test existant `test_handle_invoice_payment_failed` reste inchangé.
   - `invoice.payment_succeeded` ne doit plus avoir de test dédié (il devient `event_ignored`).

### Vérification régression

8. Un test vérifie que `invoice.payment_succeeded` retourne désormais `"event_ignored"` (l'événement n'est plus dans le tuple de dispatch).

9. Un test vérifie que le remplacement de `invoice.payment_succeeded` par `invoice.paid` ne modifie pas le contrat d'idempotence : un même `event.id` reçu deux fois pour `invoice.paid` est traité une seule fois (le second appel retourne immédiatement via la garde `last_stripe_event_id` de `update_from_event_payload`).

### Documentation

10. `docs/stripe-webhook-dev.md` est mis à jour :
    - La commande `stripe trigger invoice.payment_succeeded` est **remplacée** par `stripe trigger invoice.paid`.
    - `stripe trigger invoice.payment_action_required` est ajouté aux commandes de test.
    - Une note sur les limites de `stripe trigger` est ajoutée (objets synthétiques, `user_not_resolved` attendu).
    - Une section **"Rationale — sélection des événements"** est ajoutée (voir Dev Notes pour le contenu attendu).

### Qualité

11. `ruff check .` et `pytest` passent sans régression après les modifications.

## Tasks / Subtasks

### Backend — Substitution d'événements

- [x] Modifier `backend/app/services/stripe_webhook_service.py` (AC: 1, 2, 3, 4, 5, 6)
  - [x] Dans `handle_event()` : retirer `"invoice.payment_succeeded"`, ajouter `"invoice.paid"` et `"invoice.payment_action_required"` au tuple de dispatch
  - [x] Dans `_resolve_user_id()` : retirer `"invoice.payment_succeeded"`, ajouter `"invoice.paid"` et `"invoice.payment_action_required"` au tuple qui résout via `customer` field

### Tests

- [x] Mettre à jour `backend/app/tests/unit/test_stripe_webhook_service.py` (AC: 7, 8, 9)
  - [x] Renommer `test_handle_invoice_payment_succeeded` → `test_handle_invoice_paid`, changer `mock_event.type = "invoice.paid"`
  - [x] Ajouter `test_handle_invoice_paid_user_not_resolved` (`invoice.paid` + user non résolu → `"user_not_resolved"`)
  - [x] Ajouter `test_handle_invoice_payment_action_required` (`invoice.payment_action_required` + user résolu → `"processed"`)
  - [x] Ajouter `test_handle_invoice_payment_action_required_user_not_resolved`
  - [x] Ajouter `test_invoice_payment_succeeded_is_now_ignored` (type `invoice.payment_succeeded` → `"event_ignored"`)
  - [x] Ajouter `test_handle_invoice_paid_is_idempotent_same_event_id_twice` (AC: 9)

### Documentation

- [x] Mettre à jour `docs/stripe-webhook-dev.md` (AC: 10)
  - [x] Remplacer `stripe trigger invoice.payment_succeeded` par `stripe trigger invoice.paid`
  - [x] Ajouter `stripe trigger invoice.payment_action_required`
  - [x] Ajouter note sur les limites de `stripe trigger`
  - [x] Ajouter section "Rationale — sélection des événements"

### Validation

- [x] Non-régression : `cd backend && ruff check . && pytest` (AC: 11)

## Dev Notes

### Architecture existante — NE PAS recréer

| Élément | Fichier |
|---------|---------|
| `StripeWebhookService` | `backend/app/services/stripe_webhook_service.py` |
| Endpoint `POST /v1/billing/stripe-webhook` | `backend/app/api/v1/routers/billing.py` |
| `StripeBillingProfileService.update_from_event_payload()` | `backend/app/services/stripe_billing_profile_service.py` (~ligne 134) |
| Tests unitaires webhook | `backend/app/tests/unit/test_stripe_webhook_service.py` |
| Tests intégration webhook | `backend/app/tests/integration/test_stripe_webhook_api.py` |
| Documentation dev Stripe | `docs/stripe-webhook-dev.md` |

### État actuel du tuple de dispatch (post 61-5)

```python
if event_type in (
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.updated",
    "invoice.payment_succeeded",   # ← à retirer
    "invoice.payment_failed",
):
```

### État cible du tuple de dispatch (post 61-6)

```python
if event_type in (
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.updated",
    "invoice.paid",                       # remplace invoice.payment_succeeded
    "invoice.payment_failed",
    "invoice.payment_action_required",    # nouveau
):
```

### État actuel de `_resolve_user_id()` (post 61-5) — extrait pertinent

```python
if event_type in (
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",   # ← à retirer
    "invoice.payment_failed",
):
    customer_id = getattr(data_obj, "customer", None)
    ...
```

### État cible de `_resolve_user_id()` (post 61-6)

```python
if event_type in (
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",                      # remplace invoice.payment_succeeded
    "invoice.payment_failed",
    "invoice.payment_action_required",   # nouveau
):
    customer_id = getattr(data_obj, "customer", None)
    ...
```

La structure de l'objet `invoice` (Stripe) expose `customer` exactement comme les objets `subscription`.
Aucune modification de `_extract_customer_id()` n'est nécessaire — il utilise déjà `getattr(data_obj, "customer", None)` pour tout ce qui n'est pas `customer.updated`.

### Rationale — sélection des événements (contenu à inclure dans la doc)

Ce tableau doit figurer dans `docs/stripe-webhook-dev.md` dans la section "Rationale — sélection des événements" :

| Événement | Traité | Raison |
|-----------|--------|--------|
| `checkout.session.completed` | ✅ Oui | Réconciliation initiale : lie le `customer_id` Stripe à l'`user_id` local via `client_reference_id`. Point d'entrée obligatoire de tout abonnement. |
| `invoice.paid` | ✅ Oui | Confirmation de référence qu'une invoice est soldée. Préféré à `invoice.payment_succeeded` car couvre aussi le cas où une invoice est marquée paid out-of-band, en plus des succès de tentative de paiement. `invoice.payment_succeeded` ne couvre que le succès d'une tentative de paiement Stripe. Source : [Stripe API Events](https://docs.stripe.com/api/events/types). |
| `invoice.payment_failed` | ✅ Oui | Échec de paiement récurrent. Permet de déclencher des alertes, du dunning, et de tenir le statut interne à jour. Note : `invoice.payment_failed` peut aussi survenir dans les flux SCA/3DS si la tentative échoue après une action requise. |
| `invoice.payment_action_required` | ✅ Oui | Identifie explicitement le cas "customer authentication required" (3DS/SCA). Permet de distinguer le cas "action client nécessaire" d'un simple échec, et de notifier l'utilisateur en conséquence. Note : ce n'est pas l'unique signal possible dans les scénarios SCA — `invoice.payment_failed` peut également survenir dans ces flux. |
| `customer.subscription.updated` | ✅ Oui | Tout changement de plan, de statut ou de période. Source de vérité pour `subscription_status` et `cancel_at_period_end`. |
| `customer.subscription.deleted` | ✅ Oui | Fin d'abonnement (résiliation ou non-renouvellement). Met à jour `subscription_status = "canceled"` et recalcule `entitlement_plan`. |
| `customer.updated` | ✅ Oui | Mise à jour des données client (email de facturation). Maintient `billing_email` cohérent. |
| `customer.subscription.created` | ✅ Oui (passif) | Reçu lors de la création via checkout, mais `checkout.session.completed` est l'événement de réconciliation principal. Traité pour cohérence, mais ne porte pas d'information que `checkout.session.completed` n'a pas. |
| `invoice.payment_succeeded` | ❌ Remplacé | Remplacé par `invoice.paid` à partir de la story 61-6. `invoice.paid` couvre un ensemble de cas strictement plus large. Désormais traité comme `event_ignored`. |
| `payment_intent.*` | ❌ Non traité | Granularité inférieure au niveau facturation. Pour un SaaS abonnement, les événements `invoice.*` et `subscription.*` sont suffisants. |
| `customer.subscription.trial_will_end` | ❌ Non traité | Notification préventive utile pour les relances marketing mais sans impact sur `entitlement_plan`. Hors scope de la story. |
| `invoice.upcoming` | ❌ Non traité | Pré-notification avant facturation. Utile pour alertes mais sans impact sur le profil de facturation. Hors scope. |

### Pattern tests unitaires existant

Tous les tests de `test_stripe_webhook_service.py` utilisent `MagicMock` pour simuler `stripe.Event`. Suivre le même pattern :

```python
def test_handle_invoice_paid(self, db):
    mock_event = MagicMock()
    mock_event.type = "invoice.paid"
    mock_event.id = "evt_test_invoice_paid"
    mock_event.data.object.customer = "cus_test123"
    mock_event.to_dict.return_value = {"type": "invoice.paid", "id": "evt_test_invoice_paid", "data": {"object": {"customer": "cus_test123"}}}
    # ... mock StripeBillingProfileService ...
    result = StripeWebhookService.handle_event(db, mock_event)
    assert result == "processed"
```

### Vérification que `invoice.payment_succeeded` est bien ignoré post-61-6

```python
def test_invoice_payment_succeeded_is_now_ignored(self, db):
    mock_event = MagicMock()
    mock_event.type = "invoice.payment_succeeded"
    mock_event.id = "evt_test_legacy"
    mock_event.data.object.customer = "cus_test123"
    result = StripeWebhookService.handle_event(db, mock_event)
    assert result == "event_ignored"
```

### Impact sur `update_from_event_payload`

`update_from_event_payload` est **indifférent au type d'événement** : il met à jour les champs présents dans `data.object` quel que soit le type. Pour les objets `invoice`, l'objet Stripe a `"object": "invoice"` — donc le bloc `if data_obj.get("object") == "subscription"` ne s'exécute pas. Seuls les champs génériques sont mis à jour : `customer_id` (via `"customer"` key), `last_stripe_event_*`, `synced_at`.

C'est le comportement correct pour les événements `invoice.*` : on ne cherche pas à reconstruire l'état de l'abonnement depuis une facture — cela est fait via les événements `customer.subscription.*`.

**Aucune modification de `update_from_event_payload` n'est requise.**

### Stripe CLI — commandes de test mises à jour

```bash
# Événements à tester manuellement (état cible post 61-6)
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger customer.updated
stripe trigger invoice.paid                         # remplace invoice.payment_succeeded
stripe trigger invoice.payment_failed
stripe trigger invoice.payment_action_required      # nouveau
```

> **Note** : `stripe trigger` génère des événements synthétiques avec des objets factices qui ne correspondent pas forcément à une vraie subscription. Les `customer_id`, `subscription_id` et `invoice_id` sont des stubs — la résolution `customer_id → user_id` retournera `user_not_resolved` en dev local (comportement attendu et loggé). Pour valider la corrélation réelle entre Customer, Subscription et Invoice, privilégier aussi un test end-to-end avec création d'un véritable abonnement de test via le Dashboard Stripe (mode test) et le forwarder `stripe listen`.

### Références

- Webhook service : `backend/app/services/stripe_webhook_service.py`
- Router billing : `backend/app/api/v1/routers/billing.py`
- Tests unitaires : `backend/app/tests/unit/test_stripe_webhook_service.py`
- Documentation Stripe CLI : `docs/stripe-webhook-dev.md`
- Story 61-4 : `_bmad-output/implementation-artifacts/61-4-webhook-stripe-et-retour-navigateur.md`
- Story 61-5 : `_bmad-output/implementation-artifacts/61-5-webhook-stripe-invoice-events-et-documentation-dev-prod.md`
- Stripe — Webhooks and subscriptions : https://docs.stripe.com/billing/subscriptions/webhooks
- Stripe — `invoice.paid` vs `invoice.payment_succeeded` : https://docs.stripe.com/billing/subscriptions/webhooks#understand

## Dev Agent Record

### Agent Model Used

gemini-2.0-pro-exp

### Debug Log References

- Fix ruff E501 (line too long) in `backend/app/tests/unit/test_stripe_webhook_service.py`.
- Fix PowerShell syntax for multiple commands (use `;` instead of `&&`).

### Completion Notes List

- Substituted `invoice.payment_succeeded` with `invoice.paid` in `StripeWebhookService`.
- Added `invoice.payment_action_required` to `StripeWebhookService` dispatch and resolution.
- Updated unit tests in `test_stripe_webhook_service.py`:
  - Renamed and updated existing invoice success tests.
  - Added test for `invoice.payment_action_required`.
  - Added test to verify `invoice.payment_succeeded` is now ignored.
  - Added test for idempotency of `invoice.paid`.
- Updated `docs/stripe-webhook-dev.md` with new Stripe CLI commands, notes on trigger limits, and a comprehensive Rationale section.
- Verified all tests pass and `ruff` checks are clean.

### File List

- `backend/app/services/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `docs/stripe-webhook-dev.md`

