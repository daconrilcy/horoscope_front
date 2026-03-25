# Story 61.4 : Webhook Stripe et retour navigateur

Status: done

## Story

En tant que système backend,
je veux recevoir, vérifier et traiter les événements Stripe via webhook pour mettre à jour le plan d'accès SaaS des utilisateurs,
afin que l'activation de l'abonnement soit fiable, idempotente et indépendante du retour navigateur.

En tant qu'utilisateur ayant complété le paiement Stripe,
je veux voir une page de confirmation adaptée lors de mon retour sur l'application,
afin de comprendre que mon paiement est en cours de traitement sans que cette page n'active elle-même mon accès.

## Contexte métier et position dans l'Epic 61

```text
61-1 (done) : table DB + StripeBillingProfileService + derive_entitlement_plan()
61-2 (done) : SDK stripe==14.4.1 + get_stripe_client() + secrets + STRIPE_PRICE_ENTITLEMENT_MAP
61-3 (done) : POST /v1/billing/stripe-checkout-session (success_url avec ?session_id={CHECKOUT_SESSION_ID})
61-4 (cette story) : Webhook handler + vérification signature + pages retour navigateur
```

**Principe fondamental (Stripe officiel)**

> L'activation de l'accès SaaS DOIT être déclenchée par le webhook, pas par le retour navigateur.
> Le navigateur peut manquer des événements, être fermé, ou subir une défaillance réseau.
> Le webhook est le mécanisme fiable pour les changements d'état d'abonnement, y compris les cas asynchrones.

Le `success_url` ne sert donc qu'au confort utilisateur et, éventuellement, à de l'affichage ou du debug contrôlé. Il ne constitue jamais la source de vérité métier.

## Acceptance Criteria

### Backend — Webhook Handler

1. [x] **Endpoint exposé sans auth JWT** : `POST /v1/billing/stripe-webhook` reçoit les requêtes Stripe sans `require_authenticated_user`. Toute requête Stripe valide doit pouvoir être traitée sans JWT.

2. [x] **Vérification de signature obligatoire** : le handler lit le body brut avec `await request.body()` puis vérifie la signature Stripe à l'aide de l'API officielle `stripe.Webhook.construct_event(payload_bytes, sig_header, webhook_secret)`.
   - Si le header `stripe-signature` est absent ou invalide, retourner HTTP 400.
   - Si `settings.stripe_webhook_secret` est `None` ou vide, retourner HTTP 503 avec un code métier `webhook_secret_not_configured`.

3. [x] **Réponse rapide à Stripe** : le endpoint doit répondre sans traitement bloquant inutile afin d'éviter les retries Stripe.
   - **Signature invalide / secret absent** : erreur explicite (`400` ou `503`).
   - **Erreur applicative interne après signature valide** : logger l'erreur, auditer l'événement, puis retourner HTTP 200 pour éviter un retry non pertinent côté Stripe.

4. [x] **Événements traités** :
   - `checkout.session.completed` : extraire `client_reference_id` posé en 61-3 (attendu comme `str(user_id)`), le convertir en `int`, puis appeler `StripeBillingProfileService.update_from_event_payload(db, user_id, event_dict)`.
   - `customer.subscription.created` / `customer.subscription.updated` / `customer.subscription.deleted` : résoudre `user_id` via `StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)`, puis appeler `update_from_event_payload()`.
   - `customer.updated` : résoudre `user_id` via `StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)` où `customer_id = event.data.object.id`, puis appeler `update_from_event_payload()`.
   - Tout autre événement : logger proprement et retourner HTTP 200 avec un statut logique de type `event_ignored`.

5. [x] **Idempotence déléguée à la couche service** : `StripeBillingProfileService.update_from_event_payload()` reste la seule source de vérité pour l'idempotence, la déduplication et la gestion du désordre temporel des événements. Le handler webhook ne doit pas réimplémenter cette logique.

6. [x] **Utilisateur non résolu** : si la résolution du `user_id` échoue, logger un warning, auditer le cas, puis retourner HTTP 200. Stripe ne doit pas retenter pour une incohérence métier locale.

7. [x] **Audit** : chaque événement webhook reçu avec signature valide, qu'il soit traité, ignoré ou en échec non fatal, est enregistré via `_record_audit_event` avec `action="stripe_webhook_event"`, `target_type="stripe_event"`, `target_id=event.id`.

