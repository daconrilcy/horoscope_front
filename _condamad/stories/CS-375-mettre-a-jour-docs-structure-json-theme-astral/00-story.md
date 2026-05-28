# Story CS-375 mettre-a-jour-docs-structure-json-theme-astral: Update Theme Astral JSON Structure Documentation
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-375-mettre-a-jour-docs-structure-json-theme-astral-apres-corrections.md`.
- Selected mode: Repo-informed story, because the documentation must align with corrected stories, backend source, examples, and reports.
- Source problem: the `theme_astral` JSON structure documentation still contains obsolete future wording about CS-371.
- Source stakes:
  - User impact: maintainers need one final document that agrees with the corrected profile, birth context, and example artifacts.
  - Technical risk: documentation can validate the previous plan instead of the corrected runtime and example contract.
  - Closure expectation: docs, example links, Mermaid diagrams, and delivery report status must stop contradicting CS-371 to CS-374.
  - Forbidden regression: no backend code, payload regeneration, new architecture, or guardrail registry maintenance is authorized.
- Source-alignment evidence: PASS. Objective, ACs, tasks, files, validation, non-goals, and guardrails map to the source brief.

## Objective

Update the `theme_astral` JSON structure documentation so it matches the corrected implementation contract, persisted profiles,
structured birth context, regenerated examples, interpretation source status, and delivery-report history.

## Target State

- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` contains no obsolete future wording about CS-371.
- The document describes `essential`, `expanded`, and `complete` consistently with provider and persisted profile intent.
- `input_data.birth_context` is documented with structured fields such as `birth_date`, `birth_time_local`, and `birth_place`.
- Interpretation sources are described as production, production-like, or mixed according to the final example artifacts.
- Links to the CS-371 Paris examples point to existing provider payloads, README, and structure comparison files.
- Mermaid diagrams remain conceptually consistent with the documented JSON shape and backend-only boundary.
- Example README and `structure-comparison.md` are updated only when the JSON structure document references stale example wording.
- The CS-361 to CS-371 delivery report is updated or explicitly classified as historical when corrected stories supersede it.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-375-mettre-a-jour-docs-structure-json-theme-astral-apres-corrections.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-375` after `CS-374`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/00-story.md` - profile correction story read.
- Evidence 5: `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/00-story.md` - birth context story read.
- Evidence 6: `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/00-story.md` - examples correction story read.
- Evidence 7: `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - targeted scan found obsolete CS-371 wording.
- Evidence 8: `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` - targeted scan found provider payload source terms.
- Evidence 9: `backend/app/domain/llm/configuration/theme_astral_contracts.py` - targeted scan found profile contract terms.
- Evidence 10: `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` - example profile terms found.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped `resolve_guardrails.py` output.
- Repository structure alert: required backend, frontend, `_condamad`, docs, examples, architecture, and report roots exist in this workspace.
- Registry gap: no exact guardrail covers post-correction `theme_astral` JSON documentation reconciliation.

## Domain Boundary

- Domain: documentation
- In scope:
  - `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`.
  - Example README and `structure-comparison.md` only for references made by the JSON structure document.
  - The CS-361 to CS-371 delivery report status note when corrected stories supersede its claims.
  - Read-only inspection of CS-372 to CS-374 stories, architecture, backend source, and CS-371 example artifacts.
  - Mermaid diagram conceptual validation inside the documentation.
- Out of scope:
  - Backend runtime edits, tests, database schema, migrations, frontend UI, auth, i18n, styling, build tooling, and provider calls.
  - Regenerating provider payload JSON examples.
  - Creating a new architecture or changing prompt assembly behavior.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No backend code modification.
  - No generated payload regeneration.
  - No new API route, frontend route, screen, client generation, or UI validation.
  - No claim that production-like fixtures are production data.

Named brief primitives in scope:

- `theme_astral`
- CS-371 examples
- CS-372 profile corrections
- CS-373 `birth_context`
- CS-374 interpretation source corrections
- `essential`
- `expanded`
- `complete`
- `birth_date`
- `birth_time_local`
- `birth_place`
- `production`
- `production-like`
- `mixed`
- Mermaid diagrams
- `structure-comparison.md`
- CS-361 to CS-371 delivery report

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits post-correction documentation reconciliation.
- Behavior change allowed: no
- Behavior change constraints:
  - Update only documentation, report status wording, and story evidence artifacts in scope.
  - Keep backend application files unchanged.
  - Keep backend tests unchanged.
  - Keep frontend files unchanged.
  - Keep generated provider payload JSON files unchanged.
  - Keep guardrail registry unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: corrected source artifacts contradict each other on profile names, birth fields, or source status.
- Additional validation rules:
  - `AST guard` or bounded `git status` evidence must prove protected source surfaces were not modified.
  - `rg` evidence must prove obsolete future wording about CS-371 is absent from the target document.
  - `rg` evidence must prove profile, birth context, example link, and source-status terms are present.
  - `python` evidence must prove the target document and persistent evidence artifacts exist.
  - `Manual check:` evidence must record conceptual Mermaid verification for the scoped document.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Backend source, corrected stories, `AST guard`, and `rg` prove documentation claims. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is scoped documentation evidence. |
| Ownership Routing | yes | JSON structure docs, examples docs, report notes, and backend source have separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation update. |
| Contract Shape | yes | The markdown document must contain exact corrected sections, links, terms, and source-status wording. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Obsolete future wording, placeholders, stale `deep`, and source-status ambiguity must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Obsolete CS-371 future wording is absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans the target doc. |
| AC2 | Canonical depths are documented. | Evidence profile: json_contract_shape; `rg` checks `essential`, `expanded`, and `complete`. |
| AC3 | Structured birth context is documented. | Evidence profile: json_contract_shape; `rg` checks `birth_date`, `birth_time_local`, and `birth_place`. |
| AC4 | Interpretation source status is explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks production and production-like labels. |
| AC5 | CS-371 example links are exact. | Evidence profile: baseline_before_after_diff; `python` checks referenced example paths. |
| AC6 | Mermaid diagrams remain coherent. | Evidence profile: json_contract_shape; `python` counts Mermaid blocks; Manual check: JSON flow. |
| AC7 | No placeholder remains in scoped docs. | Evidence profile: targeted_forbidden_symbol_scan; `rg` rejects `TODO`, `TBD`, and template markers. |
| AC8 | Report status is historical or updated. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks report status wording. |
| AC9 | Protected application surfaces are unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded `git status` paths. |
| AC10 | Persistent evidence is stored. | Evidence profile: baseline_before_after_diff; `python` checks the CS-375 evidence directory. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-372, CS-373, CS-374, architecture, backend source, examples, and report before editing. (AC: AC2, AC3, AC4)
- [ ] Task 2: Capture a baseline scan for the target doc, example docs, and delivery report. (AC: AC1, AC5, AC8, AC10)
- [ ] Task 3: Remove obsolete future wording about CS-371 from the JSON structure document. (AC: AC1)
- [ ] Task 4: Align documented depths to `essential`, `expanded`, and `complete`. (AC: AC2)
- [ ] Task 5: Document `birth_context` with structured birth fields and visibility boundaries. (AC: AC3)
- [ ] Task 6: Document interpretation source status as production, production-like, or mixed. (AC: AC4)
- [ ] Task 7: Correct CS-371 example links in the JSON structure doc and update example docs only for referenced stale wording. (AC: AC5)
- [ ] Task 8: Verify Mermaid diagram concepts against the corrected JSON shape and record the manual check. (AC: AC6)
- [ ] Task 9: Update or classify the delivery report as historical after corrected stories. (AC: AC8)
- [ ] Task 10: Run scans, protected-surface checks, backend validation commands, and persist outputs. (AC: AC7, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-375-mettre-a-jour-docs-structure-json-theme-astral-apres-corrections.md`
- `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/00-story.md`
- `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/00-story.md`
- `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/00-story.md`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json`
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`

