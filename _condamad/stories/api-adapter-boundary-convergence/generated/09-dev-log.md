# Dev Log

## Preflight

- Initial `git status --short`: `?? _condamad/stories/api-adapter-boundary-convergence/` with warnings for protected pytest temp directories.
- Current branch: pending capture.
- Existing dirty files: untracked story capsule directory only.
- AGENTS considered: root `AGENTS.md`.
- Capsule generated: yes, required files were missing and were generated with `condamad_prepare.py` after activating `.venv`.

## Search evidence

- Initial schemas FastAPI scan found many active hits under `backend/app/api/v1/schemas`.
- Initial non-API import scan found active `app.api` imports in `backend/app/services`.
- Initial legacy error scan found active `raise_http_error`, `legacy_detail`, and `content["detail"]` hits in API errors and routers.

## Implementation notes

- Removed active legacy HTTP error helper paths and kept only architecture guard text references.
- Post-review fixes migrated remaining tests from top-level `detail` to the canonical `error` envelope.
- Removed broad `ruff: noqa` suppressions from `app/services/api_contracts`, deleted stale logging/import noise, and added French docstrings to moved public contract classes.
- Targeted post-review validation passed with 103 tests; user reported the full backend suite green.

## Commands run

| Command | Result | Notes |
|---|---|---|

## Issues encountered

## Decisions made

## Final `git status --short`
