# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-152-normaliser-profils-signes-astraux`
- Source story: `_condamad/stories/CS-152-normaliser-profils-signes-astraux/00-story.md`
- Capsule path: `_condamad/stories/CS-152-normaliser-profils-signes-astraux`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial dirty files: `.codex-artifacts/**`, `docs/recherches astro/signs_keywords.json`, `output/`
- Final unrelated dirty files still preserved: `.codex-artifacts/**`, `docs/recherches astro/Soleil Signes.png`, `output/`
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Existing source story. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC9 passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `AstralSignModel` / `astral_signs`, Alembic `20260513_0087`. | Migration + seed tests PASS. | PASS | 12 signes conservés. |
| AC2 | `AstralElementModel`, `AstralModalityModel`, `AstralPolarityModel`. | Seed test asserts exact code sets. | PASS | 4/3/2 valeurs. |
| AC3 | `AstralSignProfileModel` + seed synchronisé depuis `signs_keywords.json`. | Seed test asserts 12-row matrix and non-empty keyword arrays. | PASS | JSON source required and validated. |
| AC4 | Unique constraint only on `astral_sign_id`. | Migration test inspects constraints. | PASS | Dimensions shared not unique. |
| AC5 | `AstralSignRulershipModel` / `astral_sign_rulerships`. | Migration test + scans PASS. | PASS | Old table absent at head. |
| AC6 | Seed `domicile`, `traditional`, `1.0`, `true`. | Seed test asserts exact tuple. | PASS | |
| AC7 | Repository `get_sign_rulerships(system="traditional")`. | Unit test with modern conflicting row PASS. | PASS | No version filter. |
| AC8 | No active shim/view/tablename for old names. | Scans zero-hit for old active patterns. | PASS | |
| AC9 | `RG-091`, `RG-092`, `RG-093`. | Tests and scans PASS; RG-091 hits classified as guard tests. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/infra/db/models/reference.py` | modified | Canonical astral sign/taxonomy/profile models. | AC1-AC4 |
| `backend/app/infra/db/models/prediction_reference.py` | modified | Non-versioned astral sign rulership model. | AC5-AC7 |
| `backend/app/infra/db/models/__init__.py` | modified | Export canonical models. | AC1-AC7 |
| `backend/app/infra/db/repositories/reference_repository.py` | modified | Seed/read `AstralSignModel`. | AC1 |
| `backend/app/infra/db/repositories/prediction_reference_repository.py` | modified | Read traditional rulerships without version filter. | AC7 |
| `backend/app/services/b2b/astrology_service.py` | modified | Consume canonical sign model. | AC1 |
| `backend/app/services/prediction/reference_seed_service.py` | modified | Seed/sync taxonomies, profiles, rulerships and keyword validation. | AC2-AC7 |
| `backend/migrations/versions/20260513_0087_normalize_astral_sign_profiles.py` | added | Rename/create schema and tolerate empty ORM pre-bootstrap tables. | AC1-AC5 |
| `backend/pyproject.toml` | modified | Package the docs keyword JSON for installed backend runtime. | AC3 |
| Targeted backend tests | modified | Rename model imports and add exact guards. | AC1-AC9 |
| `docs/recherches astro/signs_keywords.json` | added/untracked source | Canonical keyword source used by seed and packaged by backend build. | AC3 |
| CONDAMAD story artifacts | added/modified | Baseline, after-state, final evidence, review evidence. | AC1-AC9 |

## Files deleted

None.

## Tests added or updated

- `backend/app/tests/unit/test_prediction_reference_repository.py`: system-aware rulership guard.
- `backend/app/tests/integration/test_reference_data_migrations.py`: `astral_*` schema and uniqueness guards.
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`: exact taxonomy sets, 12 profile mappings, non-empty keywords, locked seed repair.
- Existing sign model imports in backend tests updated to `AstralSignModel`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `ruff format .` | `backend` | PASS | 0 | Formatting completed. |
| `ruff check .` | `backend` | PASS | 0 | All checks passed. |
| `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` | `backend` | PASS | 0 | 15 passed. |
| `pytest app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py -q` | `backend` | PASS | 0 | 4 passed. |
| `rg -n 'SignRulershipModel\.reference_version_id|SignRulershipModel\(reference_version_id' app tests` | `backend` | PASS | 1 | Zero active hit. |
| `rg -n 'get_sign_rulerships\(reference_version_id\)|__tablename__ = "signs"' app tests` | `backend` | PASS | 1 | Zero active hit. |
| `rg -n '__tablename__ = "sign_rulerships"' app tests` | `backend` | PASS | 1 | Zero active hit. |
| `rg -n 'AstroCharacteristicModel|astro_characteristics' app tests` | `backend` | PASS | 0 | Only expected migration guard test hits. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; line-ending warnings only. |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765` smoke via hidden process | `backend` | PASS | 0 | Process remained alive after startup and was stopped. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

| Pattern | Classification | Evidence |
|---|---|---|
| `SignRulershipModel.reference_version_id` / constructor version field | `active_legacy_removed` | Zero active hit. |
| `get_sign_rulerships(reference_version_id)` | `active_legacy_removed` | Zero active hit. |
| `__tablename__ = "signs"` | `active_legacy_removed` | Zero active hit. |
| `__tablename__ = "sign_rulerships"` | `active_legacy_removed` | Zero active hit. |
| `AstroCharacteristicModel|astro_characteristics` | `test_guard_expected_hit` | Hits only in migration guard test baseline/head assertions. |

## Review / fix evidence

- Independent review subagents used: yes, three read-only layers.
- Review/fix iterations: 1.
- Accepted findings fixed:
  - strict keyword validation and profile synchronization;
  - exact 12-profile test coverage;
  - `system="traditional"` repository filtering;
  - locked seed repair for empty taxonomy/profile tables;
  - packaged keyword JSON inclusion;
  - completed final evidence.
- Rejected findings: none; unrelated `.codex-artifacts/**`, `Soleil Signes.png`, and `output/` classified as pre-existing/unrelated worktree state.

## Diff review

- Story diff reviewed with `git diff --stat` and targeted file diffs.
- Frontend unchanged.
- No commit or push performed.

## Final worktree status

Expected story changes remain uncommitted. Pre-existing unrelated dirty files remain preserved.

## Remaining risks

Aucun risque restant identifie.

## Suggested reviewer focus

Review Alembic behavior around empty pre-bootstrap target tables and confirm the packaged docs JSON policy is acceptable for production installs.