## Runtime Source of Truth

- Primary source of truth:
  - CS-372, CS-373, and CS-374 final implementation evidence once those stories are completed.
  - `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`.
  - `ThemeAstralProviderPayloadBuilder`.
  - `THEME_ASTRAL_INPUT_SCHEMA` and delivery profile constants in `theme_astral_contracts.py`.
  - CS-371 example payloads, README, and `structure-comparison.md`.
  - `AST guard` or bounded `git status` evidence for unchanged protected source surfaces.
- Secondary evidence:
  - Targeted `rg` scans for profile names, structured birth fields, source-status labels, example paths, placeholders, and report status.
- Static scans alone are not sufficient for this story because:
  - Documentation claims must map to corrected stories and backend owners, not only to words inside the edited markdown.

## Contract Shape

- Contract type:
  - Markdown documentation reconciliation for final `theme_astral` LLM JSON structure.
- Fields:
  - `delivery_profile`: canonical non-commercial depth documented as `essential`, `expanded`, or `complete`.
  - `birth_context`: structured provider-visible birth context block.
  - `birth_date`: documented birth date field.
  - `birth_time_local`: documented local time field.
  - `birth_place`: documented structured place field.
  - `interpretation_material`: documented source-traceable material block.
  - `source_status`: explicit production, production-like, or mixed classification.
  - `example_link`: exact relative path to CS-371 example artifacts.
  - `report_status`: updated or historical classification for the prior delivery report.
