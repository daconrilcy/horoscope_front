# Story CS-360 audit-admin-manual-execution-provider-capable: Audit Admin Manual Execution Provider Capability
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-360-audit-admin-manual-execution-provider-capable.md`.
- Source problem: admin manual execution is admin-only and provider-capable, but its policy is not decided.
- Source stakes:
  - User impact: future agents need a sourced decision before documenting, restricting, migrating, or decommissioning this admin surface.
  - Technical risk: `chart_json` can remain in admin sample payloads without a clear policy for live provider execution.
  - Closure expectation: create a timestamped audit report under `_condamad/audits/admin-manual-llm-execution/`.
  - Forbidden regression: no backend runtime, permission, frontend, database, migration, or provider behavior change.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a sourced audit report for the admin manual execution surface.

The audit must decide whether this admin-only provider-capable surface should be documented as supported, restricted, migrated away from
legacy carriers, or decommissioned.

## Target State

A timestamped report exists at:
`_condamad/audits/admin-manual-llm-execution/YYYY-MM-DD-HHMM/01-admin-manual-execution-provider-capable-audit.md`.

The report contains:

- Resume executif.
- Trace route -> sample payload -> gateway.
- Matrice permissions, logs et audit.
- Matrice sample payloads et carriers legacy.
- Decision recommandee: documenter, restreindre, migrer ou decommissionner.
- Stories candidates d'implementation.

The report proves whether the surface is strictly admin-only or indirectly exposable.
The report separates sample payload CRUD from live provider execution.
The report documents the role of `chart_json` in admin sample payloads.
The report keeps no implicit debt: each unresolved policy item becomes a blocker or a candidate implementation story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-360-audit-admin-manual-execution-provider-capable.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-360`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: all mandatory source files named by the brief exist in this workspace.
- Evidence 5: targeted `rg` found `execute_admin_catalog_sample_payload`, `AdminCatalogManualExecute`, `chart_json`, and `LLMGateway`.
- Evidence 6: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` names admin manual execution as a policy gap.
- Evidence 7: `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md` names F-003.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Evidence 9: `resolve_guardrails.py` returned `RG-002`, `RG-003`, `RG-007`, and `RG-022` for this backend admin LLM audit scope.
- Registry gap: no exact guardrail exists for admin manual execution provider-capable policy audits.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `_condamad/docs`, and `_condamad/audits` exist.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Specialized audit under `_condamad/audits/admin-manual-llm-execution/`.
  - Admin LLM prompt router manual execution route and contracts.
  - Admin sample payload CRUD, validation, and `chart_json` handling.
  - Permission checks, logs, audit events, and test coverage for admin manual execution.
  - Provider-capability trace from route to sample payload to `LLMGateway.execute_request`.
  - Recommended decision and candidate implementation stories.
- Out of scope:
  - Backend runtime changes, permission changes, frontend UI, database schema, auth, i18n, styling, build tooling, and migrations.
  - Real provider calls.
  - Direct edits to prompt-generation cartography documentation.
  - Guardrail registry maintenance or enrichment.
  - Promoting admin manual execution as a public flow.
- Explicit non-goals:
  - No implementation code change.
  - No route, permission, gateway, sample payload, prompt, or test behavior change.
  - No frontend route, screen, client generation, or UI validation.
  - No real LLM or provider call.

Named brief primitives in scope:

- `admin manual execution`
- `AdminCatalogManualExecute*`
- `execute_admin_catalog_sample_payload`
- `sample payload CRUD`
- `chart_json`
- `LLMGateway.execute_request`
- `permissions`
- `logs`
- `audit events`
- `integration tests`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend admin LLM audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the admin manual execution audit report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep prompt-generation cartography documentation unchanged.
  - Record candidate follow-up stories without implementing them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the audit cannot choose document, restrict, migrate, or decommission from source evidence.
- Additional validation rules:
  - The report must cite route, contract, sample payload, permission, log, audit event, test, and cartography sources.
  - The trace must prove whether live provider execution calls `LLMGateway.execute_request`.
  - Sample payload CRUD must be separated from manual live execution in the report.
  - `chart_json` must be classified as necessary, tolerable temporary, migration target, or decommission blocker.
  - The recommendation must choose exactly one primary decision from document, restrict, migrate, or decommission.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source reads, `AST guard`, targeted `rg`, and pytest paths prove the admin execution trace. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the audit report plus story evidence. |
| Ownership Routing | yes | The audit belongs under `_condamad/audits`, not runtime code or final documentation. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The report has required sections, matrices, citations, recommendation, and candidate stories. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Admin-only, provider-capable, sample CRUD, and carrier classifications must stay explicit. |
| Persistent Evidence | yes | Report, source evidence, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The admin manual execution audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Mandatory report sections are present. | Evidence profile: json_contract_shape; `rg` checks required headings in the report. |
| AC3 | Route to gateway trace is sourced. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/test_admin_llm_catalog.py`; `rg` checks gateway terms. |
| AC4 | Admin-only exposure is classified. | Evidence profile: json_contract_shape; `rg` checks permission, admin-only, indirect exposure terms. |
| AC5 | Sample CRUD is separated from live execution. | Evidence profile: json_contract_shape; `rg` checks CRUD and provider execution labels. |
| AC6 | `chart_json` policy is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `chart_json` classification labels. |
| AC7 | Observability coverage is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks log and audit event terms. |
| AC8 | Implementation recommendation is single. | Evidence profile: json_contract_shape; `python` checks one primary recommendation label. |
| AC9 | Candidate implementation stories are listed. | Evidence profile: json_contract_shape; `rg` checks candidate story section and policy labels. |
| AC10 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded `git status` app surfaces. |
| AC11 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and baseline source availability artifact. (AC: AC1, AC11)
- [ ] Task 2: Inspect the admin LLM prompt router route, request contract, response contract, and gateway call path. (AC: AC3)
- [ ] Task 3: Inspect sample payload CRUD, validation, target scoping, and natal `chart_json` rules. (AC: AC5, AC6)
- [ ] Task 4: Inspect permission checks, admin-only assumptions, indirect exposure paths, logs, and audit events. (AC: AC4, AC7)
- [ ] Task 5: Inspect integration tests for runtime preview, live execution, provider doubles, errors, and redaction behavior. (AC: AC3, AC7)
- [ ] Task 6: Read the cartography document and CS-353 audit finding to preserve prior policy gaps. (AC: AC6, AC8, AC9)
- [ ] Task 7: Build the route -> sample payload -> gateway trace with cited paths and symbols. (AC: AC3)
- [ ] Task 8: Build the permissions, logs, audit, sample payload, and carrier matrices. (AC: AC4, AC5, AC6, AC7)
- [ ] Task 9: Choose one primary recommendation and record rejected alternatives with evidence. (AC: AC8)
- [ ] Task 10: List candidate implementation stories for restriction, migration, documentation, or decommission work. (AC: AC9)
- [ ] Task 11: Run validation scans, persist command output, and confirm runtime files remain unchanged. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-360-audit-admin-manual-execution-provider-capable.md` - source scope and acceptance criteria.
- `backend/app/api/v1/routers/admin/llm/prompts.py` - manual execution route and gateway call path.
- `backend/app/services/api_contracts/admin/llm/prompts.py` - `AdminCatalogManualExecute*` contracts.
- `backend/app/services/llm_generation/admin_sample_payloads.py` - sample payload validation and `chart_json` rules.
- `backend/app/api/v1/routers/admin/llm/sample_payloads.py` - sample payload CRUD route ownership.
- `backend/tests/integration/test_admin_llm_catalog.py` - admin catalog preview and manual execution integration tests.
- `backend/tests/integration/test_admin_llm_sample_payloads.py` - sample payload CRUD and validation tests.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - current policy gap statement.
- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md` - CS-353 finding F-003.

