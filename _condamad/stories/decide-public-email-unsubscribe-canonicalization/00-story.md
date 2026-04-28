# Story decide-public-email-unsubscribe-canonicalization: Décider la canonicalisation de la route publique email unsubscribe

Status: ready-for-review

## 1. Objective

Décider et appliquer le statut cible de l'URL historique `GET /api/email/unsubscribe`.
Elle devient soit une exception permanente documentée, soit une route migrée vers un canonique borné,
soit une surface gouvernée en attente de décision utilisateur explicite.
La story doit inventorier les consommateurs, mettre à jour `API_ROUTE_MOUNT_EXCEPTIONS`,
et empêcher toute suppression silencieuse d'une URL déjà émise dans des emails.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/api-adapter/2026-04-28-0046`
- Reason for change: le finding `F-002` indique que `/api/email/unsubscribe`
  reste une surface publique historique hors `/v1`, gouvernée mais sans décision cible.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api`
- In scope:
  - Inventorier les consommateurs de `/api/email/unsubscribe` dans services email, templates, tests, docs, OpenAPI et frontend si présent.
  - Déterminer la classification de la route: `external-active`, `historical-facade`, `canonical-active`, `dead` ou `needs-user-decision`.
  - Enregistrer la décision dans un artefact persistant de story et dans `backend/app/api/route_exceptions.py`.
  - Si migration approuvée explicitement: créer une route canonique et une stratégie de transition bornée conforme au No Legacy contract.
  - Si conservation permanente: documenter la permanence et renforcer les tests runtime du registre d'exceptions.
- Out of scope:
  - Changer la logique métier de désabonnement ou la persistance utilisateur.
  - Refactorer les autres exceptions de montage (`/health`, routes internes LLM QA).
  - Modifier les campagnes email au-delà du lien de désabonnement si une décision de migration le demande.
  - Supprimer l'URL historique sans décision utilisateur explicite et preuve d'impact.
- Explicit non-goals:
  - Ne pas supprimer `/api/email/unsubscribe` pendant l'étape d'inventaire.
  - Ne pas créer de wrapper, alias, fallback ou redirection permanente non bornée.
  - Ne pas contourner `RG-008`: toute route hors registre API v1 doit rester exacte et justifiée.
  - Ne pas modifier `RG-007`: les endpoints admin LLM observability restent hors scope.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: legacy-facade-removal
- Archetype reason: la story traite une URL publique historique hors surface canonique.
  Elle doit la classifier comme permanente ou planifier sa migration sans façade legacy durable.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Aucun changement de comportement n'est autorisé avant inventaire et décision explicite.
  - Si la décision est `keep-permanent`, le comportement HTTP doit rester identique.
  - Si la décision est `migrate`, les nouveaux liens peuvent viser la route canonique.
  - L'ancien chemin ne peut être supprimé qu'après classification non-external-active ou décision utilisateur explicite.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: la route est `external-active`, si des emails déjà envoyés peuvent contenir l'ancien lien,
  ou si la suppression change un contrat public observé.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La présence/absence de la route doit être prouvée par OpenAPI et route table runtime. |
| Baseline Snapshot | yes | Toute décision doit comparer la surface avant/après. |
| Ownership Routing | yes | Le propriétaire canonique de la responsabilité unsubscribe doit être explicite. |
| Allowlist Exception | yes | `API_ROUTE_MOUNT_EXCEPTIONS` est l'exception register de la route historique. |
| Contract Shape | yes | La story touche un chemin HTTP public et potentiellement ses statuts/réponses. |
| Batch Migration | yes | Une migration éventuelle doit distinguer anciens liens, nouveaux liens générés et retrait. |
| Reintroduction Guard | yes | La garde doit empêcher le retour d'une route legacy non décidée ou hors registre. |
| Persistent Evidence | yes | L'inventaire de consommation et la décision doivent rester auditables. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - `app.main.app.routes` pour la présence effective de `/api/email/unsubscribe`.
  - `app.main.app.openapi()` pour l'exposition publique du chemin.
  - `API_ROUTE_MOUNT_EXCEPTIONS` pour la décision structurée de montage.
- Secondary evidence:
  - `rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" backend frontend _condamad`
  - Tests d'intégration `backend/tests/integration/test_email_unsubscribe.py`.
