# Story converge-admin-llm-observability-router: Converger les endpoints admin LLM observability vers leur routeur canonique

Status: ready-for-dev

## 1. Objective

Faire de `backend/app/api/v1/routers/admin/llm/observability.py` l'unique propriétaire runtime
des endpoints admin LLM d'observabilité, tout en conservant les chemins HTTP existants.
La story supprime la façade historique située dans `prompts.py`, monte le routeur canonique
via le registre API v1, et ajoute une preuve runtime empêchant le retour d'un double propriétaire.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/api-adapter/2026-04-27-1906`
- Reason for change: l'audit F-001 signale deux propriétaires de code pour les endpoints
  d'observabilité LLM. `observability.py` contient déjà le routeur spécialisé mais n'est
  pas monté, tandis que `prompts.py` expose encore les endpoints runtime.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api`
- In scope:
  - Monter `app.api.v1.routers.admin.llm.observability.router` via `backend/app/api/v1/routers/registry.py`.
  - Retirer de `backend/app/api/v1/routers/admin/llm/prompts.py` les quatre handlers d'observabilité dupliqués et leurs imports devenus inutiles.
  - Préserver les URLs, méthodes HTTP, modèles de réponse, dépendances d'authentification admin et payloads existants des quatre endpoints.
  - Ajouter ou mettre à jour des tests d'architecture et d'intégration prouvant le propriétaire runtime canonique.
  - Persister un court audit de consommation pour les surfaces retirées de `prompts.py`.
- Out of scope:
  - Extraire les autres opérations SQL de `prompts.py`.
  - Modifier les endpoints admin LLM de personas, schemas, catalog, use-cases, prompts, assemblies, releases, consumption ou sample payloads.
  - Modifier les services `app.services.llm_observability.*`, `app.ops.llm.*`, le frontend, les migrations DB ou les modèles SQLAlchemy.
  - Résoudre les findings F-002, F-003 et F-004 de l'audit API adapter.
- Explicit non-goals:
  - Ne pas créer de wrapper, alias, re-export ou fallback entre `prompts.py` et `observability.py`.
  - Ne pas changer les chemins HTTP publics/admin existants pour cette story.
  - Ne pas déplacer de logique métier hors de `prompts.py` sauf suppression stricte des handlers d'observabilité dupliqués.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: `prompts.py` conserve une surface historique concurrente pour des endpoints dont le propriétaire canonique existe déjà dans `admin/llm/observability.py`.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les quatre routes doivent rester exposées avec les mêmes chemins et méthodes HTTP.
  - Le module d'endpoint enregistré à runtime doit devenir `app.api.v1.routers.admin.llm.observability`.
  - Les formes de réponse existantes doivent rester portées par les modèles `LlmCallLogListResponse`, `LlmDashboardResponse`, `ReplayPayload` et `dict`.
  - Aucun autre endpoint de `prompts.py` ne doit changer de chemin, méthode ou modèle de réponse.
- Deletion allowed: yes
- Replacement allowed: no
- Registration rule: canonical router registration is required; replacement remains forbidden for
  deleted handlers.
- User decision required if: un usage externe prouvé dépend explicitement du module Python
  `app.api.v1.routers.admin.llm.prompts` comme propriétaire de ces quatre handlers, ou si le
  service canonique `app.services.llm_observability.admin_observability` ne couvre pas le
  contrat runtime actuel.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La réussite dépend du routeur effectivement monté dans `app.routes` et de `app.openapi()`, pas seulement du contenu des fichiers. |
| Baseline Snapshot | yes | Les quatre chemins HTTP doivent être conservés avant/après avec seul changement attendu sur le module propriétaire. |
| Ownership Routing | yes | La responsabilité observability doit être routée vers le propriétaire canonique `admin/llm/observability.py`. |
| Allowlist Exception | no | Aucune exception n'est autorisée: il ne doit plus rester de handler d'observabilité dans `prompts.py`. |
| Contract Shape | yes | La story touche des routes API et doit figer méthodes, chemins, modèles de réponse et impact OpenAPI. |
| Batch Migration | no | Le lot contient une seule surface cohérente: les quatre endpoints admin LLM observability. |
| Reintroduction Guard | yes | Un test doit échouer si ces handlers reviennent dans `prompts.py` ou si le runtime les enregistre depuis le mauvais module. |
| Persistent Evidence | yes | L'audit de consommation et les snapshots OpenAPI/route table doivent être conservés dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - `app.main.app.routes` pour le module propriétaire effectif de chaque chemin et méthode.
  - `app.main.app.openapi()` pour les chemins, méthodes et schémas exposés.
- Secondary evidence:
  - Scans AST de `backend/app/api/v1/routers/admin/llm/prompts.py`, `backend/app/api/v1/routers/admin/llm/observability.py` et `backend/app/api/v1/routers/registry.py`.
  - `rg` ciblés sur les symboles `list_call_logs`, `get_dashboard`, `replay_request`, `purge_logs`, `call-logs`, `dashboard`, `replay` et `call-logs/purge`.
- Static scans alone are not sufficient for this story because:
  - FastAPI peut exposer des routes par montage effectif même si plusieurs fichiers déclarent les mêmes decorators; seule la table runtime prouve le propriétaire réellement servi.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/converge-admin-llm-observability-router/openapi-before.json`:
    snapshot OpenAPI complet.
  - `_condamad/stories/converge-admin-llm-observability-router/route-owners-before.md`
