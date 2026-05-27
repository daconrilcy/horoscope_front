# Story CS-350 documentation-cartographie-generation-prompt-llm-mermaid: Document Prompt Generation Cartography With Mermaid
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md`.
- Selected mode: Repo-informed story, because the story must name current source paths and required evidence artifacts without inventing facts.
- Source problem: CS-343 to CS-349 define the prompt-generation evidence chain; this story must compile it into a final readable map.
- Source stakes:
  - A new developer or agent must understand the current LLM prompt generation flow without rereading every source file.
  - The prompt-visible boundary must stay separate from backend-only audit data.
  - Mermaid diagrams must make the runtime flow, assembly flow, LLM input construction, provider handoff, and audit path readable.
  - Missing source artifacts must be called out as blockers for implementation closure, not silently replaced by invented facts.
- Source-alignment evidence: the objective, ACs, tasks, files, and validation plan preserve every required section and diagram from the brief.

## Objective

Create the final detailed documentation for the current LLM prompt generation implementation, including maintained Mermaid diagrams and traceable source paths.

## Target State

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` exists as the canonical final document.
- The document explains the current flow from use-case selection to provider messages, output validation, persistence audit, and observability.
- The document includes the six required Mermaid diagrams from the brief or a strictly equivalent maintained version.
- The document separates prompt-visible data from backend-only evidence, provenance, hashes, audit fields, and observability data.
- The document cites source files, symbols, audits, architecture, report artifacts, tests, guardrails, residual risks, and open questions.
- The document does not modify backend runtime, frontend UI, database schema, prompts, provider behavior, or tests.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-350`.
- Evidence 3: `backend/app/domain/llm/runtime/gateway.py` - current `LLMGateway` source path exists.
- Evidence 4: `backend/app/domain/llm/configuration/assembly_resolver.py` - current `assemble_developer_prompt` owner exists.
- Evidence 5: `backend/app/domain/llm/prompting/prompt_renderer.py` - current `PromptRenderer` owner exists.
- Evidence 6: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current LLM input builder path exists.
- Evidence 7: `backend/app/services/llm_generation/natal/interpretation_service.py` - current natal service path exists.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted by resolved IDs only.
- Repository structure alert: `_condamad/audits/prompt-generation-cartography` is absent in this workspace at drafting time.
- Repository structure alert: `_condamad/architecture/prompt-generation-cartography` is absent in this workspace at drafting time.
- Repository structure alert: `_condamad/reports/prompt-generation-cartography` is absent in this workspace at drafting time.
- Implementation note: CS-343 to CS-349 must create or provide the missing artifacts before CS-350 can close with full source coverage.

## Domain Boundary

- Domain: documentation
- In scope:
  - Final documentation under `_condamad/docs/prompt-generation-cartography/`.
  - Mermaid diagrams describing prompt generation, configuration resolution, LLM input construction, provider composition, and audit flow.
  - Source traceability to audits CS-343 to CS-347, architecture CS-348, report CS-349, and current backend LLM source files.
  - Verification instructions for the produced documentation.
- Out of scope:
  - Backend runtime changes, frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and prompt rewriting.
  - Provider calls, generated client changes, test implementation changes, and prompt contract changes.
- Explicit non-goals:
  - No runtime behavior change.
  - No frontend route, screen, client generation, or UI validation.
  - No provider call.
  - No correction of gaps discovered in CS-343 to CS-349.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a final documentation contract with Mermaid diagrams.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add documentation artifacts only under `_condamad/docs/prompt-generation-cartography/`.
  - Add story evidence artifacts only under `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-343 to CS-349 final artifacts are unavailable and the document cannot cite required source evidence.
- Additional validation rules:
  - The main document must include each mandatory heading listed in the brief.
  - The main document must include at least six fenced Mermaid blocks.
  - The main document must cite each required backend source file or mark a source evidence blocker.
  - The final evidence must prove prompt-visible and backend-only terms are both present.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Backend source paths are evidence sources, but runtime behavior remains unchanged. |
