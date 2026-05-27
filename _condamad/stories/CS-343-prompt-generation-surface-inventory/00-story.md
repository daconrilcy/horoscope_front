# Story CS-343 prompt-generation-surface-inventory: Audit Prompt Generation Surface Inventory
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md`.
- Source problem: after CS-324 to CS-342, the project needs one complete source map of every active, config, test, seed, and archival LLM prompt surface.
- Source stakes:
  - Prompt-generation ownership must be visible before later architecture or refactor stories.
  - Text matches must not be confused with active execution influence.
  - The inventory must separate prompt-visible, validation-only, audit-only, and execution-only boundaries.
  - The report must preserve gaps and dependencies for CS-344 to CS-350 without changing runtime behavior.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a timestamped audit inventory of backend LLM prompt-generation surfaces, with each surface classified by role, status, owner path, key symbols,
and evidence. The story creates documentation and evidence artifacts only; it does not modify application runtime behavior.

## Target State

- A report exists under `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/01-surface-inventory-audit.md`.
- The report covers backend LLM domain owners, LLM generation services, astrology input builders, LLM models, migrations, seeds, bootstrap, routers, tests, and CONDAMAD artifacts.
- Each relevant surface has one explicit status: active runtime, active configuration, test guard, bootstrap/seed, observability/audit, historical, or debt.
- Each active surface is mapped to a file path, symbol or function name, producer, consumer, and prompt influence boundary.
- Prompt-visible, validation-only, audit-only, and runtime-only boundaries are separated without merging evidence roles into prompt material.
- Archival carriers and debt occurrences are classified without accepting them as target implementation paths.
- Gaps are converted into concrete questions or dependencies for CS-344 to CS-350.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md` - prior calculation-to-LLM audit source read.
- Evidence 3: `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md` - prior natal prompt pipeline audit source read.
- Evidence 4: `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` - prior prompt config audit source read.
- Evidence 5: `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - target LLM astrology input contract source read.
- Evidence 6: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - evidence boundary source read.
- Evidence 7: `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` - final evidence boundary source read.
- Evidence 8: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-343`.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through scoped resolver output only.
- Evidence 10: `resolve_guardrails.py` returned RG-002 and RG-022 for the backend LLM inventory scope.
- Evidence 11: targeted path checks confirmed `backend`, `frontend`, and all priority backend files listed by the brief exist in this workspace.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist in this workspace.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit inventory for backend LLM prompt-generation owners under `backend/app/domain/llm/**`.
  - Audit inventory for generation services under `backend/app/services/llm_generation/**`.
  - Audit inventory for astrology builders that feed `llm_astrology_input_v1`.
  - Audit inventory for LLM models, migrations, seeds, bootstrap, assemblies, personas, schemas, and profiles.
  - Audit inventory for admin, public, or internal routers that trigger or expose LLM generation.
  - Audit inventory for backend tests and CONDAMAD artifacts that guard prompt generation, validation, or archival carrier boundaries.
- Out of scope:
  - Frontend UI, database schema change, auth, i18n, styling, build tooling, migration file modifications, and public API behavior changes.
  - Prompt rewrite, provider call changes, bug fixes, runtime refactor, architecture synthesis, and delivery report closure.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No runtime code change, prompt text rewrite, model migration, seed execution, or provider integration.
  - No final architecture decision report; this story produces the source map required by later stories.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend LLM audit-inventory contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only audit, evidence, validation, and generated review artifacts.
  - Do not change application code, prompt text, seed definitions, migrations, tests, or runtime behavior.
  - Preserve existing prompt-visible, validation-only, audit-only, and runtime-only boundaries.
  - Classify archival carriers and debt without creating a compatibility path.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a required source surface cannot be inspected or the audit needs a product decision to classify a surface.
- Additional validation rules:
  - The inventory must cite concrete file paths and symbol names for every active surface it classifies.
  - The report must distinguish executable influence from textual occurrence through `rg`, source reads, and `AST guard` evidence.
  - Runtime-boundary claims must be backed by `pytest`, `AST guard`, or bounded source-trace evidence.
  - Gaps must be written as questions or dependencies for CS-344 to CS-350, not as hidden implementation work.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, source traces, and targeted `pytest` paths prove active execution influence. |
