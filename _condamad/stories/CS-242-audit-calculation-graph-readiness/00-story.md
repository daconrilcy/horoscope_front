# Story CS-242 audit-calculation-graph-readiness: Audit Calculation Graph Readiness
Status: ready-to-dev

## Trigger / Source

- Source type: audit-to-story with repository-informed boundary.
- Source reference: `_story_briefs/cs-242-audit-calculation-graph-readiness-audit.md`.
- Related context: CS-225 to CS-228 introduced the calculation graph contracts, `natal_chart_v1`, runner execution, cache, and provenance.
- Problem statement: produce a CONDAMAD audit proving whether the current graph runner can support future astrology graph families.
- Source-alignment evidence: PASS; the story preserves the requested audit folder, six standard files, mandatory questions, and CS-243 to CS-245.

## Objective

Create one timestamped CONDAMAD audit folder under `_condamad/audits/astro-calculation-graph-readiness/`.

The audit must document runner readiness, `natal_chart_v1` readiness, node purity, output typing, dependencies, tracing, replay, versioning,
graph comparison, local cache, application cache, and reference-version invalidation.

## Target State

- A latest audit folder exists under `_condamad/audits/astro-calculation-graph-readiness/`.
- `00-audit-report.md` contains the runner, graph, cache, provenance, error, replay, trace, comparison, and multi-graph readiness analysis.
- `01-evidence-log.md` contains reproducible proof for runner behavior, `natal_chart_v1`, dependencies, tests, cache, and provenance.
- `02-finding-register.md` records every readiness limit with severity, evidence, impacted graph families, and closure route.
- `03-story-candidates.md` qualifies CS-243, CS-244, and CS-245 with priority, source finding, validation plan, and stop condition.
- `04-risk-matrix.md` maps orchestration, provenance, replay, cache, dependency, typing, and graph-family risks.
- `05-executive-summary.md` gives a decision-ready summary for future graph-family work.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-242-audit-calculation-graph-readiness-audit.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-242`.
- Evidence 3: `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md` - sibling audit story shape consulted.
- Evidence 4: `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md` - graph contract predecessor consulted.
- Evidence 5: `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md` - `natal_chart_v1` predecessor consulted.
- Evidence 6: `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md` - runner predecessor consulted.
- Evidence 7: `backend/app/domain/astrology/runtime/calculation_graph_runner.py` - scoped scan found `CalculationGraphRunner`.
- Evidence 8: `backend/app/domain/astrology/runtime/calculation_graph_contracts.py` - scoped scan found `CalculationGraphDefinition`.
- Evidence 9: `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - scoped scan found `natal_chart_v1`.
- Evidence 10: `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py` - scoped scan found runner tests.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - registry consulted through the guardrail resolver for this audit scope.
- Source-alignment review result: PASS; all mandatory questions, graph families, cache distinctions, and no-code-change limits are preserved.

## Domain Boundary

- Domain: backend-astrology-audit
- In scope:
  - Documentation-only audit of calculation graph readiness for backend astrology runtime.
  - Analysis of `CalculationGraphRunner`, `CalculationGraphDefinition`, `natal_chart_v1`, node registry, graph validation, and tests.
  - Analysis of node purity, typed outputs, declared dependencies, node errors, local runner cache, provenance, and execution order.
  - Distinction between local cache, application cache, provenance, debug trace, replay, graph versioning, graph comparison, and reference invalidation.
  - Readiness assessment for `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`, `progressed_chart_v1`, and `composite_chart_v1`.
  - Qualification of candidate stories CS-243, CS-244, and CS-245.
- Out of scope:
  - Frontend UI, API endpoint creation, DB migrations, auth, i18n, styling, build tooling, and production configuration changes.
  - Modifying the graph runner, adding new graph families, adding an application cache, or changing calculation behavior.
- Explicit non-goals:
  - No code change outside the audit artifacts.
  - No new graph definition, runner feature, schema, public payload, database table, seed data, migration, or frontend screen.
  - No partial replacement of implementation work for CS-243, CS-244, or CS-245.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend calculation graph readiness audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Produce documentation artifacts only under the scoped audit folder.
  - Do not change runner behavior, graph definitions, node functions, public payloads, database schema, API routes, tests, or frontend behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: repository evidence cannot determine runner multi-graph readiness or current provenance semantics.
