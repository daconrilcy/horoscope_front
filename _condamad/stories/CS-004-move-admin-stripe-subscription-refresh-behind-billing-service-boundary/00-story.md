# Story CS-004 move-admin-stripe-subscription-refresh-behind-billing-service-boundary: Move admin Stripe subscription refresh behind a billing service boundary

Status: ready-to-review

## 1. Objective

Deplacer l'orchestration du refresh force Stripe admin hors du routeur HTTP vers un use case billing/admin unique.
Preserver le contrat runtime de `POST /v1/admin/users/{user_id}/refresh-subscription`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/stripe-implementation/2026-05-03-1659/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-001` montre que `backend/app/api/v1/routers/admin/users.py` possede directement le client Stripe.
  Il recupere la subscription et construit l'evenement synthetique, ce qui duplique une responsabilite de service billing.

## 3. Domain Boundary

- Domain: `backend/app/services/billing`
- In scope:
  - Use case service-owned pour refresh force d'une subscription Stripe depuis l'admin.
  - Routeur admin reduit a l'adaptation HTTP, l'autorisation et la traduction d'erreurs.
  - Tests admin Stripe ajustes pour patcher la frontiere service.
  - Garde anti-retour contre les appels Stripe SDK directs depuis `backend/app/api/v1/routers`.
- Out of scope:
  - Refactor global du routeur admin users.
  - Changement du modele de persistance billing ou introduction de repositories.
  - Changement des endpoints `reveal-stripe-id`, `assign-plan`, `commercial-gesture`.
  - Changement de version API Stripe ou de politique timeout/retry.
- Explicit non-goals:
  - Ne pas modifier les enveloppes d'erreur API protegees par `RG-004`.
  - Ne pas reintroduire de logique metier ou de persistance nouvelle dans la couche API protegee par `RG-005`.
  - Ne pas creer de wrapper, alias ou fallback transitoire autour de l'ancien ownership routeur.

## 4. Operation Contract

- Operation type: move
- Primary archetype: service-boundary-refactor
- Archetype reason: la story deplace une orchestration metier Stripe depuis un adaptateur API vers le proprietaire service canonique sans changer le comportement HTTP attendu.
- Behavior change allowed: no
- Behavior change constraints:
  - La route doit conserver son chemin, sa methode, son autorisation admin et sa reponse de succes.
  - Les erreurs subscription absente, client Stripe absent et exception generique doivent rester equivalentes.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'implementation exige de changer la forme de reponse, les codes HTTP existants, ou le modele de persistance billing.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le comportement de la route admin doit etre prouve par OpenAPI/runtime et tests, pas seulement par scan. |
| Baseline Snapshot | yes | Le contrat avant/apres de la route et des appels Stripe directs doit etre capture. |
| Ownership Routing | yes | La responsabilite Stripe SDK/use case doit etre routee vers `services/billing`, pas `api`. |
| Allowlist Exception | yes | La garde anti-retour doit accepter uniquement les proprietaires non-API explicites. |
| Contract Shape | yes | Le contrat HTTP admin existant doit rester stable. |
| Batch Migration | no | Une seule route/use case est migree. |
| Reintroduction Guard | yes | Un test ou scan deterministe doit echouer si un routeur API rappelle Stripe directement. |
| Persistent Evidence | yes | Les preuves avant/apres doivent rester consultables dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `app.openapi()` pour verifier que `/v1/admin/users/{user_id}/refresh-subscription` reste expose.
  - AST guard test pour verifier que les routeurs API ne possedent plus les appels Stripe SDK interdits.
- Secondary evidence:
  - Tests d'integration admin et scan cible des imports/appels Stripe dans `app/api/v1/routers`.
- Static scans alone are not sufficient for this story because:
  - Ils ne prouvent ni l'exposition runtime de la route ni le mapping des erreurs HTTP.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/evidence/admin-refresh-baseline.md`
- Comparison after implementation:
  - `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/evidence/admin-refresh-after.md`
- Expected invariant:
  - La route, l'autorisation admin, les status codes testes, le payload audit et la reponse succes restent stables.
  - Seuls l'ownership interne et la cible de patch des tests changent.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case: recuperer le client Stripe et appeler `subscriptions.retrieve` | `backend/app/services/billing` via `app.infra.stripe.client` | `backend/app/api/**` |
| Application use case: construire l'evenement `admin.forced_refresh` | `backend/app/services/billing` | `backend/app/api/**` |
| HTTP-only adapter: authentifier admin et retourner la reponse | `backend/app/api/v1/routers/admin/users.py` | `backend/app/services/**` |
| Application use case: enregistrer l'audit admin | Service billing/admin ou orchestration service appelee par route | Nouveau helper API local |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `app/services/billing/stripe_billing_profile_service.py` | `get_stripe_client`, `client.subscriptions` | Use cases billing Stripe. | Permanent: factory infra unique. |
| `app/services/billing/stripe_checkout_service.py` | `get_stripe_client`, `client.checkout` | Checkout Stripe. | Permanent: service canonique. |
| `app/services/billing/stripe_customer_portal_service.py` | `get_stripe_client`, `client.billing_portal` | Portal Stripe. | Permanent: service canonique. |
| `app/startup/stripe_portal_validation.py` | `get_stripe_client`, `client.billing_portal` | Validation startup non-API. | Permanent; jamais routeur API. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract type:
  - HTTP endpoint contract.