| Baseline Snapshot | yes | Inventory scans and symbol lists create a reproducible before-state for later stories. |
| Ownership Routing | yes | Prompt rendering, use-case selection, astrology input, provider handoff, audit, and tests need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit inventory story. |
| Contract Shape | yes | The audit report has required sections, statuses, boundaries, evidence columns, and gap outputs. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Archival carriers must stay classified and must not become accepted implementation paths. |
| Persistent Evidence | yes | Report, scan output, validation output, final evidence, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The surface inventory audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | Every relevant surface has one explicit status. | Evidence profile: json_contract_shape; `python` checks required status labels in the report. |
| AC3 | Active execution surfaces cite owner symbols. | Evidence profile: ast_architecture_guard; `AST guard`; targeted `rg` over backend LLM paths. |
| AC4 | Configuration surfaces use a distinct status. | Evidence profile: json_contract_shape; `rg` output plus report surface table. |
| AC5 | Priority source files from the brief are covered. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n` checks priority filenames in the report. |
| AC6 | Prompt influence boundaries are classified. | Evidence profile: json_contract_shape; `python` checks boundary labels in the report. |
| AC7 | Archival carriers are classified as non-target. | Evidence profile: repo_wide_negative_scan; `rg` scan plus report classification table. |
| AC8 | CS-344 to CS-350 gaps are explicit. | Evidence profile: baseline_before_after_diff; `python` checks `CS-344` and `CS-350` markers in the report. |
| AC9 | Backend app source files are unchanged. | Evidence profile: ast_architecture_guard; `python` checks git status; `AST guard` confirms no app edits. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and baseline evidence artifact set. (AC: AC1, AC10)
- [ ] Task 2: Inventory `backend/app/domain/llm/**` owners for use-case selection, assembly resolution, prompt rendering, and provider handoff. (AC: AC2, AC3, AC6)
- [ ] Task 3: Inventory `backend/app/services/llm_generation/**` services for natal, chat, guidance, horoscope daily, validation, and audit flows. (AC: AC2, AC3, AC6)
- [ ] Task 4: Inventory astrology builders and contracts feeding `llm_astrology_input_v1`. (AC: AC2, AC3, AC5, AC6)
- [ ] Task 5: Inventory LLM models, migrations, seeds, bootstrap, assemblies, personas, schemas, and profiles. (AC: AC2, AC4, AC6)
- [ ] Task 6: Inventory routers and backend tests that trigger, expose, or guard prompt generation. (AC: AC2, AC4, AC5)
- [ ] Task 7: Classify archival carriers and debt without treating text presence as execution influence. (AC: AC7, AC9)
- [ ] Task 8: Write gaps as questions or dependencies for CS-344 to CS-350. (AC: AC8)
- [ ] Task 9: Run validation scans, persist outputs, and confirm backend app and test files remain unchanged. (AC: AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md` - source scope and acceptance criteria.
- `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md` - prior calculation and interpretation audit context.
- `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md` - prior natal prompt pipeline context.
- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` - prior prompt configuration context.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - target internal LLM astrology input contract.
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - evidence prompt-boundary context.
- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` - final evidence validation context.
- `backend/app/domain/llm/runtime/gateway.py` - provider handoff and message assembly owner.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly resolution owner.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use-case registry owner.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - developer prompt rendering owner.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - modern astrology input owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal generation service owner.
- `backend/app/services/llm_generation/chat/public_chat.py` - chat generation service owner.
- `backend/app/services/llm_generation/guidance/guidance_service.py` - guidance generation service owner.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - daily horoscope narration service owner.
- `backend/app/ops/llm/bootstrap/**` - prompt, assembly, persona, schema, and profile bootstrap surfaces.
- `backend/tests/**/test*llm*` - backend LLM tests and guards.
- `backend/tests/**/test*prompt*` - backend prompt tests and guards.

## Runtime Source of Truth

- Primary source of truth:
  - Source traces from backend LLM domain, service, astrology input, bootstrap, router, and backend test files.
  - `AST guard` checks for symbol-level ownership and active execution classification.
  - Targeted `pytest` paths that already guard prompt generation and LLM boundaries.
- Secondary evidence:
  - Targeted `rg` scans for prompt, LLM, assembly, persona, provider, `llm_astrology_input_v1`, and archival carrier terms.
- Static scans alone are not sufficient for this story because:
  - The audit must classify whether each occurrence is active execution, configuration, seed, test guard, observability, history, or debt.

## Contract Shape

- Contract type:
  - Timestamped backend audit report and persistent evidence bundle.
- Fields:
  - `file path`: exact repository path for each inspected surface.
  - `owner`: canonical module or artifact owner.
  - `symbol or function`: concrete class, function, constant, test, or seed symbol.
  - `role`: source role in prompt generation or validation.
  - `status`: one value from the required status list.
  - `boundary`: one value from the required boundary list.
  - `evidence`: short source or command evidence.
  - `gap or dependency marker`: next-story question or dependency.
- Required report sections:
  - Executive summary.
  - Inspected surface table.
  - Surface status for every relevant surface.
  - Key symbols or functions.
  - Evidence by file path and symbol name.
  - Boundaries: prompt-visible, validation-only, audit-only, runtime-only.
  - Classified archival carrier occurrences.
  - Gaps for CS-344 to CS-350.
- Required status values:
  - `active runtime`
  - `active configuration`
  - `test guard`
  - `bootstrap/seed`
  - `observability/audit`
  - `historical`
  - `debt`
- Required boundary values:
  - `prompt-visible`
  - `validation-only`
  - `audit-only`
  - `runtime-only`
- Required fields:
  - file path
  - owner
  - symbol or function
  - role
  - status
  - boundary
  - evidence
  - gap or dependency marker
- Optional fields:
  - none for active surfaces; historical and debt rows may use `not active` as consumer.
- Status codes:
  - none; this story does not change a public API route.
- Serialization names:
  - Report column names must use the exact field names listed above.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/prompt-generation-scan-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/prompt-generation-scan-after.txt`
