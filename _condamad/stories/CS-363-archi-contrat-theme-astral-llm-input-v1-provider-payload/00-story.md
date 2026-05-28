# Story CS-363 archi-contrat-theme-astral-llm-input-v1-provider-payload: Define Theme Astral LLM Input V1 Architecture
Status: ready-to-dev

## Trigger / Source

- Mode: Repo-informed story from architecture brief.
- Source brief: `_story_briefs/cs-363-archi-contrat-theme-astral-llm-input-v1-et-provider-payload.md`.
- Source problem: theme astral needs one stable prompt/provider architecture for `free`, `basic`, and `premium`.
- Source stakes:
  - User impact: future implementation stories need one target contract before changing prompt, runtime, DB, or payload owners.
  - Technical risk: plan-specific values can be confused with structural drift, or a parallel prompt contract can survive.
  - Closure expectation: create a timestamped architecture report with decisions, persistence, guardrails, and CS-364 to CS-368 slices.
  - Forbidden regression: no application code, migration, prompt seed, provider payload, frontend, DB schema, or runtime behavior change.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce the architecture report for `theme_astral_llm_input_v1` and the stable theme astral provider payload.

The report must define one feature-level JSON skeleton, the internal contract, plan-derived delivery profile, astrologer voice,
interpretation material, output contract versioning, DB persistence strategy, and a bigbang transition sequence.

## Target State

A timestamped report exists at:
`_condamad/architecture/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/archi-theme-astral-prompt-contract-v1.md`.

The report contains:

- Executive summary.
- Decisions d'architecture.
- Non-goals.
- Squelette provider cible.
- Contrat `theme_astral_llm_input_v1`.
- Bloc `interpretation_material`.
- Bloc `astrologer_voice`.
- Bloc `delivery_profile`.
- Bloc `output_contract`.
- Persistence DB et versioning.
- Integration avec assembly/prompt registry existants.
- Bigbang migration plan.
- Legacy a supprimer.
- Tests et guardrails.
- Risques et decisions ouvertes.