- Additional validation rules:
  - The audit report must answer every mandatory question from the source brief.
  - The audit report must assess each target graph family separately.
  - The evidence log must cite code, tests, docs, configuration, generated evidence, or bounded absence scans.
  - Cache local, cache applicatif, provenance, trace, replay, comparison, and reference invalidation must be separate rows.
  - The story candidates file must qualify CS-243, CS-244, and CS-245 with source-finding links and stop conditions.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Readiness claims must cite runner code, graph contracts, tests, docs, and scans proving actual backend behavior. |
| Baseline Snapshot | yes | The audit must persist a reproducible baseline for runner, graph, cache, provenance, and readiness evidence. |
| Ownership Routing | yes | Audit artifacts have canonical CONDAMAD locations and must not be mixed into app code or test suites. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only audit. |
| Contract Shape | yes | The audit has required files, mandatory questions, graph-family rows, and candidate stories. |
| Batch Migration | no | No migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | The story must guard against implementing runner or graph changes while auditing readiness. |
| Persistent Evidence | yes | The audit folder itself is the review handoff evidence. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The timestamped audit folder exists. | Evidence profile: baseline_before_after_diff; `python` checks `_condamad/audits/astro-calculation-graph-readiness`. |
| AC2 | All six standard audit files exist. | Evidence profile: baseline_before_after_diff; `python` checks required filenames in the latest audit folder. |
| AC3 | Runner multi-graph readiness is answered. | Evidence profile: baseline_before_after_diff; `rg` checks `CalculationGraphRunner` and multi-graph terms. |
| AC4 | `natal_chart_v1` readiness is assessed. | Evidence profile: baseline_before_after_diff; `rg` checks `natal_chart_v1` and readiness terms. |
| AC5 | Node purity is documented. | Evidence profile: ast_architecture_guard; `rg` checks node purity evidence in `00-audit-report.md`. |
| AC6 | Output typing is documented. | Evidence profile: ast_architecture_guard; `rg` checks typed output evidence in `00-audit-report.md`. |
| AC7 | Dependencies are declared. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`. |
| AC8 | Execution trace readiness is classified. | Evidence profile: baseline_before_after_diff; `rg` checks trace and debug terms in audit artifacts. |
| AC9 | Replay readiness is classified. | Evidence profile: baseline_before_after_diff; `rg` checks replay and reproducible input terms in audit artifacts. |
| AC10 | Versioning readiness is classified. | Evidence profile: baseline_before_after_diff; `rg` checks graph version and reference version terms. |
| AC11 | Graph comparison readiness is classified. | Evidence profile: baseline_before_after_diff; `rg` checks comparison terms in `00-audit-report.md`. |
| AC12 | Cache boundaries are separated. | Evidence profile: baseline_before_after_diff; `rg` checks local cache, application cache, and invalidation terms. |
| AC13 | Target graph families are assessed. | Evidence profile: json_contract_shape; `rg` checks all five target graph family codes. |
| AC14 | Candidate stories are qualified. | Evidence profile: baseline_before_after_diff; `rg` checks `03-story-candidates.md` for CS-243, CS-244, and CS-245. |
| AC15 | Audit validation commands pass. | Evidence profile: baseline_before_after_diff; `python` runs the CONDAMAD audit validator. |
| AC16 | No application files are changed. | Evidence profile: no_legacy_contract; `python` or `git diff --name-only` verifies only audit artifacts changed. |

## Implementation Tasks

- [ ] Task 1: Create the latest audit folder under `_condamad/audits/astro-calculation-graph-readiness/`. (AC: AC1)
- [ ] Task 2: Create the six standard audit files with coherent cross-references. (AC: AC2)
- [ ] Task 3: Inventory `CalculationGraphRunner`, graph contracts, node registry, and `natal_chart_v1`. (AC: AC3, AC4)
- [ ] Task 4: Audit node purity from runner call boundaries, node files, tests, and bounded scans. (AC: AC5)
- [ ] Task 5: Audit typed outputs from graph contracts, node definitions, assembler usage, and validator tests. (AC: AC6, AC7)
- [ ] Task 6: Audit dependency declaration, dependency ordering, failure behavior, and tested validation rules. (AC: AC7)
- [ ] Task 7: Distinguish provenance, debug trace, replay, graph versioning, and graph comparison readiness. (AC: AC8, AC9, AC10, AC11)
- [ ] Task 8: Distinguish runner local cache, application cache need, and reference-version invalidation. (AC: AC12)
- [ ] Task 9: Assess each target graph family with prerequisites and blockers. (AC: AC13)
- [ ] Task 10: Register readiness findings with severity, evidence, impacted families, closure route, and source question. (AC: AC3, AC14)
- [ ] Task 11: Qualify CS-243, CS-244, and CS-245 with priority, source finding, validation evidence, and stop condition. (AC: AC14)
- [ ] Task 12: Run document validation and verify that no app, test, migration, config, or frontend file changed. (AC: AC1, AC2, AC15, AC16)

## Files to Inspect First

- `_story_briefs/cs-242-audit-calculation-graph-readiness-audit.md` - source contract.
- `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md` - calculation graph contract predecessor.
- `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md` - `natal_chart_v1` predecessor.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md` - runner cache and provenance predecessor.
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md` - migration predecessor.
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md` - sibling audit story shape.
- `docs/architecture/astrology-calculation-graph.md` - architecture documentation for graph concepts.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py` - graph, node, input, output, and execution contracts.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py` - runner execution, cache, dependency, provenance, and error behavior.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py` - declaration validation behavior.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - current `natal_chart_v1` graph definition.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` - node helper functions and input/output boundaries.
- `backend/app/domain/astrology/runtime/natal_calculation_registry.py` - node registry ownership.
- `backend/app/domain/astrology/runtime/natal_result_assembler.py` - graph output assembly into natal result.
- `backend/app/domain/astrology/natal_calculation.py` - runtime integration path.
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py` - runner tests.
- `backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py` - contract tests.
- `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py` - validator tests.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py` - graph definition tests.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py` - runtime graph execution tests.
- `backend/tests/integration/astrology/test_natal_calculation_graph_integration.py` - integration evidence.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`, generated audit manifest, Python source files, unit tests, integration tests, and architecture docs.
- Secondary evidence:
  - Targeted `rg` scans proving graph codes, dependencies, provenance, cache terms, trace gaps, replay gaps, and target graph-family absence.