| Baseline Snapshot | yes | Before and after documentation scans prove the only allowed surface delta. |
| Ownership Routing | yes | Documentation belongs under `_condamad/docs`, not backend runtime or frontend code. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only story. |
| Contract Shape | yes | The markdown document has required headings, Mermaid blocks, glossary, and verification sections. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Runtime prompt carriers and audit-only data must not be reintroduced into prompt-visible documentation as allowed payload. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The main documentation file exists. | Evidence profile: baseline_before_after_diff; `python` checks the markdown path. |
| AC2 | The document includes every mandatory brief heading. | Evidence profile: json_contract_shape; `python` checks the required heading list. |
| AC3 | At least six Mermaid diagrams are fenced. | Evidence profile: json_contract_shape; `python` checks Mermaid fence count. |
| AC4 | The prompt-visible boundary is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks prompt-visible and backend-only terms. |
| AC5 | Source symbols are cited. | Evidence profile: baseline_before_after_diff; `rg` checks `LLMGateway`, `PromptRenderer`, source paths. |
| AC6 | Non-nominal paths are separated. | Evidence profile: json_contract_shape; `rg` checks fallback, repair, rejection, degraded terms. |
| AC7 | Guardrails are cited. | Evidence profile: baseline_before_after_diff; `rg` checks tests, guardrails, validation markers. |
| AC8 | Gaps are marked without invented facts. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks gaps, open questions, and source blockers. |
| AC9 | A developer can follow the natal prompt flow. | Evidence profile: baseline_before_after_diff; `rg` checks natal flow terms. |
| AC10 | Persistent evidence artifacts are stored. | Evidence profile: baseline_before_after_diff; `python` checks final evidence paths. |

## Implementation Tasks

- [x] Task 1: Read CS-343 to CS-347 audit artifacts and record unavailable source blockers. (AC: AC5, AC8)
- [x] Task 2: Read CS-348 architecture and CS-349 report artifacts before writing final synthesis. (AC: AC5, AC8)
- [x] Task 3: Inspect current backend LLM source paths listed in this story before drafting technical sections. (AC: AC5, AC9)
- [x] Task 4: Create the main documentation file with the nineteen mandatory sections from the brief. (AC: AC1, AC2)
- [x] Task 5: Add the six mandatory Mermaid diagrams with maintained labels and source-aligned nodes. (AC: AC3, AC9)
- [x] Task 6: Document prompt-visible versus backend-only projection boundaries. (AC: AC4)
- [x] Task 7: Separate nominal flow, repair flow, rejection flow, degraded payloads, and residual risks. (AC: AC6, AC8)
- [x] Task 8: Cite tests, guardrails, and verification commands with paths or bounded source blockers. (AC: AC7)
- [x] Task 9: Persist validation output and final evidence for review handoff. (AC: AC10)

## Files to Inspect First

- `_condamad/audits/prompt-generation-cartography/*/01-surface-inventory-audit.md` - CS-343 final audit source.
- `_condamad/audits/prompt-generation-cartography/*/02-configuration-assembly-placeholder-audit.md` - CS-344 final audit source.
- `_condamad/audits/prompt-generation-cartography/*/03-runtime-gateway-handoff-audit.md` - CS-345 final audit source.
- `_condamad/audits/prompt-generation-cartography/*/04-natal-astrology-input-audit.md` - CS-346 final audit source.
- `_condamad/audits/prompt-generation-cartography/*/05-output-validation-persistence-audit.md` - CS-347 final audit source.
- `_condamad/architecture/prompt-generation-cartography/*/architecture-prompt-generation-llm.md` - CS-348 architecture source.
- `_condamad/reports/prompt-generation-cartography/*/report-prompt-generation-cartography.md` - CS-349 report source.
- `backend/app/domain/llm/runtime/gateway.py` - gateway, plan resolution, message composition, validation, and provider handoff.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly resolution and `assemble_developer_prompt`.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use-case contract registry.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - placeholder extraction and rendering owner.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - rich natal LLM input contract construction.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal runtime orchestration and audit persistence inputs.

