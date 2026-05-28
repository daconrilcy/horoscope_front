# Story CS-374 renforcer-exemples-json-theme-astral-textes-interpretation: Strengthen Theme Astral JSON Examples With Interpretation Texts
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-374-renforcer-exemples-json-theme-astral-avec-textes-interpretation-reels.md`.
- Selected mode: Repo-informed story, because the examples must reuse existing runtime builders, repository sources, and CS-371 artifacts.
- Source problem: CS-371 examples prove plumbing, quotas, and repository access, but their seeded interpretation texts remain too generic.
- Source stakes:
  - Future editorial quality checks need richer, representative, and traceable interpretation material.
  - The examples must keep the Paris 1973 scenario and the existing `free`, `basic`, and `premium` payload structure.
  - Source attribution must distinguish DB content, production-like fixtures, and mixed sources without overstating production truth.
  - The generator must not call an LLM provider while enriching example material.
  - Validation must fail when known generic seeded phrases return in final payloads.
- Source-alignment evidence: PASS. Objective, ACs, tasks, validation, non-goals, and guardrails preserve the brief deliverables.

## Objective

Regenerate the `theme_astral` JSON examples so `interpretation_material` contains richer interpretation texts, explicit `source_ref`
values, and documented source coverage across planets, houses, aspects, dominants, and runtime signals.

## Target State

- CS-371 `generate_examples.py` reuses `InterpretationMaterialSourceRepository` for DB-backed planet, house, and aspect sources.
- Remaining supplemental sources are explicitly documented as `production-like` fixtures when no application table source exists.
- `free-provider-payload.json`, `basic-provider-payload.json`, and `premium-provider-payload.json` are regenerated for Paris 1973.
- Each payload keeps non-empty `interpretation_material` and exposes explicit `source_ref` values.
- Interpretation texts are richer than the known generic CS-371 seeded phrases.
- `source-coverage.md`, `structure-comparison.md`, and README explain source nature and profile density.
- Validation fails if generic interpretation phrases return in final payloads.
- No provider LLM call is performed.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-374-renforcer-exemples-json-theme-astral-avec-textes-interpretation-reels.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-374`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: `backend/app/infra/db/repositories/interpretation_material_source_repository.py` - DB source repository inspected.
- Evidence 5: `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` - runtime material builder inspected.
- Evidence 6: `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/generate_examples.py` - generator inspected.
- Evidence 7: `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py` - validator inspected.
- Evidence 8: `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` - README inspected.
- Evidence 9: `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` - density doc inspected.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped `resolve_guardrails.py` output.
- Repository structure alert: `backend`, `frontend`, `_condamad`, and CS-371 example roots exist in this workspace.
- Registry gap: no exact guardrail covers enriched `theme_astral` interpretation material examples by delivery profile.
- Current source gap: CS-371 local seeds include known generic phrases that the new validator must reject in final payloads.

## Domain Boundary

- Domain: documentation-examples
- In scope:
  - CS-371 example generator and validator under `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/`.
  - Example artifacts under `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/`.
  - Source coverage, structure comparison, README, validation output, and no-provider proof for regenerated examples.
  - Read-only inspection of backend interpretation repository, runtime material builder, and prompt-contract audit artifacts.
- Out of scope:
  - Frontend UI, API routes, auth, i18n, styling, build tooling, migrations, DB schema, provider clients, and astrology rule changes.
  - Adding a new interpretation family without an owner.
  - Importing unsourced or unauthorized interpretation text.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No real LLM provider call.
  - No new backend API route.
  - No modification of astrology calculation rules.
  - No claim that production-like fixtures are production data.

Named brief primitives in scope:

- `theme_astral`
- `free`
- `basic`
- `premium`
- `source_ref`
- `source_coverage`
- `InterpretationMaterialSourceRepository`
- `interpretation_material`
- `planet_sign_interpretations`
- `planet_house_interpretations`
- `aspect_interpretations`
- `dominant_themes`
- `tensions`
- `resources`
- `integration_levers`
- `warnings`
- `production-like`
- `validate_examples.py`

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits enriched backend-generated documentation examples.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Update only the example generation, validation, documentation, and evidence surfaces in scope.
  - Reuse `InterpretationMaterialSourceRepository` for planet, house, and aspect materials.
  - Keep `InterpretationMaterialBuilder` as the runtime selection path.
  - Keep the existing Paris 1973 scenario and three delivery profiles.
  - Keep supplemental source fixtures named and documented as `production-like`.
  - Keep backend runtime, frontend, migrations, DB schema, provider clients, and prompt contracts unchanged.
  - Never invoke a real LLM provider.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: no authorized source exists for a required interpretation family.