- Static scans alone are not sufficient for this story because:
  - Les liens déjà envoyés sont externes au dépôt; la route runtime et la décision utilisateur sont nécessaires avant suppression.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract
changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-before.json`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-before.md`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/route-consumption-audit.md`
- Comparison after implementation:
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-after.json`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-after.md`
  - `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md`
- Expected invariant:
  - La décision cible est explicite et testée.
  - Aucune route hors `/v1` non enregistrée n'apparaît.
  - Toute différence OpenAPI est explicitement autorisée dans `decision-record.md`.
- Allowed differences:
  - `keep-permanent`: aucune différence de route attendue, seulement décision/raison mise à jour.
  - `migrate`: ajout éventuel d'une route canonique et changement des nouveaux liens générés.
  - Le maintien ou retrait de l'ancien chemin dépend de la classification et de la décision.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime exception metadata for non-v1 route | `backend/app/api/route_exceptions.py` | Hard-coded exception in tests or `main.py` |
| Public unsubscribe route handler | `backend/app/api/v1/routers/public/email.py` or approved canonical route module | Duplicate active handler |
| Unsubscribe link generation | `backend/app/services/email/service.py` | Route module generating links |
| Product/architecture decision record | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md` | Implicit decision in code diff only |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/api/route_exceptions.py` | `public_email_unsubscribe` | Historical public URL outside `/v1`. | Permanent or migration-bound decision. |
| `backend/app/tests/unit/test_api_router_architecture.py` | route exception guard | Runtime route must match register. | Enforce selected decision only. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI
contract, generated client, or frontend type.

- Contract type:
  - Public HTTP route and OpenAPI path.
- Fields:
  - Query parameter `token`: JWT unsubscribe token generated by the email service.
  - HTML response body: confirmation or error response produced by the route.
- Required fields:
  - `token`
- Optional fields:
  - none known from current route evidence.
- Status codes:
  - Preserve current tested success and error status codes unless `decision-record.md` explicitly authorizes a migration difference.
- Serialization names:
  - Wire query name `token` remains `token`.
- Frontend type impact:
  - No frontend impact expected unless a repository frontend consumer of this URL is discovered.
- Generated contract impact:
  - OpenAPI path presence/absence or canonical replacement must be captured before/after.

## 4g. Batch Migration Plan

Use when the archetype or scope requires migration by independent batches.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Decision and inventory | `/api/email/unsubscribe` | selected decision | none | route tests | consumption audit done | External usage unresolved |
| New links if migrate | old generated link | approved canonical URL | email service | email integration/link tests | new links omit old path | no approval |
| Legacy route retirement | old route | approved canonical URL | tests and register | runtime route tests | OpenAPI proves absence | external-active without decision |

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration
mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Route consumption audit | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/route-consumption-audit.md` | Classify the route and consumers before any removal. |
| Decision record | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/decision-record.md` | Record keep/migrate/delete decision plus user approval status. |
| OpenAPI before snapshot | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-before.json` | Baseline public contract. |
| OpenAPI after snapshot | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/openapi-after.json` | Prove final public contract. |
| Runtime route before | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-before.md` | Prove baseline route table. |
| Runtime route after | `_condamad/stories/decide-public-email-unsubscribe-canonicalization/runtime-routes-after.md` | Prove final route table. |

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

- `/api/email/unsubscribe` without an exact `API_ROUTE_MOUNT_EXCEPTIONS` decision.
- Any second active unsubscribe handler with the same responsibility.
- Any permanent redirect, wrapper, alias or fallback if deletion is approved.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_api_router_architecture.py` checks route exception exactness and runtime route registration.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/api-adapter/2026-04-28-0046/02-finding-register.md` -
  `F-002` classifies `/api/email/unsubscribe` as governed but unconverged.
- Evidence 2: `backend/app/api/route_exceptions.py` -
  `public_email_unsubscribe` is `GET /api/email/unsubscribe`, condition `always`.
- Evidence 3: `backend/app/services/email/service.py` - `EmailService.get_unsubscribe_link` generates the backend URL plus `/api/email/unsubscribe?token=`.
- Evidence 4: `backend/tests/integration/test_email_unsubscribe.py` - tests call `/api/email/unsubscribe` directly for success and error cases.
- Evidence 5: `_condamad/stories/harden-api-adapter-boundary-guards/route-exception-register.md` - previous evidence records this route as an exact exception.
- Evidence 6: `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md` -
  previous story classified the route as `external-active`.
