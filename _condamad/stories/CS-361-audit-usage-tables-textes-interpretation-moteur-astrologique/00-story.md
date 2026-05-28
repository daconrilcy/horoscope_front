# Story CS-361 audit-usage-tables-textes-interpretation-moteur-astrologique: Audit Usage Tables Textes Interpretation Moteur Astrologique
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md`.
- Source problem: current natal provider JSON appears fact-rich but weak in controlled interpretive material from business tables and references.
- Source stakes:
  - User impact: future stories need proof before enriching the astrological engine or LLM input construction.
  - Technical risk: existence of rich texts can be confused with effective runtime usage.
  - Closure expectation: create a timestamped audit report under `_condamad/audits/theme-astral-prompt-contract/`.
  - Forbidden regression: no application, DB, migration, prompt, test, frontend, or provider behavior change.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a sourced read-only audit of interpretive astrology texts and logic sources.

The audit must prove which tables, seeds, files, repositories, builders, projections, LLM inputs, and provider payload JSON use or lose those
interpretive sources before the provider boundary.

## Target State

A timestamped report exists at:
`_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/01-audit-usage-tables-textes-interpretation.md`.

The report contains:

- Executive summary.
- Inventaire des sources de textes.
- Matrice source -> owner -> usage runtime.
- Trace d'appel vers projections et LLM.
- Comparaison avec les JSON provider actuels.
- Tables/textes utilises.
- Tables/textes non utilises.
- Gaps et risques.
- Story candidates for CS-363 through CS-368.

Every identified interpretive source is classified as `used`, `unused`, `legacy`, `test-only`, `seed-only`, `admin-only`, or `unknown`.
The report proves whether rich interpretive texts reach the LLM payload, stop in projections, remain dormant, or exist only in references.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-361`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: mandatory source roots named by the brief exist in this workspace.
- Evidence 5: targeted `rg` found interpretive terms under `backend/app`, `docs`, and `backend/migrations`.
- Evidence 6: targeted `rg` found provider, plan, and `interpretation_hints` terms under prompt-generation examples and docs.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Evidence 8: `resolve_guardrails.py` returned `RG-002` and `RG-022` for this backend prompt audit scope.
- Registry gap: no exact guardrail covers read-only audits of interpretive text source usage in the astrological engine.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `_condamad/docs`, `_condamad/examples`, and `docs` exist.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Specialized audit under `_condamad/audits/theme-astral-prompt-contract/`.
  - DB models, migrations, repositories, seeds, ops scripts, and reference files that contain astrological interpretive text or logic.
  - Classification by sign, planet, house, aspect, dominance, dignity, rulership, advanced condition, structural profile, and pattern.
  - Call tracing from natal engine and projection builders to LLM input builders and provider payload examples.
  - Comparison with `free`, `basic`, and `premium` JSON examples from prompt-generation cartography.
  - Classification of used, unused, legacy, test-only, seed-only, admin-only, and unknown sources.
  - Candidate follow-up stories for CS-363 through CS-368.
- Out of scope:
  - Backend runtime changes, database schema changes, migrations, prompt edits, provider calls, frontend UI, auth, i18n, styling, and build tooling.
  - Redefining the target contract for enriched interpretive material; that belongs to CS-363.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No implementation code change.
  - No route, service, builder, repository, seed, migration, prompt, provider, or test behavior change.
  - No frontend route, screen, client generation, or UI validation.
  - No real LLM or provider call.

Named brief primitives in scope:

- `tables`
- `fichiers`
- `seeds`
- `modeles`
- `textes interpretatifs`
- `moteur natal`
- `builders de projections`
- `builders LLM`
- `JSON provider`
- `interpretation_hints`
- `story candidates CS-363 to CS-368`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend astrological interpretation usage audit contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the audit report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep migrations, seeds, prompt docs, and prompt examples unchanged.
  - Record follow-up candidate stories without implementing them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: source evidence cannot classify whether a text source reaches projections, LLM inputs, or provider payloads.
