# Story CS-357 graphiques-mermaid-construction-prompts-theme-astral: Add Mermaid Diagrams For Natal Prompt Construction
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md`.
- Selected mode: Repo-informed story, because the diagrams must stay aligned with CS-350, CS-356, audits, and backend owners.
- Source problem: readers can see the current prompt-generation cartography, but the natal prompt construction flow lacks dedicated Mermaid diagrams.
- Source stakes:
  - The final prompt path must be understandable from birth data to compiled provider messages.
  - `free`, `basic`, and `premium` must share calculations while differing on prompt-visible selection and editorial depth.
  - Prompt-visible data must stay separated from backend-only, validation-only, audit-only, and provider parameter data.
  - Persona, hard policy, non-invention, validation, repair, rejection, and no provider call must not be conflated.
  - The diagrams must complement CS-356 without changing runtime, prompts, schemas, provider integration, or dependencies.
- Source-alignment evidence: the objective, ACs, tasks, validation plan, non-goals, and guardrails preserve every mandatory diagram from the brief.

## Objective

Create maintainable Mermaid diagrams that explain how natal theme prompts are built for `free`, `basic`, and `premium` plans.

The diagrams must cover the full path from birth data and natal calculations to the compiled provider-ready messages, while proving the no-call boundary.

## Target State

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md` exists as the CS-357 diagram deliverable.
- The document is cited from `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` once that CS-356 document exists.
- At least seven Mermaid diagrams are present, with short ASCII labels and a short legend below each diagram.
- The diagrams cover the global pipeline, injected data construction, plan differentiation, persona, safety, provider message order, and exclusions.
- A `Comment lire les diagrammes` section explains the notation without adding a rendering dependency.
- Backend runtime, prompts, frontend UI, database schema, migrations, provider calls, and generated final JSON examples remain unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-357`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - CS-350 cartography exists.
- Evidence 5: `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md` - CS-356 story exists.
- Evidence 6: `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - target CS-356 document is absent now.
- Evidence 7: `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` - handoff audit read.
- Evidence 8: `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` - natal input audit read.
- Evidence 9: `backend/app/domain/llm/runtime/gateway.py` - current gateway owner exists.
- Evidence 10: `backend/app/domain/llm/configuration/assembly_resolver.py` - current assembly owner exists.
- Evidence 11: `backend/app/domain/llm/prompting/prompt_renderer.py` - current renderer owner exists.
- Evidence 12: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current input owner exists.
- Evidence 13: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID search.

Repository structure alert: the preferred CS-356 document is absent. Implementation must create it or create the CS-357 annex and cite it later.

## Domain Boundary

- Domain: documentation
- In scope:
  - Documentation under `_condamad/docs/prompt-generation-cartography/`.
  - Mermaid diagrams for natal theme prompt construction by `free`, `basic`, and `premium`.
  - Source alignment with CS-350, CS-356 story contract, gateway handoff audit, natal input audit, and backend LLM owners.
  - Diagram legends, short ASCII labels, and a `Comment lire les diagrammes` section.
  - Explicit boundaries for prompt-visible, backend-only, validation-only, audit-only, provider parameters, and no provider call.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, prompt seed changes, output schema changes, and provider calls.
  - Runtime code changes, prompt text rewrites, generated final JSON examples, Mermaid rendering dependencies, and product plan changes.
- Explicit non-goals:
  - No runtime behavior change.
  - No prompt text rewrite.
  - No output schema modification.
  - No real LLM call.
  - No frontend route, screen, client generation, or UI validation.
  - No generated final JSON examples; CS-358 owns that surface.

Named brief primitives in scope:

