# Story CS-002 upgrade-stripe-api-version-with-webhook-contract-validation: Upgrade Stripe API version with webhook contract validation

Status: ready-for-review

## 1. Objective

Mettre a niveau la version API Stripe configuree par defaut vers `2026-04-22.dahlia`.
La validation couvre checkout, portail client, facturation, subscription schedule et webhook.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/stripe-implementation/2026-05-03-1003/03-story-candidates.md`
- Reason for change: le finding `F-002` indique que la version par defaut `2024-12-18.acacia` est obsolete selon l'audit du 2026-05-03.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/infra/stripe`
- In scope:
  - Version API Stripe chargee dans `settings.stripe_api_version`.
  - Client Stripe infra.
  - Tests checkout, portail client, webhook et version du client.
  - Documentation des attentes webhook et rollback de version.
- Out of scope:
  - Migration du compte Stripe production dans le Dashboard.
  - Changement des produits, prix ou plans Stripe.
  - Ajout de nouveau flux de paiement.
- Explicit non-goals:
  - Ne pas recreer `backend/app/integrations/stripe_client.py`.
  - Ne pas changer les invariants webhook proteges par `RG-004` et `RG-006`.
  - Ne pas ajouter de dependance Stripe alternative.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story change une configuration runtime externe tout en preservant les contrats applicatifs existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - La valeur par defaut devient `2026-04-22.dahlia`.
  - Les appels checkout, portail client, invoice preview, subscription schedule et webhook gardent leurs formes testees.
  - Le SDK `stripe==14.4.1` reste accepte seulement si les tests prouvent sa compatibilite.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le compte Stripe production ne peut pas etre aligne sur `2026-04-22.dahlia` maintenant.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La version effective vient de `settings` et du client Stripe runtime. |
| Baseline Snapshot | yes | Les assumptions payload avant mise a niveau doivent etre comparees aux tests apres changement. |
| Ownership Routing | no | Aucun transfert de responsabilite entre packages n'est requis. |
| Allowlist Exception | no | Aucune exception de gouvernance n'est autorisee par cette story. |
| Contract Shape | yes | Les payloads Stripe traites par les services et webhooks doivent rester explicites. |
| Batch Migration | no | Aucun lot de migration multi-consommateur n'est requis. |
| Reintroduction Guard | no | Aucun ancien module ou chemin n'est supprime par cette story. |
| Persistent Evidence | yes | La verification de compatibilite SDK et payloads doit etre persistante. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `settings.stripe_api_version` charge depuis `STRIPE_API_VERSION`.
  - Instance `stripe.StripeClient` creee par `backend/app/infra/stripe/client.py`.
- Secondary evidence:
  - `.env.example`, tests unitaires client Stripe, tests des services billing.
- Static scans alone are not sufficient for this story because:
  - La valeur pertinente est la configuration chargee au runtime et transmise au SDK Stripe.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/evidence/stripe-api-version-baseline.md`
- Comparison after implementation:
  - `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/evidence/stripe-api-version-after.md`
- Expected invariant:
  - Les contrats applicatifs checkout, portail client et webhook restent valides avec la nouvelle version.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: this story preserves the current canonical owner `backend/app/infra/stripe/client.py`.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - Loaded configuration plus Stripe SDK request and webhook payload assumptions.
- Fields:
  - `STRIPE_API_VERSION: string` controls Stripe API version.
  - `stripe_version: string` is passed to `stripe.StripeClient`.
  - Webhook event fields consumed include `id`, `type`, `data.object`, `customer`, and `client_reference_id`.
- Required fields:
  - `STRIPE_API_VERSION`.
  - `stripe_event.id`, `stripe_event.type`, `stripe_event.data.object`.
- Optional fields:
  - `customer`, `client_reference_id`, subscription schedule fields present only for their event families.
- Status codes:
  - No public HTTP status change is allowed by this story.
- Serialization names:
  - Environment name remains `STRIPE_API_VERSION`.
  - Stripe event wire names remain unchanged.
- Frontend type impact:
  - None expected; frontend receives existing backend billing contracts only.
- Generated contract impact:
  - OpenAPI for billing endpoints must not change except metadata unrelated to this story.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Version baseline | `evidence/stripe-api-version-baseline.md` | Record old default and installed SDK version. |
| Compatibility result | `evidence/stripe-api-version-after.md` | Record new default, SDK decision, tests, and rollback guidance. |

## 4i. Reintroduction Guard

- Reintroduction guard: not applicable
- Reason: no removed, forbidden, or converged-away legacy surface can be reintroduced by this story.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/stripe-implementation/2026-05-03-1003/01-evidence-log.md` - `E-015` records default `2024-12-18.acacia` and SDK `14.4.1`.
- Evidence 2: `backend/app/core/config.py` - `settings.stripe_api_version` defaults to `2024-12-18.acacia`.
- Evidence 3: `.env.example` - `STRIPE_API_VERSION=2024-12-18.acacia`.
- Evidence 4: `backend/app/infra/stripe/client.py` - the infra client passes `settings.stripe_api_version` into `stripe.StripeClient`.
- Evidence 5: `backend/app/tests/unit/test_stripe_client.py` - tests assert the current version through mocked settings.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- `STRIPE_API_VERSION` defaults to `2026-04-22.dahlia` in code and `.env.example`.
- The infra Stripe client uses the updated version without recreating legacy integration paths.
- Tests prove checkout, portal, invoice preview, subscription schedule and webhook assumptions still hold.
- Documentation states endpoint version expectations and rollback instructions.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-004` - API error behavior must remain centralized.
  - `RG-006` - Stripe services and infra must not depend on `app.api`.
- Non-applicable invariants:
  - `RG-024` - this story does not change local dev startup scripts.
  - `RG-023` - this story does not add root scripts.
- Required regression evidence:
  - Stripe client unit tests, billing service tests, webhook integration tests, and import boundary scan.
- Allowed differences:
  - Effective default Stripe API version changes from `2024-12-18.acacia` to `2026-04-22.dahlia`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime settings default is `2026-04-22.dahlia`. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_stripe_client.py` plus loaded settings command. |
