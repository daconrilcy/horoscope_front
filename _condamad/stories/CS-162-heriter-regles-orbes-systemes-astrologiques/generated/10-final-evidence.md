<!-- Preuve finale CONDAMAD de CS-162. -->

# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-162-heriter-regles-orbes-systemes-astrologiques`
- Source story: `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/00-story.md`
- Capsule path: `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes
- Story sufficiency gate: PASS

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC26 covered and passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `AstralSystemModel.inherits_from_system_id`; migration `20260514_0105`. | `pytest -q app/tests/integration/test_reference_data_migrations.py` | PASS | Self-FK reflected. |
| AC2 | `_ensure_astral_systems` maps child systems to `traditional`. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py` | PASS | Exact map asserted. |
| AC3 | JSON uses `inherits_from`, not `copy_rules_from`. | `rg -n "copy_rules_from" "..\docs\recherches astro\astral_aspect_orb_rules.json"` zero hit | PASS | |
| AC4 | Seed count changed to 79 and tested by system. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py` | PASS | `modern=39`, `traditional=40`, children `0`. |
| AC5-AC16 | `resolve_orb` resolves local/parent chain, priority, specificity, cycle and fallback behavior. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_prediction_reference_repository.py` | PASS | 48 tests passed. |
| AC17 | Seed rejects full inherited copies and migration cleans old duplicates. | `pytest -q app/tests/unit/test_reference_data_service.py app/tests/integration/test_seed_31_prediction_v2.py`; `pytest -q app/tests/integration/test_reference_data_migrations.py` | PASS | Guard + data migration test. |
| AC18-AC26 | Three research docs include inheritance title and mappings. | Documentation `rg` scans passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/reference.py` | modified | Add astral system inheritance relation. | AC1 |
| `backend/migrations/versions/20260514_0105_add_astral_system_inheritance.py` | added | Add self-FK and clean old child duplicate orb rules. | AC1, AC4, AC17 |
| `backend/migrations/versions/20260514_0104_add_astral_aspect_orb_rules.py` | modified | Stop historical migration from accepting `copy_rules_from`. | AC3, AC17 |
| `backend/app/services/prediction/reference_seed_service.py` | modified | Seed inheritance map, 79 physical rules, anti-copy and unknown-parent guards. | AC2, AC4, AC17 |
| `backend/app/infra/db/repositories/reference_repository.py` | modified | Expose `astral_systems` inheritance metadata. | AC7, AC8 |
| `backend/app/domain/astrology/calculators/aspects.py` | modified | Resolve local then inherited rules with cycle guard. | AC5-AC16 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Pass inheritance metadata to aspect calculation. | AC7, AC8 |
| Backend tests | modified | Add resolver, seed, repository and migration guards. | AC1-AC17 |
| `docs/recherches astro/*.md` and `astral_aspect_orb_rules.json` | modified | Document inheritance and remove physical child copies. | AC3, AC18-AC26 |
| `_condamad/stories/CS-162-*/generated/*.md` | added/modified | Capsule and review evidence. | all |

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/unit/test_aspect_orb_overrides.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .` | repo root | PASS | 0 | Formatting applied where needed. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_prediction_reference_repository.py` | repo root | PASS | 0 | 48 passed. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_reference_data_service.py app/tests/integration/test_seed_31_prediction_v2.py` | repo root | PASS | 0 | 14 passed, known SQLAlchemy reflection warnings. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/integration/test_reference_data_migrations.py` | repo root | PASS | 0 | 2 passed, known SQLAlchemy reflection warnings. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/integration/test_reference_data_migrations.py` | repo root | PASS | 0 | 64 passed, 35 known SQLAlchemy reflection warnings. |
| `rg -n "copy_rules_from" "..\docs\recherches astro\astral_aspect_orb_rules.json"` | `backend` | PASS | 1 | Zero hits expected. |
| `rg -n "Héritage des systèmes astrologiques" ...` | `backend` | PASS | 0 | Three docs contain the section. |
| `rg -n "hellenistic.*traditional\|medieval.*traditional" ...` | `backend` | PASS | 0 | Required mappings present. |
| `rg -n "app\.domain\.prediction\|app\.services\.prediction" app/domain/astrology -g "*.py"` | `backend` | PASS | 1 | Zero hits expected. |
| `rg -n "astro_characteristics\|AstroCharacteristicModel" app tests` | `backend` | PASS | 0 | Only expected migration guard hits. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8016` | repo root | PASS | 0 | Startup verified then process stopped; existing Stripe portal advisory logged. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Full `pytest -q` | no | Targeted unit/integration suites cover changed domain; full suite is outside story validation plan. | Residual unrelated regression risk. | Targeted seed, migration, resolver, repository and lint checks passed. |

## DRY / No Legacy evidence

- No `copy_rules_from` remains in active JSON.
- `hellenistic` and `medieval` store no copied physical rules in seed output.
- Migration `0105` deletes copied child rows for databases that already ran the older `0104` state.
- Resolver has one canonical implementation path in `domain/astrology/calculators/aspects.py`.
- No forbidden `app.domain.prediction` or `app.services.prediction` import exists under `app/domain/astrology`.

## Diff review

- Diff scope is limited to backend reference/orb runtime, tests, docs, migration, and story evidence.
- `git diff --check` passed.
- New migration file is part of the story changes and must be included with the change set.
- Review/fix iteration 2 corrected migration SQL portability and empty inheritance metadata validation, then re-ran lint, targeted tests, scans and startup smoke.

## Final worktree status

- `git status --short` shows only expected CS-162 code, docs, migration, capsule and status files.

## Remaining risks

- No remaining story risk identified.

## Suggested reviewer focus

- Review `20260514_0105` data cleanup semantics for preserving true child local overrides.
- Review resolver ordering: local depth first, then priority, then specificity.