- `llm_astrology_input_v1`
- `facts`
- `signals`
- `limits`
- `shaping`
- `evidence`
- `provenance`
- `system_core`
- `developer prompt`
- `persona astrologue`
- `payload user`
- `free`
- `basic`
- `premium`
- `hard policy`
- `non-invention`
- `projection_hash`
- `llm_input_hash`
- `provider_response`
- `observability`
- `chart_json`
- `natal_data`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this source-aligned Mermaid documentation contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create or update documentation only under `_condamad/docs/prompt-generation-cartography/`.
  - Create story execution evidence only.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-356 implementation chooses a different canonical documentation path before CS-357 starts.
- Additional validation rules:
  - `AST guard` or bounded `git status` evidence must prove no application source was modified.
  - `python` path checks must prove the diagram document and persistent evidence artifacts exist.
  - `rg` evidence must prove all seven Mermaid diagram themes and all three plans are present.
  - `rg` evidence must prove prompt-visible and backend-only boundaries include the mandatory excluded fields.
  - The document must state that no provider LLM call is represented or performed.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Current docs, audits, stories, and backend owners are source evidence for diagrams. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed documentation surface delta. |
| Ownership Routing | yes | Diagram documentation belongs under `_condamad/docs`, not backend runtime or frontend code. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only story. |
| Contract Shape | yes | The markdown document has required diagrams, legends, source citations, and verification notes. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | Backend-only and audit-only data must not be drawn as prompt-visible. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The Mermaid diagram document exists. | Evidence profile: baseline_before_after_diff; `python` checks the markdown path. |
| AC2 | At least seven Mermaid diagrams are present. | Evidence profile: json_contract_shape; `python` counts fenced Mermaid blocks. |
| AC3 | The three plans are covered. | Evidence profile: json_contract_shape; `rg -n "free|basic|premium"` checks the document. |
| AC4 | The global pipeline is diagrammed. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks birth, input, assembly, messages. |
| AC5 | Injected data construction is diagrammed. | Evidence profile: json_contract_shape; `rg` checks `facts`, `signals`, `limits`, `shaping`. |
| AC6 | Persona is drawn separately. | Evidence profile: baseline_before_after_diff; `rg` checks `persona`, `developer prompt`, and owner paths. |
| AC7 | Safety controls are drawn. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks hard policy, non-invention, validation, rejection. |
| AC8 | Provider message order is exact. | Evidence profile: json_contract_shape; `rg` checks `system_core`, `developer prompt`, `payload user`. |
| AC9 | Prompt exclusions are visible. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks hashes, `provider_response`, and carriers. |
| AC10 | No provider call is represented. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks the no provider call statement. |
| AC11 | CS-356 integration is explicit. | Evidence profile: baseline_before_after_diff; `rg` checks the CS-356 citation path or annex note. |
| AC12 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC13 | Persistent evidence is stored. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-350, CS-356, and the two required audit artifacts before drafting diagrams. (AC: AC4, AC5, AC8)
- [ ] Task 2: Inspect gateway, assembly resolver, prompt renderer, and `llm_astrology_input_v1` owners. (AC: AC6, AC9)
- [ ] Task 3: Create `natal-prompt-construction-mermaid.md` with `Comment lire les diagrammes`. (AC: AC1, AC11)
- [ ] Task 4: Add the global pipeline and injected-data Mermaid diagrams with short ASCII labels. (AC: AC2, AC4, AC5)
- [ ] Task 5: Add the plan differentiation diagram for `free`, `basic`, and `premium`. (AC: AC2, AC3)
- [ ] Task 6: Add persona, safety, provider-message-order, and prompt-boundary diagrams. (AC: AC2, AC6, AC7, AC8, AC9)
- [ ] Task 7: Add a short legend below each diagram and cite source owners without copying long source excerpts. (AC: AC6, AC11)
- [ ] Task 8: Run validation commands and persist command output in the CS-357 evidence directory. (AC: AC12, AC13)

## Files to Inspect First