| AC2 | Infra Stripe client passes the configured version. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_stripe_client.py`. |
| AC3 | Billing Stripe flows keep existing backend contracts. | Evidence profile: `json_contract_shape`; test path `app/tests/unit/test_stripe_checkout_service.py`. |
| AC4 | Public billing integration tests still pass. | Evidence profile: `runtime_openapi_contract`; test path `app/tests/integration/test_stripe_webhook_api.py`. |
| AC5 | Upgrade evidence records SDK decision. | Evidence profile: `baseline_before_after_diff`; `rg -n "stripe==14.4.1|2026-04-22.dahlia|rollback" ../docs`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture current version baseline (AC: AC1, AC5)
  - [x] Record current default, `.env.example` value, and installed SDK version.
  - [x] Record affected Stripe service tests before editing.
- [x] Task 2 - Update runtime configuration default (AC: AC1, AC2)
  - [x] Change `backend/app/core/config.py`.
  - [x] Change `.env.example`.
  - [x] Update client tests that assert configured version behavior.
- [x] Task 3 - Validate Stripe flow compatibility (AC: AC3, AC4)
  - [x] Review checkout session creation payload assumptions.
  - [x] Review customer portal, invoice preview, upgrade, and subscription schedule assumptions.
  - [x] Review webhook payload assumptions for supported events.
- [x] Task 4 - Persist upgrade decision (AC: AC5)
  - [x] Document whether `stripe==14.4.1` remains acceptable.
  - [x] Document webhook endpoint version expectations and rollback procedure.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/infra/stripe/client.py` as the only Stripe SDK client owner.
  - Existing billing service tests for compatibility proof.
  - Existing docs for webhook behavior and Stripe local testing.
- Do not recreate:
  - `backend/app/integrations/stripe_client.py`.
  - A second settings variable for Stripe API version.
  - A per-service Stripe API version override.
- Shared abstraction allowed only if:
  - It removes concrete duplication in Stripe API version access and remains under `backend/app/infra/stripe`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/integrations/stripe_client.py`
- `from app.integrations.stripe_client`
- default `STRIPE_API_VERSION=2024-12-18.acacia`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Stripe SDK client construction | `backend/app/infra/stripe/client.py` | `backend/app/integrations/stripe_client.py` |
| Stripe API version configuration | `backend/app/core/config.py` | Per-service constants |
| Developer environment sample | `.env.example` | Duplicated docs-only defaults |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: applicable
- Required generated-contract evidence:
  - Runtime OpenAPI billing paths remain present.
  - No public billing response schema changes occur.
  - Generated client impact is documented as none or listed with evidence.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/core/config.py`
- `.env.example`
- `backend/app/infra/stripe/client.py`
- `backend/app/services/billing/stripe_checkout_service.py`
- `backend/app/services/billing/stripe_customer_portal_service.py`
- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/tests/unit/test_stripe_client.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/core/config.py` - update default Stripe API version.
- `.env.example` - update sample Stripe API version.
- `backend/app/tests/unit/test_stripe_client.py` - update expectations.
- `docs/billing-webhook-local-testing.md` - document endpoint version expectations or link the evidence artifact.

Likely tests:

- `backend/app/tests/unit/test_stripe_client.py` - settings and client version assertions.
- `backend/app/tests/unit/test_stripe_checkout_service.py` - checkout payload compatibility.
- `backend/app/tests/unit/test_stripe_customer_portal_service.py` - portal and upgrade compatibility.
- `backend/app/tests/unit/test_stripe_webhook_service.py` - webhook payload compatibility.

Files not expected to change:

- `frontend/src/api/billing.ts` - backend public billing contracts should not change.
- `backend/app/infra/stripe/__init__.py` - package export should remain minimal.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/infra/stripe/client.py app/core/config.py app/services/billing app/tests/unit/test_stripe_client.py
pytest -q app/tests/unit/test_stripe_client.py
pytest -q app/tests/unit/test_stripe_checkout_service.py
pytest -q app/tests/unit/test_stripe_customer_portal_service.py
pytest -q app/tests/unit/test_stripe_webhook_service.py
pytest -q app/tests/integration/test_stripe_checkout_api.py
pytest -q app/tests/integration/test_stripe_customer_portal_api.py
pytest -q app/tests/integration/test_stripe_webhook_api.py
python -c "from app.core.config import Settings; assert Settings().stripe_api_version == '2026-04-22.dahlia'"
rg -n "2024-12-18\.acacia|app\.integrations\.stripe_client|app/integrations/stripe_client.py" app tests ../.env.example ../docs
```

## 22. Regression Risks

- Risk: SDK version cannot send the requested Stripe API version.
  - Guardrail: client test and evidence artifact must record the SDK decision.
- Risk: Webhook payload assumptions drift under the new version.
  - Guardrail: webhook unit and integration tests must pass.
- Risk: Legacy integration client returns.
  - Guardrail: existing `test_legacy_integrations_stripe_client_module_is_absent` remains passing.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/stripe-implementation/2026-05-03-1003/00-audit-report.md` - audit verdict and version observation.
- `_condamad/audits/stripe-implementation/2026-05-03-1003/01-evidence-log.md` - evidence `E-015`.
- `_condamad/audits/stripe-implementation/2026-05-03-1003/03-story-candidates.md` - source candidate `SC-002`.
- `_condamad/stories/regression-guardrails.md` - shared non-regression invariants.
