# Story 61.5 : Extension du webhook Stripe aux événements `invoice.*` et documentation dev/prod

Status: done

## Contexte dans l'Epic 61

```text
61-1 (done) : table DB + StripeBillingProfileService + derive_entitlement_plan()
61-2 (done) : SDK stripe==14.4.1 + get_stripe_client() + secrets + STRIPE_PRICE_ENTITLEMENT_MAP
61-3 (done) : POST /v1/billing/stripe-checkout-session
61-4 (done) : socle webhook Stripe signé + dispatch checkout/subscription.* + pages retour navigateur
61-5 (cette story) : extension du webhook existant aux événements invoice.* + documentation dev/prod + Stripe CLI
```

**Pré-requis critique** : lire 61-4 et le code existant avant toute modification.
Cette story **ne recrée pas** le webhook Stripe.
Le endpoint signé, la vérification de signature et le dispatch existent déjà dans `StripeWebhookService` (story 61-4).

## Story

En tant que système backend,
je veux étendre le webhook Stripe déjà en place pour traiter les événements de facturation récurrente `invoice.payment_succeeded` et `invoice.payment_failed`, et documenter clairement les modes dev et prod,
afin que les renouvellements d'abonnement et les échecs de paiement récurrents soient gérés proprement, et que l'équipe puisse tester localement avec Stripe CLI sans ambiguïté sur les secrets de signature.

## Acceptance Criteria

### Backend — Extension du routage webhook

1. `StripeWebhookService.handle_event()` prend en charge `invoice.payment_succeeded`.
2. `StripeWebhookService.handle_event()` prend en charge `invoice.payment_failed`.
3. Pour ces deux événements, le `user_id` est résolu via `customer_id = event.data.object.customer`, puis `StripeBillingProfileService.update_from_event_payload(db, user_id, event_dict)` est appelé avec l'événement Stripe sérialisé complet.
4. Si aucun `user_id` ne peut être résolu depuis le `customer_id`, logger un warning et retourner `"user_not_resolved"` — cohérent avec le comportement existant.
5. Les nouveaux événements s'ajoutent au bloc de dispatch existant dans `handle_event()`, sans réécriture de l'architecture établie en 61-4.

### Tests unitaires

6. `backend/app/tests/unit/test_stripe_webhook_service.py` couvre :
   - `invoice.payment_succeeded` avec user résolu → `"processed"`
   - `invoice.payment_failed` avec user résolu → `"processed"`
   - `invoice.payment_succeeded` avec user non résolu → `"user_not_resolved"`
   - `invoice.payment_failed` avec user non résolu → `"user_not_resolved"`

### Configuration

7. `backend/.env.example` contient une section `# Stripe` complète avec tous les champs lus par `config.py` :
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_PRICE_BASIC`
   - `STRIPE_PRICE_PREMIUM`
   - `STRIPE_WEBHOOK_SECRET` — commenté distinctement pour dev vs prod (voir AC10)
   - `STRIPE_CHECKOUT_SUCCESS_URL`
   - `STRIPE_CHECKOUT_CANCEL_URL`

8. Aucune nouvelle variable n'est ajoutée à `config.py` — les champs existent déjà.

### Documentation d'exploitation

9. Un document `docs/stripe-webhook-dev.md` décrit le workflow local avec Stripe CLI :
   - Installation : `winget install Stripe.StripeCLI`
   - Authentification : `stripe login`
   - Forwarder local : `stripe listen --forward-to localhost:8001/v1/billing/stripe-webhook`
   - Récupération du `whsec_...` affiché dans le terminal → reporter dans `.env` comme `STRIPE_WEBHOOK_SECRET`
   - Déclenchement des événements test via `stripe trigger` (voir commandes en Dev Notes)

10. La documentation distingue explicitement les deux contextes de `STRIPE_WEBHOOK_SECRET` :
    - **DEV (Stripe CLI)** : fourni par `stripe listen`, stable entre les redémarrages de la commande, mais distinct du secret Dashboard
    - **PROD (Dashboard)** : secret permanent depuis Dashboard Stripe > Développeurs > Webhooks > [endpoint] > Signing secret

### Qualité

11. `ruff check .` et `pytest` passent sans régression après les modifications.

## Tasks / Subtasks

### Backend — Ajout événements invoice

- [x] Modifier `backend/app/services/stripe_webhook_service.py` (AC: 1, 2, 3, 4, 5)
  - [x] Ajouter `"invoice.payment_succeeded"` et `"invoice.payment_failed"` au tuple du bloc de dispatch dans `handle_event()`
  - [x] Étendre la résolution du `user_id` pour les événements `invoice.*` en réutilisant la logique existante `customer_id -> user_id`
  - [x] Étendre `_extract_customer_id()` si nécessaire pour couvrir les objets `invoice`

- [x] Mettre à jour `backend/app/tests/unit/test_stripe_webhook_service.py` (AC: 6)
  - [x] Cas `invoice.payment_succeeded` avec user résolu → `"processed"`
  - [x] Cas `invoice.payment_failed` avec user résolu → `"processed"`
  - [x] Cas `invoice.payment_succeeded` avec user non résolu → `"user_not_resolved"`
  - [x] Cas `invoice.payment_failed` avec user non résolu → `"user_not_resolved"`

### Configuration

- [x] Compléter `backend/.env.example` (AC: 7, 8)
  - [x] Ajouter la section `# Stripe` avec tous les champs
  - [x] Commenter `STRIPE_WEBHOOK_SECRET` avec distinction explicite DEV vs PROD

