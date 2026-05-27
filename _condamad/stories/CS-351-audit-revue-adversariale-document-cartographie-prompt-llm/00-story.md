# Story CS-351 audit-revue-adversariale-document-cartographie-prompt-llm: Audit Revue Adversariale Document Cartographie Prompt LLM
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-351-audit-revue-adversariale-document-cartographie-prompt-llm.md`.
- Source problem: the final prompt-generation cartography document became an important reading source and must be challenged as a critical contract.
- Source stakes:
  - Future agents must not be misled by unsupported, ambiguous, or overconfident documentation claims.
  - Prompt-visible, runtime-only, validation-only, audit-only, and backend-only boundaries must remain distinct.
  - Fallback paths, seeds, tests, and old paths must not be presented as runtime truth.
  - Known blockers and source gaps from CS-343 to CS-349 must remain visible.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a timestamped adversarial audit report for `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
The report must challenge factual accuracy, omissions, contradictions, source strength, and wording risk without modifying runtime code or the source document.

## Target State

- A report exists under `_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/01-adversarial-document-review-audit.md`.
- The report reviews the final cartography document line by line against code, CS-343 to CS-347 audits, CS-348 architecture, and CS-349 report artifacts.
- Each challenged statement is classified as factual error, omission, ambiguity, contradiction, or wording risk.
- Each finding cites a file path and a symbol, section, heading, or row marker when the source provides one.
- The report includes matrices for validated claims, claims requiring correction, omissions, contradictions or tensions, recommended corrections, and final decision.
- The report does not request runtime changes and does not rewrite the final cartography document.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-351-audit-revue-adversariale-document-cartographie-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-351`.
- Evidence 3: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - target document path exists.
- Evidence 4: `_condamad/audits/prompt-generation-cartography` - CS-343 to CS-347 audit root exists.
- Evidence 5: `_condamad/architecture/prompt-generation-cartography` - CS-348 architecture root exists.
- Evidence 6: `_condamad/reports/prompt-generation-cartography` - CS-349 report root exists.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted by resolved IDs and targeted ID search.
- Evidence 8: `resolve_guardrails.py` returned no locally applicable guardrail for this documentation-review scope.
- Registry gap: no exact guardrail exists for adversarial review of prompt-generation documentation.
- Repository structure alert: none. `backend`, `frontend`, `_condamad/docs`, `_condamad/audits`, `_condamad/architecture`, and `_condamad/reports` exist.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Adversarial document review under `_condamad/audits/prompt-generation-document-review/`.
  - Source checking against CS-343 to CS-347 audits, CS-348 architecture, CS-349 report, and listed backend code files.
  - Classification of unsupported claims, omissions, contradictions, boundary confusion, and risky wording.
  - Candidate documentation corrections recorded in the audit report only.
- Out of scope:
  - Backend runtime changes, frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and provider calls.
  - Direct edits to `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.
  - Re-running CS-343 to CS-347 audits, producing new architecture, or changing prompt contracts.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No runtime behavior change.
  - No source document rewrite.
  - No frontend route, screen, client generation, or UI validation.
  - No provider call.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits an adversarial documentation audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the adversarial audit report, story evidence, validation output, and generated review handoff.
  - Do not modify application code, prompt text, tests, migrations, the final cartography document, or runtime behavior.
  - Preserve prompt-visible, runtime-only, validation-only, audit-only, and backend-only boundaries as review axes.
  - Record candidate documentation corrections without applying them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a required source artifact is unavailable and the report cannot classify a claim without inventing evidence.
- Additional validation rules:
  - Every finding must cite a concrete source path and a symbol, heading, section, row marker, or bounded source note.
  - The report must distinguish factual error, omission, ambiguity, contradiction, and wording risk.
  - Claims about runtime truth must be checked against source artifacts, targeted `rg`, `AST guard`, or bounded source reads.
  - The final decision must be one of `acceptable`, `acceptable with corrections`, or `not acceptable`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source traces, `AST guard`, and targeted `rg` prove whether documentation claims match runtime owners. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is the audit report plus story evidence. |
