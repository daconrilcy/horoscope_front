# Story CS-234 enrichir-profils-structurels-signes-db: Enrichir Profils Structurels Signes DB
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-234-enrichir-profils-structurels-signes-db.md`.
- Source problem: `astral_sign_profiles` stores element, modality, polarity and editorial keywords, but not the missing structural sign attributes.
- Source expectation: persist seasonal quadrant, fertility, voice and form classifications for all twelve signs before any natal runtime consumption.
- Conditional source expectation: inspect source material for sect or gender-compatible sign traits and record the DB decision.
- Selected mode: Repo-informed story, because the brief names existing backend DB, seed and test surfaces that must be checked before drafting.
- Source-alignment result: objective, ACs, tasks and validation commands preserve the DB + seed + integrity scope from the brief.

## Objective

Add canonical DB-backed structural sign classifications to `astral_sign_profiles` and seed complete values for the twelve zodiac signs.

## Target State

- `astral_sign_profiles` exposes non-null canonical structural references for seasonal quadrant, fertility class, voice class and form class.
- Dedicated taxonomy tables are used unless the implementer records a narrower DB-code decision with explicit evidence in the story artifacts.
- The twelve signs have complete seeded values for each new structural attribute.
- Sect or gender-compatible sign traits are explicitly checked in source material and either persisted or ruled out with evidence.
- `keywords_json` and `shadow_keywords_json` remain editorial fields and are not used as structural classification sources.
- Domain astrology and natal services do not introduce local mappings for these sign attributes.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-234-enrichir-profils-structurels-signes-db.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-234`.
- Evidence 3: `backend/app/infra/db/models/reference.py` - `AstralSignProfileModel` currently has element, modality, polarity and keyword fields.
- Evidence 4: `backend/app/services/prediction/reference_seed_service.py` - `ensure_astral_sign_profiles` seeds the current profile records.
- Evidence 5: `backend/app/tests/integration/test_reference_data_migrations.py` - existing migration tests assert current sign profile schema.
- Evidence 6: `backend/app/tests/unit/test_prediction_reference_repository.py` - unit repository tests already cover reference model contracts.
- Evidence 7: `docs/db_seeder/astrology` - astrology seed directory exists and is the expected seed source surface.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through `resolve_guardrails.py` with a backend DB seed scope vector.

## Domain Boundary

- Domain: backend-db-reference-data
- In scope:
  - DB schema and SQLAlchemy models for structural sign classifications.
  - Alembic migration under `backend/migrations/versions`.
  - Seed data and seed service synchronization for the twelve signs.
  - Integration and unit tests proving schema, seed and anti-mapping behavior.
  - Minimal backend documentation or seed metadata describing the new classifications.
- Out of scope:
  - Frontend UI, public JSON projection, `SignReferenceData`, `SignRuntimeData`, natal balances, signatures, prompts and LLM calls.
  - Runtime consumption of the new sign attributes.
  - Auth, i18n, styling, build tooling and unrelated migrations.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No local sign classification mapping in `backend/app/domain/astrology` or `backend/app/services/natal`.
  - No text interpretation layer or narrative prompt change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend DB seed integrity contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only canonical structural sign classification persistence and seed synchronization.
  - Keep runtime natal payloads and public JSON unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: dedicated taxonomy tables conflict with an existing canonical source that already owns these attributes.
- Additional validation rules:
  - `DB schema` inspection must prove the new profile columns or documented code columns exist at Alembic head.
  - `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` must prove all twelve signs are seeded.
  - `AST guard` or targeted `rg` scans must prove no local mapping is introduced in domain astrology or natal services.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | DB schema, seed rows and loaded SQLAlchemy models prove the canonical source of truth. |
| Baseline Snapshot | yes | Before and after schema or seed artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | DB, seed and repository responsibilities must stay in canonical backend owners. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this DB seed story. |
| Contract Shape | yes | New structural attributes need exact table, column, FK, code and non-null contracts. |
| Batch Migration | yes | Alembic migration and seed synchronization form a bounded DB migration batch. |
| Reintroduction Guard | yes | Domain and natal local mappings must remain absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Four structural sign attributes exist. | Evidence profile: baseline_before_after_diff; DB schema via `pytest` migration test. |
| AC2 | The twelve signs have complete seeded values. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC3 | Expected taxonomy codes are persisted. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC4 | Editorial keyword fields stay non-structural. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` runs the migration test path. |
| AC5 | Domain astrology has no new local mappings. | Evidence profile: ast_architecture_guard; `rg` checks `backend/app/domain/astrology`. |
| AC6 | Natal services have no new local mappings. | Evidence profile: ast_architecture_guard; `rg` checks `backend/app/services/natal`. |
| AC7 | Old `signs` tables are not restored at head. | Evidence profile: reintroduction_guard; `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC8 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the story evidence directory. |
| AC9 | Conditional sect or gender traits are decided from sources. | `rg "sect|gender"` source scan plus `source-decision.txt`. |

