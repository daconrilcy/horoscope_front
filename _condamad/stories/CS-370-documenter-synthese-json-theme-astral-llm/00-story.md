# Story CS-370 documenter-synthese-json-theme-astral-llm: Document Theme Astral LLM JSON Structure
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-370-documenter-synthese-nouvelle-structure-json-theme-astral-llm.md`.
- Selected mode: Repo-informed story, because the document must cite architecture, sibling stories, backend owners, and source gaps.
- Source problem: the final `theme_astral` LLM JSON contract needs one maintainable synthesis document after CS-363 to CS-369.
- Source stakes:
  - Developers, product owners, and prompt editors must understand the JSON without reading code.
  - The document must separate common skeleton, `delivery_profile` variation, LLM-visible data, and backend-only data.
  - Commercial plan labels must not be described as LLM payload data.
  - Interpretation text provenance and astrologer voice boundaries must stay clear.
  - CS-371 must be identified as the owner of complete JSON examples by profile.
- Source-alignment evidence: PASS. Objective, ACs, tasks, files, validation, non-goals, and guardrails map to the brief.

## Objective

Create the reference document for the new `theme_astral` JSON structure sent to the LLM.

The document must explain the canonical skeleton, every block role, source, visibility rule, delivery profile variation, output contract,
and Mermaid construction diagrams without modifying runtime code or generating complete per-profile payloads.

## Target State

- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` exists.
- The document contains the ten mandatory sections requested by the source brief.
- The canonical skeleton includes `runtime_contract`, `safety_contract`, `astrologer_voice`, `feature_context`, and `delivery_profile`.
- The canonical skeleton includes `input_data.birth_context`, `input_data.astrological_facts`, `input_data.interpretation_material`,
  `input_data.selected_themes`, `input_data.limits`, and `output_contract`.
- Every block has a description, source, and visibility rule.
- The document explains that `delivery_profile` is resolved by backend logic and that commercial plan labels stay backend-only.
- The document explains that table-backed interpretation texts remain source-traceable on the backend side.
- The document explains that `astrologer_voice` influences style, tone, emphasis, and lexicon only.
- Two Mermaid diagrams cover JSON construction and the backend-only versus LLM-visible boundary.
- The document links CS-371 as the owner of complete payload examples.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-370-documenter-synthese-nouvelle-structure-json-theme-astral-llm.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-370`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture story read.
- Evidence 5: `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md` - review story read.
- Evidence 6: `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md` - prior documentation pattern read.
- Evidence 7: `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md` - Mermaid documentation pattern read.
- Evidence 8: targeted `rg` checked backend domain, services, ops, and tests for LLM input and output contract terms.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped `resolve_guardrails.py` output.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract` is absent in this workspace.
- Repository structure alert: `_condamad/audits/theme-astral-prompt-contract` is absent in this workspace.
- Repository structure alert: implementation must create missing source paths only when upstream stories actually produce them.
- Registry gap: no exact guardrail covers documentation of `theme_astral` LLM JSON skeleton synthesis.
- Assumption risk: CS-364 to CS-369 may still be `ready-to-dev`; implementation must verify final artifacts before citing final behavior.

## Domain Boundary

- Domain: documentation
- In scope:
  - Documentation under `_condamad/docs/prompt-generation-cartography/`.
  - Synthesis of the `theme_astral` LLM JSON structure after CS-363 to CS-369.
  - Read-only inspection of architecture, audit, backend domain, backend services, backend ops, and backend tests.
  - Canonical skeleton, block descriptions, block sources, visibility rules, and delivery profile variation.
  - Mermaid diagrams for JSON construction and backend-only versus LLM-visible boundaries.
  - Links toward CS-371 complete examples without producing those examples.
- Out of scope:
  - Backend runtime edits, database contracts, migrations, frontend UI, auth, i18n, styling, build tooling, and provider calls.
  - Full payload generation by commercial plan.
  - Prompt text rewrite, output schema rewrite, or guardrail registry maintenance.
