# Story CS-362 audit-contrats-prompt-theme-astral-json-provider-actuels: Audit Current Natal Provider JSON Prompt Contracts
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md`.
- Source problem: current natal provider JSON examples may diverge by plan in structure, payload volume, prompt instructions, and LLM-visible data.
- Source stakes:
  - User impact: CS-363 needs a source-aligned diagnostic before defining the target prompt contract.
  - Technical risk: plan-specific values can be confused with structural drift or hidden commercial metadata exposure.
  - Closure expectation: create a timestamped audit report under `_condamad/audits/theme-astral-prompt-contract/`.
  - Forbidden regression: no provider JSON, runtime, prompt seed, backend, frontend, DB, or migration behavior change.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the brief stakes.

## Objective

Produce a sourced read-only audit of the current `free`, `basic`, and `premium` natal provider JSON prompt contracts.

The audit must distinguish stable contract shape, structural divergences, value divergences, plan-specific variability, LLM-needed data,
backend-only data, payload data to drop from future contracts, and contract material to preserve for CS-363.

## Target State

A timestamped report exists at:
`_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/02-audit-json-provider-theme-astral-actuels.md`.

The report contains:

- Executive summary.
- Tableau comparatif `free/basic/premium`.
- Divergences structurelles.
- Divergences de quantite de donnees.
- Donnees inutiles ou backend-only.
- Donnees manquantes pour la redaction.
- Incoherences de prompt.
- Matrice `keep / move backend-only / replace / drop-from-provider-payload`.
- Recommandations pour CS-363.

The report explicitly validates or invalidates the claim that the top-level and nested structures are not stable across plans.
It also states whether the commercial plan, runtime metadata, audit data, hashes, traces, debug data, developer/user duplication,
and premium-oriented instructions appear in the current provider payloads.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-362`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer contract read first.
- Evidence 4: all mandatory source paths named by the brief exist in this workspace.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver and targeted ID lookup.
- Evidence 6: `resolve_guardrails.py` returned `RG-002` for the backend prompt audit scope.
- Registry gap: no exact guardrail covers read-only audits of plan-differentiated provider JSON prompt contracts.
- Repository structure alert: none. `backend`, `backend/app`, `backend/tests`, `_condamad/docs`, and `_condamad/examples` exist.

## Domain Boundary

- Domain: condamad-audit-documentation
- In scope:
  - Specialized audit under `_condamad/audits/theme-astral-prompt-contract/`.
  - Mechanical comparison of `free-provider-payload.json`, `basic-provider-payload.json`, and `premium-provider-payload.json`.
  - Comparison of top-level JSON shape, `messages`, `user` payload, `response_format`, and `provider_parameters`.
  - Identification of structural divergences and value divergences.
  - Classification of plan-variable data, LLM-needed data, backend-only data, future-contract replacements, and future-contract removals.
  - Verification of commercial plan visibility, runtime metadata, audit data, hashes, traces, debug data, and duplicated developer/user data.
  - Verification of premium-oriented instructions in the `basic` payload.
  - Recommendations for CS-363 without defining the full target architecture.
- Out of scope:
  - Backend runtime changes, JSON example edits, prompt seed edits, database schema, migrations, provider calls, frontend UI, auth, i18n, styling, and build tooling.
  - Redefining the target prompt architecture in detail; that belongs to CS-363.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No implementation code change.
  - No provider JSON rewrite.
  - No prompt, seed, gateway, runtime, test, migration, or frontend behavior change.
  - No real LLM or provider call.

Named brief primitives in scope:

- `free-provider-payload.json`
- `basic-provider-payload.json`
- `premium-provider-payload.json`
- `intermediate-data.json`
- `messages`
- `developer`
- `user`
- `response_format`
- `provider_parameters`
- `plan`
- `metadata runtime`
- `audit`
- `hashes`
- `traces`
- `debug`
- `delivery profile`
- `feature context`
- `astrologer voice`
- `interpretation material`
- `output contract`
- `keep / move backend-only / replace / drop-from-provider-payload`

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this read-only provider JSON prompt contract audit.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only the audit report and story evidence artifacts.
  - Keep provider JSON examples unchanged.
  - Keep backend runtime files unchanged.
  - Keep backend test files unchanged.
  - Keep frontend files unchanged.
  - Keep prompt seed files unchanged.
  - Record recommendations for CS-363 without implementing them.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the three provider JSON examples cannot support a mechanical structural comparison.
