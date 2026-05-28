# Story CS-368 audit-cloture-bascule-theme-astral-prompt-contract: Audit Cloture Bascule Theme Astral Prompt Contract
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-368-audit-cloture-bascule-theme-astral-prompt-contract.md`.
- Source problem: after CS-361 to CS-367, the `theme_astral` prompt contract needs a closure verdict.
- Source stakes:
  - User impact: closure must not validate the switch while hidden old runtime paths still influence the prompt payload.
  - Technical risk: provider shape, DB versioning, table material, or plan hiding can look complete while one proof is missing.
  - Closure expectation: create one timestamped closure audit report with a clear verdict and residual risks.
  - Forbidden regression: no code, migration, test, seed, JSON example, prompt architecture, or provider behavior change.
- Source-alignment review: PASS. Objective, ACs, tasks, evidence, non-goals, and guardrails map to the closure stakes.

## Objective

Produce the final closure audit for the `theme_astral` prompt contract switch after CS-361 through CS-367.

The report must give a non-ambiguous verdict and prove contract uniqueness, versioning, interpretation-table material, stable delivery profiles,
backend-only commercial plan handling, DB persistence, and absence of active old `theme_astral` runtime paths.

## Target State

A timestamped report exists at:
`_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/03-audit-cloture-bascule-theme-astral-prompt-contract.md`.

The report contains:

- Verdict.
- Statut des criteres CS-361 a CS-367.
- Preuve d'utilisation des textes d'interpretation.
- Preuve de structure stable entre delivery profiles.
- Preuve de non-exposition du plan commercial.
- Preuve de persistence/versioning DB.
- Preuve de suppression legacy.
- Commandes executees.
- Risques residuels.

The verdict must use exactly one of these outcomes: `valide`, `valide avec risques residuels acceptes`, or `invalide`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-368-audit-cloture-bascule-theme-astral-prompt-contract.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-368`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: CS-361 through CS-367 story files were read as closure prerequisites.
- Evidence 5: `_condamad/stories/regression-guardrails.md` was consulted through scoped `resolve_guardrails.py`.
- Evidence 6: resolver returned `RG-002` and `RG-022` for this audit, backend, prompt-contract, and validation scope.
- Repository structure alert: `_condamad/audits/theme-astral-prompt-contract` is absent in this workspace.
- Repository structure alert: `_condamad/architecture/theme-astral-prompt-contract` is absent in this workspace.
- Repository structure alert: implementation must create the missing report directory and must treat missing prerequisite deliverables as blockers.
- Registry gap: no exact guardrail covers final closure audits for the `theme_astral` prompt contract switch.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Read-only closure audit under `_condamad/audits/theme-astral-prompt-contract/`.
  - Reading CS-361, CS-362, CS-363, CS-364, CS-365, CS-366, and CS-367 deliverables.
  - Re-reading final backend code, migrations, seeds, versioning, tests, guardrails, examples, and audit artifacts named by the brief.
  - Verification that `interpretation_material` reaches the LLM payload from table-backed or audited interpretation owners.
  - Verification that provider payload structure is stable between delivery profiles.
  - Verification that commercial plan labels stay backend-only.
  - Verification that `theme_astral` prompt contract persistence and versioning are DB-backed.
  - Verification that active old `theme_astral` runtime paths are absent.
  - Conversion of unresolved gaps into explicit risks or follow-up story candidates.
- Out of scope:
  - Backend code edits, migrations, seed edits, tests, JSON example changes, prompt architecture changes, frontend UI, auth, i18n, styling, and build tooling.
  - Real LLM provider calls.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No implementation code change.
  - No migration file change.
  - No test creation or test edit.
  - No provider JSON rewrite.
  - No frontend route, screen, client generation, or UI validation.
  - No architecture re-decision.

Named brief primitives in scope:

- `CS-361`
- `CS-362`
- `CS-363`
- `CS-364`
- `CS-365`
- `CS-366`
- `CS-367`
- `theme_astral`
- `interpretation_material`
- `delivery_profile`
- `astrologer_voice`
- `plan commercial`
- `backend-only`
- `persistence/versioning DB`
- `migrations`
- `seeds`
- `tests`
- `guardrails`
- `exemples JSON`
- `legacy runtime actif`
- `rapport court de cloture`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this read-only closure audit over a multi-story backend prompt contract switch.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the closure audit report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend tests unchanged.
  - Keep migrations and seeds unchanged.
  - Keep prompt architecture, examples, frontend files, and guardrail registry entries unchanged.
  - Convert any unresolved closure gap into an explicit residual risk or follow-up story candidate.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a closure gap prevents a `valide` verdict and cannot be accepted as a named residual risk.
