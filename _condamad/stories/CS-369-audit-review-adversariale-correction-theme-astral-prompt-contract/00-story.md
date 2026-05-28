# Story CS-369 audit-review-adversariale-correction-theme-astral-prompt-contract: Audit Review Adversariale Correction Theme Astral Prompt Contract
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-369-audit-review-adversariale-correction-theme-astral-prompt-contract.md`.
- Selected mode: Audit-to-story.
- Source problem: after CS-361 to CS-368, the `theme_astral` prompt contract needs adversarial review and accepted corrections.
- Source stakes: prompt coherence, sourced interpretation text, stable delivery profiles, backend-only plan handling, versioned persistence, and old-path closure.
- Closure expectation: produce the adversarial report, correct accepted critical and major findings, and prove the corrected runtime contract.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, validation, non-goals, and guardrails map to the brief stakes.

## Objective

Review the implemented `theme_astral` prompt contract adversarially, then correct every accepted critical or major finding in the same story scope.
The result must prove that `theme_astral_llm_input_v1`, provider payload shape, interpretation material, delivery profile rules,
output contract, persistence, and old-path closure are coherent and tested.

## Target State

- An adversarial report exists at `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/04-review-adversariale-correction-theme-astral-prompt-contract.md`.
- The report contains verdict, severity-ranked findings, file or line evidence, decisions, applied corrections, tests, commands, and residual risks.
- Accepted critical and major findings are corrected inside the `theme_astral` backend prompt contract perimeter.
- `interpretation_material` reaches the LLM payload from audited table-backed or runtime-owned interpretation sources.
- The provider payload JSON skeleton is identical across delivery profiles.
- Commercial plan labels remain backend-only and are not emitted to the LLM payload.
- The output contract and versioned persistence surfaces remain explicit and test-backed.
- Active old carriers such as `chart_json` and `natal_data` cannot drive `theme_astral` prompt construction.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-369-audit-review-adversariale-correction-theme-astral-prompt-contract.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-369`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through scoped resolver output.
- Evidence 4: CS-361 through CS-368 story files were targeted as same-domain sibling contracts.
- Evidence 5: targeted `rg` found `chart_json`, `natal_data`, `legacy`, and `output_contract` in backend app or tests.
- Repository structure alert: `_condamad/audits/theme-astral-prompt-contract` is absent in this workspace.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract` is absent in this workspace.
- Repository structure alert: implementation must create missing audit or architecture directories/files that remain in scope.
- Registry gap: no exact guardrail covers adversarial correction of the `theme_astral` prompt contract.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Adversarial review of CS-361, CS-362, CS-363, CS-364, CS-365, CS-366, CS-367, and CS-368 deliverables.
  - Backend `theme_astral` prompt contract code, DTOs, builders, seeds, migrations, services, ops, and tests.
  - Corrections for accepted findings inside `theme_astral_llm_input_v1`, `interpretation_material`, provider payload, and persistence.
  - Report creation under `_condamad/audits/theme-astral-prompt-contract/`.
- Out of scope:
  - Frontend UI, auth, i18n, styling, unrelated LLM features, provider calls, and a new architecture rewrite.
  - Broad prompt-generation refactors beyond accepted `theme_astral` findings.
- Explicit non-goals:
  - No new feature outside `theme_astral`.
  - No LLM provider invocation.
  - No durable second prompt-construction path.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits adversarial backend review plus accepted correction work.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only code, tests, seeds, migrations, docs, and audit artifacts required by accepted `theme_astral` findings.
  - Preserve the stable `theme_astral_llm_input_v1` contract intent from CS-363 unless the report proves a defect.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a critical finding requires changing the CS-363 architecture boundary.
- Additional validation rules:
  - Runtime proof must name `pytest`, loaded payload objects, DB schema or migration checks, and targeted `rg` scans.
  - Every accepted finding must map to one correction decision, one changed file set, and one validation evidence item.
  - Findings marked false positive or out of scope must include source evidence and a bounded reason.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, payload builder tests, loaded config, and DB checks prove the runtime prompt contract. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta for accepted findings. |
| Ownership Routing | yes | Canonical owners are required across domain, service, ops, migrations, and tests. |
| Allowlist Exception | no | No broad allowlist handling is authorized for old prompt carriers or plan labels. |
| Contract Shape | yes | `theme_astral_llm_input_v1` and provider JSON fields have exact shape rules. |
| Batch Migration | no | This story is not a planned batch conversion across unrelated domains. |
| Reintroduction Guard | yes | Old carriers and duplicate prompt paths must stay inactive for `theme_astral`. |
| Persistent Evidence | yes | The report and validation artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The adversarial report covers all required axes. | Evidence profile: json_contract_shape; `python` checks report headings. |
| AC2 | Each real finding has a severity. | Evidence profile: baseline_before_after_diff; `python` parses report finding rows. |
| AC3 | Accepted critical findings are closed or blocked. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests`. |
| AC4 | Accepted major findings are closed or blocked. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests`. |
| AC5 | `interpretation_material` reaches the LLM payload. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration`. |
| AC6 | The provider payload skeleton is profile-stable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration`. |
| AC7 | Commercial plan labels stay backend-only. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests`; `rg` scans payload code. |
| AC8 | Active old carriers do not drive `theme_astral`. | Evidence profile: route_absence_runtime; `pytest -q backend/tests/architecture`; `rg` scans old carrier tokens. |
| AC9 | Versioned persistence remains proven. | Evidence profile: json_contract_shape; `pytest -q backend/tests`; DB schema or migration check. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |
| AC11 | Each real finding has source proof. | Evidence profile: baseline_before_after_diff; `python` parses report finding rows. |