- Evidence N: `_condamad/stories/regression-guardrails.md` - shared regression invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- `route-consumption-audit.md` classifies all known consumers and records unresolved external risk.
- `decision-record.md` states one decision: `keep-permanent`, `migrate-with-bounded-compatibility`,
  `delete-after-explicit-approval`, or `needs-user-decision` when explicit approval is absent.
- `backend/app/api/route_exceptions.py` decision text matches the selected target.
- Runtime route tests and OpenAPI snapshots prove the final state.
- No duplicate unsubscribe route, unbounded compatibility alias, or hidden exception remains.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - if the historical route is removed, it must not return as wrapper, alias, fallback or re-export.
  - `RG-003` - route architecture must remain canonical without a competing route registry.
  - `RG-006` - `backend/app/api` remains an HTTP adapter, not a business owner.
  - `RG-008` - route exceptions outside API v1 must remain exact, justified and blocked against silent growth.
- Non-applicable invariants:
  - `RG-007` - admin LLM observability endpoints are not touched.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_api_router_architecture.py`
  - `pytest -q tests/integration/test_email_unsubscribe.py`
  - OpenAPI before/after snapshots.
  - Consumption audit scan for unsubscribe links.
- Allowed differences:
  - Only differences explicitly recorded in `decision-record.md`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Consumption audit classifies `/api/email/unsubscribe`. | `python -B -c "from app.main import app; app.openapi()"`; `route-consumption-audit.md`; unsubscribe `rg`. |
| AC2 | The target decision blocks external-active deletion. | Artifact: `decision-record.md`. Command: `rg -n "Decision|User decision|Risk" decision-record.md`. |
| AC3 | `API_ROUTE_MOUNT_EXCEPTIONS` reflects the selected decision exactly. | Guard: `pytest -q app/tests/unit/test_api_router_architecture.py`. Inspect `route_exceptions.py`. |
| AC4 | Keep-permanent decision preserves route behavior. | Runtime: OpenAPI snapshots. Test: `pytest -q tests/integration/test_email_unsubscribe.py`. |
| AC5 | Migrate decision makes new links canonical. | `pytest -q tests/integration/test_email_unsubscribe.py`; runtime route inventory; link generation test. |
| AC6 | Delete-approved decision leaves no wrapper. | `python -B -c "from app.main import app; app.openapi()"`; negative `rg`; architecture tests. |
| AC7 | No duplicate active unsubscribe implementation exists. | Scan: `rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" backend/app`. Runtime owner inventory. |

## 8. Implementation Tasks

- [x] Task 1 - Inventorier les consommateurs et baseline runtime (AC: AC1, AC4, AC7)
  - [x] Subtask 1.1 - Capturer `openapi-before.json` et `runtime-routes-before.md`.
  - [x] Subtask 1.2 - Créer `route-consumption-audit.md` avec la table de classification requise.
  - [x] Subtask 1.3 - Scanner `backend`, `frontend`, `_condamad` et docs disponibles pour les liens unsubscribe.

- [x] Task 2 - Produire la décision cible (AC: AC2)
  - [x] Subtask 2.1 - Classifier `/api/email/unsubscribe` selon les règles de suppression.
  - [x] Subtask 2.2 - Si la classification est `external-active`, obtenir ou enregistrer la décision utilisateur avant toute suppression.
  - [x] Subtask 2.3 - Rédiger `decision-record.md` avec l'option retenue et les différences autorisées.

- [x] Task 3 - Appliquer la décision dans l'API (AC: AC3, AC4, AC5, AC6, AC7)
  - [x] Subtask 3.1 - Mettre à jour `backend/app/api/route_exceptions.py` pour refléter la décision exacte.
  - [x] Subtask 3.2 - Si `keep-permanent`, renforcer les tests sans changer le comportement.
  - [x] Subtask 3.3 - Si `migrate`, ajouter la route canonique approuvée et modifier uniquement les nouveaux liens générés.
  - [x] Subtask 3.4 - Si deletion approved, supprimer l'ancien montage sans redirect, alias, wrapper ou fallback.

