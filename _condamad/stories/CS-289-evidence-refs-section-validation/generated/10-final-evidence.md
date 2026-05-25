# CS-289 Final Evidence

## Story status

- Story key: CS-289-evidence-refs-section-validation
- Validation outcome: PASS
- Ready for review: clean
- Registry status: done
- Source story: `_condamad/stories/CS-289-evidence-refs-section-validation/00-story.md`
- Source brief: `_story_briefs/cs-289-implement-evidence-refs-validation.md`

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- `.git`: present.
- Initial worktree: dirty before CS-289, with many unrelated modified/untracked files already present.
- Story registry row matched `CS-289`, target path and source brief.
- Required generated capsule files were missing, so `condamad_prepare.py --repair-generated-only` and `condamad_validate.py` were run after venv activation.

## Capsule validation

- Initial repaired capsule validation: PASS.
- Final capsule validation: PASS.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Decorative string test rejects non-structured refs. | Targeted pytest and full pytest PASS. | PASS |
| AC2 | Projection hash-backed proof test accepts matching source hash. | Targeted pytest and full pytest PASS. | PASS |
| AC3 | LLM input hash-backed proof test accepts matching source hash. | Targeted pytest and full pytest PASS. | PASS |
| AC4 | No-proof-required section returns `not_required`. | Section status tests PASS. | PASS |
| AC5 | Missing source, unsupported type, missing hash and hash mismatch are classified. | Validation and section status tests PASS. | PASS |
| AC6 | `grounded` section status covered. | Section status tests PASS. | PASS |
| AC7 | `partial` section status covered. | Section status tests PASS. | PASS |
| AC8 | `ungrounded` section status covered. | Section status tests PASS. | PASS |
| AC9 | Repository integration persists section validation payloads in audit `evidence_refs`. | Integration test PASS. | PASS |
| AC10 | No route/schema added for proof internals. | Runtime `app.routes` and `app.openapi()` checks PASS. | PASS |
| AC11 | Architecture guard finds one canonical validator definition. | Architecture guard PASS. | PASS |
| AC12 | Evidence folder and generated evidence are persisted. | Capsule validation PASS. | PASS |

## Review/fix loop closure

- Iteration 1 finding: orphan or unscoped `evidence_refs` in multi-section audits could be ignored instead of reported as invalid section evidence.
- Iteration 1 finding: `source_hash` format validation only checked length and now enforces SHA-256 hexadecimal content.
- Fix evidence: validator now emits ungrounded orphan sections for unknown or unscoped references and tests cover unknown, unscoped decorative and non-hex hash cases.
- Fresh iteration 2 review: CLEAN.
- Alignment recheck 2026-05-25: source brief, tracker row, story ACs, implementation, tests and evidence reviewed.
- Evidence correction: missing declared artifact `evidence/duplicate-validator-scan.txt` was added after recheck.

## Files changed

- `backend/app/domain/astrology/interpretation/evidence_refs_validation.py`
- `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py`
- `backend/tests/unit/test_evidence_refs_validation.py`
- `backend/tests/unit/test_evidence_refs_section_status.py`
- `backend/tests/integration/test_narrative_answer_audit_evidence_refs.py`
- `backend/tests/architecture/test_evidence_refs_validation_boundary.py`
- `_condamad/stories/CS-289-evidence-refs-section-validation/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/unit/test_evidence_refs_validation.py`.
- Added `backend/tests/unit/test_evidence_refs_section_status.py`.
- Added `backend/tests/integration/test_narrative_answer_audit_evidence_refs.py`.
- Added `backend/tests/architecture/test_evidence_refs_validation_boundary.py`.

## Commands run

- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --root . --repair-generated-only _condamad\stories\CS-289-evidence-refs-section-validation` PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-289-evidence-refs-section-validation` PASS before implementation.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format <changed python files>` PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check <changed python files>` PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --tb=short tests\unit\test_evidence_refs_validation.py tests\unit\test_evidence_refs_section_status.py tests\integration\test_narrative_answer_audit_evidence_refs.py tests\architecture\test_evidence_refs_validation_boundary.py` PASS, 9 passed, 1 deselected.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --tb=short tests\unit\test_evidence_refs_validation.py tests\unit\test_evidence_refs_section_status.py tests\integration\test_narrative_answer_audit_evidence_refs.py tests\architecture\test_evidence_refs_validation_boundary.py app\tests\unit\test_backend_db_test_harness.py` PASS, 13 passed, 1 deselected.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --tb=short` PASS, 3358 passed, 1 skipped, 1209 deselected.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; ..."` PASS.
- `rg -n "validate_evidence_refs_by_section" backend\app backend\tests -g '!**/__pycache__/**' -g '!**/.pytest_cache/**'` PASS with expected canonical definition plus imports/tests.
- `rg -n "def validate_evidence_refs_by_section|class EvidenceRefsValidationResult|evidence_refs_validation" backend\app backend\tests -g '!**/__pycache__/**' -g '!**/.pytest_cache/**'` PASS and persisted to `evidence/duplicate-validator-scan.txt`.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-289-evidence-refs-section-validation\00-story.md` PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-289-evidence-refs-section-validation\00-story.md` PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-289-evidence-refs-section-validation\00-story.md` PASS after alignment evidence correction.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-289-evidence-refs-section-validation\00-story.md` PASS after alignment evidence correction.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check <CS-289 changed python files>` PASS after alignment evidence correction.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --tb=short tests\unit\test_evidence_refs_validation.py tests\unit\test_evidence_refs_section_status.py tests\integration\test_narrative_answer_audit_evidence_refs.py tests\architecture\test_evidence_refs_validation_boundary.py` PASS, 12 passed, 1 deselected after alignment evidence correction.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; ..."` PASS after alignment evidence correction.

## Commands skipped or blocked

- Local app server start: skipped, not applicable because CS-289 changes internal backend validation/audit logic only and adds no API/frontend surface.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback validator or frontend/client path was added.
- `validate_evidence_refs_by_section` is defined once in the canonical domain owner.
- Audit integration reuses the existing repository/model instead of adding a parallel audit writer or DB table.
- Decorative strings remain invalid and cannot mark a section grounded.

## Diff review

- Reviewed scoped status for changed CS-289 paths.
- Intended application delta is limited to validator, repository integration and tests.
- The first integration test used local `Base.metadata.create_all`; the global DB harness caught it and the test now uses the project `db` fixture.

## Final worktree status

- CS-289 scoped files are modified/untracked as expected.
- Broader repository remains dirty from unrelated pre-existing changes; those were not reverted or edited for this story.

## Remaining risks

- Aucun risque restant identifie.
- Post-review alignment recheck 2026-05-25: PASS after adding the missing declared duplicate-validator scan evidence artifact.

## Suggested reviewer focus

- Confirm the `evidence_refs` JSON section result shape is sufficient for downstream admin/audit consumers before they build UI or reports on it.

## Feedback loop routing

- no-propagation: implementation and validations converged after replacing an initial test DB `create_all` usage with the project DB fixture; the existing harness already covers the reusable lesson.