## Implementation Tasks

- [ ] Task 1: Read CS-361 through CS-368 stories and generated review outputs as upstream contract context. (AC: AC1)
- [ ] Task 2: Inspect `theme_astral` code, DTOs, builders, seeds, migrations, payloads, and tests. (AC: AC1, AC2)
- [ ] Task 3: Create the adversarial report with verdict, severity, source proof, decision, corrections, commands, and residual risks. (AC: AC1, AC2, AC11)
- [ ] Task 4: Correct accepted critical findings inside the `theme_astral` backend perimeter. (AC: AC3)
- [ ] Task 5: Correct accepted major findings inside the `theme_astral` backend perimeter. (AC: AC4)
- [ ] Task 6: Add tests proving sourced `interpretation_material` reaches provider payload construction. (AC: AC5)
- [ ] Task 7: Add tests proving identical provider payload skeleton across delivery profiles. (AC: AC6)
- [ ] Task 8: Add tests proving plan labels stay backend-only and `delivery_profile` is the LLM-visible derivative. (AC: AC7)
- [ ] Task 9: Add guards proving old carriers do not drive `theme_astral` prompt construction. (AC: AC8)
- [ ] Task 10: Validate persistence or migration evidence for versioned prompt contract structures and texts. (AC: AC9)
- [ ] Task 11: Persist validation output, scans, report path, and review handoff artifacts. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-369-audit-review-adversariale-correction-theme-astral-prompt-contract.md` - source scope.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` - upstream audit scope.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md` - current contract audit scope.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture contract.
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md` - persistence contract.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` - material builder contract.
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md` - provider payload contract.
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md` - old-path closure contract.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md` - closure audit contract.
- `_condamad/audits/theme-astral-prompt-contract/` - expected implementation-created path.
- `_condamad/architecture/theme-astral-prompt-contract/` - expected implementation-created path.
- `_condamad/examples/prompt-generation-cartography/` - existing examples path.
- `_condamad/docs/prompt-generation-cartography/` - existing documentation path.
- `backend/app/domain/**` - domain prompt contract, builders, and interpretation owners.
- `backend/app/services/**` - use-case integration paths.
- `backend/app/ops/**` - operational scripts or seeds.
- `backend/tests/**` - contract, architecture, and regression tests.
- `backend/migrations/versions/**` - versioned persistence changes.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest` over backend tests that instantiate the payload builder, resolver, persistence, and guard behavior.
  - Loaded payload objects for `theme_astral_llm_input_v1`, `interpretation_material`, `delivery_profile`, and `output_contract`.
  - `AST guard`, loaded config, `DB schema`, and generated manifest checks for persistence and boundary proof.
- Secondary evidence:
  - Targeted `rg` scans for old carriers, plan labels, report headings, and contract tokens.
- Static scans alone are not sufficient for this story because:
  - The payload can look correct in source while runtime builder, resolver, or persistence wiring still diverges.

## Contract Shape

- Contract type:
  - Backend prompt input, provider payload JSON, and versioned persistence contract.
- Fields:
  - `theme_astral_llm_input_v1`: stable internal input contract for theme astral prompt construction.
  - `interpretation_material`: sourced interpretive material from audited owners.
  - `delivery_profile`: LLM-visible delivery profile derived from backend commercial plan handling.
  - `astrologer_voice`: style and emphasis influence that must not alter facts or safety rules.
  - `output_contract`: explicit schema constraints for generated answer structure.
- Required fields:
  - `theme_astral_llm_input_v1`
  - `interpretation_material`
  - `delivery_profile`
  - `astrologer_voice`
  - `output_contract`
- Optional fields:
  - none for the canonical provider payload skeleton unless CS-363 authorizes the field as profile-stable.
- Status codes:
  - none; no API route behavior is created by this story.
- Serialization names:
  - JSON keys must remain stable across profiles.
- Frontend type impact:
  - none.
- Generated contract impact:
  - Runtime payload snapshots must prove profile-stable shape and backend-only plan handling.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/baseline-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/baseline-after.txt`
