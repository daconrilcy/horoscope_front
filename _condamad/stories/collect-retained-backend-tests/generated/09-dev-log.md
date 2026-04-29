# Dev Log

## Preflight

- Repository root: `C:/dev/horoscope_front`
- Story source: `_condamad/stories/collect-retained-backend-tests/00-story.md`
- Initial `git status --short`: multiple pre-existing untracked `_condamad` directories; permission warnings for pytest temp artifact directories.
- Applicable AGENTS.md: root `AGENTS.md`.
- Regression guardrails read: `_condamad/stories/regression-guardrails.md`, `RG-001` through `RG-009` applicable.
- Capsule generated: yes, required `generated/*` files created because only `00-story.md` existed.

## Decisions

- Place the guard under `backend/app/tests/unit` because it is already collected by the current pytest config, proving the guard is active immediately.
- Use `pytest --collect-only --json-report` only if already available is not assumed; use plain collect-only output parsing to avoid new dependencies.
- Treat `app/domain/llm/prompting/tests/test_qualified_context.py` as an exact opt-in exception: adding its package as `testpaths` makes collection fail because `app/domain/llm/prompting/tests/__init__.py` loads missing `tests/data/prompt_governance_registry.json`.

## Validation notes

- Initial collect-only attempt from `backend/` used the root-relative activation path and failed before the corrected run. The corrected commands were run from the repository root with the venv activated before `cd backend`.
- Full `pytest -q` now collects the previously hidden `tests/llm_orchestration` suite and fails there: 18 failed, 3436 passed, 12 skipped, 2 errors. These failures are in stale LLM tests and are outside this collection-hardening story.