## Implementation Tasks

- [ ] Task 1: Inspect current sign profile model, migration head and seed service before editing. (AC: AC1, AC2)
- [ ] Task 2: Add dedicated taxonomies for seasonal quadrant, fertility class, voice class and form class. (AC: AC1, AC3)
- [ ] Task 3: Add non-null sign profile references or justified non-null code columns for the four attributes. (AC: AC1)
- [ ] Task 4: Create the Alembic migration under `backend/migrations/versions`. (AC: AC1, AC3, AC7)
- [ ] Task 5: Update astrology seed data under `docs/db_seeder/astrology`. (AC: AC2, AC3, AC4)
- [ ] Task 6: Update `ensure_astral_sign_profiles` or the canonical seed path to sync all four attributes. (AC: AC2, AC3)
- [ ] Task 7: Add migration integration tests for schema, codes, twelve rows and old table absence. (AC: AC1, AC2, AC3, AC7)
- [ ] Task 8: Add repository or seed-service tests covering the model contract if the repository surface changes. (AC: AC2, AC4)
- [ ] Task 9: Add targeted anti-mapping guards for domain astrology and natal services. (AC: AC5, AC6)
- [ ] Task 10: Inspect source material for sect or gender-compatible sign traits and record the DB decision. (AC: AC9)
- [ ] Task 11: Persist before and after evidence artifacts in this story directory. (AC: AC8)

## Files to Inspect First

- `backend/app/infra/db/models/reference.py` - canonical SQLAlchemy reference models.
- `backend/migrations/versions/20260513_0087_normalize_astral_sign_profiles.py` - current sign profile normalization baseline.
- `backend/app/services/prediction/reference_seed_service.py` - canonical sign profile seed synchronization.
- `docs/db_seeder/astrology/astral_sign_keywords.json` - current sign profile editorial source.
- `docs/db_seeder/astrology/astral_structural_reference_catalog.json` - existing structural reference source to compare.
- `docs/recherches astro` - targeted source search for sect or gender-compatible sign traits.
- `backend/app/tests/integration/test_reference_data_migrations.py` - migration and seed assertions at Alembic head.
- `backend/app/tests/unit/test_prediction_reference_repository.py` - repository model contract tests.
- `backend/app/domain/astrology` - bounded anti-mapping scan surface.
- `backend/app/services/natal` - bounded anti-mapping scan surface.

## Runtime Source of Truth

- Primary source of truth:
  - Alembic head schema, SQLAlchemy metadata, seeded DB rows and `pytest` integration tests.
- Secondary evidence:
  - Targeted `rg` scans for unauthorized local structural mappings.
- Static scans alone are not sufficient for this story because:
  - DB shape and seed completeness must be proven from migrated tables.

## Contract Shape

- Contract type:
  - DB reference tables, sign profile attributes and seed rows.
- Fields:
  - `seasonal_quadrant`: one canonical code per sign.
  - `fertility`: one canonical code per sign.
  - `voice`: one canonical code per sign.
  - `form`: one canonical code per sign.
- Required fields:
  - `seasonal_quadrant`
  - `fertility`
  - `voice`
  - `form`
- Recommended taxonomy tables:
  - `astral_sign_seasonal_quadrants`
  - `astral_sign_fertility_classes`
  - `astral_sign_voice_classes`
  - `astral_sign_form_classes`
- Recommended profile references:
  - `astral_sign_profiles.seasonal_quadrant_id`
  - `astral_sign_profiles.fertility_class_id`
  - `astral_sign_profiles.voice_class_id`
  - `astral_sign_profiles.form_class_id`
- Expected codes:
  - Seasonal quadrant: `spring`, `summer`, `autumn`, `winter`.
  - Fertility: `fruitful`, `semi_fruitful`, `barren`.
  - Voice: `vocal`, `semi_vocal`, `mute`.
  - Form: `humane`, `bestial`, `double_bodied`, `hybrid`.
- Optional fields:
  - none for the four structural attributes.
- Status codes:
  - none; this story has no API route surface.
- Serialization names:
  - DB code values use their stored snake_case code names unchanged.
- Frontend type impact:
  - none; generated frontend clients and public JSON are out of scope.