| Ownership Routing | yes | The review belongs under `_condamad/audits`, not runtime code or the final documentation path. |
| Allowlist Exception | no | No allowlist handling is authorized for this documentation-review story. |
| Contract Shape | yes | The audit report has required matrices, categories, source citations, recommendations, and final decision. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Old paths, fallbacks, seeds, and tests must not be promoted to runtime truth in the report. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The adversarial audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | The report includes all mandatory sections. | Evidence profile: json_contract_shape; `python` checks required headings in the report. |
| AC3 | Findings cite source paths. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks source path markers in the report. |
| AC4 | Finding categories are explicit. | Evidence profile: json_contract_shape; `python` checks the five required category labels. |
| AC5 | Boundary roles are reviewed. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks prompt-visible and backend-only terms. |
| AC6 | Carrier role claims are controlled. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks fallback, legacy, seed, and test terms. |
| AC7 | Runtime ownership claims are source-backed. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks LLM owner symbols in report. |
| AC8 | The report avoids behavior change requests. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks no behavior-change instruction in the report. |
| AC9 | The final decision is evidence-backed. | Evidence profile: json_contract_shape; `python` checks accepted decision labels plus proof wording. |
| AC10 | Persistent evidence artifacts are stored. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped review folder and baseline evidence artifact set. (AC: AC1, AC10)
- [ ] Task 2: Read the final cartography document line by line and extract reviewable claims. (AC: AC2, AC3)
- [ ] Task 3: Cross-check claims against CS-343 to CS-347 audit artifacts. (AC: AC3, AC4, AC5)
- [ ] Task 4: Cross-check architecture and report claims against CS-348 and CS-349 artifacts. (AC: AC3, AC4, AC9)
- [ ] Task 5: Inspect listed backend code owners for claims that require source-level proof. (AC: AC3, AC7)
- [ ] Task 6: Classify each challenged claim by finding category and wording risk. (AC: AC4, AC9)
- [ ] Task 7: Verify prompt-visible, runtime-only, validation-only, audit-only, and backend-only boundaries. (AC: AC5)
- [ ] Task 8: Control fallback, legacy, seed, and test references so they are not treated as runtime truth. (AC: AC6)
- [ ] Task 9: Write recommended documentation corrections without editing the source document. (AC: AC8, AC9)
- [ ] Task 10: Run validation scans, persist outputs, and confirm runtime files remain unchanged. (AC: AC8, AC10)

## Files to Inspect First

- `_story_briefs/cs-351-audit-revue-adversariale-document-cartographie-prompt-llm.md` - source scope and acceptance criteria.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - document under adversarial review.
- `_condamad/audits/prompt-generation-cartography/*/01-surface-inventory-audit.md` - CS-343 source map audit.
- `_condamad/audits/prompt-generation-cartography/*/02-configuration-assembly-placeholder-audit.md` - CS-344 configuration audit.
- `_condamad/audits/prompt-generation-cartography/*/03-runtime-gateway-handoff-audit.md` - CS-345 runtime gateway audit.
- `_condamad/audits/prompt-generation-cartography/*/04-natal-astrology-input-audit.md` - CS-346 natal input audit.
- `_condamad/audits/prompt-generation-cartography/*/05-output-validation-persistence-audit.md` - CS-347 output validation audit.
- `_condamad/architecture/prompt-generation-cartography/*/architecture-prompt-generation-llm.md` - CS-348 architecture source.
- `_condamad/reports/prompt-generation-cartography/*/report-prompt-generation-cartography.md` - CS-349 report source.
- `backend/app/domain/llm/runtime/gateway.py` - `LLMGateway` runtime owner.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly resolution owner.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use-case registry owner.
- `backend/app/domain/llm/prompting/prompt_renderer.py` - `PromptRenderer` owner.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - natal LLM input owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal orchestration owner.

## Runtime Source of Truth

- Primary source of truth:
  - The final cartography document, CS-343 to CS-349 artifacts, and listed backend LLM source files.
  - `AST guard` evidence confirms no backend runtime files changed for this audit-only story.
- Secondary evidence:
  - Targeted `rg` scans for source symbols, boundaries, non-runtime carrier terms, and report-required sections.
- Static scans alone are not sufficient for this story because:
  - The audit must compare documentation claims against primary sources and classify source strength.

## Contract Shape

- Contract type:
  - Timestamped adversarial documentation audit report.
- Fields:
  - `claim`: exact or summarized documentation claim under review.
  - `expected source`: primary source path or artifact family used to check the claim.
  - `status`: validated, correction required, nuance required, unresolved, or source blocker.
  - `finding category`: factual error, omission, ambiguity, contradiction, or wording risk.
  - `evidence`: path plus symbol, section, heading, row marker, or bounded source note.
  - `recommended correction`: documentation-only candidate correction.
- Required report sections:
  - Resume executif.
  - Methode de revue adversariale.
  - Matrice des affirmations validees.
  - Matrice des affirmations a corriger ou a nuancer.
  - Omissions potentielles.
  - Contradictions ou tensions entre document, audits et code.
  - Corrections documentaires recommandees.
  - Decision finale.
- Required fields:
  - claim
  - expected source
  - status
  - finding category
  - evidence
  - recommended correction
- Optional fields:
  - none for findings; validated claims may use `none` for recommended correction.
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
  - `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/document-review-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/document-review-after.txt`
- Expected invariant:
  - The only intended repository surface delta is the adversarial audit report and CS-351 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Adversarial document review report | `_condamad/audits/prompt-generation-document-review/` | `_condamad/docs/**` |
| Story evidence | `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/` | `backend/app/**` |
| Runtime behavior | Existing backend LLM modules | `_condamad/audits/**` |
| Source document corrections | Candidate list in the audit report | Direct edit to `_condamad/docs/**` |

## Mandatory Reuse / DRY Constraints

- Reuse CS-343 to CS-349 artifacts as primary evidence; do not duplicate their full contents.
- Reference source paths, symbols, headings, and row markers instead of copying long code or report excerpts.
- Keep all adversarial review output in the timestamped audit report and story evidence folder.
- Use the same labels consistently for prompt-visible, runtime-only, validation-only, audit-only, and backend-only boundaries.
- Do not create a second canonical cartography document.