- Additional validation rules:
  - The report must cite CS-361 through CS-367 deliverable paths or state the exact missing deliverable blocker.
  - Runtime closure claims must use `AST guard`, targeted `rg`, loaded config, DB schema, or `pytest` evidence.
  - The report must prove table-backed `interpretation_material` reaches provider payload construction or mark the verdict `invalide`.
  - The report must prove `free`, `basic`, and `premium` share a stable provider structure or mark the verdict `invalide`.
  - The report must prove commercial plan labels remain backend-only or mark the verdict `invalide`.
  - The report must prove DB persistence/versioning for prompt, input, response, delivery, persona, and assembly contracts.
  - The report must name every residual old `theme_astral` runtime path, seed, prompt, mock, or test artifact.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, `pytest`, loaded config, DB schema, and scans prove closure claims. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is audit evidence. |
| Ownership Routing | yes | Closure report, evidence, source stories, backend code, DB, and examples must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit-only story. |
| Contract Shape | yes | The report has required verdict, criteria, proofs, commands, and residual risk sections. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Old prompt paths, plan leakage, and unstable provider shapes must stay flagged. |
| Persistent Evidence | yes | Report, scans, command outputs, and review handoff must persist for closure review. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The closure audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | The verdict is non-ambiguous. | Evidence profile: json_contract_shape; `rg` checks the allowed verdict labels. |
| AC3 | CS-361 to CS-367 criteria are covered. | Evidence profile: json_contract_shape; `rg` checks each story ID in the report. |
| AC4 | Interpretation material reaches the payload. | Evidence profile: ast_architecture_guard; `AST guard`; `pytest` checks material handoff. |
| AC5 | Delivery profile structures are stable. | Evidence profile: json_contract_shape; `pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`. |
| AC6 | Commercial plan stays backend-only. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks plan visibility. |
| AC7 | DB versioning proof is present. | Evidence profile: baseline_before_after_diff; `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`. |
| AC8 | Old runtime paths are audited. | Evidence profile: targeted_forbidden_symbol_scan; `AST guard`; `pytest`; `rg` checks old path tokens. |
| AC9 | Residual risks are decided. | Evidence profile: json_contract_shape; `rg` checks risk acceptance and follow-up labels. |
| AC10 | Protected sources stay unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded git diff. |
| AC11 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and source availability artifact. (AC: AC1, AC11)
- [ ] Task 2: Read CS-361 through CS-367 deliverables and map each criterion into the closure report. (AC: AC3)
- [ ] Task 3: Re-read final code, migrations, seeds, tests, guardrails, examples, audits, and architecture artifacts named by the brief. (AC: AC3, AC10)
- [ ] Task 4: Prove `interpretation_material` comes from table-backed or audited interpretation owners and reaches payload construction. (AC: AC4)
- [ ] Task 5: Compare delivery profile payload structures across `free`, `basic`, and `premium`. (AC: AC5)
- [ ] Task 6: Prove commercial plan labels stay backend-only and do not appear in provider-visible payloads. (AC: AC6)
- [ ] Task 7: Prove persistence and versioning through DB models, migrations, seeds, and active-read tests. (AC: AC7)
- [ ] Task 8: Audit old theme astral runtime paths, prompt carriers, seeds, mocks, and tests for active usage. (AC: AC8)
- [ ] Task 9: Write the verdict and classify every residual risk as accepted, blocker, or follow-up story. (AC: AC2, AC9)
- [ ] Task 10: Run validation commands, persist output, and prove protected sources are unchanged. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-368-audit-cloture-bascule-theme-astral-prompt-contract.md` - source scope.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` - prerequisite audit contract.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md` - provider JSON audit contract.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` - architecture contract.
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md` - persistence contract.
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` - material builder contract.
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md` - provider payload builder contract.
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md` - bigbang switch contract.
- `_condamad/audits/theme-astral-prompt-contract/**` - expected implementation-created path for audit reports.
- `_condamad/architecture/theme-astral-prompt-contract/**` - expected implementation-created path for architecture report.
- `_condamad/examples/prompt-generation-cartography/**` - JSON payload examples.
- `backend/app/domain/llm/**` - prompt contract, runtime, configuration, and gateway owners.
- `backend/app/domain/astrology/interpretation/**` - interpretation material and theme astral input owners.
- `backend/app/services/llm_generation/natal/**` - natal generation runtime boundary.
- `backend/app/ops/llm/bootstrap/**` - seeds and bootstrap registration surfaces.
- `backend/tests/**` - validation and guard test surfaces.
- `backend/migrations/versions/**` - DB versioning and migration history.

