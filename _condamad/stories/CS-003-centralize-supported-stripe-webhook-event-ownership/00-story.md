# Story CS-003 centralize-supported-stripe-webhook-event-ownership: Centralize supported Stripe webhook event ownership

Status: ready-to-review

## 1. Objective

Creer un registre canonique unique des evenements webhook Stripe supportes par le backend billing.
Ce registre doit alimenter dispatch, resolution utilisateur, documentation locale et gardes de parite.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/stripe-implementation/2026-05-03-1003/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-003` signale une duplication entre runtime, resolver, docs, scripts et tests pour les types d'evenements Stripe.

## 3. Domain Boundary

- Domain: `backend/app/services/billing`
- In scope:
  - Registre canonique des evenements webhook supportes.
  - Refactor de `StripeWebhookService.handle_event`.
  - Refactor de `_resolve_user_id`.
  - Parite docs, script PowerShell local, tests et garde locale.
- Out of scope:
  - Changement de version API Stripe.
  - Changement de semantique d'acquittement des echecs signes.
  - Ajout de nouveaux flux de facturation.
- Explicit non-goals:
  - Ne pas casser le demarrage local opt-in Stripe protege par `RG-024`.
  - Ne pas modifier les contrats d'erreur API proteges par `RG-004`.
  - Ne pas ajouter un second registre local dans docs ou tests.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: registry-catalog-refactor
- Behavior change allowed: constrained
- Behavior constraints:
  - Les evenements intentionnellement supportes restent traites.
  - Les evenements non supportes comme `invoice.payment_succeeded` restent ignores.
  - `checkout.session.async_payment_succeeded` et `subscription_schedule.*` doivent etre classes explicitement.
- Deletion allowed: no
- Replacement allowed: yes

## 5. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le registre doit etre prouve comme source des decisions runtime. |
| Baseline Snapshot | yes | La liste actuelle dispersee doit etre capturee avant convergence. |
| Ownership Routing | yes | Le proprietaire canonique doit etre un module billing non-API. |
| Contract Shape | yes | La forme du registre exporte et des groupes typed doit etre explicite. |
| Batch Migration | yes | Plusieurs consommateurs doivent migrer vers le registre. |
| Reintroduction Guard | yes | Les listes concurrentes ne doivent pas revenir. |
| Persistent Evidence | yes | La parite avant/apres doit etre conservee. |

## 6. Contract Shape

- Contract type: Python registry export for Stripe webhook event ownership.
- Fields:
  - `event_type: str`
  - `user_resolution: str`
  - `handler_group: str`
  - `local_listener: bool`
  - `documentation_note: str | None`
- Registry field names are internal Python names and do not define a JSON API.
- Frontend type impact: none.
- Generated contract impact: OpenAPI must not change.

## 7. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Event list baseline | `evidence/webhook-event-registry-baseline.md` | Record current service, docs, script, and test event lists. |
| Event list after | `evidence/webhook-event-registry-after.md` | Prove every consumer validates against the canonical registry. |

## 8. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-005` - event ownership must stay outside the API route.
  - `RG-006` - services must not import `app.api`.
  - `RG-024` - PowerShell local listener remains the canonical opt-in Stripe local dev path.
- Non-applicable invariants:
  - `RG-004` - this story does not change API error envelopes.
  - `RG-023` - this story modifies an existing script at most and does not add root scripts.
- Required regression evidence:
  - Registry parity tests, webhook service tests, webhook API tests, and target scans for duplicated event lists.

## 9. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Canonical registry exists outside API. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py`. |
| AC2 | Dispatch consumes registry. | `pytest -q app/tests/unit/test_stripe_webhook_service.py` plus dispatch scan. |
| AC3 | User resolution consumes registry grouping. | `pytest -q app/tests/unit/test_stripe_webhook_service.py` plus resolver scan. |
| AC4 | Local docs match registry. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py`. |
| AC5 | Unsupported invoice success remains ignored. | `pytest -q app/tests/integration/test_stripe_webhook_api.py`. |

## 10. Implementation Tasks

- [x] Task 1 - Capture current event-list baseline (AC: AC1, AC4)
- [x] Task 2 - Create canonical registry (AC: AC1)
- [x] Task 3 - Migrate runtime service consumption (AC: AC2, AC3, AC5)
- [x] Task 4 - Migrate docs and guards (AC: AC4)
- [x] Task 5 - Add anti-drift proof (AC: AC1, AC2, AC3, AC4)

## 11. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- duplicated tuple of `subscription_schedule.created`
- duplicated tuple of `checkout.session.async_payment_succeeded`
- `scripts/stripe-listen-webhook.sh`

## 12. Files to Inspect First

- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `scripts/stripe-listen-webhook.ps1`
- `docs/billing-webhook-local-testing.md`
- `docs/stripe-webhook-dev.md`

## 13. Expected Files to Modify

- `backend/app/services/billing/stripe_webhook_events.py`
- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `docs/billing-webhook-local-testing.md`
- `docs/stripe-webhook-dev.md`
- `scripts/stripe-listen-webhook.ps1`

## 14. Dependency Policy

- New dependencies: none.

## 15. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/services/billing/stripe_webhook_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py
pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py
python -c "from app.main import app; assert '/v1/billing/stripe-webhook' in app.openapi()['paths']"
rg -n "subscription_schedule|checkout.session.async_payment_succeeded" app/services/billing ../docs ../scripts app/tests
```

## 16. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not preserve legacy behavior for convenience.
- Do not bypass convergence through wrapper, alias, fallback, or re-export.
