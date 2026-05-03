# Story CS-001 harden-stripe-webhook-failure-retry-semantics: Harden Stripe webhook failure retry semantics

Status: ready-for-review

## 1. Objective

Garantir qu'un evenement Stripe signe dont le traitement metier local echoue ne devienne jamais terminal en silence.
Le choix de mise en oeuvre retenu par cette story est le retry automatique Stripe: l'endpoint doit retourner un statut non-2xx quand le traitement signe echoue.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/stripe-implementation/2026-05-03-1003/03-story-candidates.md`
- Reason for change: le finding `F-001` signale qu'un traitement signe peut etre marque `failed` puis acquitte en HTTP 200.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/billing`
- In scope:
  - Webhook public `/v1/billing/stripe-webhook`.
  - Semantique `StripeWebhookService.handle_event` pour les erreurs de traitement signe.
  - Idempotence `stripe_webhook_events.status = failed`.
  - Documentation du comportement de retry et chemin operateur pour lignes deja `failed`.
- Out of scope:
  - Creation d'une file durable asynchrone.
  - Changement des endpoints checkout ou portail client.
  - Changement du catalogue de plans.
- Explicit non-goals:
  - Ne pas deplacer de logique metier vers `backend/app/api`.
  - Ne pas modifier les invariants `RG-004`, `RG-005`, `RG-006`.
  - Ne pas rendre Stripe obligatoire au demarrage local protege par `RG-024`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: api-contract-change
- Archetype reason: la story change le contrat HTTP observe par Stripe pour les erreurs de traitement signe.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les signatures invalides restent en HTTP 400 avec enveloppe d'erreur existante.
  - Les evenements ignores ou doublons restent acquittes en HTTP 200.
  - Les erreurs internes apres signature valide et traitement tente doivent retourner un non-2xx retryable.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'implementation choisit une file durable asynchrone plutot que le retry automatique Stripe.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le statut HTTP runtime du webhook est le contrat consomme par Stripe. |
| Baseline Snapshot | yes | Le statut actuel 200 pour `failed_internal` doit etre capture puis compare. |
| Ownership Routing | yes | La route reste adaptateur HTTP et le service reste proprietaire du traitement. |
| Allowlist Exception | no | Aucune exception de gouvernance n'est autorisee par cette story. |
| Contract Shape | yes | La forme de reponse et les statuts HTTP du webhook changent. |
| Batch Migration | no | Aucun lot de migration multi-consommateur n'est requis. |
| Reintroduction Guard | yes | Le retour silencieux HTTP 200 sur echec signe ne doit pas revenir. |
| Persistent Evidence | yes | Les preuves avant/apres du contrat webhook doivent etre conservees. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Tests `TestClient` sur `/v1/billing/stripe-webhook` avec signature valide et erreur service.
- Secondary evidence:
  - Scans cibles de `failed_internal`, `mark_failed`, `HTTPException`, `JSONResponse`.
- Static scans alone are not sufficient for this story because:
  - Stripe reagit au statut HTTP effectif, pas a la presence d'un symbole dans le code.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-001-harden-stripe-webhook-failure-retry-semantics/evidence/webhook-failure-http-baseline.md`
- Comparison after implementation:
  - `_condamad/stories/CS-001-harden-stripe-webhook-failure-retry-semantics/evidence/webhook-failure-http-after.md`
- Expected invariant:
  - Seul le cas traitement signe echoue passe de HTTP 200 vers un statut non-2xx retryable.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `backend/app/services/billing/stripe_webhook_service.py` | `backend/app/api/v1/routers/public/billing.py` |
| HTTP-only adapter | `backend/app/api/v1/routers/public/billing.py` | `backend/app/services/billing` |
| Persistence detail | `backend/app/infra/db/models/stripe_webhook_event.py` | `backend/app/api` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - API route response for `POST /v1/billing/stripe-webhook`.
- Fields:
  - `status: string` describes the logical webhook outcome.
  - `code: string` may be present only for existing non-fatal service parse cases.
  - `error: object` follows the shared error envelope for non-2xx adapter responses.