- `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md`
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - expected implementation-created path.
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`

## Runtime Source of Truth

- Primary source of truth:
  - CS-350 current cartography, CS-356 story contract, required audits, and current backend source owners.
  - `AST guard` or bounded status evidence confirms no backend runtime file changed for this documentation-only story.
- Secondary evidence:
  - Targeted `rg` scans over the produced document and source evidence.
  - Source evidence file with cited paths, symbols, absent CS-356 target state, and blockers.
- Static scans alone are not sufficient for this story because:
  - The diagrams must explain source-supported behavior and avoid inventing runtime prompt text.

## Contract Shape

- Contract type:
  - Markdown documentation contract with Mermaid diagrams, legends, source citations, and verification commands.
- Fields:
  - `diagram`: one mandatory diagram from the source brief.
  - `plan`: one of `free`, `basic`, or `premium`.
  - `visibility`: `prompt-visible`, `backend-only`, `validation-only`, `audit-only`, or `provider-parameter`.
  - `source`: code path, audit artifact, story, existing documentation, or explicit source blocker.
  - `legend`: one short explanatory sentence below each Mermaid block.
- Required fields:
  - `diagram`
  - `plan`
  - `visibility`
  - `source`
  - `legend`
- Required diagrams:
  - `Pipeline global theme astral`
  - `Construction des donnees injectees`
  - `Differenciation par plan`
  - `Introduction astrologue/persona`
  - `Securite et non-invention`
  - `Messages finaux provider`
  - `Frontiere prompt-visible vs backend-only`
- Optional fields:
  - Additional small Mermaid diagrams that split a broad diagram for readability.
- Status codes:
  - none; no HTTP route or API behavior is in scope.
- Serialization names:
  - Diagram labels are documentation labels, not generated schema fields.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; this story creates human documentation, not OpenAPI, final JSON examples, or generated frontend contracts.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-after.txt`
- Expected invariant:
  - The only intended repository surface delta is prompt-generation documentation plus CS-357 evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal prompt Mermaid documentation | `_condamad/docs/prompt-generation-cartography/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/` | `_condamad/docs/**` |
| Runtime prompt behavior | Existing backend LLM modules | `_condamad/docs/**` |
| Frontend behavior | Existing frontend owners | `_condamad/docs/**` |

## Mandatory Reuse / DRY Constraints

- Reuse CS-350, CS-356, gateway handoff audit, and natal input audit as the evidence base.
- Cite source paths and symbols instead of copying long code excerpts.
- Keep the diagrams in one annex or in the CS-356 document, not split across unrelated documentation files.
- Use Mermaid standard syntax only.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be drawn as an authorized prompt-visible input.
- No compatibility prompt carrier may be drawn as an authorized prompt-visible input.
- No fallback prompt path may replace missing source evidence.
- Do not draw `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, or observability as prompt-visible.
- Do not modify backend runtime, frontend UI, database migrations, prompt definitions, provider integrations, or output schemas.

## Reintroduction Guard

- Guarded boundaries:
  - `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, provider response, and observability stay outside prompt-visible payload.
  - `chart_json` and `natal_data` stay outside the modern natal prompt-visible carrier when `llm_astrology_input_v1` is used.
  - The no-call boundary stays after compiled messages and provider parameters.
  - Plan differences are documented as prompt-visible selection, editorial depth, output shape, sections, and length budget.
- Required deterministic guards:
  - `rg` must find `prompt-visible`, `backend-only`, `validation-only`, and `audit-only` in the final document.
  - `rg` must find `projection_hash`, `llm_input_hash`, `provider_response`, `chart_json`, and `natal_data` in the final document.
  - `python` or `git status` must prove application source surfaces are unchanged.

## Regression Guardrails

