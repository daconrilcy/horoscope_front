# Story CS-409 contrats-versionnes-lecture-natale-basic-v2: Definir Les Contrats Versionnes De Lecture Natale Basic V2
Status: done

## Trigger / Source
- Source type: product-contract
- Source reference: `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md`
- Reason for change: le moteur Basic doit fixer ses contrats versionnes avant toute nouvelle generation LLM.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Source-alignment evidence: le contrat couvre le pipeline cible, les preuves, les versions, la denylist publique et la purete backend.

## Objective
Creer le socle contractuel minimal de lecture natale Basic V2 sans brancher de nouvelle generation narrative.

## Target State
- Les objets `EligibilityContext`, `NatalFactGraph`, `NatalSalienceModel`, `NatalNarrativeThemeModel`,
  `NatalSynthesis`, `BasicNatalReadingPlan` et `BasicNatalInterpretationV2` existent dans un owner backend canonique.
- Les constantes de versions Basic sont centralisees et testees.
- Les niveaux `internal_evidence`, `editorial_evidence` et `public_evidence` sont explicites.
- Le contrat public Basic V2 expose `locale`, `level=basic`, `engine_version=basic-natal-reading-v1`
  et `schema_version=basic_natal_interpretation_v2`.

## Current State Evidence
- Evidence 1: `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-149`, `RG-150`, `RG-152`, `RG-154`, `RG-155`, `RG-156` consulted.
- Evidence 4: `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py` - existing public narrative contract inspected.
- Evidence 5: `backend/app/domain/llm/prompting/schemas.py` - existing LLM response schemas inspected.
- Evidence 6: `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` - current projection builder inspected.
- Evidence 7: `backend/app/services/api_contracts/public/natal_interpretation.py` - public natal API contract inspected.
- Repository structure alert: backend roots exist in this workspace; implementation must create only missing contract files.

## Domain Boundary
- Domain: backend-domain
- In scope:
  - Pure backend contract models for the Basic natal reading pipeline.
  - Backend tests for serialization, unknown fields and architecture boundaries.
  - Short technical documentation for the target flow and contract responsibilities.
- Out of scope:
  - Frontend UI, database schema, auth, i18n runtime, styling, build tooling and migrations.
  - Fact extraction, fact scoring, complete narrative construction and provider LLM calls.
- Explicit non-goals:
  - No route, endpoint, persistence migration, prompt execution or frontend generated client.
  - No weakening of existing V1 or V3 public schemas.

## Operation Contract
- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add pure versioned contract models and tests only.
  - Preserve existing runtime routing and persisted interpretation behavior.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the owner path must replace an existing public schema module.

Additional validation rules:
- Public models must reject unknown fields through Pydantic strict configuration.
- Pure contract modules must not import FastAPI, SQLAlchemy, repositories or runtime LLM providers.
- Public contract serialization must reject `ranking_score`, `condition_axis`, `score_profile`, `weighted_score`,
  `prompt_hint`, `audit_input` and internal identifiers.
- Existing V1 and V3 schemas must remain unchanged unless a test proves their public behavior is unchanged.

## Required Contracts
| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Pydantic serialization and import guards prove the loaded contract behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove no runtime route or DB surface is changed. |
| Ownership Routing | yes | Canonical ownership prevents duplicated public schema definitions. |
| Allowlist Exception | no | No allowlist handling is authorized for this contract creation. |
| Contract Shape | yes | The versioned models have exact public, editorial and internal boundaries. |
| Batch Migration | no | No multi-record migration or conversion is in scope. |
| Reintroduction Guard | yes | Forbidden technical fields must stay out of the public V2 model. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic engine version constants are centralized. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`. |
| AC2 | Contract models separate internal proof levels. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`. |
| AC3 | Public V2 rejects unknown fields. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`. |
| AC4 | Public V2 blocks technical markers. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`; `rg`. |
| AC5 | Basic public identity is serialized. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`. |
| AC6 | Existing public schemas remain strict. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py`. |
| AC7 | Contracts avoid runtime imports. | Evidence profile: ast_architecture_guard; AST guard; `pytest`. |
| AC8 | Technical documentation defines LLM as writer. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "redacteur controle|source d'intelligence" backend/docs`. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks
- [x] Task 1: Create the canonical pure contract owner for Basic natal reading V2. (AC: AC1, AC2, AC5, AC7)
- [x] Task 2: Define all requested contract models with strict Pydantic extra handling. (AC: AC2, AC3, AC4, AC5)
- [x] Task 3: Centralize version constants for facts, salience, themes, plan builder, prompt, validator and public schema. (AC: AC1)
- [x] Task 4: Add serialization tests for public identity, proof levels and unknown field rejection. (AC: AC1, AC2, AC3, AC5)
- [x] Task 5: Add a forbidden technical marker test and bounded `rg` validation command. (AC: AC4)
- [x] Task 6: Add an AST architecture guard for pure contract imports. (AC: AC7)
- [x] Task 7: Add short backend documentation for the target flow and responsibility split. (AC: AC8)
- [x] Task 8: Persist validation and baseline artifacts under this story evidence directory. (AC: AC9)

## Files to Inspect First
- `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
- `_condamad/stories/regression-guardrails.md`

