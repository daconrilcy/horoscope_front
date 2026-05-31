# Story CS-403 quota-natal-transactionnel-remediation: Quota Natal Transactionnel Et Remediation
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: une lecture complete invalide peut epuiser le quota Basic lifetime et bloquer une correction gratuite.
- Source stakes: debit exact, persistance valide, remediation auditee, concurrence corrective, fermeture durable de `RG-157`.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent les primitives du brief sans deplacer le sujet vers UI.

## Objective

Garantir que le quota `natal_chart_long` est debite uniquement apres acceptation et persistance d'une lecture complete valide.
Garantir qu'une lecture historique invalide peut etre regeneree gratuitement, de facon idempotente, auditee et sans mutation silencieuse.

## Target State

- L'acces `natal_chart_long` est verifie avant generation sans debit definitif.
- Le debit final est execute dans la meme transaction applicative que la lecture complete acceptee.
- Un rejet editorial, un rejet grounding, une erreur provider ou un rollback DB laisse le quota utilisateur unchanged.
- Les lectures completes invalides sont detectees par absence narrative, chapitre manquant, contenu duplique ou sources vides.
- La remediation corrective reserve une lecture invalide de facon atomique et ne debite pas l'utilisateur.
- Deux demandes correctives concurrentes ne produisent pas deux lectures actives pour la meme lecture invalide.
- Le routeur public reste un adaptateur HTTP; la responsabilite metier vit dans les services entitlement, quota et generation.
- La politique de remediation est documentee dans un artefact backend ou CONDAMAD durable.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-403`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-002`, `RG-005`, `RG-006`, `RG-150`, `RG-152`, and `RG-157`.
- Evidence 4: guardrail resolver ran for backend-domain quota/remediation scope; local exact IDs were confirmed by targeted registry lookup.
- Evidence 5: `backend/app/api/v1/routers/public/natal_interpretation.py` calls `check_access_for_complete_generation` before generation.
- Evidence 6: `backend/app/api/v1/routers/public/natal_interpretation.py` calls `consume_on_acceptance` after accepted response assembly.
- Evidence 7: `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py` still exposes `check_and_consume`.
- Evidence 8: `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` defines rejected and corrective payload markers.
- Evidence 9: `backend/app/services/llm_generation/natal/interpretation_service.py` contains corrective claim and release methods.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created root directory is required.
- Scope vector:
  - operation `update`, domain `backend-domain`
  - paths `backend/app/api/v1/routers/public`, `backend/app/services/entitlement`, `backend/app/services/quota`
  - contracts `quota`, `transaction`, `corrective-regeneration`, `narrative-reading`

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| access verification | in scope | AC1, Task 1, Task 2 |
| optional reservation | in scope | AC7, AC8, Task 5 |
| final quota consumption | in scope | AC2, AC3, Task 3 |
| same application transaction | in scope | AC3, AC4, Task 3, Task 4 |
| deterministic compensation | in scope | AC4, Task 4 |
| rejected validation | in scope | AC1, AC4, Task 6 |
| rejected grounding | in scope | AC1, AC4, Task 6 |
| provider error | in scope | AC4, Task 6 |
| rollback DB | in scope | AC4, Task 6 |
| invalid complete reading detector | in scope | AC5, Task 5 |
| missing narrative | in scope | AC5, Task 5 |
| missing chapter | in scope | AC5, Task 5 |
| duplicated content | in scope | AC5, Task 5 |
| empty Basic or Premium sources | in scope | AC5, Task 5 |
| corrective free regeneration | in scope | AC6, AC7, Task 5 |
| idempotent audit | in scope | AC7, AC8, Task 5, Task 9 |
| concurrency tests | in scope | AC8, Task 8 |
| remediation documentation | in scope | AC10, Task 9 |
| plan commercial limits | out of scope | Non-goals |
| generic manual quota reset | out of scope | Non-goals |
| frontend accordion rendering | out of scope | Non-goals |
| unsecured admin route | out of scope | Non-goals |
| CS-396 dependency | dependency | Must remain done before implementation starts |

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend entitlement verification, quota debit timing, corrective regeneration and invalid complete-reading detection.
  - Backend persistence transaction around accepted complete readings.
  - Backend audit trace for corrective remediation.
  - Backend tests for rejection, rollback, accepted debit and concurrent corrective requests.