- Explicit non-goals:
  - No runtime behavior change.
  - No complete per-profile JSON payload.
  - No commercial plan label emitted as LLM data.
  - No real LLM call.
  - No frontend route, screen, client generation, or UI validation.

Named brief primitives in scope:

- `runtime_contract`
- `safety_contract`
- `astrologer_voice`
- `feature_context`
- `delivery_profile`
- `input_data.birth_context`
- `input_data.astrological_facts`
- `input_data.interpretation_material`
- `input_data.selected_themes`
- `input_data.limits`
- `output_contract`
- Mermaid construction diagram
- Mermaid backend-only and LLM-visible boundary diagram
- CS-371 complete examples link

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this source-aligned documentation contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create or update only the target documentation page.
  - Create story execution evidence only.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep migrations unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: upstream CS-364 to CS-369 artifacts contradict the CS-363 target skeleton.
- Additional validation rules:
  - `AST guard` or bounded `git status` evidence must prove no application source was modified.
  - `python` path checks must prove the documentation and persistent evidence artifacts exist.
  - `rg` evidence must prove every canonical skeleton key is present.
  - `rg` evidence must prove plan labels are not described as LLM payload data.
  - `python` or `rg` evidence must prove exactly two required Mermaid diagram themes are present.
  - The document must state that no provider LLM call was performed.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | CS-363 to CS-369, backend owners, `AST guard`, and `rg` prove documentation claims. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is documentation evidence. |
| Ownership Routing | yes | The synthesis belongs under `_condamad/docs`, not runtime, tests, migrations, or frontend code. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only story. |
| Contract Shape | yes | The markdown document has required sections, skeleton keys, block tables, diagrams, and source citations. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Plan labels and backend-only proof data must not be documented as LLM-visible payload data. |
| Persistent Evidence | yes | Source scans, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The synthesis document exists. | Evidence profile: baseline_before_after_diff; `python` checks the markdown path. |
| AC2 | All mandatory sections are present. | Evidence profile: json_contract_shape; `python` checks the heading list. |
| AC3 | The canonical skeleton is documented. | Evidence profile: json_contract_shape; `rg` checks all JSON skeleton keys. |
| AC4 | Every block has source evidence. | Evidence profile: json_contract_shape; `python` parses block table rows. |
| AC5 | Delivery profile variation is explained. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `delivery_profile` and backend resolution terms. |
| AC6 | Commercial plan labels stay backend-only. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks plan-label boundary terms. |
| AC7 | Interpretation material provenance is explicit. | Evidence profile: ast_architecture_guard; `rg` checks table-backed source and traceability terms. |
| AC8 | Astrologer voice is style-only. | Evidence profile: json_contract_shape; `rg` checks style, tone, emphasis, lexicon, and facts boundary. |
| AC9 | Two Mermaid diagrams are present. | Evidence profile: json_contract_shape; `python` counts fenced Mermaid blocks and required titles. |
| AC10 | CS-371 example ownership is linked. | Evidence profile: baseline_before_after_diff; `rg` checks `CS-371` and complete examples wording. |
| AC11 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC12 | Persistent evidence is stored. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |
| AC13 | Every block has a visibility rule. | Evidence profile: json_contract_shape; `python` parses block table rows. |

## Implementation Tasks