- Comparison after implementation:
  - `_condamad/stories/converge-admin-llm-observability-router/openapi-after.json`:
    snapshot OpenAPI complet.
  - `_condamad/stories/converge-admin-llm-observability-router/route-owners-after.md`
  - `_condamad/stories/converge-admin-llm-observability-router/openapi-contract-diff.md`:
    diff filtré limité aux quatre chemins observability et aux operationIds.
- Expected invariant:
  - Les quatre chemins observability restent présents avec leurs méthodes existantes.
  - Les autres chemins exposés par `prompts.py` restent présents avec leurs méthodes existantes.
- Allowed differences:
  - Le module propriétaire des quatre endpoints observability passe de `app.api.v1.routers.admin.llm.prompts` à `app.api.v1.routers.admin.llm.observability`.
  - Les operationIds OpenAPI peuvent changer uniquement si FastAPI les dérive du nom de
    fonction et que les tests confirment que chemins, méthodes et schémas restent équivalents.
  - Si un client généré est présent ou référencé dans le repo, tout diff d'operationId doit être
    neutralisé ou documenté comme non consommé avec preuve de scan.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| HTTP adapter for admin LLM observability | `backend/app/api/v1/routers/admin/llm/observability.py` | `backend/app/api/v1/routers/admin/llm/prompts.py` |
| Admin LLM prompt/catalog HTTP adapter | `backend/app/api/v1/routers/admin/llm/prompts.py` | `backend/app/api/v1/routers/admin/llm/observability.py` |
| Observability application use cases | `backend/app/services/llm_observability/admin_observability.py` | `backend/app/api/**` |
| LLM replay operation | `backend/app/ops/llm/replay_service.py` through existing service imports | `backend/app/api/**` |
| Persistence details for LLM call logs | `backend/app/infra/db/**` and services | New SQL orchestration in `backend/app/api/**` |
| Shared API contracts | `backend/app/services/api_contracts/**` | Imports croisés entre `prompts.py` et `observability.py` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI
contract, generated client, or frontend type.

- Contract type:
  - FastAPI route/OpenAPI contract for admin LLM observability.
- Fields:
  - `GET /v1/admin/llm/call-logs`: query `use_case`, `status`, `prompt_version_id`, `from_date`, `to_date`, `page`, `page_size`; response model `LlmCallLogListResponse`.
  - `GET /v1/admin/llm/dashboard`: query `period_hours`; response model `LlmDashboardResponse`.
  - `POST /v1/admin/llm/replay`: body `ReplayPayload`; response model `dict`.
  - `POST /v1/admin/llm/call-logs/purge`: no request body; response model `dict`.
