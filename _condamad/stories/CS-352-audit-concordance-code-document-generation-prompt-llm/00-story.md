# Story CS-352 audit-concordance-code-document-generation-prompt-llm: Audit Concordance Code Document Generation Prompt LLM
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-352-audit-concordance-code-document-generation-prompt-llm.md`.
- Source problem: the final prompt-generation cartography document must be checked against executable backend code and tests.
- Source stakes:
  - Future agents must not trust a prompt-generation document that cites absent, renamed, or wrongly owned symbols.
  - Prompt-visible, backend-only, audit-only, validation, repair, persistence, and observability boundaries must remain distinct.
  - The nominal flow from use-case selection to provider handoff must be source-aligned rather than inferred from editorial structure.
  - Missing tests or weak guardrails must be reported as coverage risk, not hidden as documentation confidence.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a timestamped code-document concordance audit for the final prompt-generation cartography document.
The audit must prove or invalidate cited paths, owners, symbols, boundaries, and prompt-visible exclusions without changing code or documentation.

## Target State

- A report exists at `_condamad/audits/prompt-generation-document-review/2026-05-27-2240/02-code-document-concordance-audit.md`.
- The report traces the nominal path from canonical use-case selection through provider handoff.
- The report maps document sections to code sources and status.
- The report maps cited symbols to presence, real responsibility, and source evidence.
- The report verifies prompt-visible exclusions for `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `chart_json`, and `natal_data`.
- The report distinguishes absence documentaire, erreur documentaire, and risque de test coverage.
- The report records candidate documentation corrections without editing the final cartography document.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-352-audit-concordance-code-document-generation-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-352`.
- Evidence 3: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - target document path exists.
- Evidence 4: required backend LLM source paths from the brief exist under `backend/app/domain/llm/**`.
- Evidence 5: required natal LLM input and orchestration source paths from the brief exist under `backend/app/**`.
- Evidence 6: required backend boundary tests from the brief exist under `backend/tests/**`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through resolved local IDs.
- Evidence 8: `resolve_guardrails.py` returned `RG-002` and `RG-022` for the backend prompt-generation audit scope.
- Registry gap: no exact guardrail exists for code-document concordance of prompt-generation cartography.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `_condamad/docs`, and `_condamad/audits` exist.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Code-document concordance audit under `_condamad/audits/prompt-generation-document-review/`.
  - Source checking against the final cartography document, listed backend source files, and listed backend tests.
  - Verification of use-case selection, assembly resolution, placeholder rendering, LLM input construction, message composition, and handoff.
  - Verification of prompt-visible exclusions and backend-only payload fields.
  - Classification of document/code gaps, symbol ownership drift, absent symbols, and coverage risk.
- Out of scope:
  - Backend runtime changes, frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and provider calls.
  - Direct edits to `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
  - Business prompt line-by-line audit, output-schema ownership decision, and real LLM calls.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No runtime behavior change.
  - No source document rewrite.
  - No frontend route, screen, client generation, or UI validation.
  - No provider call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a backend code-document concordance audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the concordance audit report, story evidence, validation output, and generated review handoff.
  - Do not modify application code, prompt text, tests, migrations, the final cartography document, or runtime behavior.
  - Preserve prompt-visible, backend-only, audit-only, validation, repair, persistence, and observability boundaries as audit axes.
  - Record candidate documentation corrections without applying them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a required source path is unavailable and concordance cannot be classified without invented evidence.
- Additional validation rules:
  - Every matrix row must cite a concrete source path and a symbol, heading, section, row marker, or bounded source note.
  - The report must distinguish absence documentaire, erreur documentaire, and risque de test coverage.
  - Runtime ownership claims must be checked against source reads, targeted `rg`, `AST guard`, or listed pytest files.
  - Non-natal surfaces discovered during tracing must be noted without forcing them into the modern natal flow.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source reads, `AST guard`, targeted `rg`, and pytest paths prove whether document claims match executable owners. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the audit report plus story evidence. |
| Ownership Routing | yes | The audit belongs under `_condamad/audits`, not runtime code or the final documentation path. |
| Allowlist Exception | no | No allowlist handling is authorized for this code-document concordance story. |
| Contract Shape | yes | The audit report has required sections, matrices, source citations, gap categories, and candidate corrections. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Backend-only and old carrier fields must not be promoted to prompt-visible truth in the report. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The concordance audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | The report includes all mandatory sections. | Evidence profile: json_contract_shape; `python` checks required headings in the report. |
| AC3 | The nominal flow is traced. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks gateway, renderer, resolver, and provider symbols. |
| AC4 | Document sections map to code status. | Evidence profile: json_contract_shape; `python` checks the section-code-status matrix headings. |
| AC5 | Cited symbols map to real responsibility. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks cited owner symbols in the report. |
| AC6 | Prompt-visible exclusions are verified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks excluded field names in backend app and tests. |
| AC7 | Boundary tests are classified. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`. |
| AC8 | Non-natal surfaces are reported separately. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks non-natal and natal-flow markers in the report. |
| AC9 | Gap categories are explicit. | Evidence profile: json_contract_shape; `python` checks absence documentaire, erreur documentaire, and coverage risk labels. |
| AC10 | Persistent evidence artifacts are stored. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and baseline evidence artifact set. (AC: AC1, AC10)
- [ ] Task 2: Read the final cartography document and extract every code-verifiable claim. (AC: AC2, AC4)
- [ ] Task 3: Trace canonical use-case selection and assembly resolution against listed configuration modules. (AC: AC3, AC5)
- [ ] Task 4: Trace placeholder rendering and message composition through the renderer and gateway. (AC: AC3, AC5)
- [ ] Task 5: Trace `llm_astrology_input_v1` construction and natal orchestration ownership. (AC: AC3, AC5)
- [ ] Task 6: Verify provider handoff, validation, repair, persistence, and observability claims against runtime owners. (AC: AC3, AC5)
- [ ] Task 7: Verify excluded prompt-visible fields by scan and by listed boundary tests. (AC: AC6, AC7)
- [ ] Task 8: Record symbols cited by the document but absent, renamed, or owned by a different source. (AC: AC5, AC9)
- [ ] Task 9: Record important code symbols absent from the document with bounded source evidence. (AC: AC4, AC9)
- [ ] Task 10: Separate non-natal surfaces from the modern natal flow in the report. (AC: AC8)
- [ ] Task 11: Write candidate documentation corrections without editing the source document. (AC: AC9)
- [ ] Task 12: Run validation scans, persist outputs, and confirm runtime files remain unchanged. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-352-audit-concordance-code-document-generation-prompt-llm.md` - source scope and acceptance criteria.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - document under concordance audit.
- `backend/app/domain/llm/runtime/gateway.py` - gateway execution, message building, provider handoff, validation, and repair flow.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly resolution owner.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use-case and contract registry owner.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - placeholder rendering and structured or chat message composition owner.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - natal LLM input contract and prompt-visible boundary owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal orchestration owner.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - payload boundary architecture guard.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - orchestration boundary guard.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - LLM input contract tests.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` - LLM input hash tests.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` - evidence boundary tests.
- `backend/tests/integration/test_llm_legacy_extinction.py` - old injection surface extinction guard.

## Runtime Source of Truth

- Primary source of truth:
  - The final cartography document, listed backend source files, and listed backend tests.
  - `AST guard` evidence confirms no backend runtime files changed for this audit-only story.
- Secondary evidence:
  - Targeted `rg` scans for source symbols, prompt-visible exclusions, backend-only carriers, and report-required sections.
  - Listed `pytest` paths for existing boundary and extinction tests.
- Static scans alone are not sufficient for this story because:
  - Concordance requires reading source context around symbols and comparing responsibility against the document.

## Contract Shape

- Contract type:
  - Timestamped code-document concordance audit report.
- Fields:
  - `document section`: section, heading, or row from the final cartography document.
  - `code source`: source path plus symbol or bounded note used to verify the section.
  - `status`: confirmed, absence documentaire, erreur documentaire, risque de test coverage, or unresolved source blocker.
  - `cited symbol`: symbol, class, function, field, or module named by the document.
  - `presence`: present, absent, renamed, or different owner.
  - `real responsibility`: responsibility proven from source context.
  - `evidence`: path plus symbol, section, row marker, or bounded source note.
  - `candidate correction`: documentation-only correction candidate.
- Required report sections:
  - Resume executif.
  - Methode de concordance code-document.
  - Trace code du flux nominal.
  - Matrice document section -> code source -> statut.
  - Matrice symbole cite -> presence -> responsabilite reelle.
  - Matrice exclusions prompt-visible/backend-only.
  - Tests et guardrails confirmes ou insuffisants.
  - Gaps de concordance.
  - Corrections documentaires candidates.
  - Decision finale.
- Required fields:
  - document section
  - code source
  - status
  - cited symbol
  - presence
  - real responsibility
  - evidence
  - candidate correction
- Optional fields:
  - none for findings; confirmed rows may use `none` for candidate correction.
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
  - `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/concordance-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/concordance-after.txt`
- Expected invariant:
  - The only intended repository surface delta is the concordance audit report and CS-352 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Code-document concordance audit report | `_condamad/audits/prompt-generation-document-review/` | `_condamad/docs/**` |
| Story evidence | `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/` | `backend/app/**` |
| Runtime behavior | Existing backend LLM modules | `_condamad/audits/**` |
| Source document corrections | Candidate list in the audit report | Direct edit to `_condamad/docs/**` |

## Mandatory Reuse / DRY Constraints

- Reuse the final cartography document and listed source files as primary evidence; do not duplicate their full contents.
- Reference source paths, symbols, headings, and row markers instead of copying long code or report excerpts.
- Keep all concordance review output in the timestamped audit report and story evidence folder.
- Use the same labels consistently for prompt-visible, backend-only, audit-only, validation, repair, persistence, and observability.
- Do not create a second canonical cartography document.

## No Legacy / Forbidden Paths

- No legacy path may be promoted to runtime truth by the audit report.
- No compatibility path may be proposed as an acceptable correction.
- No fallback path may be treated as nominal prompt generation.
- No backend-only carrier field may be described as prompt-visible without source proof.
- Forbidden edit surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`

## Reintroduction Guard

- Guard target:
  - `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `chart_json`, and `natal_data` must remain correctly classified.
  - Legacy injection and fallback terms must stay separated from the nominal modern natal flow.
- Required guard evidence:
  - `rg -n "llm_astrology_input_v1|chart_json|natal_data|evidence|provenance|prompt_visible" backend/app backend/tests`
  - `rg -n "def execute_request|def _resolve_plan|def _build_messages|def _call_provider" backend/app/domain/llm/runtime/gateway.py`
  - `rg -n "compose_chat_messages|compose_structured_messages" backend/app/domain/llm/runtime/gateway.py backend/app/domain/llm/prompting/prompt_renderer.py`
- Review handoff:
  - Any candidate correction that changes runtime semantics must be rejected from this story and recorded as out of scope.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must stay collected and current. | Listed `pytest` paths; targeted report scan. |
| RG-002 `refactor-api-v1-routers` | Backend responsibility must not move opportunistically during audit work. | `AST guard`; no backend diff. |
| Registry gap | No exact code-document concordance guardrail exists for this scope. | `resolve_guardrails.py`; targeted ID search. |

## Persistent Evidence Artifacts

All paths below are relative to `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/`.

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `evidence/concordance-baseline.txt` | Capture source availability and target markers before the audit report. |
| Final scan | `evidence/concordance-after.txt` | Capture produced report markers and validation evidence. |
| Validation output | `evidence/validation.txt` | Store story implementation validation command output. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this code-document concordance story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-document-review/2026-05-27-2240/02-code-document-concordance-audit.md` - final concordance audit report.
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/concordance-baseline.txt` - baseline evidence.
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/concordance-after.txt` - final scan evidence.
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- No new automated tests are expected because this is a documentation audit story.
- Assumption risk: `_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/validation.txt` carries checks.
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

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/audits/prompt-generation-document-review/2026-05-27-2240/02-code-document-concordance-audit.md').exists()"`
- VC2: `python -c "from pathlib import Path; p=Path('_condamad/audits/prompt-generation-document-review/2026-05-27-2240/02-code-document-concordance-audit.md'); print(p)"`
- VC3: `rg -n "Resume executif|Trace code du flux nominal|Gaps de concordance|Decision finale" _condamad/audits/prompt-generation-document-review`
- VC4: `rg -n "section -> code|symbole cite|responsabilite reelle|exclusions prompt-visible" _condamad/audits/prompt-generation-document-review`
- VC5: `rg -n "def execute_request|def _resolve_plan|def _build_messages|def _call_provider" backend/app/domain/llm/runtime/gateway.py`
- VC6: `rg -n "compose_chat_messages|compose_structured_messages" backend/app/domain/llm/runtime/gateway.py backend/app/domain/llm/prompting/prompt_renderer.py`
- VC7: `rg -n "llm_astrology_input_v1|chart_json|natal_data|evidence|provenance|prompt_visible" backend/app backend/tests`
- VC8: `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- VC9: `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC10: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC11: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- VC12: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`
- VC13: `pytest -q backend/tests/integration/test_llm_legacy_extinction.py`
- VC14: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-352-audit-concordance-code-document-generation-prompt-llm/evidence/validation.txt').exists()"`
- VC15: `python -c "import subprocess; out=subprocess.check_output(['git','status','--short'], text=True); assert 'backend/app/' not in out and 'frontend/src/' not in out"`
- VC16: `ruff format .`
- VC17: `ruff check .`
- VC18: `pytest -q`

## Regression Risks

- The report may treat symbol presence as responsibility; AC5 and tasks 3 to 6 force source-context ownership checks.
- The report may flatten non-natal surfaces into the modern natal flow; AC8 and task 10 force separate classification.
- Candidate corrections may drift into runtime work; ownership routing and forbidden edit surfaces keep this story audit-only.
- Prompt-visible exclusions may be claimed from prose alone; AC6, AC7, and VC7 force scan and test evidence.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Read the target document and required source files before writing the audit report.
- Cross-check each technical claim against source context, not only symbol presence.
- Record unsupported claims as findings instead of inventing source evidence.
- Store command outputs under the CS-352 evidence folder.

## References

- `_story_briefs/cs-352-audit-concordance-code-document-generation-prompt-llm.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`
- `backend/tests/integration/test_llm_legacy_extinction.py`