Scope vector: operation `create`, domain `documentation`, paths `_condamad/docs/prompt-generation-cartography`,
`backend/app/domain/llm`, `backend/app/domain/astrology/interpretation`, contracts `source-aligned-documentation`,
`mermaid-diagram`, and `prompt-construction`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-042 `CS-022-uniformiser-gouvernance-docs-llm-source-truth` | LLM docs must stay source-aligned or explicitly non-canonical. | `rg` source citations; manual check. |
| RG-149 `CS-350-prompt-generation-current-implementation` | Prompt process classes and exclusions must stay documented correctly. | `rg` diagram terms; source scan. |
| Registry gap | Resolver returned RG-002 but missed exact Mermaid prompt-doc guards RG-042 and RG-149. | `python` resolver output; targeted ID search. |
| RG-041 non-applicable | Entitlement documentation is outside this prompt-construction diagram scope. | Manual check: no entitlement surface. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/guardrails.txt` | Keep resolved scope evidence. |
| Baseline scan | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-baseline.txt` | Keep pre-documentation scan evidence. |
| After scan | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-after.txt` | Keep post-documentation scan evidence. |
| Source coverage map | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/source-coverage.md` | Track sources and blockers. |
| Validation output | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/validation.txt` | Keep validation command output. |
| Review output | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md` - final Mermaid documentation deliverable.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - preferred CS-356 integration target.
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/guardrails.txt` - resolver output.
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-baseline.txt` - baseline scan.
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-after.txt` - after scan.
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/source-coverage.md` - source coverage.
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/validation.txt` - validation output.

Likely tests:

- No new tests are expected because the story is documentation-only.
- `backend/tests/**` - existing backend `pytest` suite may be run unchanged to prove no runtime regression.
- Assumption risk: no new test file is expected because this story creates documentation and evidence artifacts only.

Files not expected to change:

- `backend/app/**` - out of scope; application runtime and service code remain unchanged.
- `backend/tests/**` - out of scope; tests are read or checked only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no schema migration is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope for normal story implementation.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md').exists()"`
- VC2:
  `python -c "from pathlib import Path; p=Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md'); assert p.read_text().count('```mermaid') >= 7"`
- VC3:
  `rg -n "Comment lire les diagrammes|```mermaid|flowchart|sequenceDiagram" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC4:
  `rg -n "free|basic|premium|editorial|budget|sections|schema" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC5:
  `rg -n "Birth data|llm_astrology_input_v1|assembly|renderer|messages provider" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC6:
  `rg -n "facts|signals|limits|shaping|evidence|provenance" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC7:
  `rg -n "persona|astrologue|developer prompt|PromptAssemblyConfig|compose_persona_block" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC8:
  `rg -n "hard policy|non-invention|validation|repair|rejection|no provider call" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC9:
  `rg -n "system_core|developer prompt|payload user|provider parameters" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC10:
  `rg -n "prompt-visible|backend-only|projection_hash|llm_input_hash" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC10b:
  `rg -n "provider_response|chart_json|natal_data" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC11:
  `rg -n "natal-prompt-construction-by-plan|CS-356" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- VC12:
  `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend/src'], text=True); assert out.strip()==''"`
- VC13:
  `python -c "from pathlib import Path; r=Path('_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence'); assert (r/'validation.txt').exists()"`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `pytest -q`

## Regression Risks

- Risk: diagrams are decorative but omit a source boundary.
  - Mitigation: each mandatory diagram has an AC and source-backed `rg` validation.
- Risk: backend-only data is drawn as prompt-visible.
  - Mitigation: AC9 and Reintroduction Guard require excluded fields in the diagram document.
- Risk: plan differences are drawn as separate calculation pipelines.
  - Mitigation: AC3 requires all plans and the story states shared calculations before plan divergence.
- Risk: a provider call is implied by the diagrams.
  - Mitigation: AC10 requires a no-provider-call statement and the no-call boundary.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Keep Mermaid labels short and ASCII.
- Do not modify backend runtime, frontend UI, tests, migrations, prompt definitions, output schemas, or provider integrations.
- Do not execute real LLM calls.
- Store command outputs in the CS-357 evidence directory.

## References

- `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