- Fields:
  - `status: str` - statut de succes retourne par la route admin.
- Required fields:
  - `status`
- Optional fields:
  - none
- Status codes:
  - Conserver les statuts couverts par les tests existants pour succes, absence subscription, client Stripe absent et exception Stripe.
- Serialization names:
  - `status`
- Frontend type impact:
  - none attendu.
- Generated contract impact:
  - OpenAPI path and method must remain present; schema change not expected.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: la story migre un seul use case admin refresh.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline admin refresh ownership | `evidence/admin-refresh-baseline.md` | Capturer route OpenAPI, tests et appels Stripe directs. |
| After admin refresh ownership | `evidence/admin-refresh-after.md` | Prouver route preservee et ownership service. |

## 4i. Reintroduction Guard

- Guard type: test AST ou scan exact execute par pytest.
- Forbidden examples: `from app.infra.stripe.client import get_stripe_client` dans `backend/app/api/v1/routers/**`, `stripe_client.subscriptions.retrieve` dans un routeur API.
- Required validation: test dedie ou commande `rg` ciblee avec zero hit hors commentaires/audits.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/stripe-implementation/2026-05-03-1659/02-finding-register.md` - `F-001` classe le refresh admin comme violation de frontiere service.
- Evidence 2: `_condamad/audits/stripe-implementation/2026-05-03-1659/01-evidence-log.md` - `E-006`, `E-007`, `E-010` documentent l'ownership routeur.
- Evidence 3: `backend/app/api/v1/routers/admin/users.py` - `refresh_subscription` construit aujourd'hui l'evenement `admin.forced_refresh` dans l'adaptateur API.
- Evidence 4: `backend/app/tests/integration/test_admin_stripe_actions_api.py` - les tests d'integration patchent actuellement `app.api.v1.routers.admin.users.get_stripe_client`.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants `RG-004`, `RG-005` et `RG-006` consultes avant cadrage.

## 6. Target State

- Le routeur admin appelle un use case service billing/admin et ne reference plus le client Stripe direct.
- Le use case service recupere la subscription Stripe et construit le payload `admin.forced_refresh`.
- Il applique `StripeBillingProfileService.update_from_event_payload`, enregistre l'audit et laisse la route adapter les erreurs.
- Les tests patchent la frontiere service, pas l'import Stripe dans le routeur.
- Une garde empeche la reintroduction d'appels Stripe SDK directs dans `backend/app/api/v1/routers`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-004` - les erreurs HTTP API doivent rester centralisees et les services ne doivent pas dependre de FastAPI.
  - `RG-005` - la couche API ne doit pas redevenir proprietaire de logique metier.
  - `RG-006` - `backend/app/api` reste un adaptateur HTTP strict.
- Non-applicable invariants:
  - `RG-023` - aucun script racine n'est ajoute ou modifie.
  - `RG-024` - la story ne change pas le demarrage local Stripe.
- Required regression evidence:
  - Tests admin Stripe, tests service billing profile, scan anti-appels Stripe SDK dans les routeurs, scan anti-import `app.api` depuis services/infra.
- Allowed differences:
  - Les tests peuvent patcher un nouveau symbole service-owned.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La route admin refresh reste exposee avec reponse succes stable. | `pytest -q app/tests/integration/test_admin_stripe_actions_api.py`; `app.openapi()`. |
| AC2 | Aucun routeur API n'appelle directement le client Stripe SDK. | AST guard; `rg -n "get_stripe_client|stripe_client" app/api/v1/routers`. |
| AC3 | Le refresh force est orchestre par un service billing/admin. | `pytest -q app/tests/unit/test_stripe_billing_profile_service.py`. |
| AC4 | Les erreurs existantes restent mappees avec statuts/messages equivalents. | `pytest -q app/tests/integration/test_admin_stripe_actions_api.py`. |
| AC5 | Les couches billing/infra ne dependent pas de `app.api` ni de FastAPI. | AST guard via `pytest`; `rg` anti `app.api` / FastAPI. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline route/ownership avant modification (AC: AC1, AC2)
  - [x] Subtask 1.1 - Documenter OpenAPI path, tests actuels et hits Stripe directs dans l'artefact baseline.
