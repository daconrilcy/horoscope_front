# Story CS-353 audit-process-paralleles-generation-prompt-llm: Audit Parallel Legacy Prompt Generation Processes
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-353-audit-process-paralleles-legacy-generation-prompt-llm.md`.
- Source problem: prompt-generation documentation may hide active or older non-natal LLM prompt flows outside the modern natal flow.
- Source stakes:
  - Future agents must know whether guidance, public chat, daily horoscope, repair, seeds, and carrier paths can reach a provider.
  - Runtime active paths, non-nominal recovery, bootstrap, tests, admin-only samples, archival artifacts, and debt must stay distinct.
  - `chart_json`, `natal_data`, textual natal summaries, seeds, and fallback catalog paths must not be treated as harmless without proof.
  - The final CS-350 document must be amended later from a complete audit, not from assumptions about one gateway or one renderer.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a timestamped audit report that inventories every parallel, older, bootstrap, fallback, repair, test, admin, or non-nominal prompt flow.
The audit must classify provider capability and relationship to the modern natal flow without changing code, prompts, assemblies, seeds, or docs.

## Target State

- A report exists at `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`.
- Guidance, public chat, conversational guidance, daily horoscope, fallback catalog, no-assembly fallback, repair, and legacy carriers are explicit.
- Each process has one justified status: runtime active, runtime non nominal, recovery, bootstrap/seed, test-only, admin-only, archival, or debt.
- Each process records trigger, owner, configuration source, prompt-visible input, renderer or assembly, provider handoff, and modern natal boundary.
- Provider-capable paths are separated from seeds, tests, admin samples, archival artifacts, and documentation-only findings.
- The report identifies document gaps and candidate follow-up stories for documentation, guardrails, migration, tests, or decommission work.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-353-audit-process-paralleles-legacy-generation-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-353`.
- Evidence 3: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - final CS-350 document exists.
- Evidence 4: `_condamad/audits/prompt-generation-cartography` - required CS-343 to CS-347 audit root exists.
- Evidence 5: required roots `backend/app/services/llm_generation`, `backend/app/domain/llm`, `backend/app/ops/llm/bootstrap`, and `backend/tests` exist.
- Evidence 6: targeted candidate checks found guidance, chat, daily horoscope, bootstrap, repair, gateway, and test roots.
- Evidence 7: `backend/app/domain/llm/configuration/catalog.py` is absent; `backend/app/domain/llm/prompting/catalog.py` is a likely catalog owner.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through resolved local IDs.
- Evidence 9: `resolve_guardrails.py` returned `RG-002` and `RG-022` for this backend prompt-generation audit scope.
- Registry gap: no exact guardrail exists for parallel legacy prompt-generation process audits.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `_condamad/docs`, and `_condamad/audits` exist.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Specialized audit under `_condamad/audits/prompt-generation-document-review/`.
  - Guidance, public chat, chat guidance, shared natal context, daily horoscope, bootstrap seeds, fallback catalog, repair prompts, and carriers.
  - Classification of provider capability, trigger path, owner, configuration source, renderer or assembly, and prompt-visible inputs.
  - Verification against CS-350, CS-343 to CS-347 audits, backend source files, backend tests, and targeted scans.
  - Candidate follow-up stories for documentation, guardrails, migration, tests, or decommission.