## Runtime Source of Truth

- Primary source of truth:
  - CS-361 through CS-367 implemented deliverables and their evidence artifacts.
  - Backend source files, migrations, seeds, tests, examples, audits, and architecture artifacts listed in Files to Inspect First.
  - `AST guard` for ownership, old-path absence, and prompt payload assembly boundaries.
  - `pytest` for provider payload shape, material handoff, persistence, migration, and bigbang guard behavior.
  - Loaded config and DB schema checks for active contract persistence and versioning.
- Secondary evidence:
  - Targeted `rg` scans for report headings, verdict labels, `interpretation_material`, `delivery_profile`, backend-only plan handling, and old path tokens.
  - Bounded git diff checks proving backend, tests, migrations, examples, docs, frontend, and guardrail registry remain unchanged.
- Static scans alone are not sufficient for this story because:
  - Closure depends on runtime handoff, DB-backed versioning, loaded builder behavior, and absence of active old prompt paths.

## Contract Shape

- Contract type:
  - Timestamped closure audit report.
- Fields:
  - `Verdict`: valide, valide avec risques residuels acceptes, or invalide.
  - `CS-361 to CS-367 criteria status`: per-story status with proof and blocker notes.
  - `Interpretation material proof`: table-backed or audited source, runtime handoff, and payload evidence.
  - `Delivery profile proof`: stable provider skeleton comparison across delivery profiles.
  - `Commercial plan proof`: backend-only handling and provider-visible absence.
  - `Persistence/versioning proof`: DB, migration, seed, active-read, prompt, input, response, delivery, persona, and assembly evidence.
  - `Legacy removal proof`: old runtime path, seed, prompt, mock, test, example, and docs scan result.
  - `Commands executed`: exact commands and artifact paths.
  - `Residual risks`: accepted residual risk, blocker, or follow-up story candidate.
- Required fields:
  - Verdict
  - CS-361 to CS-367 criteria status
  - Interpretation material proof
  - Delivery profile proof
  - Commercial plan proof
  - Persistence/versioning proof
  - Legacy removal proof
  - Commands executed
  - Residual risks
