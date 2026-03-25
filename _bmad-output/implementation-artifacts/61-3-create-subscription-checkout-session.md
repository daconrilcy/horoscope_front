# Story 61.3 : Endpoint `POST /v1/billing/stripe-checkout-session`

Status: ready-for-dev

## Story

En tant qu'utilisateur authentifié,
je veux que le backend crée une Stripe Checkout Session d'abonnement lorsque je demande à souscrire à un plan,
afin d'être redirigé vers la page de paiement Stripe sécurisée sans que le backend ne manipule directement ma carte bancaire.

## Contexte métier et position dans l'Epic 61

```
61-1 (done) : table DB + service de mapping StripeBillingProfileService
61-2 (done) : SDK stripe==14.4.1 + StripeClient + secrets + STRIPE_PRICE_ENTITLEMENT_MAP alimentée
61-3 (cette story) : endpoint create_checkout_session via get_stripe_client()
61-4 (à venir) : Webhook handler + vérification de signature
```

L'endpoint reçoit `plan` ("basic" | "premium") depuis un utilisateur JWT authentifié, retrouve ou crée son `stripe_customer_id`, puis crée une Checkout Session Stripe en mode `subscription`. Stripe recommande de créer une **nouvelle session à chaque tentative** — pas d'idempotence de session (à la différence des PaymentIntent).

## Acceptance Criteria

1. **Endpoint exposé** : `POST /v1/billing/stripe-checkout-session` est accessible et requiert un JWT valide. Un utilisateur avec rôle autre que `"user"` ou `"admin"` reçoit un 403.

2. **Paramètre `plan` validé** : le corps de la requête contient `{"plan": "basic"}` ou `{"plan": "premium"}`. Toute autre valeur retourne un 422 `invalid_checkout_request`.

3. **Stripe indisponible** : si `get_stripe_client()` retourne `None` (clé absente), l'endpoint retourne un 503 `stripe_unavailable` sans crash.

4. **Price ID introuvable** : si le `plan` demandé n'a pas de `price_id` dans `STRIPE_PRICE_ENTITLEMENT_MAP` (variable d'env absente), l'endpoint retourne un 422 `plan_price_not_configured`.

5. **`stripe_customer_id` récupéré ou créé** : avant l'appel Stripe, `StripeBillingProfileService.get_or_create_profile(db, user_id)` est appelé. Si le profil a déjà un `stripe_customer_id`, il est passé dans le paramètre `customer` de la session. Sinon, `customer_email` de l'utilisateur est utilisé.

6. **Session créée avec les bons paramètres** : l'appel `client.checkout.sessions.create(params={...})` inclut obligatoirement :
   - `mode="subscription"`
   - `line_items=[{"price": price_id, "quantity": 1}]`
   - `success_url` (depuis config `settings.stripe_checkout_success_url`)
   - `cancel_url` (depuis config `settings.stripe_checkout_cancel_url`)
   - `client_reference_id=str(user_id)` (reconciliation user interne)
   - `metadata={"app_user_id": str(user_id)}`
   - `customer=stripe_customer_id` OU `customer_email=user.email` (pas les deux en même temps)

7. **Réponse nominale** : l'endpoint retourne `{"data": {"checkout_url": "<url_stripe>"}, "meta": {"request_id": "..."}}` avec HTTP 200.

8. **Erreur Stripe API** : toute `stripe.StripeError` est interceptée et retourne un 502 `stripe_api_error` avec log d'erreur. Ne jamais laisser remonter une exception Stripe non gérée.

9. **Audit** : chaque tentative de création de session (succès ou échec) est loguée via `_record_audit_event` (action `"stripe_checkout_session_created"` ou `"stripe_checkout_session_failed"`).

10. **Rate limiting** : l'endpoint applique les limites de `_enforce_billing_limits` avec `operation="stripe_checkout"`.

11. **Config** : deux nouvelles variables `STRIPE_CHECKOUT_SUCCESS_URL` et `STRIPE_CHECKOUT_CANCEL_URL` sont ajoutées dans `config.py` et `.env.example`. Valeurs de défaut pour le dev local : `http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}` et `http://localhost:5173/billing/cancel`.

12. **Non-régression** : `ruff check backend --fix && ruff check backend` retourne 0 erreur. `pytest -q backend` passe entièrement, **aucun appel réseau réel à Stripe** (mock obligatoire).