8. [x] **Logs structurés** : les logs doivent inclure au minimum `event_id`, `event_type`, `customer_id` si disponible, `user_id` si résolu, et l'action finale (`processed`, `ignored`, `failed_non_fatal`).

9. [x] **Tests unitaires** : `StripeWebhookService` est couvert pour les événements suivants :
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `customer.updated`
   - signature invalide
   - événement ignoré
   - utilisateur introuvable

10. [x] **Tests d'intégration** : le endpoint HTTP est testé avec payload signé valide, payload signé invalide, secret absent, et cas d'erreur applicative non fatale.

### Frontend — Pages de retour Stripe

11. [x] **Page `/billing/success`** :
   - Lit le paramètre `?session_id=cs_...` via `useSearchParams()`.
   - Affiche un état du type : **"Paiement en cours de confirmation"**.
   - Affiche un indicateur visuel de traitement.
   - Explique clairement que l'activation peut prendre quelques instants.
   - Propose un bouton **"Retour au tableau de bord"** vers `/dashboard`.
   - N'appelle aucune API destinée à activer l'accès SaaS.
   - Peut, à titre optionnel, afficher ou conserver le `session_id` pour debug ou usage futur non bloquant.

12. [x] **Page `/billing/cancel`** :
   - Affiche un état du type : **"Paiement annulé"**.
   - Affiche un message rassurant indiquant qu'aucune activation n'a eu lieu.
   - Propose un bouton **"Retour aux abonnements"** vers `/settings/subscription`.
   - Propose un bouton **"Réessayer"** vers `/billing`.

13. [x] **Aucune logique métier d'activation côté front** : ni `/billing/success` ni `/billing/cancel` ne doivent déclencher de modification d'accès, de plan ou d'entitlement. Le front reste purement informatif.

14. [x] **Routes enregistrées** : les deux pages sont ajoutées sous `AuthGuard` dans `frontend/src/app/routes.tsx`, sous la forme `/billing/success` et `/billing/cancel`.

15. [x] **i18n** : tous les textes sont externalisés dans `frontend/src/i18n/`, dans `settings.ts` si cohérent avec l'organisation existante, ou dans un nouveau fichier `billing.ts`.

16. [x] **CSS** : aucun style inline. Les pages utilisent les variables CSS existantes du design system (`var(--text-1)`, `var(--text-2)`, `var(--glass)`, `var(--glass-border)`, `var(--primary)`, etc.) dans un fichier dédié ou dans les fichiers de style existants.

### Config & Dev

17. [x] **Variable `STRIPE_WEBHOOK_SECRET`** : la variable existe déjà dans `config.py` et ne doit pas être recréée. La documentation doit expliciter les deux modes d'utilisation :
   - **mode dev** via Stripe CLI installée localement avec `winget install Stripe.StripeCLI`
   - **mode production** via endpoint déclaré dans le Dashboard Stripe

18. [x] **Documentation `.env.example`** : le fichier documente clairement la différence entre le secret de signature webhook local fourni par `stripe listen` et le secret de signature webhook production fourni par le Dashboard Stripe.

19. [x] **Non-régression** : `ruff` et `pytest` passent intégralement.

## Tasks / Subtasks

### Backend

- [x] **Créer `StripeWebhookService`** dans `backend/app/services/stripe_webhook_service.py` (AC: 2, 4, 5, 6, 8, 9)
- [x] **Ajouter le endpoint `POST /v1/billing/stripe-webhook`** dans `backend/app/api/v1/routers/billing.py` (AC: 1, 2, 3, 7, 10)
- [x] **Créer les tests unitaires** `backend/app/tests/unit/test_stripe_webhook_service.py` (AC: 9)
- [x] **Créer les tests d'intégration** `backend/app/tests/integration/test_stripe_webhook_api.py` (AC: 10)

### Frontend

- [x] **Créer `/billing/success`** dans `frontend/src/pages/billing/BillingSuccessPage.tsx` (AC: 11)
- [x] **Créer `/billing/cancel`** dans `frontend/src/pages/billing/BillingCancelPage.tsx` (AC: 12)
- [x] **Créer le CSS** dans `frontend/src/pages/billing/billing-return.css` ou fichier équivalent (AC: 16)
- [x] **Déclarer les routes** dans `frontend/src/app/routes.tsx` (AC: 14)
- [x] **Ajouter les traductions i18n** avec les clés `billingSuccess.*` et `billingCancel.*` (AC: 15)

### Config & Validation

