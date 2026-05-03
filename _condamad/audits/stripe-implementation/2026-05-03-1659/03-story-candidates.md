# Story Candidates - stripe-implementation

<!-- Stories redigees avec le skill condamad-story-writer le 2026-05-03. -->

## SC-001 -> CS-004

- Candidate ID: SC-001
- Story ID: CS-004
- Story key: `move-admin-stripe-subscription-refresh-behind-billing-service-boundary`
- Source finding: F-001
- Story title: Move admin Stripe subscription refresh behind a billing service boundary
- Status: ready-to-dev
- Story path: `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/00-story.md`
- Primary archetype: `service-boundary-refactor`
- Primary domain: `backend/app/services/billing`
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Allowlist Exception, Contract Shape, Reintroduction Guard, Persistent Evidence.
- Regression guardrails: `RG-004`, `RG-005`, `RG-006`.

### Objective

Deplacer l'orchestration du refresh force Stripe admin hors du routeur HTTP vers un use case billing/admin unique, tout en preservant le contrat runtime de `POST /v1/admin/users/{user_id}/refresh-subscription`: autorisation admin, codes d'erreur, payload d'audit et reponse `{"status": "success"}`.

### Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `refresh_subscription` reste expose en runtime avec le meme chemin/methode et une reponse succes `{"status": "success"}`. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/integration/test_admin_stripe_actions_api.py` plus assertion `app.openapi()`. |
| AC2 | Aucun routeur sous `backend/app/api/v1/routers` ne recupere ni n'appelle directement le client Stripe SDK. | Evidence profile: `targeted_forbidden_symbol_scan`; test de garde ou `rg -n "get_stripe_client\\(|stripe_client\\.|client\\.subscriptions" app/api/v1/routers` avec zero hit applicable. |
| AC3 | Le refresh force est orchestre par un service billing/admin qui gere recuperation Stripe, payload `admin.forced_refresh`, sync profile et audit. | Evidence profile: `ast_architecture_guard`; tests unitaires service dans `app/tests/unit/test_stripe_billing_profile_service.py` ou nouveau test dedie. |
| AC4 | Les erreurs existantes restent mappees avec des statuts/messages equivalents pour subscription absente, client Stripe absent et exception Stripe. | Evidence profile: `json_contract_shape`; tests d'integration admin Stripe couvrant les cas d'erreur. |
| AC5 | Les couches billing/infra ne dependent pas de `app.api` ni de FastAPI pour realiser le use case. | Evidence profile: `repo_wide_negative_scan`; `rg -n "from app\\.api|import app\\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"` avec zero hit non allowliste. |

### Implementation Tasks

- [ ] Task 1 - Capturer le baseline route/ownership avant modification (AC: AC1, AC2)
- [ ] Task 2 - Creer ou reutiliser un use case service billing/admin pour le refresh force (AC: AC3, AC4, AC5)
- [ ] Task 3 - Amincir le routeur admin (AC: AC1, AC2, AC4)
- [ ] Task 4 - Adapter les tests et ajouter la garde anti-retour (AC: AC2, AC3, AC4, AC5)
- [ ] Task 5 - Capturer l'evidence after et executer la validation (AC: AC1, AC2, AC3, AC4, AC5)

### Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/api/v1/routers/admin/users.py app/services/billing app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py
pytest -q app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py
python -c "from app.main import app; assert '/v1/admin/users/{user_id}/refresh-subscription' in app.openapi()['paths']"
rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers
rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"
```

## SC-002 -> CS-005

- Candidate ID: SC-002
- Story ID: CS-005
- Story key: `define-central-stripe-timeout-and-retry-policy`
- Source finding: F-002
- Story title: Define a central Stripe timeout and retry policy
- Status: ready-to-dev
- Story path: `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/00-story.md`
- Primary archetype: `architecture-guard-hardening`
- Primary domain: `backend/app/infra/stripe`
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Allowlist Exception, Reintroduction Guard, Persistent Evidence.
- Regression guardrails: `RG-004`, `RG-006`, `RG-024`.
- User decision required if: webhook hydration fail-open/fail-closed semantics need to change, or timeout/retry values cannot be chosen from current app/ops expectations.

### Objective

Rendre explicite et unique la politique applicative de timeout/retry des appels Stripe en la configurant au niveau du client infra central, puis verifier que checkout, portal, validation startup, hydration webhook et refresh admin consomment ce client sans proprietaire concurrent ni comportement d'erreur incoherent.

### Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le client Stripe central applique des valeurs app-owned explicites pour timeout et retry. | Evidence profile: loaded config/runtime client; `pytest -q app/tests/unit/test_stripe_client.py` assert les options effectives. |
| AC2 | Aucun service, routeur ou module startup ne declare une politique timeout/retry Stripe concurrente. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "timeout|max_network_retries|StripeClient\\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"` avec allowlist exacte. |
| AC3 | Checkout et customer portal conservent leurs mappings d'erreur sur client absent, timeout ou erreur Stripe transitoire. | Evidence profile: `api_error_shape_contract`; `pytest -q app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py`. |
| AC4 | Startup portal validation et webhook hydration ont une decision explicite fail-open/fail-closed sur timeout/transient failure et des tests couvrent cette decision. | Evidence profile: `runtime_contract_preservation`; `pytest -q app/tests/unit/test_stripe_portal_startup_validation.py app/tests/integration/test_stripe_webhook_api.py`. |
| AC5 | La politique est documentee si elle est operable via settings/env, et les exemples locaux restent compatibles avec Stripe opt-in. | Evidence profile: `reintroduction_guard`; test docs/assets existant si doc modifiee, plus scan `rg -n "STRIPE_.*TIMEOUT|STRIPE_.*RETRY|max_network_retries" docs .env.example backend/app`. |

### Implementation Tasks

- [ ] Task 1 - Choisir et documenter les valeurs app-owned de timeout/retry (AC: AC1, AC5)
- [ ] Task 2 - Configurer le client infra Stripe central (AC: AC1, AC2)
- [ ] Task 3 - Couvrir les surfaces d'erreur Stripe critiques (AC: AC3, AC4)
- [ ] Task 4 - Ajouter une garde anti-drift central-client (AC: AC2, AC5)
- [ ] Task 5 - Capturer l'evidence after et executer validation (AC: AC1, AC2, AC3, AC4, AC5)

### Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/infra/stripe app/core/config.py app/services/billing app/startup/stripe_portal_validation.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/integration/test_stripe_webhook_api.py
pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/integration/test_stripe_webhook_api.py
rg -n "timeout|max_network_retries|StripeClient\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"
rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe app/startup -g "*.py"
```

## Needs User Decision

### F-003

- Decision needed: whether to converge Stripe billing persistence toward repositories/ports now, or accept current SQLAlchemy-in-service style as a local architecture exception until a broader billing persistence refactor.
- Reason: the current code is tested and stable, but it does not match the strict service-boundary contract that prefers infra/repository ownership for persistence access.