13. **Tests unitaires** : la logique de `StripeCheckoutService.create_checkout_session()` est testée avec un `StripeClient` mocké — cas nominaux (customer existant, customer absent), cas d'erreur (plan inconnu, stripe unavailable, StripeError).

14. **Tests d'intégration** : l'endpoint HTTP est testé via `TestClient` avec `get_stripe_client` patché — 200 nominal, 401/403 auth, 503 stripe unavailable, 422 plan inconnu.

## Tasks / Subtasks

- [ ] **Config — nouvelles variables** (AC: 11)
  - [ ] Dans `backend/app/core/config.py`, bloc Stripe (après `stripe_api_version`) :
    ```python
    self.stripe_checkout_success_url = os.getenv(
        "STRIPE_CHECKOUT_SUCCESS_URL",
        "http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}",
    ).strip()
    self.stripe_checkout_cancel_url = os.getenv(
        "STRIPE_CHECKOUT_CANCEL_URL",
        "http://localhost:5173/billing/cancel",
    ).strip()
    ```
  - [ ] Dans `.env.example`, section Stripe, ajouter sous les variables existantes :
    ```dotenv
    STRIPE_CHECKOUT_SUCCESS_URL=http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}
    STRIPE_CHECKOUT_CANCEL_URL=http://localhost:5173/billing/cancel
    ```

- [ ] **Service `StripeCheckoutService`** (AC: 3, 4, 5, 6, 8)
  - [ ] Créer `backend/app/services/stripe_checkout_service.py`
  - [ ] Implémenter `StripeCheckoutServiceError(code, message, details)` (même pattern que `BillingServiceError`)
  - [ ] Implémenter `StripeCheckoutService.create_checkout_session(db, *, user_id, user_email, plan, success_url, cancel_url) -> str`
    - [ ] Appeler `get_stripe_client()` → 503 si `None`
    - [ ] Résoudre `price_id` depuis `STRIPE_PRICE_ENTITLEMENT_MAP` → 422 si absent
    - [ ] Appeler `StripeBillingProfileService.get_or_create_profile(db, user_id)`
    - [ ] Construire `params` avec `customer` OU `customer_email` selon le profil
    - [ ] Appeler `client.checkout.sessions.create(params=params)` et retourner `session.url`
    - [ ] Intercepter `stripe.StripeError` → logger + relever `StripeCheckoutServiceError(code="stripe_api_error")`

- [ ] **Endpoint HTTP** (AC: 1, 2, 7, 9, 10)
  - [ ] Dans `backend/app/api/v1/routers/billing.py`, ajouter :
    - [ ] Import de `StripeCheckoutService`, `StripeCheckoutServiceError` depuis `app.services.stripe_checkout_service`
    - [ ] Pydantic model `StripeCheckoutRequest(plan: str)` et `StripeCheckoutResponse(checkout_url: str)`
    - [ ] Endpoint `POST /stripe-checkout-session` avec :
      - [ ] Auth JWT obligatoire (`require_authenticated_user`)
      - [ ] Validation du rôle (`_ensure_user_role`)
      - [ ] Rate limiting (`_enforce_billing_limits` avec `operation="stripe_checkout"`)
      - [ ] Validation du `plan` : uniquement `"basic"` ou `"premium"` → 422 sinon
      - [ ] Appel `StripeCheckoutService.create_checkout_session(...)`
      - [ ] Audit succès/échec
      - [ ] Gestion des erreurs : `StripeCheckoutServiceError(code="stripe_unavailable")` → 503, `code="plan_price_not_configured"` → 422, `code="stripe_api_error"` → 502

- [ ] **Tests unitaires** (AC: 13)
  - [ ] Créer `backend/app/tests/unit/test_stripe_checkout_service.py`
  - [ ] Test nominal avec `stripe_customer_id` existant : `customer` présent dans params
  - [ ] Test nominal sans `stripe_customer_id` : `customer_email` présent dans params
  - [ ] Test `stripe_unavailable` : `get_stripe_client()` retourne `None` → `StripeCheckoutServiceError(code="stripe_unavailable")`
  - [ ] Test `plan_price_not_configured` : plan absent de la map → `StripeCheckoutServiceError(code="plan_price_not_configured")`
  - [ ] Test `stripe_api_error` : `client.checkout.sessions.create` lève `stripe.StripeError` → `StripeCheckoutServiceError(code="stripe_api_error")`

