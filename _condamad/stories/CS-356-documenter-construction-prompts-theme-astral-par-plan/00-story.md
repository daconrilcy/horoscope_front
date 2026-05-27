# Story CS-356 documenter-construction-prompts-theme-astral-par-plan: Document Natal Prompt Construction By Plan
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-356-documenter-construction-prompts-theme-astral-par-plan.md`.
- Selected mode: Repo-informed story, because the document must cite current audits, backend owners, symbols, and source-aligned limits.
- Source problem: CS-350 maps the general prompt generation flow, but no operational document explains natal prompt construction by `free`, `basic`, and `premium` plans.
- Source stakes:
  - Product and engineering readers must understand the exact prompt-visible data boundary for each plan.
  - The document must distinguish backend-only, validation-only, audit-only, and prompt-visible data without speculation.
  - Persona assembly, hard policy, non-invention limits, output validation, repair, rejection, and provider handoff must be separated.
  - Unknown prompt text stored in runtime configuration must be marked as a runtime extraction item, not invented.
- Source-alignment evidence: the objective, ACs, tasks, files, validation plan, non-goals, and guardrails preserve every mandatory brief section.

## Objective

Create a source-aligned documentation page that explains how natal theme prompts are constructed for `free`, `basic`, and `premium` plans.

The document must cover the path from data received by the prompt process to the compiled provider payload, including persona assembly, safety,
plan shaping, prompt-visible blocks, excluded data, output validation, and rejection.

## Target State

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` exists as the dedicated natal prompt construction document.
- The document contains the fifteen mandatory sections listed by the source brief.
- The document explains `free`, `basic`, and `premium` prompt construction with plan-specific tables.
- The document cites code paths, symbols, audits, prior stories, and source blockers for each major technical statement.
- The document states that no provider LLM call was performed.
- Backend runtime, frontend UI, database schema, prompt seeds, output schemas, and provider integration remain unchanged.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-356-documenter-construction-prompts-theme-astral-par-plan.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-356`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - CS-350 current cartography exists.
- Evidence 5: `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md` - one CS-343 audit artifact exists.
- Evidence 6: `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md` - one CS-344 audit artifact exists.
- Evidence 7: `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md` - one CS-345 audit artifact exists.
- Evidence 8: `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md` - one CS-346 audit artifact exists.
- Evidence 9: `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md` - one CS-347 audit artifact exists.
- Evidence 10: `backend/app/domain/llm/runtime/gateway.py` - current `LLMGateway` owner exists.
- Evidence 11: `backend/app/domain/llm/prompting/prompt_renderer.py` - current `PromptRenderer` owner exists.
- Evidence 12: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and resolved IDs only.

## Domain Boundary

- Domain: documentation
- In scope:
  - Documentation under `_condamad/docs/prompt-generation-cartography/`.
  - Natal theme prompt construction for `free`, `basic`, and `premium`.
  - Source traceability to CS-350, CS-343 to CS-347 audits, CS-320, CS-330 to CS-342, and current backend LLM owners.
  - Matrices for prompt-visible, backend-only, validation-only, and audit-only data.
  - Safety, non-invention, persona assembly, provider message composition, validation, repair, rejection, and residual risks.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, prompt seed changes, output schema changes, and provider calls.
  - Runtime code changes, generated JSON examples, full Mermaid schema production, and product plan changes.
- Explicit non-goals:
  - No runtime behavior change.
  - No prompt text rewrite.
  - No output schema modification.
  - No real LLM call.
  - No frontend route, screen, client generation, or UI validation.

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

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this source-aligned documentation contract for natal prompt construction.
- Behavior change allowed: no
- Behavior change constraints:
  - Create the dedicated documentation page only.
  - Create story execution evidence only.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: mandatory source artifacts contradict each other and no source-aligned conclusion can be written.
- Additional validation rules:
  - `AST guard` or bounded `git status` evidence must prove no application source was modified.
  - `python` path checks must prove the documentation and persistent evidence artifacts exist.
  - `rg` evidence must prove the required plan, persona, safety, source-owner, and exclusion terms are present.
  - The document must mark unknown runtime prompt text as `a extraire depuis la configuration runtime`.
  - The document must state that no provider LLM call was performed.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Current docs, audits, stories, and backend owners are source evidence for documentation. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta. |
| Ownership Routing | yes | Documentation belongs under `_condamad/docs`, not backend runtime or frontend code. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-only story. |
| Contract Shape | yes | The markdown document has required sections, matrices, source citations, and verification notes. |
| Batch Migration | no | No multi-file conversion is in scope. |
| Reintroduction Guard | yes | Backend-only and audit-only data must not be described as prompt-visible. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The dedicated document exists. | Evidence profile: baseline_before_after_diff; `python` checks the markdown path. |
| AC2 | All mandatory sections are present. | Evidence profile: json_contract_shape; `python` checks the heading list. |
| AC3 | Each plan has a clear section. | Evidence profile: json_contract_shape; `rg -n "free|basic|premium"` checks the document. |
| AC4 | The prompt journey is complete. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks process, provider, payload terms. |
| AC5 | Injected data is classified. | Evidence profile: json_contract_shape; `rg` checks `facts`, `signals`, `limits`, `shaping`, `evidence`. |
| AC6 | Persona assembly is explained. | Evidence profile: baseline_before_after_diff; `rg` checks `persona`, `astrologue`, and assembly owners. |
| AC7 | Safety controls are separated. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks hard policy, non-invention, validation, rejection. |
| AC8 | Prompt exclusions are explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `provenance`, hashes, provider response, observability. |
| AC9 | Important claims cite sources. | Evidence profile: ast_architecture_guard; `rg` checks backend paths, audit paths, and key symbols. |
| AC10 | No real LLM call is claimed. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks the no-provider-call statement. |
| AC11 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks `git status --short -- backend/app backend/tests frontend/src`. |
| AC12 | Persistent evidence is stored. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-350 and the five prompt-generation audit artifacts before drafting the document. (AC: AC4, AC9)
- [ ] Task 2: Read CS-320 and CS-330 to CS-342 story contracts for plan and LLM input boundaries. (AC: AC3, AC5, AC8)
- [ ] Task 3: Inspect the backend owners named in the source brief and record cited symbols in source evidence. (AC: AC6, AC9)
- [ ] Task 4: Create `natal-prompt-construction-by-plan.md` with the fifteen mandatory sections. (AC: AC1, AC2)
- [ ] Task 5: Add plan matrices for prompt-visible blocks, backend-only data, validation-only data, and audit-only data. (AC: AC3, AC5, AC8)
- [ ] Task 6: Document persona assembly, developer prompt composition, hard policy, non-invention limits, validation, repair, and rejection. (AC: AC6, AC7)
- [ ] Task 7: Mark unknown prompt text as runtime configuration extraction work instead of inventing exact text. (AC: AC9, AC10)
- [ ] Task 8: Run validation commands and persist command output in the CS-356 evidence directory. (AC: AC11, AC12)

## Files to Inspect First

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/stories/CS-330-llm-astrology-input-v1-contract/00-story.md`
- `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/00-story.md`
- `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/00-story.md`
- `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/00-story.md`
- `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/00-story.md`
- `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/00-story.md`
- `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/00-story.md`
- `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/00-story.md`
- `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/00-story.md`
- `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/00-story.md`
- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/00-story.md`
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/00-story.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`