- Required fields:
  - `status` for 2xx webhook acknowledgements.
  - `error.code`, `error.message`, `error.request_id` for error envelope responses.
- Optional fields:
  - `code` for `error_non_fatal` parse cases already handled by the route.
- Status codes:
  - `200` for processed, ignored, duplicate, and documented non-fatal parse cases.
  - `400` for invalid signature.
  - `500` or `503` for signed processing failure requiring Stripe delivery retry.
- Serialization names:
  - Wire names remain `status`, `code`, `error`, `request_id`, `details`.
- Frontend type impact:
  - None; Stripe calls this public webhook and the frontend does not consume it.
- Generated contract impact:
  - OpenAPI responses for `/v1/billing/stripe-webhook` must include the retryable non-2xx response.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Baseline HTTP result | `evidence/webhook-failure-http-baseline.md` | Prove the audited 200 behavior before the fix. |
| After HTTP result | `evidence/webhook-failure-http-after.md` | Prove signed failed processing is retryable after the fix. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- importable Python modules
- frontend route table
- generated OpenAPI paths
- forbidden symbols or states

Required forbidden examples:

- `failed_internal` returned with HTTP 200 from signed webhook processing failure
- `StripeWebhookService.handle_event` swallowing business processing failure as terminal success

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/integration/test_stripe_webhook_api.py` checks the retryable failure status.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/stripe-implementation/2026-05-03-1003/02-finding-register.md` - `F-001` documents the silent terminal failure risk.
- Evidence 2: `backend/app/api/v1/routers/public/billing.py` - the webhook route commits `handle_event` status then returns `{"status": status}`.
- Evidence 3: `backend/app/services/billing/stripe_webhook_service.py` - business processing errors are marked failed then returned as `failed_internal`.
- Evidence 4: `docs/billing-webhook-idempotency.md` - documentation states failed rows let Stripe retry later.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- Signed processing failures persist a `failed` row and return non-2xx so Stripe can retry delivery.
- The route keeps HTTP adapter responsibilities only.
- Existing failed rows have a documented operator reconciliation path.
- Docs describe the actual retry contract.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-004` - webhook error responses must keep centralized API error handling.
  - `RG-005` - route handlers must not own billing business logic.
  - `RG-006` - non-API layers must not import `app.api`.
  - `RG-024` - Stripe local listener remains opt-in for local dev.
- Non-applicable invariants:
  - `RG-009` - this story does not touch the removed API schema package.
  - `RG-023` - this story does not add root scripts.
- Required regression evidence:
  - Targeted webhook API tests, service tests, idempotency tests, and scans for API imports from services.
- Allowed differences:
  - Signed processing failure HTTP status changes from 200 to a retryable non-2xx response.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Signed processing failure returns retryable non-2xx. | Evidence profile: `json_contract_shape`; test path `app/tests/integration/test_stripe_webhook_api.py`. |
| AC2 | Failed rows remain reclaimable on redelivery. | Evidence profile: `json_contract_shape`; test path `app/tests/unit/test_stripe_webhook_idempotency_service.py`. |
| AC3 | Unsupported events remain acknowledged. | Evidence profile: `json_contract_shape`; test path `app/tests/unit/test_stripe_webhook_service.py`. |
| AC4 | API adapter boundary remains intact. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_api_adapter_boundary.py` plus targeted scan. |
| AC5 | Documentation matches retry behavior. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/integration/test_stripe_webhook_api.py` plus targeted docs scan. |

## 8. Implementation Tasks

- [x] Task 1 - Capture current webhook failure baseline (AC: AC1)
  - [x] Write the baseline evidence artifact before editing runtime code.
  - [x] Record current status code and response body for signed processing failure.

- [x] Task 2 - Change signed failure acknowledgement semantics (AC: AC1, AC2)
  - [x] Update `StripeWebhookService` or its result contract so failure is explicit.
  - [x] Update the route to return retryable non-2xx after committing the failed idempotency row.

- [x] Task 3 - Preserve existing success paths (AC: AC2, AC3)
  - [x] Keep processed, duplicate, ignored, and user-not-resolved semantics covered by tests.
  - [x] Ensure failed rows can be reclaimed by a later Stripe delivery.

- [x] Task 4 - Update docs and operator path (AC: AC5)
  - [x] Correct idempotency documentation for Stripe automatic retry.
  - [x] Document how an operator identifies or resends existing failed rows.

- [x] Task 5 - Add non-regression guards (AC: AC4)
  - [x] Update targeted API, service, and idempotency tests.
  - [x] Add or reuse a boundary guard preventing service imports from `app.api`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `StripeWebhookIdempotencyService` for claim, processed, and failed state transitions.
  - `app.api.errors` and `_raise_error` for HTTP error envelopes.
  - Existing billing webhook tests for status contract coverage.
- Do not recreate:
  - A second idempotency table.
  - A second webhook route.
  - A local JSON error builder in the webhook route.
- Shared abstraction allowed only if:
  - It replaces duplicated webhook result handling and is consumed by both service and route tests.

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

- `failed_internal` as HTTP 200 for signed processing failure
- `from app.api` inside `backend/app/services/billing`
- `JSONResponse` local construction inside `backend/app/api/v1/routers/public/billing.py`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Stripe webhook HTTP status mapping | `backend/app/api/v1/routers/public/billing.py` | `backend/app/services/billing` |
| Stripe webhook business processing | `backend/app/services/billing/stripe_webhook_service.py` | `backend/app/api` |
| Stripe webhook idempotency state | `backend/app/services/billing/stripe_webhook_idempotency_service.py` | `backend/app/api` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: applicable
- Required generated-contract evidence:
  - Runtime OpenAPI contains the webhook route.
  - Runtime OpenAPI includes the new retryable non-2xx response.
  - No generated frontend client change is required.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/v1/routers/public/billing.py`