- [ ] Task 1: Read CS-363 architecture and CS-364 to CS-369 final story or generated artifacts before drafting. (AC: AC3, AC5)
- [ ] Task 2: Inspect backend domain, services, ops, and tests for final skeleton owner evidence. (AC: AC4, AC7)
- [ ] Task 3: Create `theme-astral-llm-json-structure-v1.md` with the ten mandatory sections. (AC: AC1, AC2)
- [ ] Task 4: Document the canonical JSON skeleton and each top-level block role. (AC: AC3, AC4)
- [ ] Task 5: Document backend-only, LLM-visible, audit-only, and source-traceable boundaries. (AC: AC4, AC6, AC7, AC13)
- [ ] Task 6: Document `delivery_profile` variation without exposing commercial plan labels as LLM data. (AC: AC5, AC6)
- [ ] Task 7: Document `astrologer_voice` as style-only influence over wording, not facts. (AC: AC8)
- [ ] Task 8: Add the two Mermaid diagrams with short labels and source notes. (AC: AC9)
- [ ] Task 9: Add the CS-371 link section for complete examples without generating payloads. (AC: AC10)
- [ ] Task 10: Run validation commands, persist command output, and prove protected sources remain unchanged. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-370-documenter-synthese-nouvelle-structure-json-theme-astral-llm.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md`
- `_condamad/architecture/theme-astral-prompt-contract/` - expected implementation-created source path.
- `_condamad/audits/theme-astral-prompt-contract/` - expected implementation-created source path.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- `_condamad/examples/prompt-generation-cartography/` - existing examples family and CS-371 reference context.
- `backend/app/domain/**`
- `backend/app/services/**`
- `backend/app/ops/**`
- `backend/tests/**`

## Runtime Source of Truth

- Primary source of truth:
  - CS-363 architecture, CS-364 to CS-369 final artifacts, and current backend source owners.
  - `AST guard` or bounded `git status` evidence confirms no backend runtime file changed for this documentation-only story.
  - Targeted `rg` traces prove the named skeleton keys and owner terms.
- Secondary evidence:
  - Source evidence file listing inspected stories, backend paths, absent upstream artifacts, and accepted assumptions.
  - Targeted scans over the produced document for required sections, keys, boundaries, and diagram blocks.
- Static scans alone are not sufficient for this story because:
  - Documentation claims must map to upstream contracts and source owners, not only to words inside the new page.

## Contract Shape

- Contract type:
  - Markdown reference document for `theme_astral` LLM JSON structure.
- Fields:
  - `section`: mandatory documentation section from the source brief.
  - `json block`: canonical skeleton block or nested block.
  - `role`: concise purpose of the block.
  - `source`: architecture, audit, backend owner, story, or accepted source gap.
  - `visibility`: `LLM-visible`, `backend-only`, `audit-only`, or `source-traceable backend`.
  - `profile variation`: how `delivery_profile` changes density, quantity, budgets, or response depth.
  - `verification`: deterministic command or manual bounded check.
- Required fields:
  - `section`
  - `json block`
  - `role`
  - `source`
  - `visibility`
  - `verification`
- Required sections:
  - `Resume executif`
  - `Principes de construction`
  - `Frontiere backend-only / LLM-visible`
  - `Squelette JSON canonique`
  - `Description des blocs`
  - `Variations par delivery profile`
  - `Contrat de retour demande au LLM`
  - `Diagrammes Mermaid`
  - `Checklist de validation`
  - `Liens vers les exemples complets CS-371`
- Optional fields:
  - none for the required block table.
- Status codes:
  - none; no API route behavior is created by this story.
- Serialization names:
  - JSON keys must be documented exactly as emitted by the target contract.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; the story documents the final contract and does not generate payload examples.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/docs-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/docs-after.txt`
- Expected invariant:
  - The only intended surface delta is the target documentation page plus CS-370 evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| JSON structure synthesis | `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` | `backend/app/**` |
| Source evidence | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/source-coverage.md` | Runtime code comments |
| Validation evidence | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/validation.txt` | Untracked console output |
| Complete payload examples | CS-371 story and examples path | CS-370 synthesis document |
| Backend contract owners | Existing backend domain, service, ops, and test paths | New parallel documentation code owner |

## Mandatory Reuse / DRY Constraints

- Reuse CS-363 architecture vocabulary for the target skeleton instead of inventing a second contract name.
- Reuse CS-364 to CS-369 final artifacts as source evidence once they exist.
- Reuse existing prompt-generation cartography documentation style under `_condamad/docs/prompt-generation-cartography/`.
- Reuse existing backend owner paths in citations instead of copying source logic into the document.
- Keep one canonical synthesis page for this JSON structure.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be presented as the canonical `theme_astral` JSON structure.
- No compatibility documentation path may be created for the same synthesis.
- No fallback documentation page may be created for the same synthesis.
- Do not describe `free`, `basic`, or `premium` as LLM payload plan labels.
- Do not place complete profile payload examples in this story.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard exact tokens:
  - `free.*LLM`
  - `basic.*LLM`
  - `premium.*LLM`
  - `chart_json`
  - `natal_data`
  - `{{`
  - `TODO`
  - `TBD`
- Required guard evidence:
  - `rg -n "\{\{|TODO|TBD|free.*LLM|basic.*LLM|premium.*LLM" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
  - `rg -n "chart_json|natal_data" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- Expected result:
  - Placeholder and plan-label scans produce no match.
  - Old-carrier terms appear only in a bounded backend-only warning when the final source evidence requires them.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 validation plans | Prompt-generation documentation must keep validation evidence explicit. | `rg` validation checks; persisted evidence. |
| RG-002 backend layout | Backend sources are read-only evidence and must not receive doc content. | `python` bounded git status check. |
| Registry gap | No exact guardrail covers this `theme_astral` JSON synthesis page. | Resolver output saved in evidence. |

Non-applicable example:

- RG-041 entitlement documentation is outside scope because this story does not touch entitlement or frontend build surfaces.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source coverage | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/source-coverage.md` | List inspected sources and gaps. |
| Guardrail resolver output | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/guardrails.txt` | Keep scoped guardrail selection. |
| Baseline snapshot | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/docs-baseline.txt` | Record target doc state before work. |
| After snapshot | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/docs-after.txt` | Record target doc state after work. |
| Validation output | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/validation.txt` | Store validation command output. |
| Review output | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - create the synthesis document.
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/source-coverage.md` - persist source coverage.
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/guardrails.txt` - persist guardrail resolver output.
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/docs-baseline.txt` - persist before snapshot.
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/docs-after.txt` - persist after snapshot.
- `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/validation.txt` - persist validation output.

Likely tests:

- No new automated runtime test is expected for documentation-only work.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - targeted `python` and `rg` checks are required.

Files not expected to change:

- `backend/app/**` - out of scope; backend runtime is read-only evidence.
- `backend/tests/**` - out of scope; tests are read-only evidence for this story.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence contract is changed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md').exists()"`
- VC2: `python` counts at least two fenced Mermaid blocks in the target document.
- VC3: `rg -n "theme_astral_llm_input_v1|runtime_contract|safety_contract|astrologer_voice" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- VC4: `rg -n "delivery_profile|interpretation_material|output_contract" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- VC5: `rg -n "\{\{|TODO|TBD|free.*LLM|basic.*LLM|premium.*LLM" _condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- VC6: `python -c "import subprocess as s; assert not s.getoutput('git status --short -- backend/app backend/tests')"`
- VC7: `python -c "import subprocess as s; assert not s.getoutput('git status --short -- frontend/src')"`
- VC8: `python -c "from pathlib import Path as P; assert P('_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence/source-coverage.md').exists()"`
- VC9: `python -c "from pathlib import Path; base=Path('_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/evidence'); assert (base / 'validation.txt').exists()"`
- VC10: `ruff format .`
- VC11: `ruff check .`
- VC12: `pytest -q`

## Regression Risks

- The document may become too abstract and fail to serve as a maintenance reference.
- Upstream CS-364 to CS-369 may still be unimplemented, leaving source gaps that must be stated rather than invented.
- Complete examples may drift into CS-370 despite CS-371 owning that deliverable.
- Plan labels may be worded in a way that suggests they are sent to the LLM.
- Mermaid diagrams may imply backend-only data crosses the LLM boundary.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Read source artifacts first and record missing source directories in `source-coverage.md`.
- Keep documentation concise but concrete enough for developers, product owners, and prompt editors.
- Do not generate complete per-profile payloads; link CS-371 as their owner.
- Persist all validation outputs under the CS-370 evidence directory.

## References

- `_story_briefs/cs-370-documenter-synthese-nouvelle-structure-json-theme-astral-llm.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- `_condamad/stories/regression-guardrails.md`
