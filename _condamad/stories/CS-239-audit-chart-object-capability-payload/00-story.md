# Story CS-239 audit-chart-object-capability-payload: Audit Chart Object Capability Payload
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-239-audit-chart-object-capability-payload-audit.md`.
- Problem statement: produire un audit CONDAMAD de la taxonomie `ChartObjectRuntimeData`, de ses capacites et de ses payloads.
- Source-alignment evidence: the story preserves the requested audit folder, six standard files, mandatory matrix, required questions, and no-app-change rule.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-chart-object-capability-payload/`.

The audit must inventory active chart object types, capabilities, payloads, producers, consumers, public projections, and interpretive projections.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-chart-object-capability-payload/`.
- `00-audit-report.md` contains the mandatory matrix and answers every required question from the source brief.
- `01-evidence-log.md` contains reproducible proof for object types, capabilities, payloads, producers, consumers, and projections.
- `02-finding-register.md` records capability/payload incoherences, missing semantics, and open decisions.
- `03-story-candidates.md` qualifies and prioritizes CS-246, CS-247, and CS-248.
- `04-risk-matrix.md` documents runtime and contract risks tied to capability/payload drift.
- `05-executive-summary.md` gives a decision-ready summary for runtime taxonomy follow-up.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-239-audit-chart-object-capability-payload-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-239`.
- Evidence 3: `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` - sibling runtime audit story shape consulted.
- Evidence 5: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - scoped scan found the canonical runtime data contract.
- Evidence 6: `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` - scoped scan found architecture coverage for consumers.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; all matrix columns, required questions, candidate stories, and no-runtime-change constraints are preserved.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Documentation-only audit of `ChartObjectRuntimeData`, `ChartObjectCapabilities`, runtime payloads, producers, consumers, and projections.
  - Inventory of active `object_type` values and their capability semantics.
  - Mapping of required payloads, optional payloads, producer calculators, consumer calculators, public projections, and interpretive projections.
  - Detection of capability/payload incoherences and open product or architecture decisions.
  - Required question coverage:
    - Clear semantics for every capability.
    - Payload without matching capability.
    - Capability true without required payload.
    - Fixed stars as objects or contact sources.
    - Angles participating in aspects.
    - Cusps becoming aspectable.
    - Lots receiving dignities, aspects, houses, or dominance.
    - Nodes treated as planets, points, or a dedicated category.
- Out of scope:
  - Frontend UI, API endpoint creation, public serializer modification, DB migrations, auth, i18n, styling, build tooling, and runtime calculators.
  - Dataclass changes, new capabilities, new payload types, and calculator behavior changes.
  - Runtime validation implementation beyond audit recommendations.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No new endpoint, schema, projection, serializer, frontend screen, seed data, migration, dataclass field, or calculation behavior.
  - No narrowing of the source audit into only a subset of object types, capabilities, payloads, or required questions.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend chart object taxonomy audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change runtime behavior, dataclasses, payload contracts, public payloads, database schema, API routes, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot classify a required capability/payload relationship from repository evidence.
- Additional validation rules:
  - The audit report must include every mandatory matrix column from the brief.
  - The audit report must answer every required question from the brief.
  - The evidence log must map each object type, capability, payload, producer, consumer, and projection claim to concrete proof.
  - The finding register must distinguish incoherence, missing semantic decision, missing runtime validation, and product taxonomy decision.
  - The story candidates file must qualify CS-246, CS-247, and CS-248 with priority and source-finding links.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime taxonomy claims must cite code, tests, docs, and scans proving actual backend behavior. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for chart object capability/payload relationships. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code. |