- Required fields:
  - `delivery_profile`
  - `birth_context`
  - `interpretation_material`
  - `source_status`
  - `example_link`
  - `report_status`
- Optional fields:
  - none newly authorized by this story.
- Status codes:
  - none; this documentation story does not define an HTTP response contract.
- Serialization names:
  - JSON keys must be documented exactly as emitted by the target contract.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; existing examples are referenced and not regenerated by this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/docs-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/docs-after.txt`
- Expected invariant:
  - The only intended surface delta is scoped documentation, report classification wording, and CS-375 evidence artifacts.
- Required proof:
  - Before and after artifacts must include targeted `rg` outputs for CS-371 wording, depths, birth fields, source labels, and placeholders.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| JSON structure documentation | `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` | `backend/app/**` |
| Example reference notes | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` | provider payload JSON |
| Example comparison notes | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` | backend tests |
| Historical report status | `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md` | runtime comments |
| Story execution evidence | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/**` | transient console output |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-372 profile vocabulary instead of introducing another depth naming model.
- Reuse the CS-373 structured `birth_context` names instead of documenting birth data as free text.
- Reuse CS-374 source-status vocabulary for production, production-like, and mixed sources.
- Reuse existing CS-371 example paths instead of creating duplicate example documentation.
- Keep one canonical JSON structure document for `theme_astral`.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy future statement may say CS-371 still has to be implemented.
- No compatibility documentation path may be created for the same JSON structure.
- No fallback wording may present `deep` as an active canonical depth.
- No generated provider payload JSON may be edited by this documentation story.
- No backend code comment may become the owner of the documentation reconciliation.
- No unresolved placeholder token may remain in scoped documentation.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard obsolete wording:
  - `rg` rejects `Quand CS-371 sera implemente` in the JSON structure document.
- Guard placeholders:
  - `rg` rejects `TODO`, `TBD`, and template markers in scoped docs.
- Guard active depth names:
  - `rg` proves `essential`, `expanded`, and `complete` in the JSON structure document and example comparison.
  - `rg` rejects unclassified active `deep` wording in the JSON structure document.
- Guard protected surfaces:
  - `python` bounded `git status` checks `backend/app`, `backend/tests`, `frontend/src`, and generated provider payloads.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend source is read-only evidence and must not receive documentation logic. | `python` bounded git status. |
| Registry gap | No exact guardrail covers post-correction `theme_astral` JSON documentation reconciliation. | Resolver output saved in evidence. |

Non-applicable examples retained to prevent scope drift:

- `RG-041` entitlement documentation is out of scope because no entitlement or security claim is touched.
- `RG-047` frontend inline styles is out of scope because no TSX or CSS surface is touched.
- `RG-052` frontend CSS namespaces is out of scope because no design-token or stylesheet migration is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/guardrails.txt` | Keep scoped guardrail selection. |
| Baseline snapshot | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/docs-baseline.txt` | Record scoped docs before work. |
| After snapshot | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/docs-after.txt` | Record scoped docs after work. |
| Mermaid check | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/mermaid-check.md` | Keep bounded manual diagram review. |
| Protected surface check | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/protected-surfaces.txt` | Prove runtime surfaces unchanged. |
| Validation output | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/validation.txt` | Store validation command output. |
| Review output | `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation update.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - reconcile final JSON structure documentation.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` - update only referenced stale notes.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` - update only referenced stale notes.
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md` - update or mark historical.
- `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/**` - validation handoff artifacts.
- `_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/generated/11-code-review.md` - review handoff.

Likely tests:

- No new automated runtime test is expected for documentation-only work.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md` - targeted `python` and `rg` checks are required.
- Targeted `rg`, `python`, backend `ruff`, and backend `pytest` commands are required.

Files not expected to change:

- `backend/app/**` - out of scope; backend runtime is read-only evidence.
- `backend/tests/**` - out of scope; tests are validation evidence only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is authorized.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json` - no payload regeneration.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.
Use `$doc = '_condamad\docs\prompt-generation-cartography\theme-astral-llm-json-structure-v1.md'`.
Use `$ex = '_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1'`.

- VC1: `rg -n "Quand CS-371 sera implemente|TODO|TBD|\{\{|\\bdeep\\b" $doc`
- VC2: `rg -n "expanded|complete|birth_date|birth_time_local|birth_place" $doc`
- VC3: `rg -n "1973-04-24-1100-paris-theme-astral-v1|free-provider-payload|basic-provider-payload|premium-provider-payload" $doc`
- VC4: `rg -n "production|production-like|mixed|mixte|source_ref|interpretation_material" $doc $ex\README.md $ex\structure-comparison.md`
- VC5: `python -c "from pathlib import Path as P; assert P('_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md').exists()"`
- VC6: `python` checks all relative example links referenced by the target document.
- VC7: `Manual check: Mermaid blocks in the target document match the documented JSON construction and boundary flow.`
- VC8: `python -c "import subprocess as s; assert not s.getoutput('git status --short -- backend/app backend/tests frontend/src backend/migrations')"`
- VC9: `python` checks provider payload JSON files are unchanged or only documented as out of scope in protected-surface evidence.
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-375-mettre-a-jour-docs-structure-json-theme-astral/evidence/validation.txt').exists()"`
- VC11: `ruff format .`
- VC12: `ruff check .`
- VC13: `pytest -q`

Interpretation rule:

- VC1 must return no result for obsolete future wording, placeholders, or unclassified active `deep` wording.
- VC2 and VC3 must find the expected documented fields and example links.
- VC4 must prove the source-status wording used by the documentation and examples.
- VC8 and VC9 must prove protected application and generated payload surfaces remain unchanged.

## Regression Risks

- Updating only the obsolete CS-371 phrase could leave profile, birth context, or source-status sections stale.
- Copying text from planned stories without checking backend source could document intended behavior as final behavior.
- Marking source fixtures as production could overstate example provenance.
- Editing generated payload JSON would hide documentation drift by changing the artifacts instead of the docs.
- Mermaid diagrams could keep the old data flow while prose changes.
- Delivery report wording could contradict the corrected final documentation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, pip, pytest, or ruff command.
- Read CS-372, CS-373, CS-374, backend owners, and example artifacts before editing docs.
- Keep generated provider payload JSON files unchanged.
- Persist all validation outputs under the CS-375 evidence directory.

## References

- `_story_briefs/cs-375-mettre-a-jour-docs-structure-json-theme-astral-apres-corrections.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-372-aligner-profils-livraison-theme-astral-db-provider/00-story.md`
- `_condamad/stories/CS-373-structurer-birth-context-theme-astral-llm-input/00-story.md`
- `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/00-story.md`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