- Out of scope:
  - Backend runtime changes, frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and real provider calls.
  - Direct edits to `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
  - Prompt, assembly, seed, gateway, API, or test implementation changes.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No runtime behavior change.
  - No source document rewrite.
  - No frontend route, screen, client generation, or UI validation.
  - No provider call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a parallel legacy prompt-generation audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the parallel legacy audit report, story evidence, validation output, and generated review handoff.
  - Do not modify application code, prompt text, assemblies, seeds, tests, migrations, CS-350 documentation, or runtime behavior.
  - Preserve active runtime, non-nominal runtime, recovery, bootstrap, test-only, admin-only, archival, and debt status labels.
  - Record candidate follow-up stories without implementing them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a provider-capable process cannot be classified from source reads, targeted `rg`, `AST guard`, or listed tests.
- Additional validation rules:
  - Every process row must cite a concrete source path plus symbol, route, script, test, heading, or bounded source note.
  - Every process must have exactly one status from the Target State list.
  - Provider capability must be proven from trigger and handoff evidence, not from gateway imports alone.
  - `chart_json`, `natal_data`, textual natal summary, seed, and fallback catalog findings must be classified explicitly.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source reads, `AST guard`, targeted `rg`, and pytest paths prove provider-capable prompt paths. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the audit report plus story evidence. |
| Ownership Routing | yes | The audit belongs under `_condamad/audits`, not runtime code or the final documentation path. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The audit report has required sections, process matrix, statuses, citations, and recommendations. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Legacy, fallback, seed, and carrier paths must stay classified by runtime capability. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The parallel process audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | The report includes all mandatory sections. | Evidence profile: json_contract_shape; `python` checks required headings in the report. |
| AC3 | Candidate process families are explicit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks guidance, chat, horoscope, fallback, repair, carriers. |
| AC4 | Each process has one status. | Evidence profile: json_contract_shape; `python` checks the status matrix for required labels. |
| AC5 | Provider-capable paths are separated. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks provider handoff markers. |
| AC6 | Bootstrap artifacts are separated. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks bootstrap, seed, test-only, admin-only, archival labels. |
| AC7 | Legacy carriers are classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `chart_json` and `natal_data` in backend app and tests. |
| AC8 | Modern natal boundary is stated. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration/test_llm_legacy_extinction.py`. |
| AC9 | Document gaps are actionable. | Evidence profile: json_contract_shape; `python` checks gaps and candidate story headings. |
| AC10 | Persistent evidence artifacts are stored. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and baseline evidence artifact set. (AC: AC1, AC10)
- [ ] Task 2: Read CS-350 and CS-343 to CS-347 artifacts to extract known prompt-generation process claims. (AC: AC2, AC9)
- [ ] Task 3: Inspect guidance route, service, bootstrap seed, configuration, renderer use, and provider handoff. (AC: AC3, AC4, AC5)
- [ ] Task 4: Inspect public chat, chat guidance, shared natal context, and prompt-visible natal summary carriers. (AC: AC3, AC4, AC5, AC7)
- [ ] Task 5: Inspect daily horoscope narration and its bootstrap narrator assembly. (AC: AC3, AC4, AC5, AC6)
- [ ] Task 6: Inspect fallback catalog ownership, no-assembly fallback, gateway fallback behavior, and provider path boundaries. (AC: AC3, AC4, AC5)
- [ ] Task 7: Inspect repair prompt modules and classify recovery-only versus provider-capable behavior. (AC: AC3, AC4, AC5)
- [ ] Task 8: Scan `chart_json`, `natal_data`, prompt, provider, guidance, chat, horoscope, fallback, and repair terms in backend app and tests. (AC: AC3, AC7)
- [ ] Task 9: Build the process matrix with trigger, owner, config source, prompt-visible input, renderer, assembly, provider handoff, and status. (AC: AC4)
- [ ] Task 10: List provider-capable paths separately from bootstrap, test, admin, and archival paths. (AC: AC5, AC6)
- [ ] Task 11: Record document gaps and candidate follow-up stories without changing docs or runtime code. (AC: AC8, AC9)
- [ ] Task 12: Run validation scans, persist outputs, and confirm runtime files remain unchanged. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-353-audit-process-paralleles-legacy-generation-prompt-llm.md` - source scope and acceptance criteria.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - final document to nuance later.
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md` - previous surface inventory audit.
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md` - configuration audit.
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md` - gateway and provider handoff audit.
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md` - natal input boundary audit.
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md` - validation and persistence audit.
- `backend/app/services/llm_generation/guidance/guidance_service.py` - guidance process owner candidate.
- `backend/app/api/v1/routers/public/guidance.py` - public guidance trigger candidate.
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` - guidance seed candidate.
- `backend/app/services/llm_generation/chat/public_chat.py` - public chat process owner candidate.
- `backend/app/services/llm_generation/chat/chat_guidance_service.py` - chat guidance process owner candidate.
- `backend/app/services/llm_generation/shared/natal_context.py` - shared natal context carrier owner.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - daily horoscope narration owner candidate.
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` - daily horoscope seed candidate.
- `backend/app/domain/llm/prompting/catalog.py` - likely catalog owner because the brief path under configuration is absent.
- `backend/app/domain/llm/runtime/gateway.py` - gateway, fallback, and provider handoff owner.
- `backend/app/domain/llm/runtime/repair.py` - repair runtime owner.
- `backend/app/domain/llm/runtime/repair_prompter.py` - repair prompt owner.
- `backend/tests/**` - test-only and guardrail evidence.

