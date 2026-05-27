# Story CS-344 audit-configuration-assembly-placeholder: Audit Configuration Assembly Placeholder Prompt Flow
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md`.
- Source problem: CS-343 inventories prompt-generation surfaces; this story must map the configuration layer that turns a use case into a developer prompt.
- Source stakes:
  - Use-case, assembly, template, persona, plan-rule, placeholder, output-schema, and execution-profile owners must be explicit.
  - The audit must separate nominal runtime resolution, bounded fallback paths, and seed/bootstrap material.
  - `llm_astrology_input_v1` must be traced from use-case contract to prompt rendering without treating seeds as runtime truth.
  - Later refactor stories need a matrix of owner, source data, output, guard, and test evidence.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the source stakes.

## Objective

Produce the second timestamped prompt-generation cartography audit focused on configuration assembly and placeholder resolution. The story creates
documentation and evidence artifacts only; it does not modify runtime code, prompt templates, governance rules, seeds, tests, or public behavior.

## Target State

- A report exists at `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/02-configuration-assembly-placeholder-audit.md`.
- The report includes a text diagram of configuration resolution from canonical use case to rendered developer prompt.
- The report contains a registry matrix with owner, source data, output, guard, and test columns.
- Developer prompt blocks are classified as feature, subfeature, persona, plan rules, hard policy, length budget, and context quality.
- Placeholders are grouped by family, declared owner, validation or replacement path, and runtime consumer.
- Output schema owners and runtime schema resolution paths are mapped without treating seed data as runtime truth.
- Bounded fallback paths are listed separately from nominal runtime resolution.
- Seeds and bootstrap files are classified as provisioning inputs, not runtime configuration source of truth.
- Existing prompt resolution, differentiation, and coherence tests are mapped to what they prove and what they do not prove.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-344`.
- Evidence 3: `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - sibling inventory story read for sequence context.
- Evidence 4: `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` - prior configuration audit brief read.
- Evidence 5: `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md` - transition architecture brief read.
- Evidence 6: `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - target input contract brief read.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through scoped resolver output only.
- Evidence 8: `resolve_guardrails.py` returned RG-002 and RG-022 for the backend prompt-configuration audit scope.
- Evidence 9: targeted `Test-Path` checks confirmed `backend`, `backend/app`, and `backend/tests` exist.
- Evidence 10: targeted `Test-Path` checks confirmed all priority files and tests named by the brief exist.
- Repository structure alert: none. The expected backend roots and priority LLM configuration files exist in this workspace.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of `canonical_use_case_registry.py` and use-case placeholder declarations.
  - Audit of factory helpers, assembly resolution, assembly registries, active release selection, and resolver behavior.
  - Audit of output schema declarations, assembly-linked schema IDs, runtime schema resolution, and schema contract tests.
  - Audit of prompt rendering, placeholder policy, prompt governance registry, and prompt governance JSON data.
  - Audit of execution profile registries, execution profiles, and runtime profile associations.
  - Audit of seeds and bootstrap surfaces that create prompts, use cases, schemas, personas, and assemblies.
  - Audit of tests for prompt resolution, plan differentiation, and configuration coherence.
  - Creation of the timestamped audit report and story evidence artifacts only.
- Out of scope:
  - Frontend UI, database schema change, auth, i18n, styling, build tooling, migrations, and public API behavior.
  - Prompt template edits, new governance rule creation, placeholder fixes, provider handoff audit, and runtime refactor.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No prompt rewrite, provider call change, seed execution, DB migration, or application code change.
  - No audit of the LLM provider handoff; that belongs to CS-345.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend LLM configuration audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only audit, evidence, validation, and generated review artifacts.
  - Do not change application code, prompt text, seed definitions, migrations, tests, or runtime behavior.
  - Preserve the distinction between nominal runtime, bounded fallback, and seed/bootstrap provisioning.
  - Classify unresolved or risky surfaces as gaps instead of implementing a correction.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a source surface cannot be inspected or a configuration owner cannot be classified from repository evidence.
- Additional validation rules:
  - The audit must cite concrete file paths and symbol names for each owner it classifies.
  - The audit must trace `llm_astrology_input_v1` from use-case contract to prompt rendering.
  - Runtime claims must use `AST guard`, targeted `rg`, or existing `pytest` evidence from backend tests.
  - Bounded fallback paths must not be described as nominal runtime paths.
  - Seed and bootstrap rows must be marked as provisioning inputs, not as loaded runtime state.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, source traces, and targeted `pytest` paths prove active configuration influence. |