- Out of scope:
  - Frontend UI, React rendering, CSS, commercial limit changes, generic manual quota reset, auth model, i18n, build tooling and DB migration.
- Explicit non-goals:
  - No frontend route, screen, client generation, unsecured admin route, history deletion, plan-limit change or accordion rendering fix.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Debit `natal_chart_long` only after an accepted complete reading is flushed in the same DB unit of work.
  - Keep cached complete replays free of quota debit.
  - Keep corrective regeneration free of quota debit and auditable.
  - Keep the public router as HTTP orchestration only.
  - Preserve public error status codes unless a test proves the current code contradicts the documented contract.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the existing DB model cannot represent a corrective reservation without silent historical mutation.
- Additional validation rules:
  - Use `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` for acceptance and rollback quota behavior.
  - Use `pytest -q backend/tests/integration -k "natal and (quota or interpretation or rejected)"` for public flow behavior.
  - Use `pytest -q --long backend/app/tests/integration/test_natal_chart_long_entitlement.py backend/app/tests/integration/test_natal_interpretation_endpoint.py`.
  - Use `app.routes`, `app.openapi()`, `TestClient` or `AST guard` only for route-boundary proofs.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, DB state checks, `app.routes` and `app.openapi()` prove runtime behavior. |
| Baseline Snapshot | yes | Before/after artifacts prove the only allowed delta is quota/remediation behavior. |
| Ownership Routing | yes | Entitlement, quota, generation and router responsibilities must stay canonical. |
| Allowlist Exception | no | No broad tolerance register is authorized for duplicate chapters or empty sources. |
| Contract Shape | yes | Corrective state, accepted reading and quota state have exact observable rules. |
| Batch Migration | no | No bulk data migration is authorized; historical rows are classified lazily or by bounded service logic. |
| Reintroduction Guard | yes | Early debit and public replay of invalid readings must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Access verification performs no quota debit. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC2 | One accepted complete reading debits one unit. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC3 | Accepted quota debit commits atomically. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration -k "natal and quota"`. |
| AC4 | Failed generation leaves quota state unchanged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration -k "natal and rejected"`. |
| AC5 | Invalid readings are classified deterministically. | Evidence profile: json_contract_shape; `pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC6 | Corrective regeneration is free. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration -k "natal and quota"`. |
| AC7 | Corrective regeneration is idempotent. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration -k "natal and interpretation"`. |
| AC8 | Corrective concurrency creates one active result. | Evidence profile: json_contract_shape; `pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py`. |
| AC9 | Public replay excludes rejected readings. | Evidence profile: json_contract_shape; `pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py`. |
| AC10 | Public adapter contains no direct consume call. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `check_and_consume`; `python` checks `app.routes`. |
| AC11 | Runtime route contract stays registered. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC12 | Remediation policy is persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Confirm `check_access_for_complete_generation` verifies access without calling quota consumption. (AC: AC1)
- [ ] Task 2: Remove public-router use of early debit paths and keep `check_and_consume` out of the route. (AC: AC1, AC10)
- [ ] Task 3: Move final quota debit into the accepted-reading transaction boundary. (AC: AC2, AC3)
- [ ] Task 4: Prove rejected output, provider error and DB rollback keep quota counters unchanged. (AC: AC4)
- [ ] Task 5: Implement deterministic invalid-complete classification for narrative, chapter, duplication and source defects. (AC: AC5)
- [ ] Task 6: Route eligible invalid readings through free corrective regeneration. (AC: AC6, AC7)
- [ ] Task 7: Preserve traceability by marking corrective state without silently rewriting historical text. (AC: AC7, AC12)
- [ ] Task 8: Add concurrent corrective tests for single active result and single quota state. (AC: AC8)
- [ ] Task 9: Document remediation policy, audit fields and frontend impact expectation. (AC: AC10, AC12)
- [ ] Task 10: Persist validation output and before/after evidence under this story directory. (AC: AC12)

## Files to Inspect First

- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py`
- `backend/app/services/entitlement/b2c_runtime_gate.py`
- `backend/app/services/quota/usage_service.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
- `backend/docs` or `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence`

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, DB assertions, `app.routes`, `app.openapi()`, and service-level quota state.
- Runtime evidence:
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
  - `pytest -q backend/tests/integration -k "natal and (quota or interpretation or rejected)"`.
  - `pytest -q --long backend/app/tests/integration/test_natal_chart_long_entitlement.py backend/app/tests/integration/test_natal_interpretation_endpoint.py`.
- Secondary evidence:
  - Targeted `rg` scans for direct router consumption and forbidden public replay paths.
- Static scans alone are not sufficient for this story because:
  - The quota debit must be proven against DB transaction state and accepted-reading persistence.

## Contract Shape

- Contract type:
  - Backend quota transaction and corrective regeneration workflow.
- Fields:
  - `NatalChartLongEntitlementResult.path`: `canonical_quota`, `canonical_unlimited`, or `corrective_regeneration`.
  - `corrective_regeneration`: true only for free corrective regeneration.
  - `corrective_interpretation_id`: references the invalid historical reading under correction.
  - `validation_status`: accepted readings only may trigger quota debit.
  - `grounding_status`: rejected readings stay out of public replay.
- Required fields:
  - `path`, `variant_code`, `usage_states`, `corrective_regeneration`.
- Optional fields:
  - `corrective_interpretation_id`, `corrective_original_use_case`.
- Status codes:
  - unchanged unless tests prove current mapping contradicts the existing public API contract.
- Serialization names:
  - Existing public response names stay unchanged; internal corrective markers remain internal.
- Frontend type impact:
  - none; document expected impact without changing React or generated clients.
- Generated contract impact:
  - `app.openapi()` must keep existing `/v1/natal/interpretation` public route shape unchanged.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/quota-remediation-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/quota-remediation-after.txt`