- [ ] **Tests d'intégration** (AC: 14)
  - [ ] Créer `backend/app/tests/integration/test_stripe_checkout_api.py`
  - [ ] Test 401 sans token
  - [ ] Test 403 rôle invalide (rôle `"support"`)
  - [ ] Test 422 plan invalide (`"gold"`)
  - [ ] Test 503 Stripe non configuré (patch `get_stripe_client` retourne `None`)
  - [ ] Test 422 plan non configuré (patch `STRIPE_PRICE_ENTITLEMENT_MAP` vide)
  - [ ] Test 200 nominal (patch `get_stripe_client` retourne mock, `session.url = "https://checkout.stripe.com/..."`)

- [ ] **Validation finale** (AC: 12)
  - [ ] `ruff check backend --fix && ruff check backend` → 0 erreur
  - [ ] `pytest -q backend` → tous les tests passent

## Dev Notes

### Appel SDK stripe-python v14.4.1 avec StripeClient

Le pattern `StripeClient` (confirmé en 61-2) utilise des ressources dédiées :

```python
client = get_stripe_client()  # depuis app.integrations.stripe_client
session = client.checkout.sessions.create(params={
    "mode": "subscription",
    "line_items": [{"price": price_id, "quantity": 1}],
    "success_url": success_url,
    "cancel_url": cancel_url,
    "client_reference_id": str(user_id),
    "metadata": {"app_user_id": str(user_id)},
    # SOIT :
    "customer": stripe_customer_id,   # si profil a déjà un customer_id Stripe
    # OU :
    "customer_email": user_email,     # si pas encore de customer Stripe
    # Ne jamais passer les deux en même temps (erreur Stripe)
})
checkout_url = session.url
```

**Ne jamais passer `customer` et `customer_email` simultanément** — Stripe retourne une erreur `400` dans ce cas.

### Résolution inverse `plan` → `price_id`

`STRIPE_PRICE_ENTITLEMENT_MAP` mappe `price_id → plan` (ex: `{"price_1Xxx": "basic"}`). Pour la création de session, il faut la direction inverse (`plan → price_id`). Implémenter dans le service :

```python
def _plan_to_price_id(plan: str) -> str | None:
    """Résolution inverse : plan applicatif → Stripe Price ID."""
    for price_id, mapped_plan in STRIPE_PRICE_ENTITLEMENT_MAP.items():
        if mapped_plan == plan:
            return price_id
    return None
```