- Static scans alone are not sufficient for graph readiness claims because:
  - Each readiness claim must cite runner code, graph definition code, deterministic tests, generated audit evidence, or documented absence scans.

## Contract Shape

- Contract type:
  - CONDAMAD domain audit folder.
- Fields:
  - `question`: mandatory source question or graph-family readiness dimension.
  - `surface_actuelle`: current code, test, documentation, generated evidence, or missing surface.
  - `preuve_reproductible`: evidence command, file, test, generated artifact, or bounded absence scan.
  - `niveau_readiness`: ready, partial, blocked, or not_started.
  - `risque_orchestration`: runner or graph-family orchestration risk.
  - `risque_provenance`: provenance, replay, trace, versioning, or comparison risk.
  - `familles_impactees`: target graph family codes impacted by the finding.
  - `story_candidate`: CS-243, CS-244, CS-245, or `none`.
- Required fields:
  - `question`
  - `surface_actuelle`
  - `preuve_reproductible`
  - `niveau_readiness`
  - `risque_orchestration`
  - `risque_provenance`
  - `familles_impactees`
  - `story_candidate`
- Optional fields:
  - none
- Status codes:
  - none; this is not an API route.
- Serialization names:
  - Markdown matrix columns keep the exact French labels from this story contract.
- Required files:
  - `00-audit-report.md`
  - `01-evidence-log.md`
  - `02-finding-register.md`
  - `03-story-candidates.md`
  - `04-risk-matrix.md`
  - `05-executive-summary.md`
- Mandatory source questions:
  - Runner supports multiple graphs.
  - Nodes are pure.
  - Outputs are typed.
  - Dependencies are declared and tested.
  - Graph execution can be traced.
  - Graph execution can be replayed.
  - Graph can be versioned.
  - Two graphs can be compared.
  - Local runner cache is sufficient or limited.
  - Application cache is required or not required.
  - Reference-version invalidation is defined or missing.