- Expected invariant:
  - The only intended behavior delta is transactional quota debit and free corrective remediation for invalid complete readings.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| HTTP request adaptation | `backend/app/api/v1/routers/public/natal_interpretation.py` | quota business rules or invalid-reading classifier |
| Access verification | `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py` | public router |
| B2C quota runtime | `backend/app/services/entitlement/b2c_runtime_gate.py` | LLM generation service |
| Counter persistence | `backend/app/services/quota/usage_service.py` | API router |
| Reading persistence workflow | `backend/app/services/llm_generation/natal/interpretation_service.py` | quota service |
| Stored payload classification | `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` | frontend code |
| Remediation documentation | backend docs or story evidence artifact | inline router comments only |

## Mandatory Reuse / DRY Constraints

- Reuse existing entitlement, quota and interpretation services; do not create a second quota subsystem.
- Reuse existing rejected payload and narrative reading validators for invalid-reading classification.
- Centralize corrective eligibility in one service owner so route, list and get flows consume the same state.
- Reuse existing DB session and transaction boundaries; do not duplicate commit logic in helper functions.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy quota debit path may run before accepted persistence.
- No compatibility route path may bypass the canonical entitlement gate.
- No fallback correction may mutate historical reading text silently.
- Do not add a shim, alias, broad tolerance register, hidden residual path, generic manual reset, or unsecured admin route.
- Forbidden public replay: rejected payloads, corrective pending rows, duplicated chapters, missing narrative and empty-source complete readings.
- Forbidden implementation surface: React components, CSS, generated frontend client or commercial plan configuration.

## Reintroduction Guard

- Guard source:
  - `rg -n "check_and_consume" app/api/v1/routers/public/natal_interpretation.py`