- [x] **Documenter `.env.example`** avec les deux modes webhook (AC: 17, 18)
- [x] **Valider la non-régression** avec `ruff` et `pytest` (AC: 19)

## Dev Notes

### Architecture Backend — Points critiques

**CRITIQUE : body brut obligatoire avant tout parsing**

```python
@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db_session)) -> Any:
    payload_bytes = await request.body()  # obligatoire avant tout parsing
    sig_header = request.headers.get("stripe-signature", "")
    ...
```

Avec FastAPI, il faut éviter un schéma qui ferait parser automatiquement le body avant la vérification Stripe.

**Vérification de signature Stripe — API à utiliser**

Utiliser l'API officielle `stripe.Webhook.construct_event(...)`, qui vérifie la signature et parse l'événement dans une seule opération.

```python
import stripe

try:
    event = stripe.Webhook.construct_event(
        payload_bytes,
        sig_header,
        settings.stripe_webhook_secret,
    )
    event_dict = event.to_dict()
except stripe.error.SignatureVerificationError:
    return JSONResponse(status_code=400, content={"error": "invalid_signature"})
```

Cette approche est plus cohérente et plus lisible que de séparer manuellement la vérification et le parsing JSON.

**Résolution du `user_id` par type d'événement**

```text
checkout.session.completed -> event["data"]["object"]["client_reference_id"] -> int(user_id)
customer.subscription.*   -> event["data"]["object"]["customer"] -> get_by_stripe_customer_id()
customer.updated          -> event["data"]["object"]["id"] -> get_by_stripe_customer_id()
```

**Le service attend l'événement Stripe complet**

```python
StripeBillingProfileService.update_from_event_payload(db, user_id, event_dict)
```

Il ne faut pas transmettre uniquement `data.object`, car l'idempotence et l'ordre reposent sur des métadonnées présentes au niveau racine de l'événement.

**Politique de réponse HTTP**

- Signature invalide : `400`
- Secret webhook non configuré : `503`
- Événement signé mais non supporté : `200`
- Échec applicatif non fatal : `200`

L'objectif est d'éviter les retries Stripe sur des problèmes purement métier internes à l'application.

### Réutilisation du code existant

| Besoin | Fichier | Symbole |
|---|---|---|
| Résoudre un profil via `stripe_customer_id` | `stripe_billing_profile_service.py` | `StripeBillingProfileService.get_by_stripe_customer_id(db, cid)` |
| Résoudre un profil via `stripe_subscription_id" | `stripe_billing_profile_service.py` | `StripeBillingProfileService.get_by_stripe_subscription_id(db, sid)` |
| Mettre à jour le profil depuis un événement | `stripe_billing_profile_service.py` | `StripeBillingProfileService.update_from_event_payload(db, user_id, event_dict)` |
| Enregistrer un audit event | `billing.py` | `_record_audit_event(db, ...)` |
| Retourner une erreur API homogène | `billing.py` | `_error_response(...)` |
| Lire le secret webhook | `config.py` | `settings.stripe_webhook_secret` |
| Client Stripe | `integrations/stripe_client.py` | `get_stripe_client()` non requis pour la vérification du webhook |

### Frontend — Pages de retour navigateur

**Route `/billing/success`**

Comportement attendu :
- écran de transition rassurant
- état visuel de chargement / confirmation en cours
- texte expliquant que l'abonnement sera activé après confirmation Stripe
- bouton de retour vers le dashboard
- aucune décision métier locale

**Route `/billing/cancel`**

Comportement attendu :
- écran simple, rassurant, non anxiogène
- rappel qu'aucune activation n'a été finalisée
- possibilité de revenir à la gestion d'abonnement
- possibilité de relancer une tentative

### Setup Dev — Deux modes webhook

#### Mode développement — Stripe CLI locale

Pré-requis local Windows :

```bash
winget install Stripe.StripeCLI
```

Connexion au compte Stripe :

```bash
stripe login
```

Forward des webhooks vers le backend local :

```bash
stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

La commande retourne un secret de signature webhook de type `whsec_...` à placer dans l'environnement local.

Exemple :

```env
STRIPE_WEBHOOK_SECRET=whsec_dev_generated_by_stripe_cli
```

Déclenchement manuel d'événements de test :

```bash
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
```

#### Mode production — Stripe Dashboard

Créer un endpoint webhook dans le Dashboard Stripe :