## Runtime Source of Truth
- Primary source of truth:
  - Pydantic model validation, `model_dump()`, module import graph and AST guard.
- Secondary evidence:
  - Targeted `rg` scans for forbidden public technical markers.
- Static scans alone are not sufficient for this story because:
  - Public serialization and unknown field rejection must be proven through loaded Pydantic models.

## Contract Shape
- Contract type:
  - Pure backend domain and public projection contracts.
- Fields:
  - `locale`: public locale string.
  - `level`: public literal identifying Basic delivery.
  - `engine_version`: public Basic engine version.
  - `schema_version`: public Basic V2 schema version.
  - `interpretation`: public reading payload.
- Required fields:
  - `locale`, `level`, `engine_version`, `schema_version`, `interpretation`.
- Optional fields:
  - `limitations`, `disclaimers` and public evidence lists.
- Status codes:
  - none; this story does not add or change an API route.
- Serialization names:
  - `locale`, `level`, `engine_version`, `schema_version` and `interpretation` are emitted unchanged.
- Required contract classes:
  - `EligibilityContext`
  - `NatalFactGraph`
  - `NatalSalienceModel`
  - `NatalNarrativeThemeModel`
  - `NatalSynthesis`
  - `BasicNatalReadingPlan`
  - `BasicNatalInterpretationV2`
- Evidence levels:
  - `internal_evidence`: backend debug and validation material only.
  - `editorial_evidence`: facts selected for controlled LLM drafting.
  - `public_evidence`: vulgarized facts allowed in the public payload.
- Required public fields:
  - `locale`
  - `level`
  - `engine_version`
  - `schema_version`
  - `interpretation`
- Required literal values:
  - `level` is emitted as `basic`.
  - `engine_version` is emitted as `basic-natal-reading-v1`.
  - `schema_version` is emitted as `basic_natal_interpretation_v2`.
- Forbidden public fields:
  - `ranking_score`, `condition_axis`, `score_profile`, `weighted_score`, `prompt_hint`, `audit_input`.
  - Internal identifiers such as user IDs, provider IDs, raw place IDs and backend trace IDs.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule
- Baseline artifact before implementation:
  - `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/baseline-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/baseline-after.md`
- Expected invariant:
  - The only intended backend surface delta is pure Basic V2 contract files, docs and tests.

## Ownership Routing Rule
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic V2 pure contracts | `backend/app/domain/astrology/reading/basic_natal_contracts.py` | `backend/app/services/api_contracts/public/natal_interpretation.py` |
| Public API projection bridge | `backend/app/services/api_contracts/public/natal_interpretation.py` | `backend/app/domain/llm/prompting/schemas.py` |
| Technical documentation | `backend/docs/basic-natal-reading-v2-contract.md` | `frontend/src/**` |
| Unit contract tests | `backend/tests/unit/test_basic_natal_reading_contracts.py` | `backend/app/tests/**` |
| Architecture boundary tests | `backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py` | `backend/tests/integration/**` |

## Mandatory Reuse / DRY Constraints
- Reuse existing Pydantic and typing patterns from backend contract modules.
- Keep version constants in one module and import them into tests.
- Do not duplicate existing `NarrativeNatalReadingV1`, `AstroResponseV3` or public endpoint schemas.
- Keep business wording in documentation; keep contract models declarative.