The target provider skeleton is stable for `free`, `basic`, and `premium`. Plans change values, quantities, budgets, and depth only.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-363-archi-contrat-theme-astral-llm-input-v1-et-provider-payload.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-363`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` - audit prerequisite story read.
- Evidence 5: `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md` - audit prerequisite story read.
- Evidence 6: `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - current plan prompt construction read.
- Evidence 7: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current internal LLM input contract read.
- Evidence 8: `backend/app/domain/llm/runtime/contracts.py` and `backend/app/domain/llm/runtime/gateway.py` - runtime contracts read.
- Evidence 9: targeted `rg` checked LLM configuration, DB models, bootstrap seeds, and LLM migrations named by the brief.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - scoped guardrail IDs resolved through `resolve_guardrails.py`.
- Registry gap: no exact guardrail covers architecture-only provider payload contract design for theme astral.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist.
- Assumption risk: CS-361 and CS-362 audit report files may be produced by their own stories before CS-363 implementation starts.

## Domain Boundary

- Domain: condamad-architecture-documentation
- In scope:
  - Architecture report under `_condamad/architecture/theme-astral-prompt-contract/`.
  - Read-only use of CS-361 and CS-362 audit outputs as mandatory architecture inputs.
  - Stable provider JSON skeleton with `runtime_contract`, `safety_contract`, `astrologer_voice`, and `feature_context`.
  - Stable provider JSON skeleton with `delivery_profile`, `input_data`, and `output_contract`.
  - Internal `theme_astral_llm_input_v1` contract boundaries and Pydantic/domain owner recommendations.
  - Plan-derived `delivery_profile` rules for `free`, `basic`, and `premium`.
  - `astrologer_voice` style boundary, with astrological truth owned by engine and tables.
  - `interpretation_material` enriched from tables and engine outputs.
  - Versioned `output_contract`, prompt, structure, and persistence strategy using existing LLM mechanisms.
  - Bigbang transition sequence and follow-up implementation stories CS-364 to CS-368.
- Out of scope:
  - Backend runtime edits, DB migrations, prompt seed edits, provider calls, frontend UI, auth, i18n, styling, and build tooling.
  - Writing final prompt prose, implementing model classes, changing migrations, or executing a real LLM provider request.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No implementation code change.
  - No migration file change.
  - No provider JSON example rewrite.
  - No frontend route, screen, client generation, or UI validation.
  - No real LLM or provider call.

Named brief primitives in scope:

- `theme_astral_prompt_v1`
- `theme_astral_llm_input_v1`
- `feature_context`
- `delivery_profile`
- `astrologer_voice`
- `input_data`
- `interpretation_material`
- `output_contract`
- `free`
- `basic`
- `premium`
- `factory`
- `factories`
- `resolver`
- `runtime`
- `catalog`
- `contract`
- `profile`
- `prompt`
- `renderer`
- `API`
- `DB`
- `migration`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this architecture-only backend LLM contract report.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the architecture report and story evidence artifacts.
  - Keep backend application files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep migrations unchanged.
  - Keep prompt seeds and provider examples unchanged.
  - Record CS-364 to CS-368 as implementation story proposals without implementing them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-361 or CS-362 audit evidence is missing and the report cannot distinguish fact, assumption, and open decision.
- Additional validation rules:
  - The report must include the exact target skeleton keys named by the brief.
  - The report must state that commercial plan remains backend-only.
  - The report must state that `delivery_profile` is resolved before LLM handoff.
  - The report must state that `astrologer_voice` changes style and emphases only.
  - The report must state that `interpretation_material` comes from tables and engine outputs.
  - The report must cite existing LLM assembly, prompt version, persona, output schema, and migration owners.
  - The report must propose CS-364, CS-365, CS-366, CS-367, and CS-368.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Source reports, `AST guard`, `rg`, and owner paths prove architecture claims. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is architecture evidence. |
| Ownership Routing | yes | Architecture, domain contracts, LLM runtime, DB models, prompts, and migrations need clear owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this architecture-only story. |
| Contract Shape | yes | The report has required sections, skeleton keys, internal blocks, persistence, and story proposals. |
| Batch Migration | yes | Bigbang transition sequencing is required by the source brief. |
| Reintroduction Guard | yes | Parallel runtime, hidden plan exposure, and non-table interpretation material must stay forbidden. |
| Persistent Evidence | yes | Report, source scans, validation output, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The architecture report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Mandatory report headings are present. | Evidence profile: json_contract_shape; `rg` checks all required headings in the report. |
| AC3 | The target provider skeleton is fixed. | Evidence profile: json_contract_shape; `rg` checks skeleton keys in the report. |
| AC4 | Plan handling is backend-only. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks plan and `delivery_profile` decisions. |
| AC5 | Astrologer voice boundary is explicit. | Evidence profile: json_contract_shape; `rg` checks `astrologer_voice` style and truth ownership terms. |
| AC6 | Interpretation material ownership is explicit. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks table and engine owners. |
| AC7 | Output contract versioning is explicit. | Evidence profile: json_contract_shape; `rg` checks `output_contract` and versioning terms. |
| AC8 | Persistence strategy cites existing LLM owners. | Evidence profile: ast_architecture_guard; `rg` checks assembly, prompt, schema, persona, and migration owners. |
| AC9 | Bigbang transition is sequenced. | Evidence profile: batch_migration_mapping; `rg` checks bigbang, sequence, and CS-364 to CS-368. |
| AC10 | Application sources remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded git diff for app surfaces. |
| AC11 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Read CS-361 and CS-362 audit reports or record a blocker in the report. (AC: AC1, AC6)
- [ ] Task 2: Create the timestamped architecture folder and baseline source availability artifact. (AC: AC1, AC11)
- [ ] Task 3: Define the stable provider skeleton and required empty object or array behavior. (AC: AC3)
- [ ] Task 4: Define `theme_astral_llm_input_v1` owners, factory helpers, resolver behavior, and runtime handoff. (AC: AC3, AC6)
- [ ] Task 5: Define `delivery_profile` as the only LLM-visible plan derivative. (AC: AC4)
- [ ] Task 6: Define `astrologer_voice` as style, tone, vocabulary, and emphases only. (AC: AC5)
- [ ] Task 7: Define `interpretation_material` from tables, engine outputs, and selected themes. (AC: AC6)
- [ ] Task 8: Define `output_contract` versioning and DB persistence with existing LLM owners. (AC: AC7, AC8)
- [ ] Task 9: Write the bigbang transition plan and CS-364 to CS-368 implementation proposal map. (AC: AC9)
- [ ] Task 10: Run validation scans, persist command output, and confirm protected sources remain unchanged. (AC: AC10, AC11)

## Files to Inspect First

- `_story_briefs/cs-363-archi-contrat-theme-astral-llm-input-v1-et-provider-payload.md` - source scope.
- `_condamad/audits/theme-astral-prompt-contract/**/01-audit-usage-tables-textes-interpretation.md` - required audit input.
- `_condamad/audits/theme-astral-prompt-contract/**/02-audit-json-provider-theme-astral-actuels.md` - required audit input.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - current prompt construction by plan.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - current internal LLM input contract.
- `backend/app/domain/llm/runtime/contracts.py` - runtime transport and resolved plan contracts.
- `backend/app/domain/llm/runtime/gateway.py` - provider handoff and prompt-visible filtering.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical use case contract owner.
- `backend/app/domain/llm/configuration/assembly_resolver.py` - assembly and persona resolution owner.
- `backend/app/domain/llm/configuration/prompt_versions.py` - prompt version owner.
- `backend/app/infra/db/models/llm/llm_assembly.py` - assembly persistence owner.
- `backend/app/infra/db/models/llm/llm_prompt.py` - prompt and use case persistence owner.
- `backend/app/infra/db/models/llm/llm_output_schema.py` - output schema persistence owner.
- `backend/app/infra/db/models/llm/llm_persona.py` - persona and astrologer voice persistence owner.
- `backend/app/ops/llm/bootstrap/use_cases_seed.py` - use case and schema seed owner.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` - assembly taxonomy seed owner.
- `backend/migrations/versions/**llm**` - existing LLM migration history.