- Required fields:
  - `ReplayPayload.request_id` and `ReplayPayload.prompt_version_id` as defined in `app.services.api_contracts.admin.llm.prompts`.
- Optional fields:
  - Optional query parameters already declared by `observability.py` for call-log filtering and dashboard period.
- Status codes:
  - Preserve current FastAPI/default status codes and existing service error translation; no new status code is introduced by this story.
- Serialization names:
  - Preserve existing wire names from `LlmCallLogListResponse`, `LlmDashboardResponse`, `ReplayPayload` and response dictionaries.
- Frontend type impact:
  - None expected; URLs and JSON shapes remain stable. If frontend generated clients exist, only operation owner metadata may differ.
- Generated contract impact:
  - OpenAPI paths and methods must remain present. OperationIds may be accepted as the only
    generated diff if route owner module or function registration changes.
  - Generated clients or referenced generated schemas must be scanned before accepting an
    operationId diff.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration
mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Route owner baseline | `_condamad/stories/converge-admin-llm-observability-router/route-owners-before.md` | Prouver le propriétaire runtime initial des quatre endpoints. |
| Route owner after snapshot | `_condamad/stories/converge-admin-llm-observability-router/route-owners-after.md` | Prouver le propriétaire runtime final. |
| OpenAPI baseline | `_condamad/stories/converge-admin-llm-observability-router/openapi-before.json` | Capturer les quatre chemins avant refactorisation. |
| OpenAPI after snapshot | `_condamad/stories/converge-admin-llm-observability-router/openapi-after.json` | Capturer les quatre chemins après refactorisation. |
| OpenAPI filtered diff | `_condamad/stories/converge-admin-llm-observability-router/openapi-contract-diff.md` | Comparer les quatre chemins, méthodes, schemas et operationIds. |
| Removal audit | `_condamad/stories/converge-admin-llm-observability-router/route-consumption-audit.md` | Documenter classification, consommateurs et décision. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- generated OpenAPI paths
- forbidden symbols or states

Required forbidden examples:

- `backend/app/api/v1/routers/admin/llm/prompts.py` defining `@router.get("/call-logs")`
- `backend/app/api/v1/routers/admin/llm/prompts.py` defining `@router.get("/dashboard")`
- `backend/app/api/v1/routers/admin/llm/prompts.py` defining `@router.post("/replay")`
- `backend/app/api/v1/routers/admin/llm/prompts.py` defining `@router.post("/call-logs/purge")`
- Runtime route owner for those paths different from `app.api.v1.routers.admin.llm.observability`
- More or fewer than exactly one `APIRoute` per expected path and method

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `pytest -q app/tests/unit/test_api_router_architecture.py tests/unit/test_story_70_14_transition_guards.py`
  checks forbidden decorators and runtime owner.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/api-adapter/2026-04-27-1906/00-audit-report.md` -
  F-001 reports duplicated LLM observability route owners and states that `observability.py`
  is not mounted.
- Evidence 2: `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md` -
  E-005 confirms runtime OpenAPI exposes the four paths, and E-006 confirms the same endpoint
  names exist in both `prompts.py` and `observability.py`.
- Evidence 3: `backend/app/api/v1/routers/admin/llm/observability.py` - declares the
  `/v1/admin/llm` router and delegates the four specialized handlers to
  `app.services.llm_observability.admin_observability`.
- Evidence 4: `backend/app/api/v1/routers/admin/llm/prompts.py` - currently declares duplicated
  handlers for `/call-logs`, `/dashboard`, `/replay` and `/call-logs/purge`.
- Evidence 5: `backend/app/api/v1/routers/registry.py` - imports `admin_llm_router` from
  `admin.llm.prompts`, but does not import/register `admin.llm.observability`.
- Evidence 6: `backend/app/tests/integration/test_admin_llm_config_api.py` - contains integration coverage for `/v1/admin/llm/call-logs` and `/v1/admin/llm/dashboard`.
- Evidence 7: `backend/tests/unit/test_story_70_14_transition_guards.py` - already proves that
  `observability.py` exposes only the four intended endpoints, but not that it is mounted runtime.

## 6. Target State

After implementation:

- `API_V1_ROUTER_REGISTRY` includes the canonical observability router.
- Runtime FastAPI routes for the four observability paths are owned by `app.api.v1.routers.admin.llm.observability`.
- Runtime FastAPI exposes exactly one `APIRoute` per expected path and method.
- The registry accepts multiple routers with `/v1/admin/llm` prefix only when their path/method
  pairs are disjoint.
- `prompts.py` no longer declares handlers or direct observability imports solely needed by those four endpoints.
- OpenAPI still exposes the four observability paths and the rest of admin LLM prompt/catalog paths.
- Tests fail if the duplicated handlers are reintroduced in `prompts.py` or if runtime ownership drifts away from `observability.py`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime owner is `admin.llm.observability`. | Evidence profile: `runtime_openapi_contract`; `app.routes`; run architecture pytest. |
| AC2 | The four HTTP contracts remain exposed in OpenAPI. | Evidence profile: `runtime_openapi_contract`; `app.openapi()`; run integration pytest. |
| AC3 | `prompts.py` no longer owns observability route decorators. | Evidence profile: `targeted_forbidden_symbol_scan`; run AST guard and `rg`. |
| AC4 | `observability.py` delegates to services without forbidden SQL symbols. | Evidence profiles: `ast_architecture_guard`, `runtime_openapi_contract`; run pytest. |
| AC5 | No duplicate active implementation remains for the four endpoints. | Evidence profile: `no_legacy_contract`; run both guard pytest commands. |
| AC6 | Evidence files exist. | Evidence profiles: `openapi_before_after_snapshot`, `runtime_openapi_contract`; `app.openapi()`; `python -B -c Path.exists`. |
| AC7 | Runtime contract covers all four endpoints. | Evidence profile: `runtime_openapi_contract`; `app.routes`; integration pytest. |
| AC8 | Runtime route cardinality is exactly one per expected route key. | Evidence profile: `runtime_openapi_contract`; `app.routes`; run architecture pytest. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture baseline evidence before editing (AC: AC1, AC2, AC6, AC8)
  - [ ] Subtask 1.1 - Generate `route-owners-before.md` from `app.routes` for the four paths.
  - [ ] Subtask 1.2 - Generate full `openapi-before.json` from `app.openapi()`.
  - [ ] Subtask 1.3 - Create `route-consumption-audit.md` with the required removal audit table.
  - [ ] Subtask 1.4 - Prepare filtered diff fields for paths, methods, schemas and operationIds.

- [ ] Task 2 - Register the canonical observability router (AC: AC1, AC2)
  - [ ] Subtask 2.1 - Import `router as admin_llm_observability_router` from `app.api.v1.routers.admin.llm.observability` in `backend/app/api/v1/routers/registry.py`.
  - [ ] Subtask 2.2 - Add `RouterRegistration(admin_llm_observability_router)` next to the admin LLM router registrations.
  - [ ] Subtask 2.3 - Verify same-prefix routers have disjoint path/method pairs.

- [ ] Task 3 - Remove duplicated observability handlers from `prompts.py` (AC: AC3, AC4, AC5)
  - [ ] Subtask 3.1 - Delete only the four duplicated route functions from `backend/app/api/v1/routers/admin/llm/prompts.py`.
  - [ ] Subtask 3.2 - Remove imports used only by those deleted handlers, including observability models/functions when no other `prompts.py` code uses them.
  - [ ] Subtask 3.3 - Keep unrelated prompt/catalog/persona/use-case handlers unchanged.

- [ ] Task 4 - Add reintroduction and contract guards (AC: AC1, AC2, AC3, AC5, AC8)
  - [ ] Subtask 4.1 - Update `backend/app/tests/unit/test_api_router_architecture.py` with an AST guard forbidding observability decorators in `prompts.py`.
  - [ ] Subtask 4.2 - Add a runtime owner guard asserting the four paths are served by `app.api.v1.routers.admin.llm.observability`.
  - [ ] Subtask 4.3 - Assert exactly one `APIRoute` exists per expected path and method.
  - [ ] Subtask 4.4 - Keep `backend/tests/unit/test_story_70_14_transition_guards.py` enforcing the four-endpoint limit for `observability.py`.
  - [ ] Subtask 4.5 - Forbid `select(`, `Session`, `db.query`, SQLAlchemy model imports and `LlmCallLogModel` in `observability.py`.
  - [ ] Subtask 4.6 - Forbid imports from `admin.llm.prompts` inside `observability.py`.

- [ ] Task 5 - Validate behavior and persist after evidence (AC: AC2, AC6, AC7)
  - [ ] Subtask 5.1 - Generate `route-owners-after.md` and `openapi-after.json`.
  - [ ] Subtask 5.2 - Generate `openapi-contract-diff.md` filtered to the four routes.
  - [ ] Subtask 5.3 - Add runtime contract coverage for replay and purge.
  - [ ] Subtask 5.4 - Run targeted unit and integration tests in the activated venv.
  - [ ] Subtask 5.5 - Run `ruff format .`, `ruff check .`, and either `pytest -q` or record why the full suite was skipped.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/v1/routers/admin/llm/observability.py` as the only HTTP adapter for these four endpoints.
  - `backend/app/services/llm_observability/admin_observability.py` for call-log listing, dashboard metrics, replay and purge use cases.
  - Existing response contracts from `app.services.api_contracts.admin.llm.prompts`.
  - Existing admin auth dependency `require_admin_user` and request id helper `resolve_request_id`.
- Do not recreate:
  - SQL queries from the deleted `prompts.py` handlers inside `observability.py`.
  - A second observability router or a wrapper module.
  - New response models equivalent to `LlmCallLogListResponse`, `LlmDashboardResponse` or `ReplayPayload`.
  - Imports from `app.api.v1.routers.admin.llm.prompts` inside `observability.py`.
- Shared abstraction allowed only if:
  - A missing helper is required by both `prompts.py` and `observability.py`, no existing service
    owns it, and the helper is placed outside `app.api` with French module comment/docstrings.

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

- `backend/app/api/v1/routers/admin/llm/prompts.py` with `@router.get("/call-logs")`
- `backend/app/api/v1/routers/admin/llm/prompts.py` with `@router.get("/dashboard")`
- `backend/app/api/v1/routers/admin/llm/prompts.py` with `@router.post("/replay")`
- `backend/app/api/v1/routers/admin/llm/prompts.py` with `@router.post("/call-logs/purge")`
- Runtime route owner for the four endpoints equal to `app.api.v1.routers.admin.llm.prompts`
- More or fewer than exactly one runtime `APIRoute` per expected path and method
- `observability.py` importing from `app.api.v1.routers.admin.llm.prompts`
- `observability.py` containing `select(`, `db.query`, direct SQLAlchemy model imports,
  `Session` annotations or `LlmCallLogModel`
- Any new module named for compatibility, legacy, shim, alias or fallback for these routes

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to or duplicates a canonical implementation only to preserve an old surface.
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

Allowed decisions:

- `delete`
- `keep`
- `needs-user-decision`

Forbidden decision for this story:

- `replace-consumer`: HTTP consumers are preserved because URLs remain stable; only Python
  handlers classified as removable may be deleted.

Audit output path when applicable:

- `_condamad/stories/converge-admin-llm-observability-router/route-consumption-audit.md`

The audit must classify these items at minimum:

- `backend/app/api/v1/routers/admin/llm/prompts.py::list_call_logs`
- `backend/app/api/v1/routers/admin/llm/prompts.py::get_dashboard`
- `backend/app/api/v1/routers/admin/llm/prompts.py::replay_request`
- `backend/app/api/v1/routers/admin/llm/prompts.py::purge_logs`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin LLM call log list HTTP endpoint | `admin/llm/observability.py::list_call_logs` | `admin/llm/prompts.py::list_call_logs` |
| Admin LLM observability dashboard HTTP endpoint | `admin/llm/observability.py::get_dashboard` | `admin/llm/prompts.py::get_dashboard` |
| Admin LLM replay HTTP endpoint | `backend/app/api/v1/routers/admin/llm/observability.py::replay_request` | `backend/app/api/v1/routers/admin/llm/prompts.py::replay_request` |
| Admin LLM call-log purge HTTP endpoint | `backend/app/api/v1/routers/admin/llm/observability.py::purge_logs` | `backend/app/api/v1/routers/admin/llm/prompts.py::purge_logs` |

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

For this story, external usage of HTTP URLs is not a blocker because URLs are preserved.
External usage of Python handler symbols in `prompts.py` is a blocker only if a concrete
consumer outside tests imports those symbols directly.

## 16. Generated Contract Check

Required generated-contract evidence:

- OpenAPI path presence for:
  - `/v1/admin/llm/call-logs`
  - `/v1/admin/llm/dashboard`
  - `/v1/admin/llm/replay`
  - `/v1/admin/llm/call-logs/purge`
- Runtime owner assertion from `app.routes`.
- Exactly one runtime `APIRoute` per expected path and method.
- Generated client/schema scan. When generated clients or schemas are present or referenced,
  operationId diffs must be neutralized or documented as non-consumed with scan evidence.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/api/v1/routers/admin/llm/observability.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/llm_observability/admin_observability.py`
- `backend/app/services/api_contracts/admin/llm/prompts.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/tests/unit/test_story_70_14_transition_guards.py`
- `backend/app/tests/integration/test_admin_llm_config_api.py`
- `_condamad/audits/api-adapter/2026-04-27-1906/00-audit-report.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/02-finding-register.md`

## 18. Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/registry.py` - register the canonical observability router.
- `backend/app/api/v1/routers/admin/llm/prompts.py` - remove duplicated observability route handlers and dead imports.
- `backend/app/tests/unit/test_api_router_architecture.py` - add runtime owner and AST reintroduction guard.
- `backend/tests/unit/test_story_70_14_transition_guards.py` - keep the existing observability router boundary guard current.
- `_condamad/stories/converge-admin-llm-observability-router/route-consumption-audit.md` - persist removal classification.
- `_condamad/stories/converge-admin-llm-observability-router/openapi-before.json` - persist baseline.
- `_condamad/stories/converge-admin-llm-observability-router/openapi-after.json` - persist after snapshot.
- `_condamad/stories/converge-admin-llm-observability-router/openapi-contract-diff.md` - persist filtered diff.
- `_condamad/stories/converge-admin-llm-observability-router/route-owners-before.md` - persist baseline owner inventory.
- `_condamad/stories/converge-admin-llm-observability-router/route-owners-after.md` - persist after owner inventory.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - architecture guards.
- `backend/tests/unit/test_story_70_14_transition_guards.py` - observability router endpoint boundary.
- `backend/app/tests/integration/test_admin_llm_config_api.py` - runtime contract for all four endpoints.

Files not expected to change:

- `backend/pyproject.toml` - no dependency change is allowed.
- `backend/alembic` - no database migration is expected.
- `backend/app/infra/db/models` - no model change is expected.
- `frontend/src` - no URL or payload change is expected.
- `backend/app/services/llm_observability/admin_observability.py` - expected reuse, not behavior
  change; modification requires a recorded contract gap that blocks ACs.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_api_router_architecture.py
pytest -q tests/unit/test_story_70_14_transition_guards.py
pytest -q app/tests/integration/test_admin_llm_config_api.py
pytest -q
rg -n "@router\.(get|post)\(\"/(call-logs|dashboard|replay|call-logs/purge)\"" app/api/v1/routers/admin/llm/prompts.py
```

Runtime OpenAPI check to include in tests or run manually inside `backend` after venv activation:

```powershell
@'
from app.main import app

schema = app.openapi()
expected = {
    "/v1/admin/llm/call-logs": "get",
    "/v1/admin/llm/dashboard": "get",
    "/v1/admin/llm/replay": "post",
    "/v1/admin/llm/call-logs/purge": "post",
}
assert all(method in schema["paths"][path] for path, method in expected.items())
'@ | python -B -
```

Runtime owner check to include in tests or run manually inside `backend` after venv activation:

```powershell
@'
from app.main import app
from fastapi.routing import APIRoute

expected = {
    ("/v1/admin/llm/call-logs", "GET"),
    ("/v1/admin/llm/dashboard", "GET"),
    ("/v1/admin/llm/replay", "POST"),
    ("/v1/admin/llm/call-logs/purge", "POST"),
}
matches = [
    (route.path, method, route.endpoint.__module__)
    for route in app.routes
    if isinstance(route, APIRoute)
    for method in route.methods
    if (route.path, method) in expected
]
assert len(matches) == len(expected)
assert {(path, method) for path, method, _owner in matches} == expected
assert {owner for _path, _method, owner in matches} == {
    "app.api.v1.routers.admin.llm.observability"
}
'@ | python -B -
```

Persistent evidence check to include after generating snapshots:

```powershell
@'
from pathlib import Path

root = Path("../_condamad/stories/converge-admin-llm-observability-router")
paths = [
    "openapi-before.json",
    "openapi-after.json",
    "openapi-contract-diff.md",
    "route-owners-before.md",
    "route-owners-after.md",
]
assert all((root / path).exists() for path in paths)
'@ | python -B -
```

Generated client / operationId check to include before accepting OpenAPI diffs:

```powershell
rg -n "operationId|openapi|generated client|client generated|api-client" ../frontend ../backend
```

## 21. Regression Risks

- Risk: duplicate FastAPI routes remain registered if `observability.py` is added before deleting the handlers in `prompts.py`.
  - Guardrail: runtime owner test must assert exactly one owner per path and reject `prompts.py`.
- Risk: OpenAPI operationIds change and break a generated client.
  - Guardrail: persist OpenAPI diff, scan generated clients, and neutralize consumed operationId diffs.
- Risk: deleting imports from `prompts.py` removes symbols still used by unrelated prompt/catalog handlers.
  - Guardrail: use AST/static checks and run targeted admin LLM integration tests before marking complete.
- Risk: service delegation in `observability.py` differs subtly from the old inline SQL behavior.
  - Guardrail: run runtime contract tests for call-log, dashboard, replay and purge.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not import `prompts.py` from `observability.py`; shared contracts must come from
  `app.services.api_contracts`.
- Respecter l'activation du venv avant toute commande Python: `.\.venv\Scripts\Activate.ps1`.
- Ne pas créer de `requirements.txt`; `backend/pyproject.toml` reste la source unique des dépendances Python.
- Tout fichier applicatif nouveau ou significativement modifié doit contenir un commentaire
  global en français et des docstrings en français pour les fonctions publiques ou non triviales.

## 23. References

- `_condamad/audits/api-adapter/2026-04-27-1906/00-audit-report.md` - rapport source et synthèse F-001.
- `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md` - preuves E-004, E-005, E-006 et E-012.
- `_condamad/audits/api-adapter/2026-04-27-1906/02-finding-register.md` - détail F-001 et action recommandée.
- `_condamad/audits/api-adapter/2026-04-27-1906/03-story-candidates.md` - candidate SC-001.
- `backend/app/api/v1/routers/admin/llm/observability.py` - routeur canonique cible.
- `backend/app/api/v1/routers/admin/llm/prompts.py` - façade historique à réduire.
- `backend/app/api/v1/routers/registry.py` - source de montage API v1.
- `backend/app/tests/integration/test_admin_llm_config_api.py` - couverture comportementale existante.
- `backend/app/tests/unit/test_api_router_architecture.py` - emplacement attendu des gardes d'architecture.
- `backend/tests/unit/test_story_70_14_transition_guards.py` - garde existante sur le périmètre du routeur observability.