## Runtime Source of Truth

- Primary source of truth:
  - CS-350 current cartography, CS-343 to CS-347 audits, CS-320, CS-330 to CS-342, and current backend source owners.
  - `AST guard` or bounded status evidence confirms no backend runtime file changed for this documentation-only story.
- Secondary evidence:
  - Targeted `rg` scans over the produced document and source evidence.
  - Source evidence file with cited paths, symbols, unknown runtime text, and blockers.
- Static scans alone are not sufficient for this story because:
  - The document must explain source-supported behavior and mark unknown prompt text without inventing it.

## Contract Shape

- Contract type:
  - Markdown documentation contract with plan matrices and source citations.
- Fields:
  - `section`: mandatory documentation section from the source brief.
  - `plan`: one of `free`, `basic`, or `premium`.
  - `prompt visibility`: `prompt-visible`, `backend-only`, `validation-only`, or `audit-only`.
  - `source`: code path, symbol, audit artifact, story, or explicit source blocker.
  - `verification`: deterministic command or manual bounded check.
- Required fields:
  - `section`
  - `plan`
  - `prompt visibility`
  - `source`
  - `verification`
- Required sections:
  - `Executive summary`
  - `Scope: theme astral natal, plans free, basic, premium`
  - `Vocabulaire: prompt-visible, backend-only, validation-only, audit-only`
  - `Point de depart: donnees recues par le process de prompt`
  - `Construction de llm_astrology_input_v1`
  - `Matrice des donnees injectees par bloc et par plan`
  - `Resolution use case, assembly, placeholders et plan rules`
  - `Introduction de l'astrologue/persona`
  - `Construction de la securite et des limites`
  - `Composition finale des messages provider`
  - `Frontiere exacte avant handoff provider`
  - `Differences free / basic / premium`
  - `Chemins non nominaux, repair, fallback et rejet`
  - `Tests et commandes de verification`
  - `Risques residuels et questions ouvertes`
- Optional fields:
  - A small diagram only inside the main document, limited to clarifying the prompt construction path.
- Status codes:
  - none; no HTTP route or API behavior is in scope.
- Serialization names:
  - Matrix labels are emitted as documentation headings and table cells, not as generated schema.
- Frontend type impact:
  - none; no frontend generated client or UI surface is in scope.
