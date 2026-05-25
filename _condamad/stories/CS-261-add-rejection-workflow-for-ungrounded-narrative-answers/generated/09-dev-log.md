# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: repository was already dirty with CS-256 to CS-260 story/evidence/docs changes and `story-status.md`; these pre-existing changes were not modified except for the exact CS-261 status row.
- Story registry check: `CS-261` row matched target path and source brief before implementation.
- Capsule preparation: generated files were missing, so `condamad_prepare.py --repair-generated-only` and `condamad_validate.py` were run with the venv activated.

## Search evidence

- Read source brief `_story_briefs/cs-261-add-rejection-workflow-for-ungrounded-narrative-answers.md`.
- Read upstream contracts `docs/architecture/narrative-answer-audit-v1-contract.md` and `docs/architecture/evidence-refs-contract.md`.
- Targeted owner scan found existing runtime observability and client masking owners without changing them:
  - `backend/app/domain/llm/runtime/observability_service.py`;
  - `backend/app/domain/llm/runtime/gateway.py`;
  - `backend/app/services/llm_generation/chat/chat_guidance_service.py`.

## Implementation notes

- Added one canonical declarative workflow document: `docs/architecture/ungrounded-narrative-rejection-workflow.md`.
- No backend app, frontend source, database, migration, provider, route, serializer, prompt, generated client or retry runtime was modified.
- A temporary lowercase capsule path was accidentally created by `condamad_prepare.py`; because Windows path resolution is case-insensitive, the target capsule was restored from git and repaired with the intended target path. No unrelated story files were reverted.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `git status --short` | PASS | Preflight showed pre-existing dirty files outside CS-261. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ...` | PASS | Venv activated; generated missing CS-261 files. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | PASS | Capsule structure valid before implementation. |
| `rg -n "rejected|ungrounded|rejection_reason|réponse rejetée|message contrôlé|retry|audit|..." ...` | PASS | Evidence stored in `evidence/validation.txt`. |
| `git status --short -- backend/app frontend/src` | PASS | Empty output stored in `evidence/app-surface-status.txt`. |
| `python -B -c "from app.main import app; ..."` | PASS | OpenAPI/routes loaded; no rejection/ungrounded public path. |
| `rg -n "retry queue|retry_queue|..." docs\architecture\ungrounded-narrative-rejection-workflow.md` | PASS | Evidence stored in `evidence/no-legacy-dry-scan.txt`. |
| `ruff check .` | PASS | Run from `backend` with venv activated. |
| `python -B -m pytest -q --tb=short` | PASS | 3236 passed, 1 skipped, 1182 deselected. |

## Issues encountered

- The first capsule prepare command produced a lowercase parallel capsule path. The run was corrected by restoring the target capsule and using `--repair-generated-only` on the exact CS-261 capsule.
- Implementation review found that `evidence/app-surface-status.txt` was cited by the story and final evidence but missing from the capsule. The file was added with the scoped app/frontend status proof.
- Implementation review found that the existing `generated/11-code-review.md` was an editorial story review rather than an implementation review. It was replaced with a fresh implementation review artifact.

## Decisions made

- Kept the story as documentation-only because the ACs and non-goals forbid runtime/API/DB/frontend/retry implementation.
- Reused CS-259 and CS-260 terminology rather than duplicating audit or proof ownership.
- Did not run frontend checks because no frontend source or generated client was touched.

## Final `git status --short`

- Captured after final validation in `generated/10-final-evidence.md`.