## Runtime Source of Truth

- Primary source of truth:
  - The final documentation must be based on CS-343 to CS-349 artifacts and current backend LLM source files.
  - `AST guard` evidence must confirm no backend runtime files changed for this documentation-only story.
- Secondary evidence:
  - Targeted `rg` scans over the produced documentation and relevant backend LLM paths.
- Static scans alone are not sufficient for this story because:
  - The final document must cite artifact-backed facts, not only matching source symbols.

## Contract Shape

- Contract type:
  - Markdown documentation contract with Mermaid diagram blocks.
- Fields:
  - `sections`: markdown headings required by the source brief.
  - `diagrams`: fenced Mermaid blocks required by the source brief.
  - `source citations`: backend paths, audit artifacts, architecture artifacts, report artifacts, or source blockers.
- Required fields:
  - `sections`
  - `diagrams`
  - `source citations`
- Status codes:
  - none; no HTTP route or API behavior is in scope.
- Serialization names:
  - none; no JSON or generated schema is in scope.
- Frontend type impact:
  - none; no frontend generated client or TypeScript type is in scope.
- Required sections:
  - Executive summary.
  - Scope et non-goals.
  - Vue d'ensemble de la chaine.
  - Glossaire.
  - Carte des owners de code.
  - Use case et contrats canoniques.
  - Resolution d'assembly et developer prompt.
  - Gouvernance des placeholders.
  - Construction de `llm_astrology_input_v1`.
  - Projection prompt-visible vs backend-only.
  - Composition des messages provider.
  - Modes `structured` et `chat`.
  - Provider parameters et output schema.
  - Validation, repair, fallback et rejet.
  - Persistence audit et observability.
  - Seeds/bootstrap et chemins non nominaux.
  - Tests et guardrails.
  - Risques residuels et open questions.
  - How to verify.
- Required Mermaid diagrams:
  - Vue globale.
  - Resolution configuration.
  - Construction de `llm_astrology_input_v1`.
  - Projection prompt-visible.
  - Composition provider.
  - Validation et audit.
- Optional fields:
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-mermaid-diagrams.md` for diagram split only when the main document stays readable.
- Generated contract impact:
  - none; this story creates human documentation, not generated API or frontend contracts.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/docs-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/docs-after.txt`
- Expected invariant:
  - The only intended repository surface delta is documentation and CS-350 evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Final prompt-generation documentation | `_condamad/docs/prompt-generation-cartography/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/` | `_condamad/docs/**` |
| Runtime behavior | Existing backend LLM modules | `_condamad/docs/**` |
| Frontend behavior | Existing frontend owners | `_condamad/docs/**` |

## Mandatory Reuse / DRY Constraints

- Reuse CS-343 to CS-349 artifacts as source evidence; do not duplicate their full contents.
- Reference source paths and symbols instead of copying long code excerpts.
- Keep Mermaid diagrams maintained in the main document or the optional diagram companion, not scattered across multiple new files.
- Use the same glossary terms consistently for use case, assembly, placeholder, prompt-visible, backend-only, provider messages, audit, and observability.
- Do not create a second canonical prompt-generation documentation location.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be documented as an authorized prompt-visible input.
- No compatibility carrier may be documented as an authorized prompt-visible input.
- No fallback route may be used to replace missing CS-343 to CS-349 evidence.
- No backend-only evidence, provenance, hashes, audit fields, or observability data may be described as prompt-visible payload.
- No runtime code, frontend code, database migration, prompt text rewrite, or provider integration may be changed under this story.

## Reintroduction Guard