- Additional validation rules:
  - The report must compare the three plan payloads mechanically and narratively.
  - The report must separate structural differences from value differences.
  - The report must classify every listed payload data family into one matrix outcome.
  - Runtime file claims must use `AST guard`, targeted `rg`, or bounded source path evidence.
  - JSON validity claims must be proven against the three named provider payload files.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Provider examples, `AST guard`, targeted `rg`, and source paths prove audit claims. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta is audit evidence. |
| Ownership Routing | yes | Audit artifacts, source examples, runtime sources, and CS-363 recommendations must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The report has exact sections, comparison axes, matrix outcomes, and CS-363 recommendations. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Runtime code, JSON examples, prompt seeds, DB schema, and provider behavior must stay unchanged. |
| Persistent Evidence | yes | Report, comparison scans, JSON validation, status guard, and review handoff must persist. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The provider JSON audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path. |
| AC2 | Mandatory report sections are present. | Evidence profile: json_contract_shape; `rg` checks required headings in the report. |
| AC3 | The three plan payloads are compared. | Evidence profile: json_contract_shape; `rg` checks `free`, `basic`, and `premium`. |
| AC4 | Structural differences are separated. | Evidence profile: json_contract_shape; `rg` checks structure and value labels. |
| AC5 | JSON validity is proven. | Evidence profile: json_contract_shape; `python` parses the three provider payload paths. |
| AC6 | LLM-hidden data is classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks backend-only data labels. |
| AC7 | LLM-needed data is classified. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks delivery, voice, and output labels. |
| AC8 | Developer/user duplication is assessed. | Evidence profile: json_contract_shape; `rg` checks developer and user findings. |
| AC9 | Basic premium-oriented instructions are assessed. | Evidence profile: json_contract_shape; `rg` checks basic and premium instruction findings. |
| AC10 | The keep matrix is present. | Evidence profile: json_contract_shape; `rg` checks keep, move backend-only, replace, and drop labels. |
| AC11 | Application sources remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` checks bounded git status app surfaces. |
| AC12 | Story evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and baseline source availability artifact. (AC: AC1, AC12)
- [ ] Task 2: Parse the three provider JSON payloads and persist JSON validation output. (AC: AC3, AC5, AC12)
- [ ] Task 3: Compare top-level keys, `messages`, `user`, `response_format`, and `provider_parameters`. (AC: AC3, AC4)
- [ ] Task 4: Separate structural divergences from value divergences in the report. (AC: AC4)
- [ ] Task 5: Classify commercial plan, runtime metadata, audit data, hashes, traces, and debug data. (AC: AC6, AC10)
- [ ] Task 6: Classify delivery profile, feature context, astrologer voice, interpretation material, and output contract. (AC: AC7, AC10)
- [ ] Task 7: Assess developer/user duplication and cite the exact payload locations. (AC: AC8)
- [ ] Task 8: Assess whether premium-oriented instructions appear in the `basic` payload. (AC: AC9)
- [ ] Task 9: Write CS-363 recommendations without changing architecture or runtime behavior. (AC: AC10)
- [ ] Task 10: Run validation scans, persist command output, and confirm protected sources remain unchanged. (AC: AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md` - source scope and acceptance criteria.
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json` - free plan provider payload.
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json` - basic plan provider payload.
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json` - premium plan provider payload.
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/intermediate-data.json` - generation context evidence.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` - current prompt construction documentation.
- `backend/app/domain/llm/runtime/gateway.py` - provider handoff boundary.
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py` - prompt seed evidence.
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` - prompt seed evidence.

## Runtime Source of Truth

- Primary source of truth:
  - The three provider JSON files listed in Files to Inspect First.
  - `intermediate-data.json` for generation context.
  - `AST guard` or bounded source trace for gateway and prompt seed claims.
  - Targeted `rg` over the generated audit report for required sections, matrix outcomes, and findings.
- Secondary evidence:
  - JSON parser output for the three provider payload files.
  - Targeted `rg` scans over prompt-generation docs and examples.
- Static scans alone are not sufficient for this story because:
  - The audit must prove JSON validity, compare nested structures, and separate source evidence from recommendations.

## Contract Shape

- Contract type:
  - Timestamped provider JSON prompt contract audit report.
- Fields:
  - `Plan`: free, basic, or premium.
  - `Surface`: top-level, messages, developer, user, response_format, provider_parameters, runtime metadata, or prompt instructions.
  - `Structure status`: stable, divergent, missing, extra, or unknown.
  - `Value status`: same, plan-variable, conflicting, duplicated, backend-only, or unknown.
  - `LLM visibility`: needed, backend-only, drop-from-provider-payload, replace, or preserve.
  - `Evidence`: JSON path, source path, scan command, `AST guard`, or bounded report note.
  - `CS-363 recommendation`: keep, move backend-only, replace, drop-from-provider-payload, preserve variability, or needs-user-decision.
- Required report sections:
  - `Executive summary`
  - `Tableau comparatif free/basic/premium`
  - `Divergences structurelles`
  - `Divergences de quantite de donnees`
  - `Donnees inutiles ou backend-only`
  - `Donnees manquantes pour la redaction`
  - `Incoherences de prompt`
  - `Matrice keep / move backend-only / replace / drop-from-provider-payload`
  - `Recommandations pour CS-363`
- Required fields:
  - Plan
  - Surface
  - Structure status
  - Value status
  - LLM visibility
  - Evidence
  - CS-363 recommendation
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
  - `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/source-availability.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/provider-json-structure-comparison.txt`
- Expected invariant:
  - The only intended repository surface delta is the CS-362 audit report and CS-362 story evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Provider JSON contract audit report | `_condamad/audits/theme-astral-prompt-contract/` | `backend/app/**` |
| Story evidence | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/` | `backend/tests/**` |
| Provider payload examples | `_condamad/examples/prompt-generation-cartography/` | generated overwrite |
| Prompt construction evidence | `_condamad/docs/prompt-generation-cartography/` | runtime comments |
| CS-363 recommendations | CS-362 audit report section | backend runtime implementation |

## Mandatory Reuse / DRY Constraints

- Reuse the source paths from the brief instead of creating a parallel source list.
- Reuse the three prompt-generation provider examples as the single comparison baseline.
- Reuse existing docs, gateway, and prompt seed files as evidence instead of copying runtime code into the report.
- Use one canonical matrix vocabulary across the report: keep, move backend-only, replace, drop-from-provider-payload, preserve variability, and needs-user-decision.
- Keep validation commands centralized in the Validation Plan and persist their output once.
- Do not duplicate CS-356 through CS-361 narrative content outside the sections required to prove this audit scope.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy prompt carrier may be introduced or endorsed by this audit.
- No compatibility prompt carrier may be introduced or endorsed by this audit.
- No fallback prompt carrier may be introduced or endorsed by this audit.
- No hidden residual work may be left outside matrix, risk, blocker, or CS-363 recommendation labels.
- Do not edit provider JSON examples, backend runtime files, backend tests, frontend files, migrations, prompt docs, prompt seeds, or guardrail registry entries.
- Do not treat a plan-specific value difference as structural drift unless the JSON key path or object shape differs.

## Reintroduction Guard

- The report must preserve separate classifications for structure, value, quantity, LLM visibility, and future-contract recommendation.
- The report must include deterministic `rg` guards for plan labels, JSON surfaces, backend-only data, duplicated developer/user data, and CS-363 recommendations.
- The report must not replace unknown payload intent with a broad assumed-keep recommendation.
- The validation output must include a bounded status guard proving backend, frontend, migration, prompt docs, prompt seeds, and JSON examples are unchanged.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend source evidence remains classified, not edited. | `rg` source trace; app status guard. |
| Registry gap | No exact guardrail covers provider JSON prompt audits. | Resolver output saved in evidence. |

Non-applicable examples:

- `RG-047` frontend inline styles is out of scope because no frontend source is touched.
- `RG-052` frontend CSS namespace migration is out of scope because no style source is touched.
- `RG-041` entitlement documentation is out of scope because this story audits natal provider payload contracts.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Source availability | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/source-availability.txt` | Prove required sources existed. |
| JSON validity | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/provider-json-validity.txt` | Store parse output. |
| Structure comparison | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/provider-json-structure-comparison.txt` | Store scan. |
| Report shape check | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/report-shape-check.txt` | Prove report sections. |
| Validation output | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/validation.txt` | Store validation commands. |
| Review output | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this audit-only story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/theme-astral-prompt-contract/YYYY-MM-DD-HHMM/02-audit-json-provider-theme-astral-actuels.md` - audit deliverable.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/source-availability.txt` - source evidence.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/provider-json-validity.txt` - JSON validity evidence.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/provider-json-structure-comparison.txt` - comparison evidence.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/report-shape-check.txt` - report shape evidence.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/validation.txt` - validation output.
- `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - inspect existing prompt payload boundary coverage.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - inspect architecture payload guards.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` - inspect current LLM input contract coverage.

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
Run VC12 from `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels`.

- VC1: `python -c "from pathlib import Path; assert Path('_condamad/audits/theme-astral-prompt-contract').exists()"`
- VC2: `rg -n "Executive summary|Tableau comparatif|Recommandations pour CS-363" _condamad/audits/theme-astral-prompt-contract`
- VC3: `rg -n "free|basic|premium|structure|valeur|response_format|provider_parameters" _condamad/audits/theme-astral-prompt-contract`
- VC4: `rg -n "backend-only|plan commercial|metadata runtime|audit|hash|trace|debug" _condamad/audits/theme-astral-prompt-contract`
- VC5: `rg -n "developer|user|duplication|premium|basic|consigne" _condamad/audits/theme-astral-prompt-contract`
- VC6: `rg -n "keep|move backend-only|replace|drop-from-provider-payload|preserve variability|needs-user-decision" _condamad/audits/theme-astral-prompt-contract`
- VC7: `python -m json.tool _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json`
- VC8: `python -m json.tool _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json`
- VC9: `python -m json.tool _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json`
- VC10: `rg -n "LLMGateway|provider|prompt|payload" backend/app/domain/llm/runtime/gateway.py backend/app/ops/llm/bootstrap`
- VC11: `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC12: `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- VC13: `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- VC14: `python -c "from pathlib import Path; assert Path('evidence/validation.txt').exists()"`
- VC15: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app','backend/tests'], check=True)"`
- VC16: `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','frontend/src','backend/migrations'], check=True)"`
- VC17: `rg -n "free|basic|premium|structure|developer|user|response_format|provider_parameters|backend-only|plan commercial" _condamad/audits/theme-astral-prompt-contract`
- VC18: `ruff format .`
- VC19: `ruff check .`
- VC20: `pytest -q`

## Regression Risks

- The audit could treat all plan differences as contract defects instead of separating allowed value variability from structural drift.
- The audit could miss duplicated data because similar material appears in both `developer` and `user` messages.
- The audit could leave commercial plan visibility unclassified.
- The audit could conclude that premium-oriented `basic` instructions exist without quoting the exact payload location.
- The audit could define the CS-363 architecture too early instead of limiting itself to recommendations.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.venv` before every Python, Ruff, or Pytest command.
- Do not make real provider calls.
- Do not modify provider JSON examples, backend runtime code, backend tests, frontend files, migrations, prompt docs, prompt seeds, or guardrail registry entries.
- Persist validation output under the CS-362 story evidence folder.

## References

- `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/intermediate-data.json`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py`
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py`
