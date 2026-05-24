# Story CS-252 astrology-doctrine-school-governance-model: Define Astrology Doctrine And School Governance Model
Status: done

## 1. Objective

Define one canonical backend-domain governance model for astrology doctrines, schools, and rule-source ownership so thresholds,
weights, profiles, and doctrine decisions cannot be added silently.

## 2. Trigger / Source

- Source type: architecture-runtime-governance.
- Source reference: `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`.
- Architecture source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md#SC-ARCH-007`.
- Remapped architecture item: `SC-ARCH-007`.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment review: PASS; the story preserves CS-240 rule families, CS-241 F-003 ownership stakes, doctrine versus
  architecture separation, guarded `needs-user-decision` values, and future temporal-technique citation.

## 3. Domain Boundary

This story belongs to one domain:

- Domain: backend-domain
- In scope:
  - canonical governance registry under `backend/app/domain/astrology/runtime`;
  - classification of CS-240 rule families as `DB-owned`, `Python-owned`, `mixed`, `documentation-only`, `test-only`,
    or `needs-user-decision`;
  - explicit handling for CS-241 F-003 weighting families: dominance, sign, house, and dignity weights;
  - doctrine model fields distinguishing canonical product doctrine from multiple versioned schools;
  - allowed status transitions for rule families and doctrine-school decisions;
  - architecture guard preventing new unclassified thresholds, weights, profiles, or school markers;
  - targeted unit and architecture tests proving classification, unresolved decisions, and guard behavior.
- Out of scope:
  - changing existing astrology weights or thresholds;
  - adding a complete astrology school;
  - migrating DB reference data or runtime constants;
  - changing narration, public API, frontend, DB schema, migrations, auth, i18n, styles, or build tooling.
- Explicit non-goals:
  - no frontend route, screen, client generation, or UI validation;
  - no Alembic migration or persistence model;
  - no public JSON contract change;
  - no new calculation technique implementation;
  - no registry enrichment in `_condamad/stories/regression-guardrails.md` during this story generation.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend doctrine governance contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical typed governance model for astrology doctrine and rule-source ownership.
  - Preserve current rule values while classifying their source owner and unresolved doctrine status.
  - Add tests and guards for complete classification, transition rules, and unmanaged rule growth.
  - Keep public API, frontend, DB, migrations, runtime calculations, and narration unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the product cannot choose between one canonical doctrine and multiple versioned schools.
- Additional validation rules:
  - every CS-240 rule family is represented exactly once.
  - every represented family has one source owner status from the allowed status set.
  - CS-241 F-003 weighting families have either a canonical owner or `needs-user-decision`.
  - doctrine decisions are separate from architecture ownership fields.
  - `needs-user-decision` values are preserved by resolver and transition tests.
  - new thresholds, weights, profiles, or school markers fail an `AST guard` until classified.
  - `app.routes`, `app.openapi()`, `pytest`, and `TestClient` prove no public API delta.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The governance model becomes the internal source for rule owner and doctrine-school classification. |
| Baseline Snapshot | yes | Before and after artifacts prove current CS-240 family coverage and allowed surface delta. |
| Ownership Routing | yes | Governance ownership must stay under astrology runtime, not API, DB, frontend, docs-only, or seed paths. |
| Allowlist Exception | no | No allowlist handling is authorized for this canonical backend-domain model. |
| Contract Shape | yes | The owner statuses, doctrine fields, transition rules, and guarded family list are the core contract. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | New unclassified thresholds, weights, profiles, and schools must stay blocked. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`;
  - `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`;
  - `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`;
  - `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`.
- Runtime/domain artifacts:
  - typed governance entry contract;
  - rule family owner status values;
  - doctrine mode and school version policy fields;
  - allowed transition map;
  - resolver behavior for known and unknown rule families.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`;
  - `pytest -q backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, generated manifest, `app.routes`, `app.openapi()`, and `TestClient`.
- Static scans alone are not sufficient because:
  - classification completeness, transition enforcement, unresolved-decision preservation, and API neutrality require executable proof.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/audits/astro-reference-governance/2026-05-23-1939/00-audit-report.md`;
  - `_condamad/audits/astro-reference-governance/2026-05-23-1939/02-finding-register.md`;
  - `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`;
  - `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/00-story.md`;
  - `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`.