- Expected invariant:
  - The only intended surface delta is accepted `theme_astral` adversarial findings and their direct tests or evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Interpretation material selection | `backend/app/domain/astrology/interpretation/**` | Provider prompt string constants |
| Provider payload assembly | `backend/app/domain/llm/**` or existing canonical LLM owner | API router or frontend |
| Runtime use-case wiring | `backend/app/services/**` | Test fixtures or audit artifacts |
| Operational seed or script evidence | `backend/app/ops/**` | Ad hoc root script |
| Versioned persistence | `backend/migrations/versions/**` and DB model owner | UI or prompt-only file |
| Adversarial report | `_condamad/audits/theme-astral-prompt-contract/**` | `_condamad/stories/**` evidence only |

## Mandatory Reuse / DRY Constraints

- Reuse the existing `theme_astral_llm_input_v1` owner instead of creating a parallel input contract.
- Reuse the existing interpretation material builder or source owner instead of copying sourced texts.
- Reuse the existing delivery profile resolver instead of adding a second plan mapping.
- Keep one canonical output contract reference for the provider payload.
- Keep validation commands centralized in the Validation Plan and persist their output once.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may stay active for `theme_astral` prompt construction.
- No compatibility prompt path may be added for this contract.
- No fallback prompt path may be added for this contract.
- `chart_json` and `natal_data` must not drive the canonical `theme_astral` LLM payload.
- Commercial labels `free`, `basic`, and `premium` must not be emitted as plan labels to the LLM payload.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard exact tokens:
  - `chart_json`
  - `natal_data`
  - `legacy`
  - `free`
  - `basic`
  - `premium`
- Required guard evidence:
  - `pytest -q backend/tests/architecture`
  - `pytest -q backend/tests/llm_orchestration`
  - `rg -n "chart_json|natal_data|legacy|free|basic|premium" backend/app backend/tests`