- Expected invariant:
  - The only intended repository delta is the audit report and story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Use-case selection inventory | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | report-only guessed ownership |
| Assembly resolution inventory | `backend/app/domain/llm/configuration/assembly_resolver.py` | service-layer assumption |
| Prompt rendering inventory | `backend/app/domain/llm/prompting/prompt_renderer.py` | provider adapter ownership |
| Provider handoff inventory | `backend/app/domain/llm/runtime/gateway.py` | prompt seed ownership |
| Astrology input inventory | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | public projection ownership |
| Generation service inventory | `backend/app/services/llm_generation/**` | domain configuration ownership |
| Bootstrap inventory | `backend/app/ops/llm/bootstrap/**` | runtime prompt renderer ownership |
| Audit report | `_condamad/audits/prompt-generation-cartography/*/01-surface-inventory-audit.md` | transient chat notes |

## Mandatory Reuse / DRY Constraints

- Reuse the status taxonomy from this story instead of creating a second classification vocabulary.
- Reuse existing source symbols, test names, and CONDAMAD report paths as evidence; do not duplicate code snippets into the report.
- Reuse the prior CS-324, CS-325, CS-327, CS-330, CS-341, and CS-342 context to avoid re-litigating already closed boundaries.
- Do not add external packages.
- Do not copy large prompt text, seed bodies, or test fixtures into the report; cite paths, symbols, and short evidence only.

## No Legacy / Forbidden Paths

- No legacy prompt-generation path may be accepted as a target implementation path.
- No compatibility route, serializer, prompt renderer, or seed path may be added by this audit story.
- No fallback prompt-generation path may be introduced to explain an unclassified surface.
- Archival carriers may be classified only as active runtime, active configuration, test guard, bootstrap/seed, observability/audit, historical, or debt.
- Forbidden implementation surfaces for this story:
  - `backend/app/**` code modifications.
  - `backend/tests/**` code modifications.
  - `backend/migrations/**` modifications.
  - `frontend/src/**` modifications.

## Reintroduction Guard

- Guard against turning the audit into runtime changes with `git status --short -- backend/app backend/tests backend/migrations frontend/src`.
- Guard against incomplete source coverage with targeted `rg` checks over priority filenames in the generated report.
- Guard against unclassified archival carriers with a targeted `rg` scan for `chart_json`, `natal_data`, `evidence`, `provider`, and `prompt`.
- Guard against text-presence drift by requiring each report row to include a status and boundary value.
- Required architecture guard: use `AST guard` or a collected `pytest -q backend/tests/architecture` target to prove source ownership did not move.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 `align-prompt-generation-story-validation-paths` | Active validation commands must target backend prompt-generation scans and tests. | `pytest` paths; `rg` scans. |
| RG-002 `refactor-api-v1-routers` | Needs-investigation only for router inventory; no API route edit is in scope. | router `rg` scan; `git status`. |
| Registry gap | No exact guardrail exists for prompt-generation surface cartography. | Resolver output recorded in evidence. |