- Guard exact boundaries:
  - `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, and audit metadata stay backend-only in the documentation.
  - Prompt-visible sections are limited to the fields proven by CS-343 to CS-349 and current source inspection.
- Required deterministic guards:
  - `rg` must find `prompt-visible`, `backend-only`, `llm_astrology_input_v1`, `LLMGateway`, and `PromptRenderer` in the final doc.
  - `rg` must find the final document path under `_condamad/docs/prompt-generation-cartography`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend route files remain untouched by this documentation-only story. | `rg` documentation scan; review changed paths. |
| Registry gap | No exact prompt-generation documentation guardrail exists in the resolved registry. | `python` resolver output stored in evidence. |
| Non-applicable RG-041 | Entitlement documentation is outside this prompt-generation scope. | Scope review only. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/guardrails.txt` | Keep resolved scope evidence. |
| Baseline scan | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/docs-baseline.txt` | Keep pre-documentation scan evidence. |
| After scan | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/docs-after.txt` | Keep post-documentation scan evidence. |
| Source coverage map | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/source-coverage.md` | Track required sources and blockers. |
| Validation output | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/validation.txt` | Keep validation command output. |
| Final evidence | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/final-evidence.md` | Summarize closure proof and residual gaps. |
| Review output | `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/generated/11-code-review.md` | Keep review handoff. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this documentation-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - final documentation deliverable.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-mermaid-diagrams.md` - optional diagram companion.
- `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/guardrails.txt` - resolver output.
- `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/docs-baseline.txt` - baseline scan.
- `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/docs-after.txt` - after scan.
- `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/source-coverage.md` - source coverage map.
- `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-350-documentation-cartographie-generation-prompt-llm-mermaid/evidence/final-evidence.md` - final evidence summary.

Likely tests:

- No new test file is expected; this documentation story uses deterministic `python` and `rg` validation commands.
- Assumption risk: `backend/tests/**` stays unchanged because this story does not alter runtime behavior.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime surface is touched.
- `backend/tests/**` - out of scope; no test implementation is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md').exists()"`
- VC2: `python -c "from pathlib import Path; p=Path('_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md'); assert p.exists()"`
- VC2b: `rg -c "```mermaid" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- VC3: `rg -n "llm_astrology_input_v1|LLMGateway|PromptRenderer|assemble_developer_prompt|prompt-visible|backend-only" _condamad/docs/prompt-generation-cartography`
- VC4: `rg -n "nominal|fallback|repair|rejet|degrade|guardrails|How to verify" _condamad/docs/prompt-generation-cartography`
- VC5: `rg -n "prompt-generation-current-implementation" _condamad/docs/prompt-generation-cartography`
- VC6: `python -c "from pathlib import Path; assert any(Path('_condamad/stories').glob('CS-350-*/evidence/final-evidence.md'))"`
- VC7: `ruff format .`
- VC8: `ruff check .`
- VC9: `pytest -q`

## Regression Risks

- Risk: the final document becomes narrative without traceable source evidence.
  - Mitigation: each technical section must cite at least one path, symbol, audit artifact, architecture artifact, report artifact, or source blocker.
- Risk: prompt-visible and backend-only data boundaries drift.
  - Mitigation: AC4 and Reintroduction Guard require exact terms and deterministic scans.
- Risk: missing CS-343 to CS-349 artifacts cause invented facts.
  - Mitigation: AC8 requires source blockers and open questions instead of unsupported claims.
- Risk: diagrams diverge from source evidence.
  - Mitigation: each diagram section must name its source basis and verification path.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Create `_condamad/docs/prompt-generation-cartography/` only for the documentation deliverable.
- Store command outputs in the CS-350 evidence directory.
- Keep the documentation factual; use source blockers for unavailable artifacts.
- Do not modify backend runtime, frontend UI, tests, migrations, or prompt definitions.

## References

- `_story_briefs/cs-350-documentation-cartographie-generation-prompt-llm-mermaid.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md`
- `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md`
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md`
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md`
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/00-story.md`
- `_condamad/stories/CS-348-architecture-cartographie-generation-prompt-llm/00-story.md`
- `_condamad/stories/CS-349-report-cartographie-generation-prompt-llm/00-story.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
