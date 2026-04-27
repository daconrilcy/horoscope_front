# Dev Log

## Preflight

- Initial `git status --short` showed pre-existing dirty files:
  - `M _condamad/stories/regression-guardrails.md`
  - `?? _condamad/stories/harden-api-adapter-boundary-guards/`
- The story folder initially contained only `00-story.md`; generated capsule files were created before code edits.
- `condamad_prepare.py` first inferred an unwanted story-key folder; it was removed after generating the requested capsule path.

## Implementation notes

- Added `app.api.route_exceptions` as the single structured exception register.
- Replaced direct exception route mounting in `main.py` with `include_registered_route_exceptions(app)`.
- Extracted `PATCH /v1/admin/content/texts/{key}` persistence to `update_config_text_value`.
- Added SQL allowlist AST guard and extracted-flow guard in `test_api_router_architecture.py`.

## Validation notes

- First architecture test run failed on a test assertion comparing `set()` to `[]`; fixed and reran successfully.
- Full `pytest -q` timed out after 604 seconds. Targeted architecture and admin-content integration tests passed.