- Additional validation rules:
  - The report must cite concrete paths and symbol names for every classified source owner.
  - Runtime usage claims must use `AST guard`, targeted `rg`, or bounded call-trace evidence.
  - Provider payload claims must cite `free`, `basic`, and `premium` JSON example paths.
  - Source classification must use only `used`, `unused`, `legacy`, `test-only`, `seed-only`, `admin-only`, or `unknown`.
  - Story candidates must map gaps to CS-363 through CS-368 without implementing them.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source traces, `AST guard`, targeted `rg`, and provider examples prove text usage. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is audit evidence. |
| Ownership Routing | yes | Text owners, repositories, builders, projections, and audit artifacts must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The report has required inventory, matrices, call trace, comparison, gaps, and candidates. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Runtime code, prompts, DB schema, migrations, and provider behavior must stay unchanged. |
| Persistent Evidence | yes | Report, source scans, classification matrix, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The interpretive text usage audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Mandatory report sections are present. | Evidence profile: json_contract_shape; `rg` checks required headings in the report. |
| AC3 | Interpretive text sources are inventoried. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks source family labels in the report. |
| AC4 | Every source has one usage status. | Evidence profile: json_contract_shape; `python` checks allowed status labels in the report. |
| AC5 | Owner citations are present. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks owner path and symbol citations. |
| AC6 | Call traces to projections are documented. | Evidence profile: ast_architecture_guard; `rg` checks projection builder and service symbols. |
| AC7 | LLM input handoff is documented. | Evidence profile: ast_architecture_guard; `rg` checks LLM input builder and gateway terms. |
| AC8 | Provider JSON examples are cited. | Evidence profile: json_contract_shape; `rg` checks free, basic, premium, and provider payload terms. |
| AC9 | Unused text groups are separated. | Evidence profile: baseline_before_after_diff; `rg` checks used and unused report sections. |
| AC10 | Gaps become CS-363 to CS-368 candidates. | Evidence profile: json_contract_shape; `rg` checks story candidate identifiers. |
| AC11 | Application code remains unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded git status app surfaces. |
| AC12 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and baseline source availability artifact. (AC: AC1, AC12)
- [ ] Task 2: Inventory DB models, migrations, repositories, seeds, ops scripts, and references with interpretive text. (AC: AC3, AC4)
- [ ] Task 3: Classify sources by sign, planet, house, aspect, dominance, dignity, rulership, condition, profile, and pattern. (AC: AC3)
- [ ] Task 4: Trace source owners through natal engine, projections, LLM input builders, and provider handoff. (AC: AC5, AC6, AC7)
- [ ] Task 5: Compare existing sources against `free`, `basic`, and `premium` provider JSON examples. (AC: AC8)
- [ ] Task 6: Separate used, unused, legacy, test-only, seed-only, admin-only, and unknown text groups. (AC: AC4, AC9)
- [ ] Task 7: Identify texts used then lost before LLM payload construction. (AC: AC6, AC7, AC9)
- [ ] Task 8: Convert gaps into candidate stories for CS-363 through CS-368. (AC: AC10)
- [ ] Task 9: Run validation scans, persist command output, and confirm runtime files remain unchanged. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md` - source scope and acceptance criteria.
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/*.json` - provider JSON examples.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/*.json` - provider JSON examples.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - current prompt construction by plan.
- `backend/app/domain/astrology/**` - natal engine, interpretive runtime, projections, and domain builders.
- `backend/app/services/**` - LLM generation and application service traces.
- `backend/app/infra/db/models/**` - DB models that may contain interpretive text fields.
- `backend/app/infra/db/repositories/**` - repository owners for DB-backed text sources.
- `backend/app/ops/**` - provisioning, seed, or operational text sources.
- `backend/migrations/versions/**` - schema and seeded table history.
- `docs/recherches astro/**` - reference documents with interpretive material.
- `backend/tests/**` - tests that prove runtime usage, dormant sources, or test-only fixtures.

## Runtime Source of Truth

- Primary source of truth:
  - Backend source files, migrations, docs, examples, and tests listed in Files to Inspect First.
  - `AST guard` or bounded source trace for owners, builders, repositories, projections, and LLM handoff symbols.
  - Targeted `rg` over backend and docs for interpretive text terms.
  - Targeted `rg` over prompt-generation JSON examples for `free`, `basic`, `premium`, `provider`, and `interpretation_hints`.
- Secondary evidence:
  - Targeted `rg` scans over the generated audit report for required sections, status labels, and story candidate identifiers.
- Static scans alone are not sufficient for this story because:
  - The audit must distinguish source existence from effective runtime use, projection loss, LLM input visibility, and provider payload presence.

## Contract Shape

- Contract type:
  - Timestamped interpretive text usage audit report.
- Fields:
  - `Source`: table, model, migration, repository, seed, ops file, reference file, builder, projection, test, or JSON example path.
  - `Family`: sign, planet, house, aspect, dominance, dignity, rulership, advanced condition, structural profile, pattern, or mixed.
  - `Owner`: canonical file path plus symbol, table, repository, builder, service, or document owner.
  - `Usage status`: used, unused, legacy, test-only, seed-only, admin-only, or unknown.
  - `Runtime path`: source-to-engine, source-to-projection, source-to-LLM-input, provider-payload, blocked, or not active.
  - `Evidence`: source path, symbol, scan, `AST guard`, JSON path, test path, or bounded report note.
  - `Gap`: no gap, dormant source, lost before LLM, owner ambiguity, missing test, contract gap, or needs-user-decision.
  - `Story candidate`: none, CS-363, CS-364, CS-365, CS-366, CS-367, or CS-368.
- Required report sections:
  - `Executive summary`
  - `Inventaire des sources de textes`
  - `Matrice source -> owner -> usage runtime`
  - `Trace d'appel vers projections et LLM`
  - `Comparaison avec les JSON provider actuels`
  - `Tables/textes utilises`
  - `Tables/textes non utilises`
  - `Gaps et risques`
  - `Story candidates`
- Required fields:
  - Source
  - Family
  - Owner
  - Usage status
  - Runtime path
  - Evidence
  - Gap
  - Story candidate
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - Matrix headings are emitted exactly as listed in this contract shape.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; no OpenAPI, generated frontend contract, or prompt schema change is in scope.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/interpretive-source-scan.txt`
- Expected invariant:
  - The only intended repository surface delta is the CS-361 audit report and CS-361 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Interpretive text usage audit report | `_condamad/audits/theme-astral-prompt-contract/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/` | `backend/tests/**` |
| Source usage classification | CS-361 audit report matrix | runtime code comments |
| Candidate story list | CS-361 audit report section | prompt docs direct edit |
| Provider example comparison | CS-361 audit report section | generated JSON overwrite |

## Mandatory Reuse / DRY Constraints

- Reuse the source paths from the brief instead of creating a parallel source list.
- Reuse the prompt-generation cartography examples and docs as comparison evidence.
- Reuse existing source symbols and tests as evidence instead of copying runtime code into the report.
- Use one canonical usage status vocabulary across the executive summary, matrix, used section, unused section, and candidates.
- Keep validation commands centralized in the Validation Plan and persist their output once.
- Do not duplicate CS-343 through CS-360 cartography content outside the sections required to prove this audit scope.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be introduced or endorsed by this audit.
- No compatibility prompt carrier may be introduced or endorsed by this audit.
- No fallback prompt carrier may be introduced or endorsed by this audit.
- No hidden residual work may be left outside gap, blocker, or candidate-story labels.
- Do not edit backend runtime files, backend tests, frontend files, migrations, prompt docs, prompt examples, or guardrail registry entries.
- Do not treat a DB table, seed, reference file, or test fixture as used unless a call trace reaches projections, LLM inputs, or provider JSON.

## Reintroduction Guard

- The report must preserve separate classifications for source existence, runtime use, projection reachability, LLM input reachability, and provider payload presence.
- The report must include deterministic `rg` guards for interpretive terms, `interpretation_hints`, provider JSON examples, and story candidates.
- The report must not replace unknown usage with a broad assumed-used status.
- The validation output must include a bounded status guard proving backend, frontend, migration, prompt docs, and prompt examples are unchanged.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend API layout remains source-classified, not edited. | `rg` source trace; app status guard. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation commands use collected backend and audit paths. | `pytest` path references; validation artifact. |
| Registry gap | No exact guardrail covers interpretive text usage audits. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-011` backend DB test fixtures is out of scope because no DB test fixture is added or modified.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/source-availability.txt` | Prove required sources existed. |
| Interpretive source scan | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/interpretive-source-scan.txt` | Store targeted scans. |
| Provider JSON comparison | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/provider-json-comparison.txt` | Store scans. |
| Report shape check | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/report-shape-check.txt` | Prove report sections. |
| Validation output | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/validation.txt` | Store validation commands. |
| Review | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/01-audit-usage-tables-textes-interpretation.md` - audit deliverable.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/source-availability.txt` - source evidence.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/interpretive-source-scan.txt` - source scan.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/provider-json-comparison.txt` - JSON scan.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/report-shape-check.txt` - report shape evidence.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - inspect existing LLM astrology input coverage.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - inspect prompt payload boundary coverage.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - inspect architecture payload guards.
- `backend/tests/unit/domain/astrology/test_astrology_full_data_contract.py` - inspect full astrology data contract coverage.

Files not expected to change:

- `backend/app/**` - out of scope; audit-only story must not change runtime code.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is touched.
- `_condamad/docs/prompt-generation-cartography/**` - out of scope; current docs are evidence only.
- `_condamad/examples/prompt-generation-cartography/**` - out of scope; JSON examples are evidence only.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run VC10 from `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique`.

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/audits/theme-astral-prompt-contract').exists()"`
- VC2: `rg -n "Executive summary|Inventaire des sources de textes|Story candidates" _condamad/audits/theme-astral-prompt-contract`
- VC3: `rg -n "used|unused|legacy|test-only|seed-only|admin-only|unknown" _condamad/audits/theme-astral-prompt-contract`
- VC4: `rg -n "interpret|keyword|texte|description|meaning|profile|dignit|rulership|condition|aspect|dominant" backend/app docs backend/migrations`
- VC5: `rg -n "free|basic|premium|provider payload|interpretation_hints" _condamad/audits/theme-astral-prompt-contract _condamad/examples`
- VC6: `rg -n "LLMAstrologyInputV1Builder|ClientInterpretationProjectionV1Builder|LLMGateway|provider" _condamad/audits/theme-astral-prompt-contract`
- VC7: `rg -n "CS-363|CS-364|CS-365|CS-366|CS-367|CS-368" _condamad/audits/theme-astral-prompt-contract`
- VC8: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC9: `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC10: `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`
- VC11: `python -c "import subprocess; p=['backend/app','backend/tests','frontend/src','backend/migrations']; subprocess.run(['git','diff','--quiet','--',*p], check=True)"`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

## Regression Risks

- The audit could list text sources without proving whether the runtime consumes them.
- The audit could treat `interpretation_hints` as equivalent to rich controlled interpretive text.
- The audit could miss texts present only in seeds, migrations, references, tests, or admin-only paths.
- The audit could conflate projection-visible data with provider payload material.
- The audit could create follow-up candidates that do not map to CS-363 through CS-368.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Do not make real provider calls.
- Do not modify backend runtime code, backend tests, frontend files, migrations, prompt docs, prompt examples, or guardrail registry entries.
- Persist validation output under the CS-361 story evidence folder.

## References

- `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/*.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/*.json`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `backend/app/domain/astrology/**`
- `backend/app/services/**`
- `backend/app/infra/db/models/**`
- `backend/app/infra/db/repositories/**`
- `backend/app/ops/**`
- `backend/migrations/versions/**`
- `docs/recherches astro/**`
- `backend/tests/**`