| Allowlist Exception | no | No allowlist handling is authorized for a documentation-only audit. |
| Contract Shape | yes | The audit has required files, mandatory matrix columns, required questions, and candidate stories. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against dataclass, calculator, endpoint, serializer, and app-code changes while auditing. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-chart-object-capability-payload`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | The mandatory matrix columns are present. | Evidence profile: json_contract_shape; `rg` checks every column in `00-audit-report.md`. |
| AC4 | Active object types are inventoried. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `object_type` and object names in `00-audit-report.md`. |
| AC5 | Capability semantics are documented. | Evidence profile: baseline_before_after_diff; `rg` checks `ChartObjectCapabilities` and `supports_` terms. |
| AC6 | Payload relationships are classified. | Evidence profile: baseline_before_after_diff; `rg` checks required and optional payload terms in `00-audit-report.md`. |
| AC7 | Producers are mapped. | Evidence profile: baseline_before_after_diff; `rg` checks producer and calculator terms in `00-audit-report.md`. |
| AC8 | Consumers are mapped. | Evidence profile: baseline_before_after_diff; `rg` checks consumer and calculator terms in `00-audit-report.md`. |
| AC9 | Projections are distinguished. | Evidence profile: baseline_before_after_diff; `rg` checks public and interpretive projection terms. |
| AC10 | Required questions are answered. | Evidence profile: baseline_before_after_diff; `rg` checks fixed stars, angles, cusps, lots, and nodes. |
| AC11 | Incoherences are registered. | Evidence profile: baseline_before_after_diff; `rg` checks `02-finding-register.md` for incoherence and open decision terms. |
| AC12 | Candidate stories are prioritized. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-246, CS-247, and CS-248. |
| AC13 | Runtime evidence is concrete. | Runtime evidence: `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`. |
| AC14 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-chart-object-capability-payload/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Inventory active `object_type` values from runtime builders, graph nodes, tests, and projections. (AC: AC4, AC13)
- [ ] Task 4: Inventory `ChartObjectCapabilities` and define one semantic consequence per `supports_` field. (AC: AC5)
- [ ] Task 5: Map required and optional payloads to capability gates and validation rules. (AC: AC6, AC11)
- [ ] Task 6: Map producer calculators and consumer calculators for each object type/capability/payload row. (AC: AC7, AC8)
- [ ] Task 7: Distinguish public projection and interpretive projection for every active object family. (AC: AC9)
- [ ] Task 8: Answer all required questions about fixed stars, angles, cusps, lots, and nodes. (AC: AC10)
- [ ] Task 9: Register incoherences, open decisions, validation recommendations, and runtime contract risks. (AC: AC11)
- [ ] Task 10: Prioritize CS-246, CS-247, and CS-248 with source-finding links and sequencing rationale. (AC: AC12)
- [ ] Task 11: Run document validation and verify that no app file changed. (AC: AC1, AC2, AC14)

## Files to Inspect First

- `_story_briefs/cs-239-audit-chart-object-capability-payload-audit.md` - source contract.
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md` - sibling audit story shape.
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md` - sibling runtime audit story shape.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - canonical data, capabilities, payloads, and validators.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - chart object construction and active object families.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - graph outputs and producer sequencing.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` - producer nodes and payload enrichment calls.
- `backend/app/domain/astrology/aspects/**` - aspect consumer behavior and capability selection.
- `backend/app/domain/astrology/dignities/**` - dignity payload and consumer behavior.
- `backend/app/domain/astrology/dominance/**` - dominance payload and consumer behavior.
- `backend/app/domain/astrology/fixed_stars/**` - fixed-star object/contact behavior.
- `backend/app/domain/astrology/interpretation/**` - interpretive projection behavior.
- `backend/tests/unit/domain/astrology/**` - deterministic unit evidence for capability and payload behavior.
- `backend/tests/integration/astrology/**` - public projection and runtime integration evidence.
- `backend/tests/architecture/**` - architecture guards for runtime boundaries.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, domain unit tests, integration tests, architecture tests, runtime dataclasses, graph nodes, builders, and projectors.
- Secondary evidence:
  - Targeted `rg` scans proving presence, absence, producer ownership, consumer ownership, public projection, or interpretive projection by field.
- Static scans alone are not sufficient for runtime taxonomy claims because:
  - Each active object, capability, payload, producer, consumer, and projection claim must cite code, tests, or bounded absence evidence.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `object_type`: active chart object type or family.
  - `capabilities`: `ChartObjectCapabilities` flags applicable to the object type.
  - `payloads_requis`: payloads required when capability semantics demand data.
  - `payloads_optionnels`: payloads allowed without being required for the object type.
  - `calculateurs_consommateurs`: calculators or selectors consuming the object type, capability, or payload.
  - `calculateurs_producteurs`: builders, graph nodes, enrichers, or calculators producing the object type or payload.
  - `projection_publique`: public contract exposure decision.
  - `projection_interpretative`: interpretation/LLM projection decision.
- Required fields:
  - `object_type`
  - `capabilities`
  - `payloads_requis`
  - `payloads_optionnels`
  - `calculateurs_consommateurs`
  - `calculateurs_producteurs`
  - `projection_publique`
  - `projection_interpretative`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown matrix columns keep the exact labels from the source brief.