- The scan may find historical, test-only, or non-theme surfaces only when the report classifies them with source proof.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend business logic must not move into API routers during corrections. | `rg`; architecture `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must point to collected tests. | `pytest`; validation artifact. |
| Registry gap `theme_astral-adversarial-correction` | No exact invariant covers this prompt contract correction scope. | Resolver output persisted. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no frontend file is touched.
- RG-052 frontend CSS namespaces are out of scope because no styling surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Adversarial report | `_condamad/audits/theme-astral-prompt-contract/dated-run/04-review-adversariale-correction-theme-astral-prompt-contract.md` | Keep report. |
| Baseline before | `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/baseline-before.txt` | Before. |
| Baseline after | `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/baseline-after.txt` | After. |
| Guardrail output | `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/guardrails.txt` | Guardrails. |
| Validation output | `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/validation.txt` | Validation. |
| Review output | `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/generated/11-code-review.md` | Review. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist is authorized for old prompt carriers, plan labels, or duplicate prompt paths.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-domain conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/04-review-adversariale-correction-theme-astral-prompt-contract.md` - audit report.
- `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/evidence/**` - validation evidence.
- `backend/app/domain/astrology/interpretation/**` - interpretation material fixes.
- `backend/app/domain/llm/**` - prompt input, payload, resolver, output contract, and persistence fixes.
- `backend/app/services/**` - runtime wiring fixes.
- `backend/app/ops/**` - seed or operational artifact fixes.
- `backend/tests/llm_orchestration/**` - provider payload and delivery profile tests.
- `backend/tests/architecture/**` - boundary and old-carrier guards.
- `backend/tests/unit/**` - domain contract tests.
- `backend/tests/integration/**` - runtime integration tests.
- `backend/migrations/versions/**` - persistence migration fixes.
- `_condamad/docs/prompt-generation-cartography/**` - synthesis docs only when corrected contract changes documented behavior.
- `_condamad/examples/prompt-generation-cartography/**` - examples only when corrected payload changes examples.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope unless a finding proves a direct API boundary defect.
- `backend/app/infra/**` - out of scope unless persistence verification proves a direct infra defect.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from pathlib import Path; p=Path('_condamad/audits/theme-astral-prompt-contract'); assert p.exists()"`
- VC2: from story directory, `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`
- VC3: `python -c "from pathlib import Path as P; assert any(P('_condamad/audits/theme-astral-prompt-contract').rglob('04-review*.md'))"`
- VC4: `rg -n "Verdict|Severite|Decision|Corrections appliquees|Risques residuels" _condamad/audits/theme-astral-prompt-contract`
- VC5: `rg -n "theme_astral_llm_input_v1|interpretation_material|delivery_profile|astrologer_voice|output_contract" app tests`
- VC6: `rg -n "chart_json|natal_data|legacy|free|basic|premium" app tests`
- VC7: `pytest -q backend/tests/llm_orchestration`
- VC8: `pytest -q backend/tests/architecture`
- VC9: `pytest -q backend/tests/unit`
- VC10: `pytest -q backend/tests/integration`
- VC11: `ruff format .`
- VC12: `ruff check .`
- VC13: `pytest -q`

## Regression Risks

- The review could classify a real contract defect as descriptive commentary without a correction decision.
- The payload could keep a stable top-level shape while nested profile data diverges silently.
- `interpretation_material` could be present but not sourced from audited table-backed or runtime-owned material.
- Old carrier tokens could remain legitimate in historical tests while active `theme_astral` runtime use is not isolated.
- Persistence evidence could prove schema presence without proving versioned structure and text content are wired.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python venv before every Python, Ruff, or Pytest command.
- From repository root, run `.\.venv\Scripts\Activate.ps1`, then `cd backend` before backend validation commands.
- Persist command output under the story evidence directory.
- Keep findings tied to file or line proof; do not accept unsupported speculation as a correction driver.

## References

- `_story_briefs/cs-369-audit-review-adversariale-correction-theme-astral-prompt-contract.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md`
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md`