- Required graph-family rows:
  - `transit_chart_v1`
  - `synastry_chart_v1`
  - `solar_return_v1`
  - `progressed_chart_v1`
  - `composite_chart_v1`
- Required candidate stories:
  - `CS-243`
  - `CS-244`
  - `CS-245`
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-242-audit-calculation-graph-readiness-audit.md`
  - `docs/architecture/astrology-calculation-graph.md`
  - `backend/app/domain/astrology/runtime`
  - `backend/app/domain/astrology/natal_calculation.py`
  - `backend/tests/unit/domain/astrology`
  - `backend/tests/integration/astrology`
- Comparison after implementation:
  - Latest child folder under `_condamad/audits/astro-calculation-graph-readiness/`.
- Expected invariant:
  - The only intended repository delta is the new audit folder and its standard CONDAMAD audit files.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Calculation graph readiness audit | `_condamad/audits/astro-calculation-graph-readiness/` | `backend/app/**` |
| Evidence log | `_condamad/audits/astro-calculation-graph-readiness/` | `backend/tests/**` |
| Story candidates | `_condamad/audits/astro-calculation-graph-readiness/` | `_condamad/stories/**` |
| Multi-graph prerequisites | `_condamad/audits/astro-calculation-graph-readiness/` | New graph files under `backend/**` |
| Cache and invalidation findings | `_condamad/audits/astro-calculation-graph-readiness/` | Runtime cache implementation files |

## Mandatory Reuse / DRY Constraints

- Reuse existing graph contracts, runner code, graph definition, node registry, tests, docs, and prior CS-225 to CS-228 story evidence.
- Use one canonical readiness vocabulary across report, evidence log, findings, candidates, risk matrix, and summary.
- Use one canonical target graph-family list across all six audit files.
- Do not duplicate large source excerpts; cite bounded files, symbols, test paths, generated artifacts, and scan commands.
- Do not add external packages or custom audit tooling.

## No Legacy / Forbidden Paths

- No legacy route path may be added during this audit.
- No compatibility route path may be added during this audit.
- No fallback route path may be added during this audit.
- Do not create app-code aliases, shims, runtime fallback branches, or compatibility wrappers.
- Do not modify the runner, graph contracts, node registry, graph definitions, validators, assemblers, or natal calculation integration.
- Do not add trace, replay, manifest, schema validation, application cache, graph family code, or reference invalidation implementation.
- Do not add API routes, serializers, frontend screens, admin/debug handlers, seed data, migrations, or runtime validation code.

## Reintroduction Guard

- Forbidden app-code delta:
  - `backend/app/**`
  - `backend/tests/**`
  - `backend/app/tests/**`
  - `backend/migrations/**`
  - `frontend/src/**`
  - `docs/db_seeder/**`
- Required guard:
  - `git diff --name-only` must show only the audit folder for implementation changes.
  - `rg` must prove readiness findings are documented in audit artifacts, not implemented as runner, graph, cache, or test changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Local anti-drift: no API router change belongs to this audit. | `git diff --name-only`; bounded `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable pattern: candidate validation paths must be concrete. | `rg` over `03-story-candidates.md`. |
| Registry gap | No exact calculation graph readiness audit guardrail was present in the resolver output. | Resolver output reviewed. |

Non-applicable examples retained to prevent scope drift:

- RG-047 frontend inline styles are out of scope because no frontend files are touched.
- RG-052 frontend CSS namespace convergence is out of scope because no styling files are touched.
- RG-041 entitlement documentation is out of scope because calculation graph readiness, not billing entitlement, is audited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit report | `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/00-audit-report.md` | Runner and graph readiness analysis. |
| Evidence log | `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/01-evidence-log.md` | Reproducible proof by question. |
| Finding register | `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/02-finding-register.md` | Readiness limits and closure routes. |
| Story candidates | `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/03-story-candidates.md` | Prioritized CS-243 through CS-245. |
| Risk matrix | `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/04-risk-matrix.md` | Orchestration and provenance risks. |
| Executive summary | `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/05-executive-summary.md` | Decision summary. |
| Review output | `_condamad/stories/CS-242-audit-calculation-graph-readiness/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only audit.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/00-audit-report.md` - readiness analysis.
- `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/01-evidence-log.md` - reproducible evidence.
- `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/02-finding-register.md` - readiness limits.
- `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/03-story-candidates.md` - prioritized CS-243 through CS-245.
- `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/04-risk-matrix.md` - orchestration and provenance risk classification.
- `_condamad/audits/astro-calculation-graph-readiness/{audit-timestamp}/05-executive-summary.md` - decision summary.

Likely tests:

- Document validation through `condamad_domain_audit_validate.py`.
- Document lint through `condamad_domain_audit_lint.py`.
- Targeted `rg` checks against latest audit artifacts.
- `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py` for existing runner behavior evidence.
- `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py` for existing dependency validation evidence.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py` for current graph definition evidence.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py` for runtime execution evidence.

Files not expected to change:

- `backend/app/**` - out of scope; no backend runtime is touched.
- `backend/tests/**` - out of scope; no test code is touched.
- `backend/app/tests/**` - out of scope; no app-local tests are touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `docs/db_seeder/**` - out of scope; no seed or reference data is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `$auditFolder = Get-ChildItem -Directory .\_condamad\audits\astro-calculation-graph-readiness | Sort-Object Name -Descending | Select-Object -First 1`
- VC2: `rg -n "CalculationGraphRunner|natal_chart_v1|CalculationGraphDefinition|provenance|cache|trace|node" backend/app backend/tests docs`
- VC3: `rg -n "transit_chart_v1|synastry_chart_v1|solar_return_v1|progressed_chart_v1|composite_chart_v1" "$($auditFolder.FullName)\00-audit-report.md"`
- VC4: `rg -n "CS-243|CS-244|CS-245|priority|priorité|stop condition" "$($auditFolder.FullName)\03-story-candidates.md"`
- VC5: `rg -n "cache local|cache applicatif|provenance|trace|replay|version|compare|invalidation" "$($auditFolder.FullName)\00-audit-report.md"`
- VC6: `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- VC7: `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`
- VC8: `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`
- VC9: `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`
- VC10: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py $auditFolder.FullName`
- VC11: `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py $auditFolder.FullName`
- VC12: `python -c "from pathlib import Path; p=max(Path('_condamad/audits/astro-calculation-graph-readiness').iterdir()); assert (p/'00-audit-report.md').exists()"`
- VC13: `git diff --name-only`

Before VC6, VC7, VC8, VC9, VC10, VC11, and VC12, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The audit may treat a single-graph runner path as multi-graph readiness without proving registry and graph-code boundaries.
- Node purity may be overstated by ignoring hidden I/O, mutation, global state, or cache coupling inside helper calls.
- Typed output readiness may be overstated by citing dataclasses while graph IO remains unchecked at runtime.
- Local runner cache may be confused with a durable application cache or invalidation strategy.
- Provenance may be confused with replay, debug trace, versioned manifest, or graph comparison.
- Candidate stories may be too vague to close trace, manifest, schema validation, and multi-family readiness findings.
- A developer may accidentally change app code, tests, config, or frontend files while producing audit artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all audit artifacts under the latest `_condamad/audits/astro-calculation-graph-readiness/` child folder.
- Treat multi-graph readiness as proven only by graph-code selection, registry behavior, runner behavior, and deterministic tests.
- Treat node purity as incomplete without code-level evidence for mutation, I/O, settings, DB, API, and global-state boundaries.
- Treat local cache as runner-local only unless the repository proves application-level cache ownership and invalidation semantics.
- Treat provenance, trace, replay, versioning, and comparison as separate readiness dimensions.
- Do not modify backend, frontend, migration, seed, serializer, dataclass, validator, graph, node, cache, or calculator files.

## References

- `_story_briefs/cs-242-audit-calculation-graph-readiness-audit.md`
- `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md`
- `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md`
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md`
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md`
- `_condamad/stories/CS-241-audit-astronomical-accuracy/00-story.md`
- `docs/architecture/astrology-calculation-graph.md`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`
- `_condamad/stories/regression-guardrails.md`