- Generated contract impact:
  - none; this story creates human documentation, not OpenAPI, JSON examples, or generated frontend contracts.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/docs-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/docs-after.txt`
- Expected invariant:
  - The only intended repository surface delta is the new documentation file plus CS-356 evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal prompt construction documentation | `_condamad/docs/prompt-generation-cartography/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/` | `_condamad/docs/**` |
| Runtime prompt behavior | Existing backend LLM modules | `_condamad/docs/**` |
| Frontend behavior | Existing frontend owners | `_condamad/docs/**` |

## Mandatory Reuse / DRY Constraints

- Reuse CS-350 and CS-343 to CS-347 artifacts as the evidence base instead of repeating their full contents.
- Cite CS-320 and CS-330 to CS-342 for plan, input, provenance, evidence, and non-invention boundaries.
- Reference source paths and symbols instead of copying long code excerpts.
- Keep one dedicated document for natal prompt construction by plan.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be documented as an authorized prompt-visible input.
- No compatibility prompt carrier may be documented as an authorized prompt-visible input.
- No fallback prompt path may replace missing source evidence.
- Do not describe `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, provider response, or observability as prompt-visible.
- Do not modify backend runtime, frontend UI, database migrations, prompt definitions, provider integrations, or output schemas.

## Reintroduction Guard

- Guarded boundaries:
  - `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, provider response, and observability stay outside prompt-visible payload.
  - Unknown prompt text is documented as `a extraire depuis la configuration runtime`.
  - Plan differences are documented as prompt-visible data, depth, sections, and budget shaping, not backend calculation removal.
- Required deterministic guards:
  - `rg` must find `prompt-visible`, `backend-only`, `validation-only`, and `audit-only` in the final document.
  - `rg` must find `projection_hash`, `llm_input_hash`, `provider response`, and `observability` in the final document.
  - `python` or `git status` must prove application source surfaces are unchanged.

## Regression Guardrails

Scope vector: operation `create`, domain `documentation`, paths `_condamad/docs/prompt-generation-cartography`,
`backend/app/domain/llm`, `backend/app/domain/astrology/interpretation`, contracts `source-aligned-documentation` and `prompt-construction`.

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend ownership must not drift into docs or API files. | `python` status guard; source `rg`. |
| RG-149 `CS-350` | Keep legacy carriers and non-natal flows outside the natal prompt contract. | `rg` exclusions and manual review. |
| RG-041 non-applicable | Entitlement documentation is outside this prompt construction scope. | Manual check: plan docs only. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/guardrails.txt` | Keep resolved scope evidence. |
| Baseline scan | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/docs-baseline.txt` | Keep pre-documentation scan evidence. |
| After scan | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/docs-after.txt` | Keep post-documentation scan evidence. |
| Source coverage map | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/source-coverage.md` | Track sources and blockers. |
| Validation output | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/validation.txt` | Keep validation command output. |
| Review output | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/generated/11-code-review.md` | Keep automatic review output. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - final documentation deliverable.
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/guardrails.txt` - resolver output.
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/docs-baseline.txt` - baseline scan.
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/docs-after.txt` - after scan.
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/source-coverage.md` - source coverage.
- `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/validation.txt` - validation output.

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

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md').exists()"`
- VC2:
  `python -c "from pathlib import Path; p=Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md'); assert 'Executive summary' in p.read_text()"`
- VC3:
  `rg -n "free|basic|premium|persona|astrologue|hard policy|non-invention" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC3a:
  `rg -n "prompt-visible|backend-only" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC3b:
  `rg -n "LLMGateway|PromptRenderer|llm_astrology_input_v1" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC4:
  `rg -n "chart_json|natal_data|evidence|provenance|projection_hash|llm_input_hash" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC5:
  `rg -n "validation-only|audit-only|provider response|observability" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC5b:
  `rg -n "a extraire depuis la configuration runtime" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC6:
  `rg -n "canonical_use_case_registry.py|assembly_resolver.py|prompt_renderer.py|gateway.py" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC6b:
  `rg -n "interpretation_service.py" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- VC7:
  `python -c "from pathlib import Path; r=Path('_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence'); assert r.exists()"`
- VC7b:
  `python -c "from pathlib import Path; r=Path('_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence'); assert (r/'validation.txt').exists()"`
- VC8: `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend/src'], text=True); assert out.strip()==''"`
- VC9: `ruff format .`
- VC10: `ruff check .`
- VC11: `pytest -q`

## Regression Risks

- Risk: the document invents exact prompt text that lives in runtime configuration.
  - Mitigation: unknown prompt text must be marked as runtime extraction work and cited to the resolution owner.
- Risk: plan differences are described as backend calculation removal.
  - Mitigation: the document must state that all plans preserve backend calculations and interpretations.
- Risk: backend-only audit data is described as prompt-visible.
  - Mitigation: AC8 and the Reintroduction Guard require explicit exclusion terms.
- Risk: documentation drifts away from source audits.
  - Mitigation: each important technical claim must cite a code path, symbol, audit, story, or blocker.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Keep documentation citations path-based and concise.
- Do not modify backend runtime, frontend UI, tests, migrations, prompt definitions, output schemas, or provider integrations.
- Do not execute real LLM calls.
- Store command outputs in the CS-356 evidence directory.

## References

- `_story_briefs/cs-356-documenter-construction-prompts-theme-astral-par-plan.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
