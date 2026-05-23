# Final Evidence - CS-235-brancher-attributs-structurels-signes-runtime-natal

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-235-brancher-attributs-structurels-signes-runtime-natal
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/00-story.md`
- Initial `git status --short`: dirty worktree present before CS-235 edits.
- Pre-existing dirty files: CS-234 DB/model/seed changes, `.gitignore`, `_condamad/codex-runs/**` deletions, generated skill/story files.
- AGENTS.md files considered: root `AGENTS.md`; no additional backend `AGENTS.md` found with bounded `rg`.
- Capsule generated: required generated files were missing and were prepared before implementation.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story source retained. |
| `generated/01-execution-brief.md` | yes | yes | PASS | CS-235 objective scoped. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All AC rows PASS. |
| `generated/04-target-files.md` | yes | yes | PASS | Final touched files listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands reflect executed checks. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No Legacy result recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Repository joins CS-234 taxonomy tables and emits `seasonal_quadrant`, `fertility`, `voice`, `form`. | Repository pytest PASS; assertions include all four fields. | PASS | DB-backed source only. |
| AC2 | Mapper requires all four fields with `_required_str`; runtime contracts reject blank/`unknown`. | Targeted pytest PASS; missing profile path still fails without fallback. | PASS | No fallback added. |
| AC3 | `SignReferenceData` has required `seasonal_quadrant`, `fertility`, `voice`, `form`. | Targeted pytest PASS. | PASS | Required dataclass fields. |
| AC4 | `SignRuntimeData` has required fields and builder copies from `SignReferenceData`. | Builder pytest PASS. | PASS | No local derivation from sign code. |
| AC5 | `_serialize_signs_runtime()` emits four additive fields. | Chart JSON pytest PASS; `evidence/signs-runtime-json.txt`. | PASS | Public JSON additive only. |
| AC6 | Guard forbids production mapping symbols; fixtures remain test-only records. | Guard pytest PASS. | PASS | No seed import in factory. |
| AC7 | No forbidden mapping symbols in `backend/app/domain/astrology`. | Targeted `rg` exit 1, PASS no matches. | PASS | Exit 1 classified as expected absence. |
| AC8 | No forbidden mapping symbols in `backend/app/services/natal`. | Targeted `rg` exit 1, PASS no matches. | PASS | Natal services unchanged. |
| AC9 | Evidence artifacts persisted under `evidence/` and generated files updated. | Evidence directory and `validation.txt` checks PASS. | PASS | Story status updated. |

## Files changed

- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`
- `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/generated/**`
- `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-235-brancher-attributs-structurels-signes-runtime-natal` | repo root | PASS | 0 | Capsule valid after preparation. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format <changed python files>` | repo root | PASS | 0 | Scoped formatting. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q app\tests\unit\test_astrology_runtime_reference_repository.py tests\unit\domain\astrology\test_sign_runtime_builder.py app\tests\unit\test_chart_json_builder.py app\tests\unit\test_astrology_runtime_reference_guard.py tests\unit\domain\astrology\test_sign_runtime_data.py tests\unit\domain\astrology\test_chart_signature.py` | repo root | PASS | 0 | 66 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `rg -n "SEASONAL_QUADRANT_BY_SIGN|FERTILITY_BY_SIGN|VOICE_BY_SIGN|FORM_BY_SIGN|HUMANE_BY_SIGN|BESTIAL_BY_SIGN" app\domain\astrology app\services\natal -g "*.py"` | `backend` | PASS | 1 | No matches, expected for negative scan. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert hasattr(app, 'routes'); assert callable(app.openapi)"` | repo root | PASS | 0 | App import smoke check. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence').is_dir(); assert Path('../_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/validation.txt').exists()"` | repo root | PASS | 0 | Evidence artifacts exist. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors. |

## Commands skipped or blocked

- Full backend `python -B -m pytest -q`: not run; targeted story checks passed. Risk: unrelated backend surfaces outside CS-235 are not covered by this handoff.
- Frontend checks: not run; frontend is explicitly out of scope and unchanged.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback, or parallel runtime source was added.
- No production sign-to-attribute mapping symbols were introduced.
- `SignReferenceData` remains the single runtime source for structural sign attributes.
- `SignRuntimeData` copies from `SignReferenceData`; it does not derive values from `sign_code`.
- Feedback-loop routing: `no-propagation`; the temporary evidence-format validation failure was local and corrected in this capsule.

## Diff review

- `git diff --stat`: reviewed; includes pre-existing unrelated CS-234 and housekeeping changes plus CS-235 files.
- `git diff --check`: PASS.
- Scoped `git diff -- <CS-235 files>` reviewed before evidence update.

## Final worktree status

- Dirty worktree remains because pre-existing unrelated changes are still present and CS-235 adds implementation/evidence changes.
- CS-235 row in `_condamad/stories/story-status.md` is `done` after the clean implementation review.

## Remaining risks

- Full backend regression was not run.
- Test fixtures contain explicit test-only sign profile records; production code has no equivalent mapping and guards cover the forbidden symbols.

## Suggested reviewer focus

- Verify the repository joins align with CS-234 taxonomy model names.
- Verify additive `signs_runtime` JSON fields are acceptable for existing consumers.
- Verify the fixture records are acceptable as test data and not a production source.