## No Legacy / Forbidden Paths
- No legacy route, service, public schema or prompt path may be added for Basic V2.
- No compatibility wrapper may map V2 into an older Basic public payload.
- No fallback path may make forbidden public fields acceptable.
- Forbidden surfaces: `frontend/src/**`, DB models, Alembic migrations, runtime provider clients and API routers.

## Reintroduction Guard
- Forbidden public markers:
  - `ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input`
- Required guard:
  - `pytest -q backend/tests/unit/test_basic_natal_reading_contracts.py`
  - `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input" backend/app/domain/astrology backend/app/services/llm_generation/natal`
- Allowed fixture pattern:
  - Test denylist literals in `backend/tests/unit/test_basic_natal_reading_contracts.py`.
- Expected false positives:
  - Existing internal enforcement or validator denylist literals only.

## Regression Guardrails
| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-149 | Basic contract scope -> natal prompt-visible payloads stay governed -> docs scan and bounded `rg`. |
| RG-150 | Public rejection scope -> rejected payloads stay out of public models -> targeted `pytest`. |
| RG-152 | Public reading scope -> technical data stays out of narrative payloads -> targeted `pytest` and `rg`. |
| RG-154 | Public denylist scope -> forbidden technical markers remain blocked -> targeted `rg`. |
| RG-155 | Semantic integrity scope -> empty public evidence and padding stay rejected -> targeted `pytest`. |
| RG-156 | Basic editorial scope -> public evidence remains diverse without technical dumps -> targeted `pytest`. |

Needs-investigation:
- `RG-002`, `RG-003`, `RG-007` and `RG-022` were resolver matches, but route and API behavior are out of this local story.

Registry gap:
- A durable invariant for `basic_natal_interpretation_v2` is expected after implementation; normal story generation must not update the registry.

Non-applicable examples:
- Frontend guardrails are out of scope because no React surface changes.
- DB and migration guardrails are out of scope because no persistence surface changes.
- Auth guardrails are out of scope because no access-control surface changes.

## Persistent Evidence Artifacts
| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/baseline-before.md` | Capture initial contract surfaces. |
| Baseline after | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/baseline-after.md` | Capture final contract surfaces. |
| Validation output | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/validation.txt` | Keep local validation proof. |
| Review output | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register
- Allowlist handling: not applicable
- Reason: no allowlist entry or broad permitted delta is authorized.

## Batch Migration Plan
- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify
Likely files:
- `backend/app/domain/astrology/reading/basic_natal_contracts.py` - define pure Basic V2 contracts and version constants.
- `backend/app/domain/astrology/reading/__init__.py` - expose the canonical contract symbols.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - attach the public V2 model only after preserving existing schemas.
- `backend/docs/basic-natal-reading-v2-contract.md` - document the target flow and responsibility split.
- `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/baseline-before.md` - persist initial evidence.
- `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/baseline-after.md` - persist final evidence.
- `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/validation.txt` - persist validation output.

Likely tests:
- `backend/tests/unit/test_basic_natal_reading_contracts.py` - cover versions, serialization and forbidden public fields.
- `backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py` - guard imports away from API, DB and provider runtime.
- `backend/tests/unit/test_narrative_natal_reading_v1.py` - prove existing public contract strictness remains intact.

Files not expected to change:
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.
- `backend/app/api/**` - out of scope; no route is touched.

## Dependency Policy
- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan
- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py --tb=short`
- VC6: `python -B -m pytest -q tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short`
- VC7: `python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py --tb=short`
- VC8 forbidden pattern: `ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input`
- VC8 allowed fixture pattern: denylist literals in `tests/unit/test_basic_natal_reading_contracts.py`
- VC8 scan roots: `app/domain/astrology` and `app/services/llm_generation/natal` after `cd backend`
- VC8 expected false positives: existing internal denylist enforcement only
- VC8 command: `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input" app/domain/astrology app/services/llm_generation/natal`
- VC9: `python -B -c "from pathlib import Path; p=Path('../_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/evidence/validation.txt'); assert p.exists()"`

## Regression Risks
- A second public Basic payload could compete with existing `narrative_natal_reading_v1`.
- A public V2 model could leak scoring markers or provider-oriented audit fields.
- A pure contract module could start importing runtime services.
- Existing V1 or V3 schemas could be loosened to absorb V2 fields.

## Dev Agent Instructions
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References
- `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md`
- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
