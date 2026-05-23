# Story CS-235 brancher-attributs-structurels-signes-runtime-natal: Brancher Attributs Structurels Signes Runtime Natal
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-235-brancher-attributs-structurels-signes-runtime-natal.md`.
- Source problem: les attributs `seasonal_quadrant`, `fertility`, `voice` et `form` de CS-234 doivent atteindre le runtime natal.
- Source expectation: `SignReferenceData` reste la seule source runtime des attributs structurels de signe.
- Selected mode: Repo-informed story, because the brief names existing backend runtime, repository, mapper, builder and JSON surfaces.
- Source-alignment result: objective, ACs, tasks, validation and guardrails preserve the source stakes without adding DB seed work.

## Objective

Brancher les attributs structurels de signes persistés par CS-234 dans le runtime natal, depuis `astral_sign_profiles`
jusqu'à `SignRuntimeData`, puis jusqu'à la projection publique contrôlée déjà portée par `signs_runtime`.

## Target State

- `AstrologyRuntimeReferenceRepository._load_sign_profiles()` lit les quatre attributs depuis les colonnes ou taxonomies CS-234.
- `AstrologyRuntimeReferenceMapper` valide ces attributs et construit `SignReferenceData` sans valeur vide, `unknown` ou `None`.
- `SignReferenceData` expose `seasonal_quadrant`, `fertility`, `voice` et `form` comme champs obligatoires.
- `SignRuntimeData` recopie ces champs depuis `SignReferenceData` sans calcul local depuis le code du signe.
- `build_sign_runtime_data()` propage les attributs aux douze signes, occupants ou non.
- `_serialize_signs_runtime()` ajoute ces champs au bloc public existant `chart["signs_runtime"]`.
- Les factories runtime et tests associés utilisent la même source contractuelle sans seed mapping de production.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-235-brancher-attributs-structurels-signes-runtime-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-235`.
- Evidence 3: `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md` - prior runtime sign profile path reviewed.
- Evidence 4: `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/00-story.md` - DB persistence prerequisite reviewed.
- Evidence 5: `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - `_load_sign_profiles()` now loads element, modality and polarity.
- Evidence 6: `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - `SignReferenceData` mapping currently reads three structural fields.
- Evidence 7: `backend/app/domain/astrology/runtime/runtime_reference.py` - `SignReferenceData` currently validates element, modality and polarity.
- Evidence 8: `backend/app/domain/astrology/runtime/sign_runtime_data.py` - `SignRuntimeData` currently validates element, modality and polarity.
- Evidence 9: `backend/app/domain/astrology/builders/sign_runtime_builder.py` - builder copies current fields from `SignReferenceData`.
- Evidence 10: `backend/app/services/chart/json_builder.py` - `_serialize_signs_runtime()` already projects `signs_runtime`.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - targeted IDs consulted after resolver output for backend runtime scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Runtime loading of structural sign attributes from the CS-234 DB-backed profile source.
  - Mapper, dataclass and builder propagation through `SignReferenceData` and `SignRuntimeData`.
  - Controlled additive projection inside existing `chart["signs_runtime"]`.
  - Runtime factories and unit tests proving propagation and guard behavior.
  - Targeted anti-mapping scans in `backend/app/domain/astrology` and `backend/app/services/natal`.
- Out of scope:
  - Frontend UI, DB migration, seed data authoring, auth, i18n, styling, build tooling, prompts and LLM calls.
  - Balance score changes, dignity doctrine changes and new interpretation phrases.
  - New parallel runtime source beside `SignReferenceData`.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No migration or CS-234 DB seed creation in this story.
  - No local sign-to-attribute mapping in production code.
  - No prompt, renderer or LLM payload enrichment beyond the existing `signs_runtime` JSON block.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend runtime propagation contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the four CS-234 structural sign attributes to the existing natal runtime sign path.
  - Keep all existing element, modality, polarity, occupant, dignity, weight and reason behavior unchanged.
  - Public JSON change is limited to additive fields inside existing `signs_runtime`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-234 does not provide persisted canonical values for all four required attributes.