- Additional validation rules:
  - `python` JSON parsing must prove all regenerated payloads remain valid.
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` must prove builder behavior stays intact.
  - `python -B ..\_condamad\stories\CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan\evidence\validate_examples.py` must fail on generic phrases.
  - `rg` scans must prove generic CS-371 seeded phrases are absent from final payloads.
  - `AST guard` or bounded git status evidence must prove protected runtime, frontend, migration, and provider-client files are unchanged.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `InterpretationMaterialSourceRepository`, `InterpretationMaterialBuilder`, and `pytest` prove runtime material behavior. |
| Baseline Snapshot | yes | Before and after snapshots prove the only allowed surface delta is examples, scripts, docs, and evidence. |
| Ownership Routing | yes | Example scripts and artifacts stay under `_condamad`; backend runtime owners remain source truth. |
| Allowlist Exception | no | No allowlist handling is authorized for this enriched example story. |
| Contract Shape | yes | Payloads must keep exact JSON blocks while enriching material text and source coverage. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Generic seeded phrases, provider calls, and unlabelled fixtures must stay absent. |
| Persistent Evidence | yes | Generation, validation, scans, source coverage, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Generator uses runtime material path. | Evidence profile: ast_architecture_guard; `AST guard`; `pytest` builder test. |
| AC2 | DB families keep source refs. | Evidence profile: json_contract_shape; `AST guard`; `python` checks refs. |
| AC3 | Supplemental families are labelled production-like. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks README and source coverage. |
| AC4 | Generic seeded phrases are absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` rejects known CS-371 phrases. |
| AC5 | `interpretation_material` remains populated. | Evidence profile: json_contract_shape; `python` checks non-empty material in all payloads. |
| AC6 | Profile density increases by delivery tier. | Evidence profile: json_contract_shape; `python` compares free, basic, and premium counts. |
| AC7 | JSON payloads remain valid. | Evidence profile: json_contract_shape; `python -B -m json.tool` checks all payloads. |
| AC8 | No provider LLM call is performed. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`. |
| AC9 | README states source nature. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks production, production-like, and mixed labels. |
| AC10 | Validation rejects generic text returns. | Evidence profile: reintroduction_guard; `python` runs the CS-371 `validate_examples.py`. |
| AC11 | Source coverage documents all families. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks source coverage for families and source owners. |
| AC12 | Persistent evidence is stored. | Evidence profile: baseline_before_after_diff; `python` checks CS-374 evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the CS-371 generator, validator, current payloads, README, and source coverage. (AC: AC1, AC4, AC9)
- [ ] Task 2: Identify authorized existing DB or seed sources for planets, houses, aspects, dominants, and signals. (AC: AC2, AC3, AC11)
- [ ] Task 3: Replace generic local profile texts with richer sourced or production-like material through repository-backed seeds. (AC: AC2, AC4)
- [ ] Task 4: Keep supplemental families explicit and documented as production-like fixtures. (AC: AC3, AC9, AC11)
- [ ] Task 5: Regenerate `free`, `basic`, and `premium` payloads for Paris 1973. (AC: AC5, AC6, AC7)
- [ ] Task 6: Update `source-coverage.md`, `structure-comparison.md`, README, and no-provider proof. (AC: AC3, AC8, AC9, AC11)
- [ ] Task 7: Extend `validate_examples.py` to reject known generic seeded phrases in final payloads. (AC: AC4, AC10)
- [ ] Task 8: Persist baseline, after snapshot, scans, validation output, and guardrail resolver output under CS-374 evidence. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-374-renforcer-exemples-json-theme-astral-avec-textes-interpretation-reels.md`
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py`
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/generate_examples.py`
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json`
- `_condamad/audits/theme-astral-prompt-contract/**`
- `_condamad/stories/regression-guardrails.md` through scoped guardrail resolution only.

## Runtime Source of Truth

- Primary source of truth:
  - `InterpretationMaterialSourceRepository`.
  - `InterpretationMaterialBuilder`.
  - `ThemeAstralProviderPayloadBuilder`.
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`.
  - `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`.
  - `AST guard` for no-provider path and protected-source stability.
- Secondary evidence:
  - Regenerated JSON payloads and `intermediate-data.json`.
  - Targeted `rg` scans for source refs, generic phrases, source labels, and provider-call markers.
- Static scans alone are not sufficient for this story because:
  - Runtime builders must still shape `interpretation_material` and delivery profile density.

## Contract Shape

- Contract type:
  - Static example artifacts for final `theme_astral` LLM v1 provider payloads.
- Fields:
  - `input_data.interpretation_material`: non-empty material selected by runtime builder.
  - `source_ref`: explicit source owner and source id for each selected material item.
  - `interpretive_text`: richer sourced or production-like text, never the known generic CS-371 phrase set.
  - `writing_hint`: sourced guidance only when the material item lacks direct interpretation text.
  - `source_coverage`: source owners, family coverage, table source counts, and fixture nature.
  - `delivery_profile`: existing density, budget, depth, section, and selection rules.
  - `output_contract`: unchanged final LLM response contract.
- Required fields:
  - `input_data`
  - `interpretation_material`
  - `source_ref`
  - `interpretive_text`
  - `source_coverage`
  - `delivery_profile`
  - `output_contract`
- Optional fields:
  - `writing_hint`
- Status codes:
  - none; no API route is created or changed.
- Serialization names:
  - JSON keys must keep the current final provider payload names.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; examples consume the final contract and do not redefine it.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/examples-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/examples-after.txt`
- Expected invariant:
  - The only intended artifact delta is CS-371 example generation assets, regenerated examples, docs, and CS-374 evidence.
- Runtime invariant:
  - Backend runtime files, frontend files, migrations, DB schema, provider clients, and prompt contracts remain unchanged.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Example generator | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/generate_examples.py` | `backend/app/**` |
| Example validator | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py` | `backend/tests/**` |
| Provider payload examples | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/*-provider-payload.json` | `frontend/src/**` |
| Example README | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` | runtime code comments |
| Source coverage proof | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/source-coverage.md` | payload JSON |
| Story execution evidence | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/**` | `_condamad/examples/**` |

## Mandatory Reuse / DRY Constraints

- Reuse `InterpretationMaterialSourceRepository` instead of handcrafting DB-family material outside the repository path.
- Reuse `InterpretationMaterialBuilder` and `ThemeAstralProviderPayloadBuilder` for runtime shaping.
- Reuse the existing CS-371 scenario, payload paths, and shared JSON skeleton.
- Centralize source labels and generic phrase rejection in `validate_examples.py`.
- Keep repeated production-like source text construction behind local helper functions in the generator.
- Do not duplicate interpretation family ownership rules in payload JSON.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy payload carrier may be used as the source of regenerated examples.
- No compatibility payload path may be created for enriched materials.
- No fallback text may fabricate interpretation content without source attribution.
- Generic phrases `texte source issu`, `contexte issu`, `articulation issue`, and `Texte source verifie` must not return in final payloads.
- No provider response, API key, bearer token, credential, or secret may appear in the example folder.
- No unresolved placeholder token may appear in generated JSON or markdown.
- Do not edit frontend files, DB migrations, provider clients, prompt contracts, or guardrail registry entries.
- Do not preserve legacy behavior.

## Reintroduction Guard

- Guard generic seeded phrases:
  - `rg` rejects the known generic phrases in the example folder.
- Guard explicit source material:
  - `rg -n "source_ref|interpretive_text|writing_hint|source_coverage|table_source_count" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- Guard source documentation:
  - `rg` checks source labels and DB owner names in examples and source coverage.
- Guard provider and secret leakage:
  - `rg -n "provider_response|api_key|OPENAI_API_KEY|sk-|Bearer|credential|secret" _condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1`
- Guard protected surfaces:
  - `python -c "import subprocess as s; assert not s.getoutput('git status --short -- backend/app frontend/src backend/migrations')"`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend runtime ownership stays source truth; examples must not move logic into API routes. | `AST guard`; bounded git status. |
| Registry gap | No exact guardrail covers enriched `theme_astral` interpretation material examples by profile. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-041` entitlement documentation is outside scope because no entitlement or security claim surface is touched.
- `RG-047` inline TSX styling is outside scope because no TSX file is touched.
- `RG-052` CSS namespace migration is outside scope because no CSS or frontend token surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source coverage | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/source-coverage.md` | Document source families and fixture nature. |
| Guardrail resolver output | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/guardrails.txt` | Keep scoped guardrail selection. |
| Baseline snapshot | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/examples-baseline.txt` | Record target folder state. |
| After snapshot | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/examples-after.txt` | Record final example paths. |
| JSON validation | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/json-validation.txt` | Prove JSON parsing and density checks. |
| Generic phrase scan | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/generic-phrase-scan.txt` | Prove generic text absence. |
| No-provider proof | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/no-provider-proof.txt` | Prove provider was not called. |
| Validation output | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/validation.txt` | Store validation command output. |
| Review output | `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/generated/11-code-review.md` | Keep generated review. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this enriched example story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/generate_examples.py` - enrich sources.
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py` - reject generic phrases.
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/source-coverage.md` - document sources.
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/no-provider-proof.txt` - update proof.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md` - source nature.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json` - source coverage.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json` - regenerated payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json` - regenerated payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json` - regenerated payload.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md` - density proof.
- `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/**` - validation handoff artifacts.
- `_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/generated/11-code-review.md` - review handoff.

Likely tests:

- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py` - generated artifact validation.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py` - payload builder behavior.
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py` - no-provider handoff behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is authorized.
- `backend/app/infra/db/models/**` - out of scope; no schema model change is authorized.
- `backend/app/infra/llm/**` - out of scope; no live provider client change is authorized.
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py` - runtime source truth is read-only.
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py` - runtime source truth is read-only.
- `_condamad/stories/regression-guardrails.md` - out of scope; no registry enrichment is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run backend quality commands from `backend` after activation.
Use `$ex = '..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1'`.
Use `$cov = '..\_condamad\stories\CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan\evidence\source-coverage.md'`.

- VC1: `python -B ..\_condamad\stories\CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan\evidence\generate_examples.py`
- VC2: `python -B ..\_condamad\stories\CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan\evidence\validate_examples.py`
- VC3: `python -B -m json.tool ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\intermediate-data.json`
- VC4: `python -B -m json.tool ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\free-provider-payload.json`
- VC5: `python -B -m json.tool ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\basic-provider-payload.json`
- VC6: `python -B -m json.tool ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\premium-provider-payload.json`
- VC7: `python` checks non-empty material, `source_ref`, family coverage, source labels, and delivery profile density.
- VC8: `rg -n "texte source issu|contexte issu|articulation issue|Texte source verifie|theme_astral_example_source" $ex`
- VC9: `rg -n "source_ref|interpretive_text|writing_hint|source_coverage|table_source_count" $ex`
- VC10: `rg -n "production|production-like|fixture|astral_planet_interpretation_profiles" $ex $cov`
- VC10b: `rg -n "astral_house_interpretation_profiles|astral_aspect_interpretation_profiles" $ex $cov`
- VC11: `rg -n "provider_response|api_key|OPENAI_API_KEY|sk-|Bearer|credential|secret" ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1`
- VC12: `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- VC13: `pytest -q backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- VC14: `ruff format .`
- VC15: `ruff check .`
- VC16: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-374-renforcer-exemples-json-theme-astral-textes-interpretation/evidence/validation.txt').exists()"`

## Regression Risks

- Richer text could be hand-written directly in payloads rather than flowing through the generator.
- Production-like fixtures could be presented as real production table content.
- A new source family could be added without an explicit owner.
- Generic seeded phrases could return while JSON and density checks still pass.
- Provider-call proof could become stale after generator changes.
- Source coverage could mention a family that is absent from the payloads.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, pip, pytest, or ruff command.
- Use the final backend builders or the CS-371 generator importing the same builders; do not handcraft payloads from memory.
- Label every remaining supplemental fixture as `production-like` in source coverage and README.
- Never call OpenAI, another LLM provider, or external provider runtime while producing these examples.
- Persist all validation outputs under the CS-374 evidence directory.

## References

- `_story_briefs/cs-374-renforcer-exemples-json-theme-astral-avec-textes-interpretation-reels.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py`
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/generate_examples.py`
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/audits/theme-astral-prompt-contract/**`