## Runtime Source of Truth

- Primary source of truth:
  - Backend source files listed in Files to Inspect First, CS-350, CS-343 to CS-347 artifacts, and backend tests.
  - `AST guard` evidence confirms no backend runtime files changed for this audit-only story.
- Secondary evidence:
  - Targeted `rg` scans for prompt, LLM, provider, guidance, chat, horoscope, fallback, repair, `chart_json`, and `natal_data`.
  - Listed `pytest` paths for existing legacy extinction and prompt-boundary tests.
- Static scans alone are not sufficient for this story because:
  - The audit must inspect triggers and provider handoff context for every candidate process.

## Contract Shape

- Contract type:
  - Timestamped parallel legacy prompt-generation audit report.
- Fields:
  - `process`: exact process family or source-owned process name.
  - `status`: runtime active, runtime non nominal, recovery, bootstrap/seed, test-only, admin-only, archival, or debt.
  - `trigger`: route, service call, script, test, admin action, or artifact source that starts the process.
  - `owner`: canonical source path plus symbol or bounded source note.
  - `configuration source`: assembly, catalog, seed, runtime profile, fixture, or source note.
  - `prompt-visible input`: fields or text that can enter provider messages.
  - `renderer or assembly`: renderer, assembly, repair prompter, gateway composition, or none with evidence.
  - `provider handoff`: provider-capable, not provider-capable, blocked, test-only, seed-only, or unresolved source blocker.
  - `modern natal boundary`: relation to `llm_astrology_input_v1` and modern natal flow.
  - `risk if ignored`: risk to CS-350 or future implementation work.
- Required report sections:
  - Resume executif.
  - Methode et scans executes.
  - Inventaire des processus paralleles et legacy.
  - Matrice statut par processus.
  - Detail par processus candidat.
  - Processus confirmes comme provider-capable.
  - Processus seulement bootstrap, test, admin ou archive.
  - Gaps documentaires.
  - Stories candidates de correction ou de documentation.
- Required fields:
  - process
  - status
  - trigger
  - owner
  - configuration source
  - prompt-visible input
  - renderer or assembly
  - provider handoff
  - modern natal boundary
  - risk if ignored
- Optional fields:
  - none for process rows; unresolved rows must use `unresolved source blocker` in provider handoff.
- Status codes:
  - none; no HTTP route or API behavior is in scope.