- Comparison after implementation:
  - `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-before.md`;
  - `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-after.json`;
  - targeted unit, architecture, and API-neutrality test output.
- Expected invariant:
  - the only allowed surface delta is an internal backend runtime governance model plus targeted tests and evidence files.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Doctrine governance model | `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py` | API routers, DB models, frontend |
| Governance unit tests | `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py` | docs-only checks |
| Unclassified rule guard | `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py` | broad manual review only |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend smoke tests |
| Evidence snapshots | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/` | app or seed folders |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this canonical backend-domain model.

## 4f. Contract Shape

- Contract type:
  - internal typed governance model for astrology doctrine, school policy, and rule-source ownership;
  - no HTTP endpoint, public serializer, DB table, seed data, or frontend type.
- Fields:
  - `rule_family`;
  - `source_owner_status`;
  - `canonical_owner`;
  - `doctrine_decision_status`;
  - `school_policy`;
  - `version_policy`;
  - `allowed_transitions`;
  - `evidence_refs`;
  - `blocker`;
  - `future_technique_notes`.
- Required fields:
  - `rule_family`;
  - `source_owner_status`;
  - `canonical_owner`;
  - `doctrine_decision_status`;
  - `school_policy`;
  - `version_policy`;
  - `allowed_transitions`;
  - `evidence_refs`;
  - `blocker`;
  - `future_technique_notes`.
- Required source owner statuses:
  - `DB-owned`;
  - `Python-owned`;
  - `mixed`;
  - `documentation-only`;
  - `test-only`;
  - `needs-user-decision`.
- Required doctrine statuses:
  - `single-canonical-doctrine`;
  - `versioned-school-supported`;
  - `needs-user-decision`.
- Required rule families:
  - `aspect_orbs`;
  - `dominance_weights`;
  - `combustion_thresholds`;
  - `cazimi_thresholds`;
  - `under_beams_thresholds`;
  - `speed_thresholds`;
  - `station_thresholds`;
  - `house_weights`;
  - `dignity_weights`;
  - `sign_profiles`;
  - `fixed_star_rules`;
  - `aspect_rules`;
  - `interpretation_rules`.
- CS-241 F-003 required weighting families:
  - `dominance_weights`;
  - `sign_profiles`;
  - `house_weights`;
  - `dignity_weights`.
- Optional fields:
  - none.
- Status codes:
  - no HTTP endpoint, method, or status code is changed.
- Serialization names:
  - no public JSON key is renamed or added.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - `app.openapi()` must not expose the internal doctrine governance model.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## 4h. Reintroduction Guard

- Guard target:
  - no CS-240 rule family is missing from the governance model;
  - no duplicate rule family is accepted;
  - no unknown rule family is accepted by resolver behavior;
  - no `needs-user-decision` value is converted into an implicit active decision;
  - no new threshold, weight, profile, or school marker appears without governance classification;
  - no public API, OpenAPI, DB migration, seed data, or frontend delta is introduced.
- Guard mechanism:
  - unit tests for required family completeness and field completeness;
  - unit tests for allowed transitions and unresolved-decision preservation;
  - architecture `AST guard` for unmanaged thresholds, weights, profiles, and school markers;
  - targeted `rg` scans for ownership drift and public exposure;
  - `TestClient`, `app.routes`, and `app.openapi()` API neutrality evidence.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`;
  - `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`;
  - `pytest -q backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()`, generated manifest, and `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/validation.md` | Keep lint, tests and scans. |
