# Story harden-api-adapter-boundary-guards: Durcir la frontière adaptateur API et les exceptions de montage

Status: ready-for-review

## 1. Objective

Corriger les findings restants F-002, F-003 et F-004 de l'audit API adapter.
La dette de persistance des routeurs doit devenir explicite, testable et non extensible.
Les exceptions ad hoc de montage API v1 doivent devenir un registre structuré validé au runtime.
La story doit aussi extraire un premier flux de persistance depuis un routeur dense vers un service
sans changer les contrats HTTP.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/api-adapter/2026-04-27-1906`
- Reason for change: après correction de F-001 par
  `_condamad/stories/converge-admin-llm-observability-router`, l'audit conserve:
  F-002 sur l'orchestration DB dans les routeurs, F-003 sur les montages hors registre
  codés dans `main.py`, et F-004 sur l'absence de garde anti-SQLAlchemy.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api`
- In scope:
  - Créer un inventaire persistant des usages DB directs actuels dans `backend/app/api/v1/routers` et `backend/app/api/dependencies`.
  - Ajouter une allowlist exacte, justifiée et contrôlée par test pour les usages DB directs encore présents.
  - Ajouter une garde AST qui échoue sur tout nouvel import SQLAlchemy, import de modèle DB,
    `get_db_session` ou opération de session hors allowlist exacte.
  - Formaliser les montages hors registre API v1 dans un registre d'exceptions structuré:
    `/api/email/unsubscribe`, routeur QA interne conditionnel et `/health`.
  - Extraire au moins un flux de persistance d'un routeur dense cité par l'audit vers un service existant ou nouveau sous `backend/app/services`, avec maintien du contrat HTTP.
  - Persister les preuves avant/après: inventaire SQL routeurs, inventaire des routes runtime hors registre, allowlist et diff OpenAPI.
- Out of scope:
  - Extraire en une seule story les 39 routeurs contenant de la persistance directe.
  - Modifier les URLs, méthodes, payloads, statuts ou schémas OpenAPI des routes existantes.
  - Modifier le frontend, les migrations Alembic, les modèles SQLAlchemy ou la stratégie d'authentification.
  - Revenir sur la propriété canonique des endpoints admin LLM observability livrée par F-001.
- Explicit non-goals:
  - Ne pas créer de wrapper, alias, fallback, re-export ou deuxième registre concurrent.
  - Ne pas autoriser une exception par dossier ou wildcard.
  - Ne pas déplacer de logique métier vers `backend/app/api`.
  - Ne pas contourner `RG-007`: `admin/llm/observability.py` reste l'unique propriétaire runtime des endpoints observability.
  - Ne pas ajouter de dossier racine sous `backend/`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: api-adapter-boundary-convergence
- Archetype reason: les findings restants convergent `backend/app/api` vers un adaptateur
  HTTP strict, avec exceptions de montage et dette SQL explicites, mesurables et gardées.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les contrats HTTP existants doivent rester équivalents: mêmes chemins, méthodes, statuts attendus, tags et schémas OpenAPI sauf différence documentée comme purement metadata.
  - La première extraction de persistance doit préserver les réponses et erreurs observables des routes ciblées.
  - Les exceptions hors registre peuvent changer de lieu de déclaration, pas de comportement runtime.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une route hors registre n'a pas de statut cible clair,
  si la première extraction impose un changement HTTP, ou si une exception SQL n'a pas
  de justification liée à une réduction future.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Prouver les montages API et le no-new-SQL par `app.routes`, `app.openapi()` et garde AST. |
| Baseline Snapshot | yes | La story promet une préservation des routes et une réduction mesurable de dette SQL; elle doit capturer avant/après. |
| Ownership Routing | yes | Router DB vers `services`/`infra`, montages API vers registre explicite, routeurs comme adaptateurs HTTP. |
| Allowlist Exception | yes | Des usages DB existants restent temporairement autorisés; chaque exception doit être exacte, justifiée et contrôlée. |
| Contract Shape | no | Aucun changement de forme d'API n'est autorisé; les contrats sont seulement surveillés par OpenAPI avant/après. |
| Batch Migration | yes | La story contient trois lots indépendants: registre d'exceptions de routes, garde SQL, et première extraction de flux DB. |
| Reintroduction Guard | yes | La garde doit échouer si un nouveau SQL router-level ou un montage hors registre implicite apparaît. |
| Persistent Evidence | yes | Les inventaires, allowlists et diffs doivent rester dans le dossier de story pour suivre la dette restante. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - `app.main.app.routes` pour l'inventaire effectif des routes, de leurs chemins et de leurs modules propriétaires.
  - `app.main.app.openapi()` pour vérifier que les chemins/méthodes exposés ne changent pas.
  - AST de `backend/app/api/v1/routers` et `backend/app/api/dependencies` pour détecter imports SQLAlchemy, modèles DB, `get_db_session` et opérations de session.