Non-applicable examples: RG-047, RG-052, and RG-041 are frontend or entitlement-documentation guardrails and remain out of scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Scan baseline | `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/prompt-generation-scan-baseline.txt` | Preserve initial scan evidence. |
| Scan after | `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/prompt-generation-scan-after.txt` | Preserve final scan evidence. |
| Symbol map | `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/symbol-map.md` | Keep path and symbol evidence. |
| Validation output | `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/validation-output.txt` | Keep command results. |
| Audit report | `_condamad/audits/prompt-generation-cartography/*/01-surface-inventory-audit.md` | Keep the inventory deliverable. |
| Final evidence | `_condamad/stories/CS-343-prompt-generation-surface-inventory/generated/10-final-evidence.md` | Keep implementation evidence. |
| Review output | `_condamad/stories/CS-343-prompt-generation-surface-inventory/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend LLM audit inventory story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-cartography/*/01-surface-inventory-audit.md` - required audit inventory deliverable.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/prompt-generation-scan-baseline.txt` - baseline scan artifact.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/prompt-generation-scan-after.txt` - final scan artifact.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/symbol-map.md` - inspected path and symbol map.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/evidence/validation-output.txt` - validation command artifact.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/generated/10-final-evidence.md` - final handoff artifact.

Likely tests:

- No new tests are expected because this story creates an audit report only.
- Existing targeted tests may be run for evidence: `backend/tests/llm_orchestration/**`, `backend/tests/unit/domain/astrology/**`, and `backend/tests/integration/llm/**`.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime source is touched.
- `backend/tests/**` - out of scope; no test source is touched.
- `backend/migrations/**` - out of scope; no migration is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run VC1, VC2, VC3, VC5, VC11, and VC12 from the repository root.
Run VC4, VC6, VC7, VC8, VC9, and VC10 from `backend`.

- VC1 report path:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/prompt-generation-cartography'); assert any(root.glob('*/01-surface-inventory-audit.md'))"`
- VC2 status taxonomy:
  `python -c "from pathlib import Path; r=Path('_condamad/audits/prompt-generation-cartography')"`
  Run `python` to read the latest `01-surface-inventory-audit.md` and assert it contains `active runtime` and `debt`.
- VC3 priority coverage:
  `rg -n "gateway.py|assembly_resolver.py|prompt_renderer.py|canonical_use_case_registry.py|llm_astrology_input_v1.py" _condamad/audits/prompt-generation-cartography`
- VC4 prompt scan:
  `rg -n "prompt|llm|assembly|persona|provider|llm_astrology_input_v1" app tests`
- VC5 archival carrier scan:
  `rg -n "chart_json|natal_data|evidence|evidence_refs|prompt_visible|provider" backend/app backend/tests _condamad _story_briefs`
- VC6 route and service inventory:
  `rg -n "LLMGateway|PromptRenderer|assembly|use_case|llm_astrology_input_v1|generate_natal_interpretation" app tests`
- VC7 targeted tests:
  `pytest -q tests/llm_orchestration tests/unit/domain/astrology tests/integration/llm --tb=short`
- VC8 format: `ruff format .`
- VC9 lint: `ruff check .`
- VC10 full backend tests: `pytest -q tests --tb=short`
- VC11 artifact paths:
  `python -c "from pathlib import Path; r=Path('_condamad/stories/CS-343-prompt-generation-surface-inventory')"`
  Run `python` to assert the `evidence` and `generated` children exist under that story directory.
- VC12 no runtime source delta:
  `git status --short -- backend/app backend/tests backend/migrations frontend/src`

## Regression Risks

- A text occurrence could be misclassified as prompt influence without tracing the producing and consuming symbols.
- A seed or archival prompt could be mistaken for an active prompt-generation source.
- Evidence or audit-only material could be described as prompt-visible if prior CS-341 and CS-342 boundaries are not respected.
- Broad scans can include reports and briefs; the implementation must classify executable surfaces separately from documentation archives.
- Full backend tests can surface unrelated failures; unrelated failures must be recorded separately while keeping inventory evidence strict.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Use PowerShell on Windows and activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, Pytest, or script command.
- Do not modify backend runtime files, backend tests, migrations, frontend files, prompt seeds, or provider integration code.
- Write the audit report under a timestamped child directory of `_condamad/audits/prompt-generation-cartography/`.
- Keep source excerpts short; cite file paths, symbols, and command evidence instead of copying full files.
- Classify remaining gaps as questions or dependencies for CS-344 to CS-350.

## References

- `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md`
- `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`
- `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`
- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`
- `_condamad/stories/regression-guardrails.md`