- Additional validation rules:
  - `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` must prove DB-backed loading.
  - `pytest -q backend/tests/unit/domain/astrology/test_sign_runtime_builder.py` must prove runtime propagation.
  - `pytest -q backend/app/tests/unit/test_chart_json_builder.py` must prove additive public projection.
  - `AST guard` or targeted `rg` scans must prove no local mapping appears in domain astrology or natal services.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | DB-backed repository loading, mapper validation and builder tests prove runtime propagation. |
| Baseline Snapshot | yes | Before and after runtime or JSON artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Infra, domain runtime, builder and serializer responsibilities must stay canonical. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this runtime propagation story. |
| Contract Shape | yes | `SignReferenceData`, `SignRuntimeData` and `signs_runtime` gain exact fields. |
| Batch Migration | no | DB migration and seed creation belong to CS-234, not this runtime story. |
| Reintroduction Guard | yes | Local sign mappings must stay absent from runtime and natal services. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Repository loads four attributes. | Evidence profile: json_contract_shape; `pytest`; `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC2 | Mapper rejects missing structural sign values. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | `SignReferenceData` exposes four required fields. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`. |
| AC4 | `SignRuntimeData` receives values from references. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`. |
| AC5 | Public `signs_runtime` exposes additive fields. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC6 | Factories avoid production sign mappings. | Evidence profile: ast_architecture_guard; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC7 | Domain astrology has no forbidden mappings. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `backend/app/domain/astrology`. |
| AC8 | Natal services have no forbidden mappings. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks `backend/app/services/natal`. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the CS-235 evidence directory. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-234 implemented schema and confirm all four structural attributes are available. (AC: AC1, AC2)
- [ ] Task 2: Extend `_load_sign_profiles()` to include `seasonal_quadrant`, `fertility`, `voice` and `form`. (AC: AC1)
- [ ] Task 3: Extend `AstrologyRuntimeReferenceMapper` to require the four attributes for every sign row. (AC: AC2, AC3)
- [ ] Task 4: Extend `SignReferenceData` validation for the four new required fields. (AC: AC2, AC3)
- [ ] Task 5: Extend `SignRuntimeData` validation for the four copied fields. (AC: AC4)
- [ ] Task 6: Update `build_sign_runtime_data()` to copy the four fields from each `SignReferenceData`. (AC: AC4)
- [ ] Task 7: Update `_serialize_signs_runtime()` to project the four fields inside the existing signs block. (AC: AC5)
- [ ] Task 8: Update runtime test factories without adding production sign classification mappings. (AC: AC6)
- [ ] Task 9: Add repository, mapper, builder, JSON and guard tests for the runtime path. (AC: AC1, AC2, AC4, AC5, AC6)
- [ ] Task 10: Persist before and after evidence artifacts plus validation output in the CS-235 story folder. (AC: AC9)

## Files to Inspect First

- `backend/app/infra/db/models/reference.py` - inspect CS-234 model fields or taxonomy relationships.
- `backend/migrations/versions/**` - inspect the implemented CS-234 Alembic head before repository changes.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - load DB-backed sign profile rows.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - map infra payloads into runtime dataclasses.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - extend `SignReferenceData`.
- `backend/app/domain/astrology/runtime/sign_runtime_data.py` - extend `SignRuntimeData`.
- `backend/app/domain/astrology/builders/sign_runtime_builder.py` - propagate sign reference fields.
- `backend/app/services/chart/json_builder.py` - project existing `signs_runtime` payload.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - repository and mapper runtime tests.
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py` - builder and dataclass propagation tests.
- `backend/app/tests/unit/test_chart_json_builder.py` - public JSON projection tests.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - anti-mapping guard tests.
- `backend/tests/factories/astrology_runtime_reference_factory.py` - runtime fixtures.

## Runtime Source of Truth

- Primary source of truth:
  - `DB schema` at Alembic head for the CS-234 `astral_sign_profiles` structural fields.
  - `astral_sign_profiles` plus CS-234 canonical columns or taxonomy relationships loaded by `AstrologyRuntimeReferenceRepository`.
  - `SignReferenceData` as the only runtime carrier of structural sign attributes.
  - `SignRuntimeData` copied from `SignReferenceData` by `build_sign_runtime_data()`.
- Secondary evidence:
  - `pytest` over repository, builder and JSON tests.
  - `AST guard` or targeted architecture test for forbidden mapping symbols.
  - Targeted `rg` scans for forbidden local mapping symbols.
- Static scans alone are not sufficient for this story because:
  - The core risk is a runtime path that compiles while skipping loaded DB-backed sign profile values.

## Contract Shape

- Contract type:
  - Backend runtime dataclasses and additive public JSON fields.
- Fields:
  - `seasonal_quadrant`: required string copied from CS-234 profile source.
  - `fertility`: required string copied from CS-234 profile source.
  - `voice`: required string copied from CS-234 profile source.
  - `form`: required string copied from CS-234 profile source.
- Required fields:
  - `seasonal_quadrant`
  - `fertility`
  - `voice`
  - `form`
- Optional fields:
  - none for these four structural attributes.
- Status codes:
  - none; this story has no API route surface.
- Serialization names:
  - `seasonal_quadrant`, `fertility`, `voice` and `form` are emitted unchanged in `signs_runtime`.
- Frontend type impact:
  - none; no frontend generated client or UI screen is in scope.
- Generated contract impact:
  - no OpenAPI route change is expected, but public chart JSON evidence must record the additive field delta.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/signs-runtime-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/signs-runtime-after.json`
- Expected invariant:
  - The only intended runtime and JSON surface delta is the four additive structural sign attributes.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| DB-backed sign profile loading | `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | domain builders |
| Infra payload to runtime mapping | `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` | JSON serializer |
| Runtime reference contract | `backend/app/domain/astrology/runtime/runtime_reference.py` | services or prompts |
| Natal sign runtime contract | `backend/app/domain/astrology/runtime/sign_runtime_data.py` | chart serializer |
| Runtime sign assembly | `backend/app/domain/astrology/builders/sign_runtime_builder.py` | API or UI layers |
| Public chart projection | `backend/app/services/chart/json_builder.py` | runtime repository |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-185 runtime sign profile pipeline instead of creating a second resolver.
- Reuse the CS-234 persisted source and taxonomy names instead of deriving values from sign codes.
- Reuse `SignReferenceData` as the single domain-facing reference contract.
- Reuse existing runtime test factories with complete explicit records.
- Tests may assert expected sample values, but production code must not contain sign classification tables.

## No Legacy / Forbidden Paths

- No legacy route path, runtime path or mapping source may be added for these attributes.
- No compatibility wrapper, dataclass alias or serializer alias may be added for these attributes.
- No fallback value may be added for missing structural sign attributes.
- Do not infer values from `sign_code`, `keywords_json`, `shadow_keywords_json` or localized labels.
- Do not add production symbols named `SEASONAL_QUADRANT_BY_SIGN`, `FERTILITY_BY_SIGN`, `VOICE_BY_SIGN` or `FORM_BY_SIGN`.
- Do not add production symbols named `HUMANE_BY_SIGN` or `BESTIAL_BY_SIGN`.
- Do not add a new Python package or a `requirements.txt`.

## Reintroduction Guard

- Forbidden route paths:
  - none; this story has no API route surface.
- Forbidden mapping symbols:
  - `SEASONAL_QUADRANT_BY_SIGN`
  - `FERTILITY_BY_SIGN`
  - `VOICE_BY_SIGN`
  - `FORM_BY_SIGN`
  - `HUMANE_BY_SIGN`
  - `BESTIAL_BY_SIGN`
- Required guard:
  - `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
  - VC10 runs the bounded `rg` scan for forbidden sign mapping symbols.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-093 `CS-152-normaliser-profils-signes-astraux` | Sign profiles stay modeled by canonical astrology reference tables. | Migration `pytest`; runtime `pytest`. |
| RG-107 `CS-172-big-bang-reference-runtime-astrology` | SQL/JSON payloads must become immutable runtime contracts. | Repository `pytest`; builder `pytest`. |
| RG-108 `regression-guardrails-maintenance` | DB-backed sign vocabulary must not be recreated locally. | Targeted `rg`; guard `pytest`. |
| RG-112 `CS-181-supprimer-constantes-astrologiques-hardcodees` | Astrology constants must not return in runtime paths. | Guard `pytest`; targeted `rg`. |
| RG-114 `CS-185-brancher-profils-signes-runtime-natal` | Structural sign runtime attributes must come from sign profiles. | Repository `pytest`; before/after artifacts. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable; frontend is out of scope. | Manual check: `frontend/src/**` unchanged. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable; CSS namespaces are out of scope. | Manual check: CSS files unchanged. |
| RG-022 `align-prompt-generation-story-validation-paths` | Non-applicable; prompt generation is out of scope. | Manual check: prompt files unchanged. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Runtime before | `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/signs-runtime-before.json` | Record current runtime sign payload. |
| Runtime after | `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/signs-runtime-after.json` | Record enriched runtime sign payload. |
| JSON projection | `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/signs-runtime-json.txt` | Record public JSON field proof. |
| Guard evidence | `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/guard-evidence.txt` | Record anti-mapping scan proof. |
| Validation output | `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/validation.txt` | Preserve final lint and test output. |
| Review output | `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this runtime propagation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - load the four CS-234 structural sign attributes.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - require and map the new fields into `SignReferenceData`.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - extend `SignReferenceData`.
- `backend/app/domain/astrology/runtime/sign_runtime_data.py` - extend `SignRuntimeData`.
- `backend/app/domain/astrology/builders/sign_runtime_builder.py` - copy fields from reference to runtime.
- `backend/app/services/chart/json_builder.py` - add fields to the existing `signs_runtime` projection.
- `backend/tests/factories/astrology_runtime_reference_factory.py` - keep complete runtime fixture records.
- `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/**` - persist implementation evidence.

Likely tests:

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/versions/**` - out of scope; CS-234 owns schema migration.
- `backend/app/services/prediction/reference_seed_service.py` - out of scope unless CS-234 implementation requires a documented handoff.
- `backend/app/domain/astrology/interpretation/**` - out of scope; no balance or interpretation scoring changes are authorized.
- `backend/pyproject.toml` - out of scope; no dependency change is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`
- VC6: `pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py`
- VC7: `pytest -q app/tests/unit/test_chart_json_builder.py`
- VC8: `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`
- VC9: `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py tests/unit/domain/astrology/test_sign_runtime_builder.py`
- VC9b: `pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_runtime_reference_guard.py`
- VC10: `rg -n "SEASONAL_QUADRANT_BY_SIGN|FERTILITY_BY_SIGN|VOICE_BY_SIGN|FORM_BY_SIGN|HUMANE_BY_SIGN|BESTIAL_BY_SIGN" app/domain/astrology app/services/natal -g "*.py"`
- VC11: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence').is_dir()"`
- VC12: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/validation.txt').exists()"`
- VC13: `python -c "from app.main import app; assert hasattr(app, 'routes'); assert callable(app.openapi)"`

## Regression Risks

- CS-234 may still be pending implementation, leaving the runtime story blocked on absent DB columns.
- Factories can hide missing production values by constructing partial runtime objects.
- Public chart JSON can add fields in a serializer path while runtime dataclasses remain incomplete.
- Local sign mappings can reappear under test helpers and later migrate into production code.
- A future interpretation layer can read the DB directly instead of consuming `SignRuntimeData`.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend venv before every Python, Ruff or Pytest command.
- Do not implement CS-234 migration or seed work in this story.
- Stop on missing CS-234 columns and record the blocker instead of inventing a local mapping.
- Keep the global French file comment and French docstrings on new or significantly modified Python files.

## References

- `_story_briefs/cs-235-brancher-attributs-structurels-signes-runtime-natal.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md`
- `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/00-story.md`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/services/chart/json_builder.py`