- [x] Task 4 - Valider et persister les preuves finales (AC: AC3, AC4, AC5, AC6, AC7)
  - [x] Subtask 4.1 - Capturer `openapi-after.json` et `runtime-routes-after.md`.
  - [x] Subtask 4.2 - Exécuter les tests d'architecture et d'intégration email.
  - [x] Subtask 4.3 - Exécuter les scans négatifs ou de stabilité selon la décision retenue.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/route_exceptions.py` as the only route exception register.
  - `backend/app/api/v1/routers/public/email.py` as the current public unsubscribe handler unless a canonical replacement is approved.
  - `backend/app/services/email/service.py` for unsubscribe link generation.
  - `backend/app/tests/unit/test_api_router_architecture.py` for route registration guards.
- Do not recreate:
  - A second permanent unsubscribe implementation.
  - A hidden allowlist in tests.
  - A redirect or compatibility route without bounded decision and explicit user approval.
- Shared abstraction allowed only if:
  - It removes duplicate unsubscribe ownership and is required by the selected migration decision.

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

- `/api/email/unsubscribe` without exact `API_ROUTE_MOUNT_EXCEPTIONS` ownership.
- A second route that performs unsubscribe without canonical ownership in `decision-record.md`.
- Redirecting the old path permanently after deletion approval.
- Tests that treat legacy behavior as nominal after the decision says delete.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions for the `Decision` column:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/decide-public-email-unsubscribe-canonicalization/route-consumption-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public unsubscribe link endpoint | Decision from `decision-record.md` | `/api/email/unsubscribe` if migration chooses a new canonical route |
| Route exception decision | `backend/app/api/route_exceptions.py` | Hidden route allowlist in tests or docs |
| Link generation | `backend/app/services/email/service.py` | Hard-coded links outside email service |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

Known blocker candidate:

- `EmailService.get_unsubscribe_link` currently generates `/api/email/unsubscribe`; already sent emails may contain this route outside repository control.

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI path presence if kept.
- OpenAPI path absence if deletion is approved.
- Generated client/schema absence or update if the repository has generated clients for this route.
- Runtime route inventory matching `API_ROUTE_MOUNT_EXCEPTIONS`.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/route_exceptions.py`
- `backend/app/api/v1/routers/public/email.py`
- `backend/app/services/email/service.py`
- `backend/tests/integration/test_email_unsubscribe.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/api/route_exceptions.py` - update decision text or exception entry according to selected target.
- `backend/app/services/email/service.py` - update generated unsubscribe link only if migration is approved.
- `backend/app/api/v1/routers/public/email.py` or an approved canonical route module - change only if migration/deletion is approved.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - assert the selected route exception decision.
- `backend/tests/integration/test_email_unsubscribe.py` - preserve or migrate tested behavior according to decision.
- Service/link generation test path, if no current unit test covers `EmailService.get_unsubscribe_link`.

Files not expected to change:

- `backend/migrations/**` - no schema change.
- `frontend/**` - only changes if a concrete consumer is discovered in `route-consumption-audit.md`.
- Other route exception entries for `/health` and internal LLM QA - out of scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_api_router_architecture.py
pytest -q tests/integration/test_email_unsubscribe.py
python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths or '/v1/email/unsubscribe' in paths"
rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" ..\backend ..\frontend ..\_condamad
```

For a deletion-approved result, replace the OpenAPI assertion with absence of `/api/email/unsubscribe` and include the explicit user-decision evidence in `decision-record.md`.

## 22. Regression Risks

- Risk: supprimer une URL encore présente dans des emails déjà envoyés.
  - Guardrail: removal audit, external usage blocker, explicit user decision.
- Risk: conserver une exception historique sans décision durable.
  - Guardrail: `decision-record.md` and exact `API_ROUTE_MOUNT_EXCEPTIONS` decision.
- Risk: créer une deuxième route unsubscribe active.
  - Guardrail: runtime route owner inventory and `rg` ownership scan.
- Risk: route hors `/v1` non gouvernée.
  - Guardrail: `RG-008` and route exception architecture tests.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- If deletion or migration needs user approval and the approval is not present in `decision-record.md`, stop before changing runtime behavior.

## 24. References

- `_condamad/audits/api-adapter/2026-04-28-0046/00-audit-report.md` - audit summary.
- `_condamad/audits/api-adapter/2026-04-28-0046/02-finding-register.md` - `F-002` source finding.
- `_condamad/audits/api-adapter/2026-04-28-0046/03-story-candidates.md` - `SC-002` candidate.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md` - previous external-active classification evidence.