## Runtime Source of Truth

- Primary source of truth:
  - CS-361 and CS-362 audit outputs.
  - Current LLM input, runtime, gateway, configuration, DB model, seed, and migration files listed in Files to Inspect First.
  - `AST guard` or bounded `rg` traces for owner, factory, resolver, runtime, catalog, contract, profile, prompt, renderer, API, DB, and migration claims.
- Secondary evidence:
  - Targeted `rg` scans over the generated architecture report for required headings, skeleton keys, and decision terms.
  - Bounded git diff checks proving runtime, tests, migrations, frontend, prompt seeds, and provider examples remain unchanged.
- Static scans alone are not sufficient for this story because:
  - The report must map target architecture decisions to existing owner surfaces and source audit findings.

## Contract Shape

- Contract type:
  - Timestamped architecture report for theme astral LLM input and provider payload.
- Fields:
  - `runtime_contract`: stable runtime metadata block, with backend ownership explicitly separated from provider-visible plan.
  - `safety_contract`: stable safety and non-invention rules.
  - `astrologer_voice`: style, tone, vocabulary, and emphases from astrologer/persona owner.
  - `feature_context`: feature, subfeature, locale, and use-case context without commercial plan leakage.
  - `delivery_profile`: resolved depth, length, selection, and budget profile derived from plan.
  - `input_data.birth_context`: normalized birth context.
  - `input_data.astrological_facts`: calculated facts from engine and stable projections.
  - `input_data.interpretation_material`: table and engine-derived interpretive material.
  - `input_data.selected_themes`: selected themes governed by feature and delivery profile.
  - `input_data.limits`: missing data, unavailable sections, and uncertainty notes.
  - `output_contract`: explicit versioned response schema for the feature.
- Required report sections:
  - `Executive summary`
  - `Decisions d'architecture`
  - `Non-goals`
  - `Squelette provider cible`
  - `Contrat theme_astral_llm_input_v1`
  - `Bloc interpretation_material`
  - `Bloc astrologer_voice`
  - `Bloc delivery_profile`
  - `Bloc output_contract`
  - `Persistence DB et versioning`
  - `Integration avec assembly/prompt registry existants`
  - `Bigbang migration plan`
  - `Legacy a supprimer`
  - `Tests et guardrails`
  - `Risques et decisions ouvertes`