## Runtime Source of Truth

- Primary source of truth:
  - Backend source files listed in Files to Inspect First.
  - Existing integration tests for admin catalog and sample payloads.
  - Current cartography document and CS-353 audit report.
  - `AST guard` or bounded status guard proving report-only changes.
- Secondary evidence:
  - Targeted `rg` scans for route path, `execute_admin_catalog_sample_payload`, `AdminCatalogManualExecute`, `sample_payload`, `chart_json`, and `LLMGateway`.
  - Targeted `rg` scans over the generated audit report for required sections and recommendation labels.
- Static scans alone are not sufficient for this story because:
  - The audit must inspect route ownership, contract shape, permission boundary, and provider handoff context together.

## Contract Shape

- Contract type:
  - Timestamped admin manual execution provider-capability audit report.
- Fields:
  - `Surface`: route, contract, CRUD, validation, permission, log, audit event, test, or documentation source.
  - `Evidence`: source path plus symbol, route, test, heading, row marker, or bounded source note.
  - `Provider capability`: provider-capable, not provider-capable, test-only, CRUD-only, or unresolved source blocker.
  - `Exposure`: admin-only, indirectly exposable, internal-only, test-only, or unresolved source blocker.
  - `Carrier`: sample payload field or execution context field, including `chart_json` classification.
  - `Risk`: policy, security, observability, data-carrier, documentation, or test-coverage risk.
  - `Decision`: document, restrict, migrate, decommission, blocker, or candidate story.
- Required report sections:
  - `Resume executif`
  - `Trace route -> sample payload -> gateway`
  - `Matrice permissions logs et audit`
  - `Matrice sample payloads et carriers legacy`
  - `Decision recommandee`
  - `Stories candidates d'implementation`