## No Legacy / Forbidden Paths

- No legacy path may be promoted to runtime truth by the audit report.
- No compatibility path may be proposed as an acceptable correction.
- No fallback path may be treated as nominal prompt generation.
- No seed, bootstrap, test, or audit-only artifact may be described as provider runtime input without primary source evidence.
- Forbidden edit surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `frontend/src/**`
  - `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`

## Reintroduction Guard

- Guard target:
  - Old paths, fallback terms, seed/bootstrap artifacts, tests, and audit-only carriers must stay classified as non-runtime unless sources prove active runtime use.
- Required guard evidence:
  - `rg -n "fallback|legacy|seed|test|backend-only|prompt-visible" _condamad/audits/prompt-generation-document-review`
  - `rg -n "LLMGateway|PromptRenderer|llm_astrology_input_v1|assembly_resolver" _condamad/audits/prompt-generation-document-review`
- Review handoff:
  - Any candidate correction that changes runtime semantics must be rejected from this story and recorded as out of scope.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| Registry gap | No exact documentation-review guardrail exists for this scope. | `resolve_guardrails.py`; targeted `rg`. |
| RG-042 `docs-llm-source-truth` | Useful adjacent guardrail for LLM source-of-truth claims. | Targeted `rg`; report source matrix. |
| RG-041 `documentation-entitlement` | Non-applicable example; entitlement docs are out of scope. | Scope vector excludes entitlement. |

## Persistent Evidence Artifacts

All paths below are relative to `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/`.

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `evidence/document-review-baseline.txt` | Capture pre-review source availability and target markers. |
| Final scan | `evidence/document-review-after.txt` | Capture produced report markers and validation evidence. |
| Validation output | `evidence/validation.txt` | Store story implementation validation command output. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this documentation-review story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-document-review/YYYY-MM-DD-HHMM/01-adversarial-document-review-audit.md` - final adversarial review report.
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/document-review-baseline.txt` - baseline evidence.
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/document-review-after.txt` - final scan evidence.
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- No new automated tests are expected because this is a documentation audit story.
- Assumption risk: `_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/validation.txt` carries checks.
- Validation relies on targeted `rg`, `python` path and heading checks, plus an `AST guard` for unchanged runtime files.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime behavior is touched.
- `backend/tests/**` - out of scope; no test implementation is touched.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` - source document is reviewed, not edited.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/audits/prompt-generation-document-review').exists()"`
- VC2: `python -c "from pathlib import Path; p=next(Path('_condamad/audits/prompt-generation-document-review').glob('*/01-adversarial-document-review-audit.md')); print(p)"`
- VC3: `rg -n "Resume executif|Methode de revue adversariale|Matrice des affirmations|Decision finale" _condamad/audits/prompt-generation-document-review`
- VC4: `rg -n "erreur factuelle|omission|ambiguite|contradiction|risque de formulation" _condamad/audits/prompt-generation-document-review`
- VC5: `rg -n "llm_astrology_input_v1|LLMGateway|PromptRenderer|fallback|legacy|backend-only|prompt-visible" _condamad/audits/prompt-generation-document-review`
- VC6: `rg -n "prompt-generation-current-implementation|adversarial-document-review|affirmation|omission|contradiction" _condamad/audits/prompt-generation-document-review`
- VC7: `rg -n "llm_astrology_input_v1|LLMGateway|PromptRenderer" _condamad/docs/prompt-generation-cartography`
- VC8: `rg -n "fallback|legacy|backend-only|prompt-visible" _condamad/audits/prompt-generation-cartography`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-351-audit-revue-adversariale-document-cartographie-prompt-llm/evidence/validation.txt').exists()"`
- VC10: `python -c "import subprocess; out=subprocess.check_output(['git','status','--short'], text=True); assert 'backend/app/' not in out and 'frontend/src/' not in out"`
- VC11: `ruff format .`
- VC12: `ruff check .`
- VC13: `pytest -q`

## Regression Risks

- The report may become a soft reread instead of an adversarial review; AC4, AC6, and VC4 force finding classification and sensitive-term control.
- The report may overstate a claim from documentation without source support; AC3, AC7, VC5, and VC7 force primary source traceability.
- Candidate corrections may drift into runtime work; AC8, ownership routing, and forbidden edit surfaces keep this story documentation-only.
- The source document may be modified directly; Expected Files and VC9 prevent edits to runtime and frontend surfaces while AC8 forbids source-document rewriting.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Read the target document line by line before writing the audit report.
- Cross-check each technical claim against at least one primary source from the required source list.
- Record unsupported claims as findings instead of inventing source evidence.
- Store command outputs under the CS-351 evidence folder.

## References

- `_story_briefs/cs-351-audit-revue-adversariale-document-cartographie-prompt-llm.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `_condamad/architecture/prompt-generation-cartography/**/architecture-prompt-generation-llm.md`
- `_condamad/reports/prompt-generation-cartography/**/report-prompt-generation-cartography.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