Si `STRIPE_PRICE_ENTITLEMENT_MAP` est vide (variables d'env Stripe absentes), retourner `None` → `StripeCheckoutServiceError(code="plan_price_not_configured")`.

### Récupération de l'email utilisateur

L'endpoint a besoin de l'email de l'utilisateur courant (`current_user.email`) pour le passer à Stripe si aucun `stripe_customer_id` n'existe. Vérifier que `AuthenticatedUser` expose bien un champ `email` (c'est le cas dans `app.api.dependencies.auth`).

### Pattern d'erreur `StripeCheckoutServiceError`

Reproduire le même pattern que `BillingServiceError` dans `billing_service.py` :

```python
class StripeCheckoutServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
```

### Mapping codes d'erreur → HTTP dans le router

| `StripeCheckoutServiceError.code` | HTTP status |
|---|---|
| `stripe_unavailable` | 503 |
| `plan_price_not_configured` | 422 |
| `stripe_api_error` | 502 |
| Tout autre code | 422 |

### `success_url` avec `{CHECKOUT_SESSION_ID}`

La valeur par défaut de `STRIPE_CHECKOUT_SUCCESS_URL` contient le placeholder `{CHECKOUT_SESSION_ID}` (syntaxe Stripe, avec accolades littérales). Stripe remplace ce placeholder par l'ID de session réel lors de la redirection. **Ne pas échapper ces accolades en Python** lors de la lecture depuis `os.getenv` — la chaîne est passée telle quelle à l'API Stripe.

```python
# ✅ CORRECT — accolades littérales préservées
self.stripe_checkout_success_url = os.getenv(
    "STRIPE_CHECKOUT_SUCCESS_URL",
    "http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}",
).strip()
```

### Mock pattern dans les tests

Pour éviter tout appel réseau dans les tests, utiliser `unittest.mock.patch` sur `get_stripe_client` :

```python
from unittest.mock import MagicMock, patch
from app.integrations import stripe_client as sc

def test_create_checkout_session_nominal():
    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch.object(sc, "get_stripe_client", return_value=mock_client):
        ...
```

Pour les tests d'intégration HTTP, patcher au niveau du module service :

```python
from unittest.mock import patch, MagicMock
from app.services import stripe_checkout_service as svc

def test_stripe_checkout_200():
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = MagicMock(
        url="https://checkout.stripe.com/pay/cs_test_abc"
    )
    with patch("app.services.stripe_checkout_service.get_stripe_client", return_value=mock_client):
        response = client.post(
            "/v1/billing/stripe-checkout-session",
            json={"plan": "basic"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
    assert response.status_code == 200
    assert "checkout_url" in response.json()["data"]
```

### Récupération de l'email depuis `current_user`

Inspecter le modèle `AuthenticatedUser` dans `backend/app/api/dependencies/auth.py` pour confirmer le champ `email`. Si le champ n'existe pas directement sur `AuthenticatedUser`, faire une requête DB pour récupérer l'email depuis `UserModel`.

### Pièges hérités de 61-1 et 61-2 (à ne pas réintroduire)

- Ne PAS appeler `db.rollback()` après `begin_nested()` dans `get_or_create_profile`.
- `cancel_at_period_end` peut être `null` côté Stripe — forcer `bool(... or False)`.
- `stripe_price_id` peut être absent d'un event — garde `if price_id:` avant assignment.
- Ne PAS utiliser `stripe.api_key = ...` au niveau global — utiliser uniquement `get_stripe_client()`.

### Fichiers à créer

- `backend/app/services/stripe_checkout_service.py` — service + `StripeCheckoutServiceError`
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/integration/test_stripe_checkout_api.py`

### Fichiers à modifier

| Fichier | Changement |
|---|---|
| `backend/app/core/config.py` | 2 nouveaux attributs dans `Settings.__init__` (bloc Stripe) |
| `backend/app/api/v1/routers/billing.py` | Imports + modèles Pydantic + endpoint `POST /stripe-checkout-session` |
| `.env.example` (racine) | 2 nouvelles variables dans la section Stripe |

### Fichiers à NE PAS TOUCHER

- `backend/app/services/billing_service.py` (service simulé legacy — ne pas modifier)
- `backend/app/services/stripe_billing_profile_service.py` (ne pas modifier la logique existante)
- `backend/app/integrations/stripe_client.py` (ne pas modifier)
- Toute migration Alembic existante (pas de migration dans cette story)
- `backend/app/infra/db/models/stripe_billing.py`

### Structure des dossiers à vérifier avant implémentation

```
backend/app/
├── api/v1/routers/billing.py         ← modifier (ajouter endpoint)
├── core/config.py                    ← modifier (2 variables)
├── integrations/stripe_client.py     ← importer, NE PAS modifier
├── services/
│   ├── billing_service.py            ← NE PAS toucher
│   ├── stripe_billing_profile_service.py  ← importer, NE PAS modifier
│   └── stripe_checkout_service.py   ← CRÉER
└── tests/
    ├── unit/
    │   └── test_stripe_checkout_service.py  ← CRÉER
    └── integration/
        └── test_stripe_checkout_api.py  ← CRÉER
```

### Project Structure Notes

- Services → `backend/app/services/` (logique métier, jamais dans routers ni infra)
- Le service `StripeCheckoutService` importe depuis `app.integrations.stripe_client` et `app.services.stripe_billing_profile_service`
- Dépendances Python → `backend/pyproject.toml` uniquement (stripe==14.4.1 déjà installé en 61-2)
- Pas de migration DB nécessaire dans cette story

### References

- Story 61-1 : `_bmad-output/implementation-artifacts/61-1-mapping-stripe-billing-profiles.md`
- Story 61-2 : `_bmad-output/implementation-artifacts/61-2-installation-sdk-stripe-et-configuration-secrets.md`
- Service existant : `backend/app/services/stripe_billing_profile_service.py`
- Client Stripe : `backend/app/integrations/stripe_client.py`
- Router billing existant : `backend/app/api/v1/routers/billing.py`
- Config existante : `backend/app/core/config.py` lignes 274–280
- Stripe Checkout Sessions API : [stripe.com/docs/api/checkout/sessions/create](https://stripe.com/docs/api/checkout/sessions/create)
- SDK Python stripe v14.4.1 : pattern `client.checkout.sessions.create(params={...})`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