- Required fields:
  - runtime_contract
  - safety_contract
  - astrologer_voice
  - feature_context
  - delivery_profile
  - input_data
  - birth_context
  - astrological_facts
  - interpretation_material
  - selected_themes
  - limits
  - output_contract
- Optional fields:
  - none
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - JSON skeleton keys are emitted exactly as listed in Required fields.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none in this story; implementation stories may later generate schemas from the architecture decision.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/report-shape-check.txt`
- Expected invariant:
  - The only intended repository surface delta is the CS-363 architecture report and CS-363 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Architecture report | `_condamad/architecture/theme-astral-prompt-contract/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/` | `backend/tests/**` |
| Internal LLM input contract decision | CS-363 report section | prompt seed text |
| Provider skeleton decision | CS-363 report section | generated JSON example overwrite |
| Persistence recommendation | CS-363 report section | new migration file |
| Follow-up story map | CS-363 report section | runtime code comments |

## Mandatory Reuse / DRY Constraints

- Reuse CS-361 and CS-362 audit outputs as source evidence instead of re-auditing the same surfaces.
- Reuse existing LLM assembly, prompt version, persona, output schema, and release concepts in the persistence recommendation.
- Reuse current `llm_astrology_input_v1` lessons without creating a second unconstrained internal contract pattern.
- Use one target provider skeleton for `free`, `basic`, and `premium`.
- Keep validation commands centralized in the Validation Plan and persist their output once.
- Do not duplicate final prompt prose in the architecture report.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy runtime path may be proposed as a durable target.
- No compatibility runtime path may be proposed as a durable target.
- No fallback runtime path may be proposed as a durable target.
- No parallel durable prompt contract may remain outside the bigbang transition sequence.
- Do not expose `plan=free/basic/premium` to the LLM provider payload.
- Do not let `astrologer_voice` change astrological truth or table-derived facts.
- Do not invent `interpretation_material` in prompt builders.
- Do not edit backend runtime files, backend tests, frontend files, migrations, prompt seeds, provider examples, or guardrail registry entries.

## Reintroduction Guard

- The report must state that `feature`, `plan`, and `astrologer_id` are backend-known inputs, while commercial plan stays backend-only.
- The report must state that the LLM receives `feature_context`, `delivery_profile`, `astrologer_voice`, `input_data`, and `output_contract`.
- The report must state that all plans share the same key skeleton for a feature.
- The report must require empty arrays or empty objects for absent fields instead of key removal.
- The report must include deterministic `rg` guards for target keys, backend-only plan, table-derived material, output contract, and CS-364 to CS-368.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend API and app paths remain evidence sources, not edited targets. | `rg` source trace; git diff guard. |
| Registry gap | No exact guardrail covers theme astral provider payload architecture design. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because no entitlement surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/source-availability.txt` | Prove required sources. |
| Source scan | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/source-scan.txt` | Store targeted scans. |
| Report shape check | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/report-shape-check.txt` | Prove report sections. |
| Validation output | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/validation.txt` | Store validation commands. |
| Review | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this architecture-only story.

## Batch Migration Plan

- Batch migration plan: required
- Reason: the source brief requires a bigbang transition with no durable double runtime.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| CS-363 | Undecided target contract | Architecture report | None | Report scans | `rg` report check | Missing CS-361 or CS-362 evidence |
| CS-364 | Current internal natal input | `theme_astral_llm_input_v1` | Domain factories | Domain tests | `rg` old carrier scan | Contract owner unresolved |
| CS-365 | Plan-shaped provider payload | Stable provider skeleton | Runtime resolver | Gateway tests | `rg` plan leakage scan | Delivery profile unresolved |
| CS-366 | Unversioned output decisions | Versioned `output_contract` | DB and seeds | Migration tests | `rg` schema owner scan | Persistence owner unresolved |
| CS-367 | Parallel prompt carrier surfaces | Single runtime target | Runtime callers | Integration tests | `rg` old path scan | Provider-capable old path remains |
| CS-368 | Open validation gaps | Closed evidence set | Review process | Full suite | `pytest` and `rg` proof | Any phase evidence missing |

- Stop condition:
  - No provider-capable theme astral runtime uses a parallel prompt carrier after the bigbang story set closes.

## Expected Files to Modify

Likely files:

- `_condamad/architecture/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/archi-theme-astral-prompt-contract-v1.md` - architecture deliverable.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/source-availability.txt` - source evidence.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/source-scan.txt` - source scan.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/report-shape-check.txt` - report shape evidence.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - inspect current prompt payload boundary coverage.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - inspect architecture payload guards.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - inspect current internal LLM input coverage.

Files not expected to change:

- `backend/app/**` - out of scope; architecture-only story must not change runtime code.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is touched.
- `backend/app/ops/llm/bootstrap/**` - out of scope; prompt and assembly seeds are evidence only.
- `_condamad/docs/prompt-generation-cartography/**` - out of scope; current docs are evidence only.
- `_condamad/examples/prompt-generation-cartography/**` - out of scope; JSON examples are evidence only.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run VC14 from `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload`.

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/architecture/theme-astral-prompt-contract').exists()"`
- VC2: `rg -n "Executive summary|Decisions d'architecture|Bigbang migration plan" _condamad/architecture/theme-astral-prompt-contract`
- VC3: `rg -n "runtime_contract|safety_contract|astrologer_voice|feature_context|delivery_profile" _condamad/architecture/theme-astral-prompt-contract`
- VC4: `rg -n "birth_context|astrological_facts|interpretation_material|selected_themes|limits|output_contract" _condamad/architecture/theme-astral-prompt-contract`
- VC5: `rg -n "plan commercial|backend-only|delivery_profile|free|basic|premium" _condamad/architecture/theme-astral-prompt-contract`
- VC6: `rg -n "astrologer_voice|style|ton|vocabulaire|emphases|verite astrologique" _condamad/architecture/theme-astral-prompt-contract`
- VC7: `rg -n "tables|moteur|interpretation_material|engine|source owner" _condamad/architecture/theme-astral-prompt-contract`
- VC8: `rg -n "llm_assembly_configs|llm_prompt_versions|llm_output_schemas|llm_personas" _condamad/architecture/theme-astral-prompt-contract`
- VC9: `rg -n "CS-364|CS-365|CS-366|CS-367|CS-368" _condamad/architecture/theme-astral-prompt-contract`
- VC10: `rg -n "theme_astral_llm_input_v1|output_contract|bigbang|legacy" _condamad/architecture/theme-astral-prompt-contract`
- VC11: `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC12: `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- VC13: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC14: `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`
- VC15: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app','backend/tests'], check=True)"`
- VC16: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','frontend/src','backend/migrations'], check=True)"`
- VC17: `ruff format .`
- VC18: `ruff check .`
- VC19: `pytest -q`

## Regression Risks

- The architecture could define a new contract without a stop condition for old provider-capable prompt carriers.
- The architecture could let plan names leak into provider-visible payloads instead of using resolved delivery profiles.
- The architecture could let astrologer voice modify factual or interpretive truth.
- The architecture could let prompt builders invent interpretation material outside tables and engine outputs.
- The architecture could propose new DB tables while ignoring reusable LLM assembly, prompt, persona, schema, and release mechanisms.
- The architecture could defer implementation stories without a clear CS-364 to CS-368 closure map.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Do not make real provider calls.
- Do not modify backend runtime code, backend tests, frontend files, migrations, prompt seeds, provider examples, or guardrail registry entries.
- Persist validation output under the CS-363 story evidence folder.

## References

- `_story_briefs/cs-363-archi-contrat-theme-astral-llm-input-v1-et-provider-payload.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md`
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md`
- `_condamad/audits/theme-astral-prompt-contract/**/01-audit-usage-tables-textes-interpretation.md`
- `_condamad/audits/theme-astral-prompt-contract/**/02-audit-json-provider-theme-astral-actuels.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/**`
- `backend/app/infra/db/models/llm/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/migrations/versions/**llm**`