| Baseline Snapshot | yes | Scan outputs and symbol lists create a reproducible before-state for later stories. |
| Ownership Routing | yes | Use-case, assembly, renderer, placeholder, governance, profile, seed, and test owners must be separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The audit report has required diagrams, matrices, placeholder families, fallback list, test map, and gaps. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Seed/bootstrap and fallback paths must not be reclassified as nominal runtime owners. |
| Persistent Evidence | yes | Report, scan output, validation output, final evidence, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The configuration audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | Use-case registries are mapped. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks `canonical_use_case_registry.py` in the report. |
| AC3 | Assembly resolution owners are mapped. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks assembly files in the report. |
| AC4 | Developer prompt blocks are classified. | Evidence profile: json_contract_shape; `rg` checks required block labels in the report. |
| AC5 | Placeholder families are listed. | Evidence profile: json_contract_shape; `rg` checks placeholder family rows in the report. |
| AC6 | Bounded fallback paths are separated. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks fallback section and nominal section labels. |
| AC7 | Seeds are separated from runtime. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks bootstrap rows in the report. |
| AC8 | Runtime profile owners are mapped. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks execution profile files in the report. |
| AC9 | Output schema owners are mapped. | Evidence profile: runtime_source_of_truth; `AST guard` plus `rg` checks schema rows. |
| AC10 | Existing tests are evaluated. | Evidence profile: baseline_before_after_diff; `pytest` paths from VC4 through VC6. |
| AC11 | Backend app source files are unchanged. | Evidence profile: ast_architecture_guard; `python` checks git status for app/test paths. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and story evidence artifact set. (AC: AC1, AC11)
- [ ] Task 2: Map canonical use cases and required placeholders from `canonical_use_case_registry.py`. (AC: AC2, AC5)
- [ ] Task 3: Map factory helpers, assembly resolver behavior, assembly registries, assemblies, and active release selection. (AC: AC3)
- [ ] Task 4: Map `PromptRenderer`, placeholder policy, prompt governance registry, and governance JSON data. (AC: AC4, AC5, AC6)
- [ ] Task 5: Map execution profile registries, execution profile data, and runtime profile associations. (AC: AC8)
- [ ] Task 6: Separate seed and bootstrap provisioning surfaces from loaded runtime configuration. (AC: AC7)
- [ ] Task 7: Trace `llm_astrology_input_v1` from use-case contract through prompt rendering. (AC: AC2, AC4, AC5)
- [ ] Task 8: Map output schema definitions, schema IDs, runtime resolution, fallback, and validation contracts. (AC: AC9)
- [ ] Task 9: Evaluate prompt resolution, differentiation, output contract, and coherence evidence. (AC: AC10)
- [ ] Task 10: Persist validation outputs and prove backend app and backend tests remain unchanged. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md` - source scope and acceptance criteria.
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` - preceding prompt surface inventory.
- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` - prior prompt configuration audit context.
- `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md` - transition architecture context.
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` - target LLM astrology input contract context.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - use-case and placeholder declaration owner.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly resolution owner.
- `backend/app/domain/llm/configuration/assembly_registry.py` - assembly registry owner.
- `backend/app/domain/llm/configuration/assemblies.py` - assembly data owner.
- `backend/app/domain/llm/configuration/active_release.py` - active release selection owner.
- `backend/app/domain/llm/configuration/config_coherence_validator.py` - configuration coherence and schema guard owner.
- `backend/app/domain/llm/governance/prompt_governance_registry.py` - prompt governance owner.
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json` - prompt governance source data.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - developer prompt rendering owner.
- `backend/app/domain/llm/prompting/catalog.py` - fallback output schema catalog owner.
- `backend/app/domain/llm/runtime/gateway.py` - runtime schema resolution and response-format owner.
- `backend/app/domain/llm/prompting/placeholder_policy.py` - placeholder policy owner.
- `backend/app/domain/llm/configuration/execution_profile_registry.py` - execution profile registry owner.
- `backend/app/domain/llm/configuration/execution_profiles.py` - execution profile data owner.
- `backend/app/ops/llm/bootstrap/**` - prompt, use-case, schema, persona, and assembly provisioning surfaces.
- `backend/tests/evaluation/test_prompt_resolution.py` - prompt resolution proof surface.
- `backend/tests/evaluation/test_differentiation.py` - differentiation proof surface.
- `backend/tests/evaluation/test_output_contract.py` - output contract proof surface.
- `backend/tests/evaluation/__init__.py` - coherence startup validation proof surface.

## Runtime Source of Truth

- Primary source of truth:
  - Source traces from backend LLM configuration, governance, prompting, bootstrap, and backend evaluation test files.
  - `AST guard` checks for owner symbols, resolver calls, renderer calls, and runtime versus provisioning classification.
  - Targeted `pytest` paths that already guard prompt resolution and differentiation behavior.
- Secondary evidence:
  - Targeted `rg` scans for `required_prompt_placeholders`, `assemble_developer_prompt`, `PromptRenderer`, `PLACEHOLDER`,
    `PLAN_RULES`, `length_budget`, `context_quality`, and `llm_astrology_input_v1`.
- Static scans alone are not sufficient for this story because:
  - The audit must classify whether each occurrence is nominal runtime configuration, bounded fallback, seed/bootstrap, test guard, or gap.

## Contract Shape

- Contract type:
  - Timestamped backend audit report and persistent evidence bundle.
- Fields:
  - `owner`: canonical module, registry, data file, seed, or test owner.
  - `source de donnees`: file, data structure, registry entry, seed input, or test fixture used by that owner.
  - `sortie`: prompt block, placeholder declaration, rendered value, profile, schema, persona, or audit row produced.
  - `garde`: validation, policy, resolver guard, test, scan, or documented gap constraining the owner.
  - `test`: exact test path, scan command, or missing coverage marker.
- Required report sections:
  - Executive summary.
  - Text diagram of configuration resolution.
  - Registry matrix: owner, source de donnees, sortie, garde, test.
  - Developer prompt block matrix.
  - Placeholder families and allowed variables.
  - Bounded fallback paths and activation conditions.
  - Seed/bootstrap separation.
  - Existing tests and coverage gaps.
- Required fields:
  - owner
  - source de donnees
  - sortie
  - garde
  - test
- Optional fields:
  - none for active runtime rows; provisioning-only rows may use `not runtime` as consumer.
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
  - `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/configuration-scan-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/configuration-scan-after.txt`
- Expected invariant:
  - The only intended repository delta is the audit report, story evidence artifacts, generated review handoff, and validation output.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Use-case placeholder declarations | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Prompt template text or provider handoff code |
| Assembly resolution | `backend/app/domain/llm/configuration/assembly_resolver.py` | Prompt renderer or bootstrap scripts |
| Assembly catalog data | `backend/app/domain/llm/configuration/assemblies.py` | Runtime provider clients |
| Prompt rendering | `backend/app/domain/llm/prompting/prompt_renderer.py` | Use-case registry or seed files |
| Placeholder validation policy | `backend/app/domain/llm/prompting/placeholder_policy.py` | Prompt template text |
| Prompt governance data | `backend/app/domain/llm/governance/data/prompt_governance_registry.json` | Runtime provider clients |
| Execution profiles | `backend/app/domain/llm/configuration/execution_profiles.py` | Prompt renderer or templates |
| Seed and bootstrap provisioning | `backend/app/ops/llm/bootstrap/**` | Loaded runtime source of truth |

## Mandatory Reuse / DRY Constraints

- Reuse the existing audit folder pattern from CS-343 for timestamped prompt-generation cartography outputs.
- Reuse the existing evidence artifact pattern under the story folder.
- Do not duplicate the full surface inventory from CS-343; reference it and focus this report on configuration assembly and placeholders.
- Do not create a second owner taxonomy when the source files already expose owner modules or registries.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy implementation path may be added for this audit.
- No compatibility path may be added for this audit.
- No fallback implementation path may be added for this audit.
- Do not edit prompt templates, provider handoff code, seeds, runtime services, tests, migrations, or frontend files.
- Do not treat a bounded fallback path as the nominal runtime owner.
- Do not use seed/bootstrap files as proof of loaded runtime configuration without source-trace evidence.

## Reintroduction Guard

- Exact forbidden implementation surfaces:
  - `backend/app/domain/llm/**` code edits.
  - `backend/app/ops/llm/bootstrap/**` seed edits or seed execution.
  - `backend/tests/**` edits outside persisted validation evidence.
  - `frontend/src/**` edits.
- Required deterministic guards:
  - `python` checks `git status --short -- backend/app backend/tests frontend/src`.
  - `rg` verifies the audit report contains the bounded fallback and seed/bootstrap separation sections.
  - `AST guard` verifies the audit evidence references source symbols rather than new implementation changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Applicable only as backend boundary control; no API routing logic may move during audit. | `python` git-status guard; targeted `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable; validation plans must use collected prompt-generation pytest paths. | `pytest` paths in VC4 and VC5. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable example; frontend styling is out of scope. | Manual check: no `frontend/src` task exists. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable example; CSS namespaces are out of scope. | Manual check: no CSS task exists. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/configuration-scan-baseline.txt` | Keep pre-audit source scan evidence. |
| After scan | `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/configuration-scan-after.txt` | Keep post-audit source scan evidence. |
| Audit report | `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/02-configuration-assembly-placeholder-audit.md` | Deliver the configuration audit. |
| Validation output | `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/validation.txt` | Keep validation command output. |
| Final evidence | `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/final-evidence.md` | Summarize final proof and residual gaps. |
| Review output | `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/02-configuration-assembly-placeholder-audit.md` - audit deliverable.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/configuration-scan-baseline.txt` - baseline scan artifact.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/configuration-scan-after.txt` - after scan artifact.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/validation.txt` - validation output artifact.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/evidence/final-evidence.md` - final evidence summary.
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/evaluation/test_prompt_resolution.py` - proves prompt resolution behavior already covered by existing tests.
- `backend/tests/evaluation/test_differentiation.py` - proves plan differentiation behavior already covered by existing tests.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime, registry, renderer, governance, seed, or provider code is edited.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; registry enrichment is not authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; p=Path('_condamad/audits/prompt-generation-cartography'); assert any(p.glob('*/02-configuration-assembly-placeholder-audit.md'))"`
- VC2: `rg -n "owner|source de donnees|sortie|garde|test" _condamad/audits/prompt-generation-cartography`
- VC3: `rg -n "required_prompt_placeholders|assemble_developer_prompt|PromptRenderer|PLACEHOLDER|PLAN_RULES|length_budget|context_quality" backend/app backend/tests`
- VC4: `pytest -q backend/tests/evaluation/test_prompt_resolution.py`
- VC5: `pytest -q backend/tests/evaluation/test_differentiation.py`
- VC6: `pytest -q backend/tests/evaluation/test_output_contract.py`
- VC7: `rg -n "run_llm_coherence_startup_validation|config_coherence_validator" backend/tests backend/app`
- VC8: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app','backend/tests','frontend/src'], check=True)"`
- VC9: `rg -n "configuration-assembly-placeholder-audit" _condamad`
- VC10: `ruff format .`
- VC11: `ruff check .`
- VC12: `pytest -q`

## Regression Risks

- Risk: the audit could merge nominal runtime configuration and bounded fallback behavior.
  - Mitigation: AC6 and the report shape require separate sections for both concepts.
- Risk: seed/bootstrap files could be mistaken for loaded runtime state.
  - Mitigation: AC7 and Ownership Routing require provisioning-only classification for seed/bootstrap rows.
- Risk: the report could duplicate CS-343 instead of deepening the configuration layer.
  - Mitigation: DRY constraints require referencing CS-343 and focusing on use-case, assembly, renderer, placeholder, governance, and profile owners.
- Risk: validation plans could point to stale prompt-generation test paths.
  - Mitigation: RG-022 requires collected `pytest` paths and explicit prompt resolution or differentiation tests.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Keep the audit as documentation plus evidence only; application files remain unchanged.
- Keep markdown table lines under 180 characters in generated evidence and final report.
- Record any missing route-specific or configuration-specific guardrail as `Registry gap` in the story evidence, not in the registry.

## References

- `_story_briefs/cs-344-audit-configuration-assemblies-placeholders-prompts-llm.md`
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md`
- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`
- `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_condamad/stories/regression-guardrails.md`