| Governance before | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-before.md` | Record CS-240 baseline. |
| Governance after | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-after.json` | Capture final model. |
| Guard manifest | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/unclassified-rule-guard.md` | Keep AST guard scope. |
| API neutrality | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/openapi-routes.md` | Keep routes and OpenAPI proof. |
| Review output | `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/11-code-review.md` | Keep automatic review separately. |

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to update `CS-252`.
- Evidence 3: `_condamad/audits/astro-reference-governance/2026-05-23-1939/00-audit-report.md` - CS-240 rule families read.
- Evidence 4: `_condamad/audits/astro-reference-governance/2026-05-23-1939/02-finding-register.md` - CS-240 findings read.
- Evidence 5: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md` - graph family dependency read.
- Evidence 6: `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/00-story.md` - taxonomy dependency read.
- Evidence 7: `resolve_guardrails.py` - scoped resolver run for backend-domain governance surfaces.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - consulted only through scoped resolver output.
- Source-alignment evidence: ACs cover rule family classification, CS-241 F-003 weighting ownership, doctrine-school
  decisions, transition rules, unmanaged rule guards, future temporal-technique citation, and API neutrality.

## 6. Target State

- One canonical typed governance model classifies all CS-240 rule families.
- Every rule family exposes source owner status, canonical owner, doctrine decision status, school policy, version policy,
  allowed transitions, evidence references, blocker, and future technique notes.
- Dominance, sign, house, and dignity weighting families have either explicit owners or `needs-user-decision`.
- Doctrine choices are separated from architecture ownership choices.
- The product decision between one canonical doctrine and multiple versioned schools is explicit.
- Unknown and duplicate rule families fail deterministic validation.
- New unclassified thresholds, weights, profiles, or school markers fail a local architecture guard.
- Public API, frontend, DB, migrations, runtime calculations, narration, auth, i18n, style, and build surfaces stay unchanged.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- doctrine governance: yes;
- rule-source ownership: yes;
- architecture guard: yes;
- public API: no behavior delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend ownership stays in canonical app paths; governance does not move into API routing. |
| RG-022 | local | Backend tests and validation evidence remain mandatory for story closure. |
| Registry gap | local | No exact doctrine-governance invariant was returned by the scoped resolver. |

Non-applicable examples:

- RG-047 frontend inline styles: out of scope, no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration: out of scope, no style or build output is touched.
- RG-041 entitlement documentation: out of scope, no entitlement or frontend build surface is touched.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | All CS-240 rule families are registered. | Evidence profile: json_contract_shape; `pytest` runs governance tests. |
| AC2 | Each rule family exposes owner status. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`. |
| AC3 | CS-241 F-003 weighting owners are explicit. | Evidence profile: json_contract_shape; `pytest` runs governance tests. |
| AC4 | Doctrine decisions stay separate. | Evidence profile: json_contract_shape; `pytest` runs governance tests. |
| AC5 | Allowed transitions are enforced. | Evidence profile: json_contract_shape; `pytest` runs governance tests. |
| AC6 | `needs-user-decision` values are preserved. | Evidence profile: json_contract_shape; `pytest` runs governance tests. |
| AC7 | New unclassified rule markers fail. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`. |
| AC8 | Future temporal techniques can cite the model. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans governance model and tests. |
| AC9 | Public API runtime contract is unchanged. | Evidence profile: runtime_openapi_contract; `pytest`; `TestClient`; `app.routes`; `app.openapi()`. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-252 evidence paths. |

## 8. Implementation Tasks

- [x] Task 1: Create the typed doctrine governance module with French file comment and docstrings. (AC: AC1, AC2)
- [x] Task 2: Declare all CS-240 rule families and the allowed owner statuses. (AC: AC1, AC2)
- [x] Task 3: Classify dominance, sign, house, and dignity weighting families from CS-241 F-003. (AC: AC3)
- [x] Task 4: Add doctrine mode, school policy, version policy, and blocker fields. (AC: AC4)
- [x] Task 5: Add transition validation for owner and doctrine status movement. (AC: AC5)
- [x] Task 6: Preserve unresolved doctrine or product choices as `needs-user-decision`. (AC: AC6)
- [x] Task 7: Add the architecture guard against unmanaged thresholds, weights, profiles, and school markers. (AC: AC7)
- [x] Task 8: Add future-technique citation fields for temporal, traditional, modern, and forecasting stories. (AC: AC8)
- [x] Task 9: Add or reuse API neutrality proof with `app.routes`, `app.openapi()`, and `TestClient`. (AC: AC9)
- [x] Task 10: Persist before, after, guard, API neutrality, and validation evidence under the CS-252 story folder. (AC: AC10)

## 9. Mandatory Reuse / DRY Constraints

- Reuse CS-240 rule family names instead of inventing a second naming set.
- Reuse CS-246 graph family concepts and CS-249 capability taxonomy context for future-technique references.
- Keep one canonical doctrine governance module.
- Do not duplicate owner statuses in API schemas, frontend code, DB seed files, or documentation-only tables.
- Do not add external packages for governance validation, serialization, or scans.
- Keep names explicit and typed; avoid unstructured dictionaries for core governance data.

## 10. No Legacy / Forbidden Paths

- No legacy governance registry may be added outside the canonical runtime module.
- No compatibility route path may expose doctrine governance data.
- No fallback resolver may silently map unknown rule families.
- No shim may convert `needs-user-decision` into an active doctrine decision.
- No frontend file may be modified.
- No DB model, seed, or migration may be modified.
- No public API route, serializer, or OpenAPI schema may expose the internal model.
- No astrology threshold, weight, profile, calculator, or narration rule may be changed.

## 11. Files to Inspect First

- `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`.
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/00-audit-report.md`.
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/02-finding-register.md`.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/00-story.md`.
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.
- `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## 12. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/validation.md`.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-before.md`.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-after.json`.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/unclassified-rule-guard.md`.
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/openapi-routes.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`.
- `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `docs/db_seeder/**` - out of scope; no reference seed value is touched.

## 13. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 14. Validation Plan

Run all Python commands from the repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted backend-domain validation from the repository root after activating the venv:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py
pytest -q backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run API neutrality proof from the repository root after activating the venv:

```powershell
$env:PYTHONPATH='backend'; python -c "from app.main import app; assert 'DoctrineGovernance' not in str(app.openapi())"
$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any('doctrine-governance' in getattr(r, 'path', '') for r in app.routes)"
```

Run ownership and no-drift scans from the repository root:

```powershell
rg -n "needs-user-decision|DB-owned|Python-owned|mixed|documentation-only|test-only" backend/app/domain/astrology/runtime backend/tests
rg -n "threshold|weight|profile|school|doctrine" backend/app/domain/astrology backend/tests/architecture
rg -n "doctrine-governance|DoctrineGovernance" backend/app/api frontend backend/alembic docs/db_seeder -g "*.py" -g "*.ts" -g "*.tsx" -g "*.json"
```

Persist evidence checks from the repository root after activating the venv:

```powershell
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/validation.md').exists()"
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-252-astrology-doctrine-school-governance-model/evidence/governance-after.json').exists()"
```

## 15. Regression Risks

- A governance model can become a hidden business decision if unresolved doctrine choices are marked active.
- A school-policy field can imply multi-school product support before the user decision exists.
- A second governance table can drift from CS-240 rule family names.
- The guard can overmatch unrelated words unless it checks typed ownership context.
- Public projection can change silently if internal doctrine fields leak into serializers.

## 16. Dev Agent Instructions

- Start by reading the files listed in `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Keep the implementation typed, small, and local to astrology runtime.
- Keep French global comments and public or non-trivial docstrings in new or significantly modified application files.
- Do not create `requirements.txt`.
- Do not modify frontend, DB migrations, API routes, auth, i18n, style, build tooling, or seed values.
- Do not change astrology thresholds, weights, profiles, calculators, or narration behavior.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Persist commands, results, scans, `app.routes`, `app.openapi()`, guard manifest, and model snapshots under the CS-252 folder.

## 17. References

- `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`.
- `_condamad/stories/story-status.md`.
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/00-audit-report.md`.
- `_condamad/audits/astro-reference-governance/2026-05-23-1939/02-finding-register.md`.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/00-story.md`.
- Scoped guardrail resolver output for backend-domain doctrine governance scope.