- [x] Task 2 - Creer ou reutiliser un use case service billing/admin pour le refresh force (AC: AC3, AC4, AC5)
  - [x] Subtask 2.1 - Deplacer recuperation Stripe, payload `admin.forced_refresh`, sync profile et audit hors du routeur.
  - [x] Subtask 2.2 - Garder les erreurs sous forme d'exceptions applicatives ou resultat service traduisible par l'API sans importer FastAPI.
- [x] Task 3 - Amincir le routeur admin (AC: AC1, AC2, AC4)
  - [x] Subtask 3.1 - Retirer l'import `get_stripe_client` et les appels `stripe_client.*` du routeur.
  - [x] Subtask 3.2 - Preserver autorisation admin, `request_id`, commit/rollback attendu et reponse.
- [x] Task 4 - Adapter les tests et ajouter la garde anti-retour (AC: AC2, AC3, AC4, AC5)
  - [x] Subtask 4.1 - Modifier `test_admin_stripe_actions_api.py` pour patcher le service boundary.
  - [x] Subtask 4.2 - Ajouter un test de garde AST/scan contre Stripe SDK direct dans les routeurs API.
- [x] Task 5 - Capturer l'evidence after et executer la validation (AC: AC1, AC2, AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `app.infra.stripe.client.get_stripe_client` reste l'unique factory client Stripe.
  - `StripeBillingProfileService.update_from_event_payload` reste le point de sync profile depuis payload event.
  - `AuditService.record_event` reste le mecanisme d'audit admin.
- Do not recreate:
  - Un second client Stripe.
  - Une seconde logique de mapping subscription vers profile.
  - Un helper d'erreur HTTP local dans le service.
- Shared abstraction allowed only if:
  - Elle remplace une duplication concrete entre admin refresh et un service billing existant.

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

- `backend/app/api/v1/routers/**` important `app.infra.stripe.client.get_stripe_client`
- `stripe_client.subscriptions.retrieve` dans `backend/app/api/v1/routers/**`
- Nouveau module hors `backend/app/services/billing` pour le use case billing admin sans justification.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Stripe SDK client factory | `backend/app/infra/stripe/client.py` | API routers. |
| Billing admin refresh use case | `backend/app/services/billing/**` | `backend/app/api/v1/routers/admin/users.py`. |
| HTTP adapter and admin auth | `backend/app/api/v1/routers/admin/users.py` | Billing services. |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: applicable
- Required generated-contract evidence:
  - OpenAPI path presence for `/v1/admin/users/{user_id}/refresh-subscription`.
  - No generated frontend type impact expected.

## 18. Files to Inspect First

- `backend/app/api/v1/routers/admin/users.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/services/billing/stripe_checkout_service.py`
- `backend/app/services/billing/stripe_customer_portal_service.py`
- `backend/app/infra/stripe/client.py`
- `backend/app/tests/integration/test_admin_stripe_actions_api.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/admin/users.py` - remplacer l'orchestration Stripe directe par l'appel au service.
- `backend/app/services/billing/stripe_billing_profile_service.py` ou nouveau module sous `backend/app/services/billing/` - ajouter le use case admin refresh.
- `backend/app/tests/integration/test_admin_stripe_actions_api.py` - patcher et verifier la frontiere service.
- `backend/app/tests/unit/test_stripe_billing_profile_service.py` ou nouveau test unitaire billing - couvrir payload, erreurs et audit.

Likely tests:

- `backend/app/tests/integration/test_admin_stripe_actions_api.py` - contrat route admin.
- `backend/app/tests/unit/test_stripe_billing_profile_service.py` - orchestration service.
- Nouveau test d'architecture sous `backend/app/tests/unit/` si aucune garde existante ne couvre le scan routeur.

Files not expected to change:

- `frontend/src/**` - aucun contrat frontend attendu.
- `backend/pyproject.toml` - aucune dependance nouvelle.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/api/v1/routers/admin/users.py app/services/billing app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py
pytest -q app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py
python -c "from app.main import app; assert '/v1/admin/users/{user_id}/refresh-subscription' in app.openapi()['paths']"
rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers
rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"
```

## 22. Regression Risks

- Risk: la route garde le comportement mais la logique Stripe reste dans l'adaptateur API.
  - Guardrail: `RG-005`, `RG-006`, scan cible et test de garde.
- Risk: la centralisation service introduit des erreurs HTTP depuis `services/billing`.
  - Guardrail: `RG-004`, scan FastAPI/HTTPException dans services.
- Risk: le payload audit change silencieusement.
  - Guardrail: tests integration admin Stripe sur `subscription_refresh_forced`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass convergence through wrapper, alias, fallback, compatibility shim, soft-disable, or re-export.
- Do not refactor unrelated admin user actions.

## 24. References

- `_condamad/audits/stripe-implementation/2026-05-03-1659/01-evidence-log.md` - preuves `E-006`, `E-007`, `E-010`.
- `_condamad/audits/stripe-implementation/2026-05-03-1659/02-finding-register.md` - finding `F-001`.
- `_condamad/audits/stripe-implementation/2026-05-03-1659/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