- Serialization names:
  - Report column names must use the exact field names listed above.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; this story creates a human audit report, not a generated API or frontend contract.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/parallel-processes-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/parallel-processes-after.txt`
- Expected invariant:
  - The only intended repository surface delta is the CS-353 audit report and CS-353 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Parallel legacy process audit report | `_condamad/audits/prompt-generation-document-review/` | `_condamad/docs/**` |
| Story evidence | `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/` | `backend/app/**` |
| Runtime behavior | Existing backend LLM modules | `_condamad/audits/**` |
| Follow-up correction decisions | Candidate story list in the audit report | Direct runtime or source document edits |

## Mandatory Reuse / DRY Constraints

- Reuse CS-350 and CS-343 to CS-347 artifacts as source context; do not duplicate their full contents.
- Reference source paths, symbols, headings, route names, scripts, and bounded notes instead of copying long source excerpts.
- Keep all CS-353 audit output in the timestamped audit report and CS-353 story evidence folder.
- Use one shared status vocabulary for all process rows.
- Do not create a second canonical prompt-generation cartography document.

## No Legacy / Forbidden Paths

- No legacy path may be promoted to nominal runtime truth by the audit report.
- No compatibility path may be proposed as an acceptable correction.
- No fallback path may be treated as nominal prompt generation without source proof.
- No bootstrap, seed, test, admin, or archival artifact may be described as provider runtime input without handoff evidence.
- Forbidden edit surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`

## Reintroduction Guard

- Guard target:
  - Guidance, chat, horoscope, fallback, repair, seeds, tests, and carrier paths must remain classified by provider capability.
  - `chart_json`, `natal_data`, and textual natal summaries must not be hidden behind a vague parallel-process label.
- Required guard evidence:
  - `AST guard` and architecture guard proving prompt process code is not reintroduced or changed for this audit-only story.
  - `rg -n "prompt|LLM|provider|guidance|chat|horoscope|fallback|repair|chart_json|natal_data" backend/app backend/tests`
  - `rg -n "parallel-legacy-processes-audit|Guidance|Chat public|Horoscope daily" _condamad/audits/prompt-generation-document-review`
  - `rg -n "fallback catalog|repair prompts|chart_json|natal_data" _condamad/audits/prompt-generation-document-review`
- Review handoff:
  - Any candidate that changes runtime semantics must be rejected from this story and recorded as out of scope.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must stay collected and current. | Listed `rg`; report scan. |
| RG-002 `refactor-api-v1-routers` | Backend responsibility must not move during audit work. | `AST guard`; no backend diff. |
| Registry gap | No exact parallel legacy prompt-generation audit guardrail exists. | `resolve_guardrails.py`; targeted ID search. |

## Persistent Evidence Artifacts

All paths below are relative to `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/`.

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `evidence/parallel-processes-baseline.txt` | Capture source availability and candidate process markers before the report. |
| Final scan | `evidence/parallel-processes-after.txt` | Capture produced report markers and validation evidence. |
| Validation output | `evidence/validation.txt` | Store story implementation validation command output. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md` - final audit report.
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/parallel-processes-baseline.txt` - baseline evidence.
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/parallel-processes-after.txt` - final scan evidence.
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- No new automated tests are expected because this is a documentation audit story.
- Assumption risk: `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/validation.txt` carries checks.
- Validation relies on targeted `rg`, `python` path and heading checks, listed `pytest` paths, and an `AST guard`.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime behavior is touched.
- `backend/tests/**` - out of scope; no test implementation is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - source document is reviewed, not edited.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md').exists()"`
- VC2: `python -c "from pathlib import Path; p=Path('_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md'); print(p)"`
- VC3: `python -c "from pathlib import Path; p=Path('_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md'); print(p.exists())"`
- VC4: `rg -n "Resume executif|Methode et scans executes|Inventaire des processus paralleles|Matrice statut par processus" _condamad/audits/prompt-generation-document-review`
- VC5: `rg -n "Guidance|Chat public|Horoscope daily|fallback catalog|repair prompts|chart_json|natal_data" _condamad/audits/prompt-generation-document-review`
- VC6: `rg -n "runtime active|runtime non nominal|recovery|bootstrap/seed|test-only|admin-only|archival|debt" _condamad/audits/prompt-generation-document-review`
- VC7: `rg -n "prompt|LLM|provider|guidance|chat|horoscope|fallback|repair|chart_json|natal_data" backend/app backend/tests`
- VC8: `rg -n "provider-capable|provider handoff|seed-only|test-only|admin-only|archival" _condamad/audits/prompt-generation-document-review`
- VC9: `pytest -q backend/tests/integration/test_llm_legacy_extinction.py`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/validation.txt').exists()"`
- VC11: `python -c "import subprocess; out=subprocess.check_output(['git','status','--short'], text=True); assert 'backend/app/' not in out and 'frontend/src/' not in out"`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

## Regression Risks

- The report may conclude too quickly that all paths share one gateway; AC5 and tasks 3 to 7 force trigger and handoff proof.
- The report may group distinct processes under broad labels; AC3, AC4, and task 9 force per-process classification.
- Seed, test, admin, and archival artifacts may be confused with provider runtime paths; AC6 and VC8 force separate lists.
- Carrier terms may be missed because they appear outside nominal prompt modules; AC7 and VC7 force backend app and test scans.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Read the target document, prior audits, and required backend source files before writing the audit report.
- Verify trigger and provider handoff for every provider-capable claim.
- Record unresolved source blockers rather than inventing process status.
- Store command outputs under the CS-353 evidence folder.

## References

- `_story_briefs/cs-353-audit-process-paralleles-legacy-generation-prompt-llm.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/api/v1/routers/public/guidance.py`
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
- `backend/app/services/llm_generation/chat/public_chat.py`
- `backend/app/services/llm_generation/chat/chat_guidance_service.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/repair.py`
- `backend/app/domain/llm/runtime/repair_prompter.py`
- `backend/tests/**`