- Generated contract impact:
  - none for OpenAPI or frontend generated clients.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/schema-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/schema-after.txt`
- Expected invariant:
  - The only intended schema surface delta is the structural sign classification storage and supporting taxonomies.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| SQLAlchemy sign profile schema | `backend/app/infra/db/models/reference.py` | `backend/app/domain/astrology/**` |
| Alembic migration | `backend/migrations/versions/**` | `backend/app/services/**` |
| Astrology seed data | `docs/db_seeder/astrology/**` | runtime calculators or prompt files |
| Seed synchronization | `backend/app/services/prediction/reference_seed_service.py` | UI, prompt or natal runtime builders |
| Integration proof | `backend/app/tests/integration/test_reference_data_migrations.py` | manual-only verification |

## Mandatory Reuse / DRY Constraints

- Reuse existing taxonomy helpers and seed service patterns before adding new helpers.
- Reuse existing `AstralSignProfileModel` ownership instead of creating a parallel sign profile source.
- Keep one canonical source for each structural code; do not duplicate the same mapping in tests and production code.
- Tests may define expected code sets, but production mappings must come from seed data and DB references.

## No Legacy / Forbidden Paths

- No legacy route path, table path or sign mapping may be added for these attributes.
- No compatibility route, model alias or table alias may be added for these attributes.
- No fallback mapping may be added in domain astrology or natal services.
- Do not restore the old `signs` or `sign_rulerships` tables at Alembic head.
- Do not infer structural classifications from `keywords_json` or `shadow_keywords_json`.

## Reintroduction Guard

- Forbidden route paths:
  - none; this story has no API route surface.
- Forbidden tables at Alembic head:
  - `signs`
  - `sign_rulerships`
- Forbidden mapping surfaces:
  - `backend/app/domain/astrology`
  - `backend/app/services/natal`
- Required guard:
  - `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`
  - `rg -n "seasonal_quadrant|fertility|voice|humane|bestial|fruitful|barren|mute" backend/app/domain/astrology backend/app/services/natal -g "*.py"`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| Registry gap | No exact DB seed guardrail was resolved for sign structural classifications. | `resolve_guardrails.py`; targeted `pytest`. |
| RG-002 `refactor-api-v1-routers` | Non-applicable; no API router is touched. | Manual check: route files stay unchanged. |
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Non-applicable; frontend is out of scope. | Manual check: `frontend/src/**` unchanged. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Non-applicable; CSS namespaces are out of scope. | Manual check: CSS files unchanged. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Schema before | `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/schema-before.txt` | Record baseline sign profile schema. |
| Schema after | `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/schema-after.txt` | Record migrated sign profile schema. |
| Seed verification | `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/seed-check.txt` | Record twelve-sign seed proof. |
| Source decision | `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/source-decision.txt` | Record conditional sect or gender trait decision. |
| Validation output | `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/validation.txt` | Preserve final lint and test output. |
| Review output | `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist Exception: not applicable
- Reason: no allowlist handling is authorized for this DB seed story.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Sign DB | Current profile fields. | Four structural fields. | Seed tests. | Migration tests. | Targeted `rg`. | Stop on missing value. |

## Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/reference.py` - add canonical taxonomy models and sign profile references.
- `backend/migrations/versions/20260523_0130_enrich_astral_sign_profiles.py` - migrate schema and seed baseline values.
- `backend/app/services/prediction/reference_seed_service.py` - synchronize new structural attributes during seed.
- `docs/db_seeder/astrology/astral_sign_keywords.json` - keep editorial fields unchanged during seed updates.
- `docs/db_seeder/astrology/astral_structural_reference_catalog.json` - use or extend structural source data for sign classifications.
- `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/**` - persist implementation evidence.

Likely tests:

- `backend/app/tests/integration/test_reference_data_migrations.py` - cover schema, codes, rows and old table absence.
- `backend/app/tests/unit/test_prediction_reference_repository.py` - cover repository or model contract changes.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/domain/astrology/**` - out of scope for production mappings; only tests or scan guards may mention the attributes.
- `backend/app/services/natal/**` - out of scope for production mappings; runtime consumption is not part of this story.
- `backend/app/api/**` - out of scope; no API route or public JSON change is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q app/tests/integration/test_reference_data_migrations.py app/tests/unit/test_prediction_reference_repository.py`
- VC6: `rg -n "seasonal_quadrant|fertility|voice|humane|bestial|fruitful|barren|mute" app/domain/astrology app/services/natal -g "*.py"`
- VC7: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/schema-after.txt').exists()"`
- VC8: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/validation.txt').exists()"`
- VC9: `rg -n "sect|gender" "../docs/recherches astro" ../docs/db_seeder/astrology`

## Regression Risks

- Seed data can drift from migration defaults if the migration and service use separate hardcoded maps.
- Conditional sect or gender-compatible source traits can be missed without a recorded source decision artifact.
- Runtime payloads can change accidentally if repository DTOs are expanded during this DB-only story.
- Local domain mappings can appear in later runtime work unless this story leaves a targeted guard.
- Taxonomy names can diverge from existing English code conventions without tests over expected codes.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the backend venv before every Python, Ruff or Pytest command.
- Keep public JSON, `SignReferenceData` and `SignRuntimeData` unchanged in this story.
- Prefer dedicated taxonomy tables unless repository inspection proves an existing canonical structure should own these codes.
- Persist evidence artifacts listed in `Persistent Evidence Artifacts` before marking implementation complete.

## References

- `_story_briefs/cs-234-enrichir-profils-structurels-signes-db.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/infra/db/models/reference.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `docs/db_seeder/astrology`