- Required files:
  - `00-audit-report.md`
  - `01-evidence-log.md`
  - `02-finding-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Required matrix columns:
  - Object type
  - Capabilities
  - Payloads requis
  - Payloads optionnels
  - Calculateurs consommateurs
  - Calculateurs producteurs
  - Projection publique
  - Projection interprétative
- Required candidate stories:
  - `CS-246`
  - `CS-247`
  - `CS-248`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-239-audit-chart-object-capability-payload-audit.md`
  - `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
  - `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-chart-object-capability-payload/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Capability payload audit | `_condamad/audits/astro-chart-object-capability-payload/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-chart-object-capability-payload/` | `backend/tests/**` |
| Story candidates | `_condamad/audits/astro-chart-object-capability-payload/` | `_condamad/stories/**` |
| Runtime taxonomy source | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | New duplicated docs under `backend/app/**` |

## Mandatory Reuse / DRY Constraints

- Reuse existing runtime dataclasses, graph nodes, builders, selectors, projectors, and tests as source evidence.
- Use one canonical object type name per runtime object family across all six audit files.
- Use one canonical capability name per `ChartObjectCapabilities` field across report, evidence log, findings, candidates, risk matrix, and summary.
- Do not duplicate large source excerpts; cite bounded files, symbols, tests, and scan commands.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not add or change `ChartObjectRuntimeData`, `ChartObjectCapabilities`, payload dataclasses, validators, graph nodes, or calculators.
- Do not add API routes, serializers, database migrations, seed data, frontend screens, admin/debug handlers, or runtime validation code.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `backend/migrations/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove capability and payload findings are documented in audit artifacts, not implemented as runtime changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: candidate validation paths must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact chart object capability/payload audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because runtime astrology taxonomy, not billing entitlement, is audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/00-audit-report.md` | Matrix and required answers. |
| Evidence log | `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/01-evidence-log.md` | Reproducible proof by object. |
| Finding register | `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/02-finding-register.md` | Incoherences and decisions. |
| Story candidates | `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/03-story-candidates.md` | Prioritized follow-up stories. |
| Risk matrix | `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/04-risk-matrix.md` | Runtime and contract risks. |
| Executive summary | `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-239-audit-chart-object-capability-payload/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/00-audit-report.md` - matrix and required answers.
- `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/02-finding-register.md` - incoherences and open decisions.
- `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/03-story-candidates.md` - prioritized follow-up stories.
- `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/04-risk-matrix.md` - runtime and contract risk classification.
- `_condamad/audits/astro-chart-object-capability-payload/{audit-timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.
- `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` for existing architecture evidence.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-chart-object-capability-payload | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "ChartObjectRuntimeData|ChartObjectCapabilities|payloads|supports_" backend/app backend/tests`
- VC3: `rg -n "capability|payload|supports_aspects|supports_dignities" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `rg -n "Object type|Capabilities|Payloads requis|Payloads optionnels|Calculateurs consommateurs" "$($auditFolder.FullName)\00-audit-report.md"`
- VC5: `rg -n "étoiles fixes|angles|cuspides|lots|noeuds|nœuds" "$($auditFolder.FullName)\00-audit-report.md"`
- VC6: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC7: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC8: `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- VC9: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-chart-object-capability-payload').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC10: `git diff --name-only`

Before VC6, VC7, VC8, and VC9, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may overstate coherence by treating optional payload presence as proof of a required capability contract.
- The audit may understate runtime coverage by missing producer or consumer paths in graph nodes, enrichers, selectors, or projectors.
- The required questions may become product opinions unless each answer cites repository evidence and an explicit open decision.
- Candidate stories may drift into implementation design before the audit identifies the highest-risk capability/payload gaps.
- A developer may accidentally change app code while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-chart-object-capability-payload/` child folder.
- Treat a capability as meaningful only when its semantic consequence and consumer behavior are documented.
- Treat a payload relationship as required only when code or tests prove the runtime contract requires it.
- Treat public projection and interpretive projection as separate audit dimensions.
- Do not modify backend, frontend, migration, serializer, dataclass, validator, graph, or calculator files.

## References

- `_story_briefs/cs-239-audit-chart-object-capability-payload-audit.md`
- `_condamad/stories/CS-237-audit-astrology-engine-feature-coverage/00-story.md`
- `_condamad/stories/CS-238-audit-runtime-surface-exposure/00-story.md`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `_condamad/stories/regression-guardrails.md`