- Runtime guard:
  - `pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
  - `pytest -q tests/integration --tb=short -k "natal and (quota or interpretation or rejected)"`.
- Route-boundary guard:
  - `python -B -c "from app.main import app; assert '/v1/natal/interpretation' in app.openapi()['paths']"`.
  - `python -B -c "from app.main import app; assert '/v1/natal/interpretation' in {getattr(r, 'path', '') for r in app.routes}"`.
- Forbidden reintroduction:
  - Direct router calls to `check_and_consume`.
  - Quota debit before accepted-reading persistence.
  - Corrective regeneration that consumes `natal_chart_long`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 | scope -> API router boundary -> no business logic in route handlers. | router `rg`; targeted `pytest`. |
| RG-005 | scope -> API/service split -> persistence logic stays in services. | ownership review; `AST guard`. |
| RG-006 | scope -> API adapter -> non-API layers do not import API. | architecture `pytest`; bounded `rg`. |
| RG-150 | scope -> rejected readings -> rejected payloads stay audit-only. | rejected-boundary `pytest`; `rg`. |
| RG-152 | scope -> accepted complete readings -> public replay requires valid narrative. | narrative `pytest`; stored-payload tests. |
| RG-157 | scope -> quota remediation -> debit after accepted persistence only. | quota `pytest`; router `rg`. |

- Needs-investigation: `RG-003` only if implementation changes route mounting or OpenAPI registration.
- Non-applicable example: frontend style guardrails are out of scope because no React or CSS file is listed.
- Non-applicable example: DB migration guardrails are out of scope because no schema migration is authorized.
- Non-applicable example: auth guardrails are out of scope because no authentication model change is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/quota-remediation-before.txt` | Record initial quota and remediation behavior. |
| Baseline after | `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/quota-remediation-after.txt` | Record final quota and remediation behavior. |
| Validation output | `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/validation.txt` | Keep final lint, test and scan command output. |
| Remediation policy | `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/remediation-policy.md` | Document corrective policy and frontend impact. |
| Review output | `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for early quota debit, duplicate chapters, empty sources or silent history mutation. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/natal_interpretation.py` - keep route thin and remove any early debit path.
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py` - own access, corrective eligibility and final debit contract.
- `backend/app/services/entitlement/b2c_runtime_gate.py` - preserve B2C access and quota runtime behavior.
- `backend/app/services/quota/usage_service.py` - preserve atomic counter persistence and concurrency behavior.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - own accepted persistence and corrective classification.
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` - own invalid stored payload helpers.
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/**` - persist proof artifacts.

Likely tests:

- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - cover no debit before acceptance, rollback and corrective behavior.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - cover rejected readings outside public replay.
- `backend/tests/integration` - cover public natal quota, interpretation and rejected flows.
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py` - cover long entitlement and concurrency behavior.
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py` - cover endpoint behavior with `TestClient`.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/api/v1/routers/admin/**` - out of scope; no admin route is authorized.
- `backend/app/domain/astrology/calculators/**` - out of scope; no astrology computation is changed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- VC6: `python -B -m pytest -q tests/integration --tb=short -k "natal and (quota or interpretation or rejected)"`
- VC7: `python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py app/tests/integration/test_natal_interpretation_endpoint.py --tb=short`
- VC8: `rg -n "check_and_consume" app/api/v1/routers/public/natal_interpretation.py`
- VC9: `python -B -c "from app.main import app; assert '/v1/natal/interpretation' in app.openapi()['paths']"`
- VC10: `python -B -c "from app.main import app; assert '/v1/natal/interpretation' in {getattr(r, 'path', '') for r in app.routes}"`
- VC11: `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/remediation-policy.md').exists()"`

`rg` scan details:

- VC8 forbidden pattern: `check_and_consume`.
- VC8 allowed fixture pattern: none in `app/api/v1/routers/public/natal_interpretation.py`.
- VC8 roots: `app/api/v1/routers/public/natal_interpretation.py`.
- VC8 expected false positives: zero.

## Regression Risks

- Moving debit timing can undercharge accepted readings; AC2 and AC3 require exact one-unit debit.
- Corrective reservation can create concurrency drift; AC8 requires one active corrective result.
- Invalid-reading classification can hide valid historical readings; AC5 requires deterministic criteria from narrative, chapters, duplication and sources.
- Router changes can absorb business logic; `RG-002`, `RG-005` and `RG-006` keep ownership routed to services.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep Python commands inside the activated `.venv`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.
- Preserve CS-396 behavior before starting quota/remediation changes.

## References

- `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md`
- `_condamad/stories/regression-guardrails.md#RG-002`
- `_condamad/stories/regression-guardrails.md#RG-005`
- `_condamad/stories/regression-guardrails.md#RG-006`
- `_condamad/stories/regression-guardrails.md#RG-150`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-157`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py`
- `backend/app/services/entitlement/b2c_runtime_gate.py`
- `backend/app/services/quota/usage_service.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