```text
Dashboard -> Developers -> Webhooks -> Add endpoint
URL : https://your-domain.com/v1/billing/stripe-webhook
```

Événements à souscrire :

```text
checkout.session.completed
customer.subscription.created
customer.subscription.updated
customer.subscription.deleted
customer.updated
```

Récupérer ensuite le `Signing secret` du webhook Stripe et le reporter dans la configuration production.

Exemple :

```env
STRIPE_WEBHOOK_SECRET=whsec_prod_from_dashboard
```

### `.env.example` — documentation attendue

```env
# Stripe Webhook
# Dev  : obtenu avec `stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook`
# Prod : obtenu dans Stripe Dashboard > Developers > Webhooks > Signing secret
STRIPE_WEBHOOK_SECRET=whsec_your_signing_secret
```

### Pattern de tests — payload signé

**Tests unitaires**

Mocket `stripe.Webhook.construct_event()` pour se concentrer sur le routage fonctionnel du service.

```python
from unittest.mock import patch


def test_handle_checkout_completed_event(...):
    payload = b'{"id": "evt_001", "type": "checkout.session.completed", ...}'
    with patch("stripe.Webhook.construct_event"):
        ...
```

**Tests d'intégration**

Construire un header `stripe-signature` valide à partir du secret de test pour exercer le vrai endpoint HTTP.

```python
import hashlib
import hmac
import time


def _sign_payload(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload.decode()}"
    signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={signature}"
```

### Project Structure Notes

**Nouveaux fichiers**

```text
backend/app/services/stripe_webhook_service.py
backend/app/tests/unit/test_stripe_webhook_service.py
backend/app/tests/integration/test_stripe_webhook_api.py
frontend/src/pages/billing/BillingSuccessPage.tsx
frontend/src/pages/billing/BillingCancelPage.tsx
frontend/src/pages/billing/billing-return.css
```

**Fichiers modifiés**

```text
backend/app/api/v1/routers/billing.py
frontend/src/app/routes.tsx
frontend/src/i18n/settings.ts ou frontend/src/i18n/billing.ts
.env.example
```

**Fichiers à ne pas modifier sauf nécessité avérée**

```text
backend/app/services/stripe_billing_profile_service.py
backend/app/infra/db/models/stripe_billing.py
backend/app/integrations/stripe_client.py
backend/app/core/config.py
```

## References

- `backend/app/api/v1/routers/billing.py` — patterns `_record_audit_event`, `_error_response`
- `backend/app/services/stripe_billing_profile_service.py` — `update_from_event_payload()`, `get_by_stripe_customer_id()`, `get_by_stripe_subscription_id()`
- `backend/app/infra/db/models/stripe_billing.py` — modèle de persistance et champs d'idempotence
- `backend/app/core/config.py` — `settings.stripe_webhook_secret`
- `frontend/src/app/routes.tsx` — routing `/billing`
- `frontend/src/i18n/settings.ts` — pattern i18n existant
- Documentation Stripe — webhook signing, `stripe.Webhook.construct_event()`, best practices webhook pour abonnements

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Fixed AuditService status validation error (received -> success)
- Fixed Button icon prop issue in frontend (icon -> leftIcon)
- Fixed i18n type exports and imports in index.ts
- Refactored StripeWebhookService to use Event objects instead of dicts

### Completion Notes List

- Stripe webhook endpoint implemented at POST /v1/billing/stripe-webhook
- Signature verification using Stripe SDK (construct_event)
- Idempotent processing via StripeBillingProfileService
- Frontend success/cancel pages with glassmorphism UI
- Full i18n support for billing return flow
- All unit and integration tests passing

### File List

- backend/app/services/stripe_webhook_service.py
- backend/app/api/v1/routers/billing.py
- backend/app/tests/unit/test_stripe_webhook_service.py
- backend/app/tests/integration/test_stripe_webhook_api.py
- frontend/src/pages/billing/BillingSuccessPage.tsx
- frontend/src/pages/billing/BillingCancelPage.tsx
- frontend/src/pages/billing/billing-return.css
- frontend/src/i18n/billing.ts
- frontend/src/i18n/index.ts
- frontend/src/app/routes.tsx
- frontend/src/i18n/astrologers.ts
- frontend/src/i18n/birthProfile.ts
- frontend/src/i18n/consultations.ts
- frontend/src/i18n/insights.ts
- frontend/src/i18n/natalChart.ts
- frontend/src/i18n/settings.ts