- Secondary evidence:
  - `rg` ciblés sur `from sqlalchemy`, `from app.infra.db.models`, `from app.infra.db.session`, `db.execute`, `db.commit`, `db.add`, `db.flush`, `db.refresh`, `db.query`.
  - Inspection de `backend/app/main.py`, `backend/app/api/v1/routers/registry.py` et `backend/app/tests/unit/test_api_router_architecture.py`.
- Static scans alone are not sufficient for this story because:
  - FastAPI peut monter des routes conditionnelles au runtime, et les imports SQL peuvent
    être masqués par alias ou imports locaux; la preuve doit combiner route table, OpenAPI et AST.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/harden-api-adapter-boundary-guards/openapi-before.json`
  - `_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-before.md`
  - `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-inventory-before.md`
- Comparison after implementation:
  - `_condamad/stories/harden-api-adapter-boundary-guards/openapi-after.json`
  - `_condamad/stories/harden-api-adapter-boundary-guards/openapi-contract-diff.md`
  - `_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-after.md`
  - `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-inventory-after.md`
- Expected invariant:
  - Aucun chemin/méthode OpenAPI existant ne disparaît.
  - Les routes hors registre sont présentes uniquement si elles figurent dans le registre d'exceptions exact.
  - Le nombre d'usages DB directs dans les routeurs ne peut pas augmenter.
  - Au moins un flux de persistance routeur est supprimé du routeur ciblé et déplacé vers un service.
- Allowed differences:
  - Diminution du nombre d'entrées SQL dans l'inventaire.
  - Déplacement du code de persistance vers `backend/app/services/**` ou réutilisation d'un service existant.
  - Diff OpenAPI uniquement vide ou limité à de la metadata non consommée, avec justification dans `openapi-contract-diff.md`.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| HTTP adapter, request parsing, dependency injection and response mapping | `backend/app/api/**` | `backend/app/services/**` |
| Application use case and DB transaction orchestration | `backend/app/services/**` | `backend/app/api/**` |
| SQLAlchemy models, sessions and persistence details | `backend/app/infra/**` | New imports in `backend/app/api/v1/routers/**` |
| Runtime API v1 router registration | `backend/app/api/v1/routers/registry.py` plus exception registry | Ad hoc `app.include_router(router)` calls in `backend/app/main.py` |
| Health route bootstrap | `backend/app/api/health.py` with explicit non-v1 exception | API v1 router registry |
| Public email unsubscribe historical URL | Exact exception registry entry for `/api/email/unsubscribe` | Hidden allowlist in a test body |
| Internal LLM QA conditional route | Exact exception registry entry with settings condition | Unstructured import/include in `main.py` without guard |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

The implementation must create or update a structured exception register and a SQL debt allowlist.
Each row must be exact; wildcard, folder-wide and undocumented temporary exceptions are forbidden.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/api/health.py` | `/health` | Route de santé hors API v1 montée au bootstrap. | Exception permanente documentée et testée par runtime route table. |
| `backend/app/api/v1/routers/public/email.py` | `/api/email/unsubscribe` | URL historique publique hors `/v1`. | Story dédiée requise pour suppression. |
| `backend/app/api/v1/routers/internal/llm/qa.py` | routeur QA interne conditionnel | Routeur interne activable par settings. | Permanent si bloqué en production sans opt-in. |
| `baseline inventory required` | `existing router SQL entries` | Dette F-002 à réduire progressivement. | Chaque entrée doit pointer vers une réduction; aucune nouvelle entrée. |

Validation required:

- Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_api_router_architecture.py`.
- Persist the full SQL allowlist at `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`.
- Persist the route exception inventory at `_condamad/stories/harden-api-adapter-boundary-guards/route-exception-register.md`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API payload, DTO, status code, error envelope, generated client type, or frontend
  type may change. OpenAPI before/after snapshots are required only to prove preservation.

## 4g. Batch Migration Plan

Use when the story crosses multiple packages, route groups, namespaces, DTO
groups, generated artifacts, or consumer categories.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 - Route exceptions | `main.py` ad hoc exceptions | Structured exception register | None | Architecture pytest | Runtime routes match exact rows | Unclassified non-v1 route |
| 2 - SQL guard | Unguarded SQL/session use | SQL allowlist plus AST guard | None | Architecture pytest | New unlisted DB use fails | Unclassified baseline entry |
| 3 - DB flow extraction | One dense router flow | Service in `backend/app/services/**` | HTTP unchanged | Targeted route tests | SQL absent from router | HTTP/schema change |

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration
mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI baseline | `_condamad/stories/harden-api-adapter-boundary-guards/openapi-before.json` | Prouver le contrat runtime initial. |
| OpenAPI after snapshot | `_condamad/stories/harden-api-adapter-boundary-guards/openapi-after.json` | Prouver le contrat runtime final. |
| OpenAPI diff | `_condamad/stories/harden-api-adapter-boundary-guards/openapi-contract-diff.md` | Documenter les différences autorisées. |
| Route mount baseline | `_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-before.md` | Inventorier les propriétaires runtime avant changement. |
| Route mount after snapshot | `_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-after.md` | Vérifier les exceptions structurées après changement. |
| SQL inventory baseline | `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-inventory-before.md` | Capturer la dette F-002 avant extraction. |
| SQL inventory after snapshot | `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-inventory-after.md` | Prouver absence d'augmentation et première réduction. |
| SQL allowlist | `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | Lister exactement les exceptions restantes avec justification. |
| Route exception register | `_condamad/stories/harden-api-adapter-boundary-guards/route-exception-register.md` | Remplacer F-003 par un registre auditable. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update deterministic guards that fail if:

- `backend/app/main.py` includes an API v1 router not represented by the canonical registry or the structured route exception register.
- A route from module `app.api.v1.*` is mounted outside `/v1/` without an exact exception row.
- A new router imports `sqlalchemy`, `app.infra.db.models`, or `app.infra.db.session.get_db_session` outside the SQL allowlist.
- A new route handler calls `db.execute`, `db.commit`, `db.add`, `db.flush`, `db.refresh` or `db.query` outside the SQL allowlist.
- The selected extracted flow still contains its old SQL operations in the API router after extraction.
- `RG-007` is violated for admin LLM observability route ownership.

Guard evidence:

- Evidence profiles: `ast_architecture_guard`, `runtime_openapi_contract`, `reintroduction_guard`, `allowlist_register_validated`.
- Required command: `pytest -q app/tests/unit/test_api_router_architecture.py`.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/api-adapter/2026-04-27-1906/02-finding-register.md` -
  F-002 reports DB orchestration in 39 API router files; F-003 reports `main.py`
  registration exceptions; F-004 reports missing SQL guard coverage.
- Evidence 2: `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md` -
  E-007 and E-008 identify direct DB operations/imports; E-009 identifies `email_router`
  and internal QA outside the v1 registry; E-011 confirms the guard gap.
- Evidence 3: `backend/app/main.py` - currently calls `include_api_v1_routers(app)`,
  `app.include_router(email_router, prefix="/api", tags=["email"])`,
  then `_include_internal_llm_qa_router(app)`.
- Evidence 4: `backend/app/tests/unit/test_api_router_architecture.py` - contains route
  architecture guards and current exact `NON_V1_ROUTE_EXCEPTIONS`, but no broad AST
  guard preventing new router-level SQL debt.
- Evidence 5: `backend/app/api/v1/routers/registry.py` - is the canonical API v1 registry and now includes `admin_llm_observability_router` after F-001.
- Evidence 6: `backend/app/api/v1/routers/admin/llm/prompts.py`,
  `backend/app/api/v1/routers/admin/content.py`, and
  `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` -
  audit F-002 cites these as dense DB-owning routers.
- Evidence 7: `_condamad/stories/converge-admin-llm-observability-router/00-story.md` - marks F-001 out of scope and establishes the observability route ownership invariant.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - shared regression invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- Every runtime route mounted outside the API v1 registry is represented by an exact structured exception with reason and permanence/expiry decision.
- `backend/app/tests/unit/test_api_router_architecture.py` fails on any new route-level SQLAlchemy/session/model usage not present in the SQL allowlist.
- The SQL allowlist is persisted, exact, and cannot grow silently.
- At least one route-handler persistence flow from a dense F-002 router is moved to `backend/app/services/**`, and the router becomes a thinner HTTP adapter for that flow.
- OpenAPI before/after proves no route contract disappeared or changed shape.
- The admin LLM observability ownership guard from F-001 remains green.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-002` - this story changes API router architecture and must preserve clear router responsibilities.
  - `RG-003` - this story touches API v1 route mounting and must keep the canonical registration mechanism auditable.
  - `RG-005` - this story directly protects the API/services persistence boundary.
  - `RG-006` - this story reinforces `backend/app/api` as a strict HTTP adapter.
  - `RG-007` - this story touches `admin/llm/prompts.py` risk context and must not regress observability route ownership.
- Non-applicable invariants:
  - `RG-001` - no historical route facade is removed by this story.
  - `RG-004` - HTTP error envelope centralization is not modified.
- Required regression evidence:
  - Runtime route inventory before/after.
  - OpenAPI before/after diff.
  - AST SQL guard test.
  - Exact allowlist validation.
  - Existing admin LLM observability owner guard.
- Allowed differences:
  - SQL debt inventory may decrease.
  - Route exception metadata may move from test-local constants to a structured registry.
  - No HTTP contract difference is allowed unless documented as OpenAPI metadata only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Non-v1 API route exceptions are exact. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_api_router_architecture.py`; register artifact. |
| AC2 | `main.py` cannot mount ad hoc API v1 routers. | Evidence profile: `ast_architecture_guard`; `app.routes`; `pytest -q app/tests/unit/test_api_router_architecture.py`. |
| AC3 | SQL/session/model use has before/after inventory. | Evidence profile: `ast_architecture_guard`; architecture pytest; inventory artifacts. |
| AC4 | New router DB usage fails outside allowlist. | Evidence profile: `ast_architecture_guard`; AST guard; `pytest -q app/tests/unit/test_api_router_architecture.py`. |
| AC5 | One dense-router DB flow moves to a service. | Evidence profile: `runtime_openapi_contract`; `app.openapi()`; targeted route pytest. |
| AC6 | OpenAPI route surface is preserved. | Evidence profile: `openapi_before_after_snapshot`; `pytest -q app/tests/unit/test_api_router_architecture.py`; `app.openapi()`. |
| AC7 | F-001 observability ownership remains fixed. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_api_router_architecture.py`. |
| AC8 | SQL allowlist rows require exact metadata. | Evidence profile: `allowlist_register_validated`; architecture pytest. |

## 8. Implementation Tasks

- [x] Task 1 - Capture baselines before editing (AC: AC1, AC3, AC6)
  - [x] Subtask 1.1 - Generate `openapi-before.json` from `app.openapi()`.
  - [x] Subtask 1.2 - Generate `runtime-route-mounts-before.md` from `app.routes`, including path, methods, endpoint module and whether it is registry-owned or exception-owned.
  - [x] Subtask 1.3 - Generate `router-sql-inventory-before.md` using AST over `backend/app/api/v1/routers` and `backend/app/api/dependencies`.

- [x] Task 2 - Formalize route exceptions (AC: AC1, AC2)
  - [x] Subtask 2.1 - Move route exception data out of ad hoc test-only logic into a structured register consumable by tests.
  - [x] Subtask 2.2 - Represent `/health`, `/api/email/unsubscribe`, and the conditional internal LLM QA router with exact reason and expiry/permanence decision.
  - [x] Subtask 2.3 - Update the runtime route architecture test to compare `app.routes` against canonical registry plus exact exceptions.

- [x] Task 3 - Add SQL debt allowlist and AST guard (AC: AC3, AC4, AC8)
  - [x] Subtask 3.1 - Create the exact SQL allowlist from the baseline inventory; do not use folder-wide or wildcard entries.
  - [x] Subtask 3.2 - Add a parser-based guard for forbidden imports and session operations in routers and API dependencies.
  - [x] Subtask 3.3 - Make the guard fail for entries not present in the allowlist and for allowlist rows missing reason or expiry/permanence.
  - [x] Subtask 3.4 - Persist `router-sql-allowlist.md` with the same entries and decisions used by the test.

- [x] Task 4 - Extract one DB-owned route flow (AC: AC3, AC5, AC6)
  - [x] Subtask 4.1 - Choose one bounded flow from `admin/llm/prompts.py`,
    `admin/content.py`, or `ops/entitlement_mutation_audits.py`.
  - [x] Subtask 4.2 - Move its SQL/query/commit orchestration to an existing service or a new focused service under `backend/app/services/**`.
  - [x] Subtask 4.3 - Keep the router responsible only for HTTP dependencies, request validation and response mapping for that flow.
  - [x] Subtask 4.4 - Add or update targeted tests proving the selected HTTP behavior is preserved.
  - [x] Subtask 4.5 - Remove the extracted SQL entries from the allowlist and prove they are absent from the router AST.

- [x] Task 5 - Persist after evidence and validate (AC: AC1, AC3, AC4, AC6, AC7, AC8)
  - [x] Subtask 5.1 - Generate `openapi-after.json`, `runtime-route-mounts-after.md` and `router-sql-inventory-after.md`.
  - [x] Subtask 5.2 - Generate `openapi-contract-diff.md` and document allowed differences.
  - [x] Subtask 5.3 - Run targeted architecture, route and service tests in the activated venv.
  - [x] Subtask 5.4 - Run `ruff format .`, `ruff check .`, and `pytest -q` or record a precise blocker if the full suite cannot run.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/v1/routers/registry.py` as the canonical API v1 registration source.
  - `backend/app/tests/unit/test_api_router_architecture.py` for architecture guards.
  - Existing service modules under `backend/app/services/**` when a suitable owner already exists for the extracted flow.
  - Existing API contracts and Pydantic schemas; do not duplicate response models.
- Do not recreate:
  - A second API route registry.
  - A second SQL scanner script if the architecture test can own the AST logic.
  - New DTOs equivalent to existing API/service contracts.
  - Wrapper services that only call router functions.
- Shared abstraction allowed only if:
  - It removes duplicated AST/route inventory logic used by more than one test or evidence generator, and it lives outside a route module with French module comment/docstrings.

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

- New `app.include_router(router)` in `backend/app/main.py` for `app.api.v1.routers.*` without exact exception registration.
- New route under `app.api.v1.*` outside `/v1/` without exact exception registration.
- New `from sqlalchemy import symbol` in `backend/app/api/v1/routers/**` outside the SQL allowlist.
- New `from app.infra.db.models import symbol` in `backend/app/api/v1/routers/**` outside the SQL allowlist.
- New `from app.infra.db.session import get_db_session` in `backend/app/api/v1/routers/**` outside the SQL allowlist.
- New `db.execute`, `db.commit`, `db.add`, `db.flush`, `db.refresh` or `db.query` in `backend/app/api/v1/routers/**` outside the SQL allowlist.
- Wildcard allowlist entries such as `backend/app/api/v1/routers/**` or module-wide exemptions without exact symbol/call rows.
- Any regression of `ADMIN_LLM_OBSERVABILITY_ROUTE_OWNER`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| API v1 route registration | `backend/app/api/v1/routers/registry.py` plus exact exception register | Ad hoc `app.include_router(router)` in `backend/app/main.py` |
| Route exception governance | Structured exception register and architecture test | Test-local memory or broad allowlist |
| SQL/session/model usage in application flows | `backend/app/services/**` and `backend/app/infra/**` | `backend/app/api/v1/routers/**` |
| HTTP request/response adaptation | `backend/app/api/v1/routers/**` | `backend/app/services/**` |
| Admin LLM observability HTTP ownership | `backend/app/api/v1/routers/admin/llm/observability.py` | `backend/app/api/v1/routers/admin/llm/prompts.py` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

Required generated-contract evidence:

- OpenAPI before/after path and method preservation.
- Runtime route table after implementation proving exception registration.
- Generated client/schema scan before accepting any OpenAPI metadata diff.

## 17. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/api-adapter/2026-04-27-1906/00-audit-report.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/02-finding-register.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/main.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/api/v1/routers/admin/content.py`
- `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py`
- `backend/app/services`

## 18. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_api_router_architecture.py` - add structured route exception and SQL guard coverage.
- `backend/app/main.py` - replace route exception usage when the structured register owns it.
- `backend/app/api/v1/routers/registry.py` - expose registration metadata for architecture tests.
- One selected dense router - thin one selected DB-owned flow after inspection.
- `backend/app/services/**.py` - add or reuse focused service for the selected extracted flow.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` - persist exact SQL exceptions.
- `_condamad/stories/harden-api-adapter-boundary-guards/route-exception-register.md` - persist exact route exceptions.
- `_condamad/stories/harden-api-adapter-boundary-guards/openapi-before.json` - persist baseline.
- `_condamad/stories/harden-api-adapter-boundary-guards/openapi-after.json` - persist after snapshot.
- `_condamad/stories/harden-api-adapter-boundary-guards/openapi-contract-diff.md` - persist route contract diff.
- `_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-before.md` - persist baseline route mounts.
- `_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-after.md` - persist after route mounts.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-inventory-before.md` - persist baseline SQL inventory.
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-inventory-after.md` - persist after SQL inventory.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - architecture guard coverage.
- Targeted tests for the selected extracted route flow, chosen after inspecting existing coverage.
- Existing tests covering admin LLM observability ownership must continue to pass.

Files not expected to change:

- `backend/pyproject.toml` - no dependency change is allowed.
- `backend/alembic` - no schema migration is expected.
- `backend/app/infra/db/models` - no model change is expected.
- `frontend/src` - no API contract or UI change is expected.
- `requirements.txt` - must not be created.

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
pytest -q
rg -n "from sqlalchemy|from app\.infra\.db\.models|from app\.infra\.db\.session|db\.(execute|commit|add|flush|refresh|query)" app/api/v1/routers app/api/dependencies
rg -n "operationId|openapi|generated client|client generated|api-client" ../frontend ../backend
```

Runtime OpenAPI snapshot command to adapt for before/after evidence:

```powershell
@'
import json
from pathlib import Path
from app.main import app

target = Path("../_condamad/stories/harden-api-adapter-boundary-guards/openapi-after.json")
target.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True), encoding="utf-8")
'@ | python -B -
```

Runtime route inventory command to adapt for before/after evidence:

```powershell
@'
from pathlib import Path
from fastapi.routing import APIRoute
from app.main import app

lines = ["| Path | Methods | Owner |", "|---|---|---|"]
for route in app.routes:
    if not isinstance(route, APIRoute):
        continue
    methods = ",".join(sorted(route.methods or []))
    owner = getattr(route.endpoint, "__module__", "")
    lines.append(f"| `{route.path}` | `{methods}` | `{owner}` |")
Path("../_condamad/stories/harden-api-adapter-boundary-guards/runtime-route-mounts-after.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
'@ | python -B -
```

Story validation commands after drafting or changing this story:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/harden-api-adapter-boundary-guards/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/harden-api-adapter-boundary-guards/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/harden-api-adapter-boundary-guards/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/harden-api-adapter-boundary-guards/00-story.md
```

## 21. Regression Risks

- Risk: l'allowlist SQL fige la dette au lieu de la réduire.
  - Guardrail: AC5 impose une première extraction et AC8 bloque toute croissance silencieuse.
- Risk: un montage hors registre reste caché dans `main.py`.
  - Guardrail: inventaire runtime `app.routes` comparé au registre canonique plus exceptions exactes.
- Risk: l'extraction d'un flux DB modifie subtilement une réponse HTTP.
  - Guardrail: OpenAPI avant/après, tests ciblés de route et absence de changement de contrat autorisé.
- Risk: la correction de F-002 touche par erreur l'observability LLM déjà convergée.
  - Guardrail: RG-007 et test runtime owner existant.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python: `.\.venv\Scripts\Activate.ps1`.
- Ne pas créer de `requirements.txt`; `backend/pyproject.toml` reste la source unique des dépendances Python.
- Tout fichier applicatif nouveau ou significativement modifié doit contenir un commentaire
  global en français et des docstrings en français pour les fonctions publiques ou non triviales.
- Choisir un seul flux DB à extraire dans cette story; ne pas transformer la story en refactor massif des 39 routeurs.
- Toute exception SQL restante doit être exacte, justifiée, et reliée à une réduction future ou à une décision de permanence.

## 23. References

- `_condamad/audits/api-adapter/2026-04-27-1906/00-audit-report.md` - rapport source et synthèse des findings restants.
- `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md` - preuves E-007, E-008, E-009 et E-011.
- `_condamad/audits/api-adapter/2026-04-27-1906/02-finding-register.md` - détail F-002, F-003 et F-004.
- `_condamad/audits/api-adapter/2026-04-27-1906/03-story-candidates.md` - candidates SC-002, SC-003 et SC-004.
- `_condamad/stories/converge-admin-llm-observability-router/00-story.md` - story F-001 déjà corrigée à préserver.
- `_condamad/stories/regression-guardrails.md` - registre des invariants inter-stories.
- `backend/app/main.py` - montage runtime FastAPI.
- `backend/app/api/v1/routers/registry.py` - registre canonique API v1.
- `backend/app/tests/unit/test_api_router_architecture.py` - garde d'architecture attendue.