### Documentation

- [x] Créer `docs/stripe-webhook-dev.md` (AC: 9, 10)
  - [x] Prérequis : installation Stripe CLI + `stripe login`
  - [x] Commande `stripe listen --forward-to ...`
  - [x] Récupération et positionnement du signing secret dans `.env`
  - [x] Commandes `stripe trigger` pour l'ensemble des événements webhook actuellement supportés
  - [x] Tableau ou note distinguant secret CLI vs secret Dashboard

### Validation

- [x] Non-régression : `cd backend && ruff check . && pytest` (AC: 11)

## Dev Notes

### Architecture existante — NE PAS recréer

| Élément | Fichier |
|---------|---------|
| `StripeWebhookService` | `backend/app/services/stripe_webhook_service.py` |
| Endpoint `POST /v1/billing/stripe-webhook` | `backend/app/api/v1/routers/billing.py` (~ligne 976) |
| Tests intégration webhook | `backend/app/tests/integration/test_stripe_webhook_api.py` |

### Pattern d'ajout d'événements invoice

`handle_event()` dispatche via `if event_type in (...)`. Ajouter les deux nouveaux types dans ce tuple, aux côtés des événements déjà gérés en 61-4 :

```python
if event_type in (
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",   # nouveau
    "invoice.payment_failed",      # nouveau
):
```

`_resolve_user_id()` : les objets `invoice` exposent `customer` comme les objets `subscription`. Réutiliser la même logique de résolution `customer_id -> user_id` :

```python
if event_type in ("invoice.payment_succeeded", "invoice.payment_failed"):
    customer_id = getattr(data_obj, "customer", None)
    if customer_id:
        profile = StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)
        if profile:
            return profile.user_id
    return None
```

`_extract_customer_id()` : étendre si nécessaire pour les objets `invoice` :

```python
if event.type in ("invoice.payment_succeeded", "invoice.payment_failed"):
    return getattr(data_obj, "customer", None)
```

### Mode dev vs prod — distinction clé

| Mode | Source du secret | Stabilité | Usage |
|------|-----------------|-----------|-------|
| DEV (Stripe CLI) | Terminal `stripe listen` | Stable entre redémarrages | Dev local uniquement |
| PROD (Dashboard) | Dashboard > Développeurs > Webhooks > endpoint | Permanent | Environnements déployés |

Le secret CLI est distinct du secret Dashboard même s'il est stable. Les deux sont incompatibles.

### Stripe CLI — commandes essentielles

```bash
# Installation (Windows, une seule fois)
winget install Stripe.StripeCLI

# Authentification (une seule fois par machine)
stripe login

# Forwarder local (dans un terminal séparé, backend doit tourner sur le port 8001)
stripe listen --forward-to localhost:8001/v1/billing/stripe-webhook
# → affiche : "Your webhook signing secret is whsec_xxxx"
# → copier cette valeur dans .env : STRIPE_WEBHOOK_SECRET=whsec_xxxx

# Déclencher des événements test manuellement
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger customer.updated
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

### Pattern tests unitaires existant

`test_stripe_webhook_service.py` utilise `MagicMock` pour simuler `stripe.Event`. Suivre le même pattern pour les nouveaux cas.

### Références

- Webhook service : `backend/app/services/stripe_webhook_service.py`
- Router billing : `backend/app/api/v1/routers/billing.py`
- Config Stripe : `backend/app/core/config.py` (lignes 274-288)
- Tests unitaires : `backend/app/tests/unit/test_stripe_webhook_service.py`
- Tests intégration : `backend/app/tests/integration/test_stripe_webhook_api.py`
- Story 61-4 : `_bmad-output/implementation-artifacts/61-4-webhook-stripe-et-retour-navigateur.md`
- Stripe — Webhooks and subscriptions : https://docs.stripe.com/billing/subscriptions/webhooks
- Stripe CLI — stripe listen : https://docs.stripe.com/cli/listen

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/services/stripe_webhook_service.py` (Implemented logic + lint fix)
- `backend/app/tests/unit/test_stripe_webhook_service.py` (New tests + lint fix)
- `backend/.env.example` (Updated section)
- `docs/stripe-webhook-dev.md` (New documentation)
- `backend/app/api/v1/routers/billing.py` (Lint fix)
- `backend/app/tests/integration/test_stripe_webhook_api.py` (Lint fix)
- `backend/migrations/versions/7507b4a98306_add_consultation_templates.py` (Lint fix)
- `backend/migrations/versions/f1274b6a70ac_add_consultation_third_party_tables.py` (Lint fix)
- `backend/scripts/seed_astrologers_6_profiles.py` (Lint fix)
- `backend/scripts/seed_consultation_templates.py` (Lint fix)
- `_bmad-output/implementation-artifacts/61-5-webhook-stripe-invoice-events-et-documentation-dev-prod.md` (Self-update)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (Status update)