- Required fields:
  - `Surface`
  - `Evidence`
  - `Provider capability`
  - `Exposure`
  - `Carrier`
  - `Risk`
  - `Decision`
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; no OpenAPI or generated frontend contract change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/admin-manual-execution-scan.txt`
- Expected invariant:
  - The only intended repository surface delta is the CS-360 audit report and CS-360 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin manual execution audit report | `_condamad/audits/admin-manual-llm-execution/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/` | `backend/tests/**` |
| Candidate story list | CS-360 audit report section | runtime code comments |
| Policy recommendation | CS-360 audit report decision section | prompt-generation cartography direct edit |

## Mandatory Reuse / DRY Constraints

- Reuse the source paths and symbols from the brief instead of creating a parallel source list.
- Reuse the CS-353 finding and current cartography statement as prior evidence.
- Do not duplicate report matrices with conflicting status labels.
- Use one canonical recommendation label across executive summary, decision section, and candidate story list.
- Keep validation commands centralized in the Validation Plan and persist their output once.

## No Legacy / Forbidden Paths

- No legacy route path may be introduced or endorsed by this audit.
- No compatibility route path may be introduced or endorsed by this audit.
- No fallback route path may be introduced or endorsed by this audit.
- No sample payload carrier may be treated as safe without explicit source evidence.
- No public-flow promotion of admin manual execution is allowed.
- No hidden residual work may be left outside blocker or candidate-story labels.

## Reintroduction Guard

- The report must preserve separate classifications for admin-only execution, sample payload CRUD, live provider execution, tests, and documentation.
- The report must include a deterministic `rg` guard for `execute_admin_catalog_sample_payload`, `AdminCatalogManualExecute`, `chart_json`, and `LLMGateway`.
- The report must not replace the required recommendation with a broad undecided status.
- The validation output must include a bounded status guard proving backend and frontend files are unchanged.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Admin router ownership stays source-classified, not edited. | `rg` source trace; app status guard. |
| RG-003 `converge-api-v1-route-architecture` | Route architecture is audited from canonical router paths. | `rg` route trace; `AST guard`. |
| RG-007 `converge-admin-llm-observability-router` | Admin LLM endpoint ownership remains separated in the audit. | `rg` owner scan; report matrix. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation commands use collected backend test paths. | `pytest` path references; validation artifact. |
| Registry gap | No exact guardrail covers admin manual execution policy audits. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because this is a backend admin audit.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/source-availability.txt` | Prove required sources existed. |
| Admin execution scan | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/admin-manual-execution-scan.txt` | Store targeted scans. |
| Report shape check | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/report-shape-check.txt` | Prove report sections. |
| Validation output | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/validation.txt` | Store validation commands. |
| Review output | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/admin-manual-llm-execution/YYYY-MM-DD-HHMM/01-admin-manual-execution-provider-capable-audit.md` - audit deliverable.
- `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/source-availability.txt` - source evidence.
- `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/admin-manual-execution-scan.txt` - targeted scan output.
- `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/report-shape-check.txt` - report shape evidence.
- `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/integration/test_admin_llm_catalog.py` - inspect existing manual execution and runtime preview coverage.
- `backend/tests/integration/test_admin_llm_sample_payloads.py` - inspect existing sample payload validation coverage.

Files not expected to change:

- `backend/app/**` - out of scope; audit-only story must not change runtime code.
- `backend/tests/**` - out of scope; audit-only story must not change test code.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/audits/admin-manual-llm-execution').exists()"`
- VC2: `rg -n "Resume executif|Trace route -> sample payload -> gateway|Decision recommandee" _condamad/audits/admin-manual-llm-execution`
- VC3: `rg -n "ADMIN_MANUAL_EXECUTE_ROUTE_PATH|execute_admin_catalog_sample_payload|AdminCatalogManualExecute|LLMGateway" backend/app backend/tests`
- VC4: `rg -n "sample_payload|chart_json|admin-only|provider-capable" _condamad/audits/admin-manual-llm-execution backend/app backend/tests`
- VC5: `pytest -q backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py`
- VC6: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/validation.txt').exists()"`
- VC7: `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','backend/app','backend/tests','frontend/src'], text=True); assert out.strip()==''"`
- VC8: `ruff format .`
- VC9: `ruff check .`
- VC10: `pytest -q`

## Regression Risks

- The audit could confuse sample payload CRUD with live provider execution and understate provider capability.
- The audit could classify `chart_json` as harmless admin data without deciding migration, restriction, documentation, or decommission work.
- The audit could promote admin manual execution as a public flow by using ambiguous wording.
- The audit could omit logs, audit events, or redaction behavior and leave operational risk implicit.
- The audit could create candidate stories that do not close the policy gap identified by CS-353 and the cartography document.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Do not make real provider calls.
- Do not modify backend runtime code, backend tests, frontend files, migrations, or guardrail registry entries.
- Persist validation output under the CS-360 story evidence folder.

## References

- `_story_briefs/cs-360-audit-admin-manual-execution-provider-capable.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/services/api_contracts/admin/llm/prompts.py`
- `backend/app/services/llm_generation/admin_sample_payloads.py`
- `backend/app/api/v1/routers/admin/llm/sample_payloads.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/integration/test_admin_llm_sample_payloads.py`