- Optional fields:
  - none.
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Report headings are emitted exactly as listed in Target State.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; this audit validates existing generated or runtime contracts without changing them.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/closure-report-shape-check.txt`
- Expected invariant:
  - The only intended repository surface delta is the CS-368 closure audit report and CS-368 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Closure audit report | `_condamad/audits/theme-astral-prompt-contract/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/` | `backend/tests/**` |
| Closure verdict | CS-368 report section | runtime code comments |
| Residual risks | CS-368 report section | silent implementation notes |
| Follow-up story candidates | CS-368 report section | code TODO markers |
| Review output | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/generated/` | audit report body |

## Mandatory Reuse / DRY Constraints

- Reuse CS-361 through CS-367 deliverables and evidence instead of re-authoring their full content.
- Reuse existing test, migration, seed, architecture, audit, and example artifacts as closure evidence.
- Use one verdict vocabulary across the summary, criteria status, and residual risk sections.
- Use one residual risk vocabulary: accepted, blocker, or follow-up story.
- Keep validation commands centralized in the Validation Plan and persist their output once.
- Do not duplicate backend code, prompt content, JSON examples, or architecture decisions inside the report.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy prompt path may be treated as closed without active-use evidence.
- No compatibility prompt path may be accepted as a durable closure outcome.
- No fallback prompt path may hide a remaining theme astral runtime route.
- No hidden residual work may be left outside blocker, accepted risk, or follow-up story labels.
- Do not edit backend runtime files, backend tests, frontend files, migrations, seeds, JSON examples, architecture docs, or guardrail registry entries.
- Do not call a real LLM provider.

## Reintroduction Guard

- The report must include deterministic `rg` guards for old carriers, old prompt constants, old use cases, seeds, mocks, and tests.
- The report must include `pytest` proof for material handoff, provider payload structure, DB persistence, and bigbang guard behavior.
- The report must include bounded checks proving protected repository surfaces remain unchanged by the audit implementation.
- The report must classify every unresolved old `theme_astral` runtime path as accepted risk, blocker, or follow-up story.
- The report must not upgrade a missing prerequisite deliverable into a valid verdict.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend app and API surfaces remain audit evidence, not edit targets. | `AST guard`; git diff guard. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths stay explicit and collected. | `pytest` paths; validation artifact. |
| Registry gap | No exact guardrail covers final theme astral prompt-contract closure audits. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because no entitlement documentation surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/source-availability.txt` | Prove required sources. |
| Closure criteria map | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/closure-criteria-map.md` | Map CS-361 to CS-367. |
| Runtime proof | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/runtime-proof.txt` | Store runtime checks. |
| DB versioning proof | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/db-versioning-proof.txt` | Store DB checks. |
| Legacy scan | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/legacy-scan.txt` | Store old-path scan. |
| Report shape check | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/closure-report-shape-check.txt` | Prove report shape. |
| Validation output | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/validation.txt` | Store validation commands. |
| Review output | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/generated/11-code-review.md` | Keep review separate. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/03-audit-cloture-bascule-theme-astral-prompt-contract.md` - audit deliverable.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/source-availability.txt` - source evidence.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/closure-criteria-map.md` - criteria evidence.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/runtime-proof.txt` - runtime evidence.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/db-versioning-proof.txt` - DB evidence.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/legacy-scan.txt` - old-path scan.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - provider shape, delivery profile, and plan hiding.
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` - runtime payload handoff.
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py` - persistence and active-read behavior.
- `backend/tests/integration/test_theme_astral_prompt_contract_migration.py` - migration and ORM metadata coherence.
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` - canonical prompt path.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` - old-path guard.

Files not expected to change:

- `backend/app/**` - out of scope; audit-only story must not change runtime code.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `backend/migrations/**` - out of scope; no migration is touched.
- `backend/app/ops/llm/bootstrap/**` - out of scope; seeds are evidence only.
- `_condamad/examples/prompt-generation-cartography/**` - out of scope; JSON examples are evidence only.
- `_condamad/architecture/theme-astral-prompt-contract/**` - out of scope; architecture artifacts are evidence only.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.

- VC1: `python -c "from pathlib import Path; assert Path('../_condamad/audits/theme-astral-prompt-contract').exists()"`
- VC2: `rg -n "Verdict|Statut des criteres CS-361 a CS-367|Risques residuels" ..\_condamad\audits\theme-astral-prompt-contract`
- VC3: `rg -n "CS-361|CS-362|CS-363|CS-364|CS-365|CS-366|CS-367" ..\_condamad\audits\theme-astral-prompt-contract`
- VC4: `pytest -q tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- VC5: `pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- VC6: `pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py`
- VC7: `pytest -q tests/integration/test_theme_astral_prompt_contract_migration.py`
- VC8: `pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- VC9: `pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py`
- VC10: `rg -n "interpretation_material|delivery_profile|backend-only" ..\_condamad\audits\theme-astral-prompt-contract`
- VC11: `rg -n "chart_json|natal_data|llm_astrology_input_v1|natal_interpretation_short" app tests`
- VC12: `rg -n "NATAL_SHORT_PROMPT|NATAL_COMPLETE_PROMPT|theme_astral_prompt_v1" app tests`
- VC13: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','app','tests','migrations'], check=True)"`
- VC14: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','../frontend/src'], check=True)"`
- VC15: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/evidence/validation.txt').exists()"`
- VC16: `ruff check .`
- VC17: `pytest -q tests --tb=short`
- VC18: `rg -n "audit-cloture-bascule-theme-astral|Verdict|interpretation_material|delivery_profile|legacy|backend-only" ..\_condamad\audits\theme-astral-prompt-contract`

## Regression Risks

- The audit could validate closure while a seed or old prompt carrier remains active.
- The audit could accept stable examples while runtime payload structure differs by delivery profile.
- The audit could miss commercial plan leakage inside serialized payload content.
- The audit could treat `interpretation_material` key presence as enough without proving table-backed material reaches the payload.
- The audit could accept persistence/versioning without proving active DB-backed read behavior.
- The audit could leave residual risks unnamed instead of converting them into accepted risks, blockers, or follow-up stories.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Use `backend/pyproject.toml` as the only Python dependency source.
- Do not make real provider calls.
- Do not modify backend runtime code, backend tests, migrations, seeds, frontend files, examples, architecture artifacts, or the guardrail registry.
- Persist validation output under the CS-368 story evidence folder.

## References

- `_story_briefs/cs-368-audit-cloture-bascule-theme-astral-prompt-contract.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md`
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md`
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md`
- `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md`
- `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md`
- `_condamad/audits/theme-astral-prompt-contract/**`
- `_condamad/architecture/theme-astral-prompt-contract/**`
- `_condamad/examples/prompt-generation-cartography/**`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/llm_generation/natal/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/**`
- `backend/migrations/versions/**`
