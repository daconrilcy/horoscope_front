# Story CS-005 define-central-stripe-timeout-and-retry-policy: Define a central Stripe timeout and retry policy

Status: done

## 1. Objective

Rendre explicite et unique la politique applicative de timeout/retry des appels Stripe au niveau du client infra central.
Verifier ensuite que checkout, portal, validation startup, hydration webhook et refresh admin consomment ce client sans proprietaire concurrent.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/stripe-implementation/2026-05-03-1659/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-002` constate que le client central configure `stripe_version`, mais aucun timeout ni `max_network_retries`.

## 3. Domain Boundary

- Domain: `backend/app/infra/stripe`
- In scope:
  - Politique centrale app-owned pour timeout et retries Stripe.
  - Tests du client Stripe et des services checkout, portal, webhook hydration, startup validation et admin refresh.
  - Garde anti-drift prouvant que le client infra reste le proprietaire unique de ces reglages.
  - Documentation locale si les valeurs retenues sont utiles aux operateurs.
- Out of scope:
  - Changement de version API Stripe.
  - Refactor repository/persistence billing.
  - Changement des schemas publics billing ou admin.
  - Ajout d'un second wrapper client Stripe.
- Explicit non-goals:
  - Ne pas contourner l'ownership infra client protege par `RG-006`.
  - Ne pas changer le mode local Stripe opt-in protege par `RG-024`.
  - Ne pas modifier les erreurs HTTP centralisees protegees par `RG-004` au-dela du mapping necessaire des echecs Stripe existants.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les appels Stripe doivent respecter les valeurs centrales retenues.
  - Les contrats HTTP existants doivent conserver leurs status codes et enveloppes, sauf difference explicitement justifiee pour timeout/transient failure.
  - Webhook hydration doit adopter une decision fail-open ou fail-closed explicite avant implementation.
- Deletion allowed: no
- Replacement allowed: yes

## 5. Target State

- Une politique centrale documentee definit les valeurs de timeout et retry Stripe.
- Le client infra Stripe applique ces valeurs a chaque instance cachee.
- Les services checkout, portal, webhook hydration, startup validation et admin refresh continuent de consommer `get_stripe_client`.
- Des tests prouvent le mapping d'erreurs sur timeout/transient failure pour les surfaces critiques.
- Une garde empeche les reglages concurrents ou un second client owner.

## 6. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-004` - les erreurs HTTP applicatives doivent rester centralisees.
  - `RG-006` - les services/infra ne doivent pas importer `app.api` et l'API ne doit pas posseder le client Stripe.
  - `RG-024` - le demarrage local Stripe reste opt-in et ne doit pas devenir obligatoire.
- Required regression evidence:
  - Tests client Stripe, checkout, portal, startup validation, webhook API et scans central-client.
- Allowed differences:
  - Ajout de valeurs settings/env example pour timeout/retry.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le client central applique une politique reseau Stripe explicite. | loaded config via `pytest -q app/tests/unit/test_stripe_client.py`. |
| AC2 | La politique reseau Stripe reste centralisee hors consommateurs. | `rg -n "timeout|max_network_retries|StripeClient" app`. |
| AC3 | Les use cases de session Stripe conservent leurs mappings d'erreur. | `pytest -q app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py`. |
| AC4 | Les hydrations Stripe transitoires ont une decision testee. | `pytest -q app/tests/unit/test_stripe_portal_startup_validation.py app/tests/integration/test_stripe_webhook_api.py`. |
| AC5 | La documentation operateur suit la source config. | `pytest -q app/tests/unit/test_stripe_client.py` plus scan docs/settings. |

## 8. Implementation Tasks

- [ ] Task 1 - Choisir et documenter les valeurs app-owned de timeout/retry (AC: AC1, AC5)
- [ ] Task 2 - Configurer le client infra Stripe central (AC: AC1, AC2)
- [ ] Task 3 - Couvrir les surfaces d'erreur Stripe critiques (AC: AC3, AC4)
- [ ] Task 4 - Ajouter une garde anti-drift central-client (AC: AC2, AC5)
- [ ] Task 5 - Capturer l'evidence after et executer validation (AC: AC1, AC2, AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `app.infra.stripe.client.get_stripe_client` comme unique factory SDK Stripe.
  - `app.core.config.settings` si les valeurs deviennent configurables.
  - Tests Stripe existants sous `backend/app/tests/unit` et `backend/app/tests/integration`.
- Do not recreate:
  - Un wrapper client Stripe parallele.
  - Des constantes timeout/retry dans chaque service.
  - Une gestion d'erreur HTTP dans le client infra.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- `stripe.StripeClient(` hors `backend/app/infra/stripe/client.py`
- `max_network_retries` hors allowlist centrale
- Timeout Stripe local dans `backend/app/services/billing/**` ou `backend/app/api/**`
- Nouveau fichier de dependances Python ou `requirements.txt`

## 11. Files to Inspect First

- `backend/app/infra/stripe/client.py`
- `backend/app/core/config.py`
- `.env.example`
- `backend/app/services/billing/stripe_checkout_service.py`
- `backend/app/services/billing/stripe_customer_portal_service.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/startup/stripe_portal_validation.py`
- `backend/app/tests/unit/test_stripe_client.py`
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/unit/test_stripe_customer_portal_service.py`
- `backend/app/tests/unit/test_stripe_portal_startup_validation.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `_condamad/stories/regression-guardrails.md`

## 12. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/infra/stripe app/core/config.py app/services/billing `
  app/startup/stripe_portal_validation.py app/tests/unit/test_stripe_client.py `
  app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py `
  app/tests/unit/test_stripe_portal_startup_validation.py app/tests/integration/test_stripe_webhook_api.py
pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py `
  app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py `
  app/tests/integration/test_stripe_webhook_api.py
rg -n "timeout|max_network_retries|StripeClient\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"
rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe app/startup -g "*.py"
```

## 13. References

- `_condamad/audits/stripe-implementation/2026-05-03-1659/01-evidence-log.md`
- `_condamad/audits/stripe-implementation/2026-05-03-1659/02-finding-register.md`
- `_condamad/audits/stripe-implementation/2026-05-03-1659/03-story-candidates.md#SC-002`
- `_condamad/stories/regression-guardrails.md`