- `backend/app/services/billing/stripe_webhook_service.py`
- `backend/app/services/billing/stripe_webhook_idempotency_service.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `docs/billing-webhook-idempotency.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/billing.py` - map signed processing failure to retryable non-2xx.
- `backend/app/services/billing/stripe_webhook_service.py` - expose failure outcome without hiding retry semantics.
- `docs/billing-webhook-idempotency.md` - align retry documentation with runtime.
- `docs/billing-webhook-local-testing.md` - align local failure expectations.

Likely tests:

- `backend/app/tests/integration/test_stripe_webhook_api.py` - assert retryable signed failure.
- `backend/app/tests/unit/test_stripe_webhook_service.py` - assert service failure outcome.
- `backend/app/tests/unit/test_stripe_webhook_idempotency_service.py` - assert failed row reclaim behavior.

Files not expected to change:

- `frontend/src/api/billing.ts` - frontend does not call the Stripe webhook.
- `backend/app/infra/db/models/stripe_webhook_event.py` - existing statuses are sufficient unless tests prove schema mismatch.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/api/v1/routers/public/billing.py
ruff check app/services/billing/stripe_webhook_service.py
ruff check app/services/billing/stripe_webhook_idempotency_service.py
ruff check app/tests/integration/test_stripe_webhook_api.py
ruff check app/tests/unit/test_stripe_webhook_service.py
ruff check app/tests/unit/test_stripe_webhook_idempotency_service.py
pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py
python -c "from app.main import app; schema = app.openapi(); assert '/v1/billing/stripe-webhook' in schema['paths']"
rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core
```

## 22. Regression Risks

- Risk: Stripe retries invalid signatures.
  - Guardrail: invalid signature API test must stay HTTP 400 only.
- Risk: Failed rows are committed but never retried.
  - Guardrail: integration test must assert non-2xx on signed processing failure.
- Risk: API route gains billing logic.
  - Guardrail: `RG-005` boundary checks and focused diff review.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/stripe-implementation/2026-05-03-1003/00-audit-report.md` - audit verdict and recommended order.
- `_condamad/audits/stripe-implementation/2026-05-03-1003/02-finding-register.md` - finding `F-001`.
- `_condamad/audits/stripe-implementation/2026-05-03-1003/03-story-candidates.md` - source candidate `SC-001`.
- `_condamad/stories/regression-guardrails.md` - shared non-regression invariants.
