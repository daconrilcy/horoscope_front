# Dev Log

- Preflight: `backend/horoscope.db` was already modified; capsule directory was untracked.
- Generated missing CONDAMAD capsule files with activated venv.
- Added canonical API error package and core `ApplicationError`.
- Migrated services from `api_error_response` imports to `ApplicationError`.
- Renamed helper surface from `_error_response` / `_create_error_response` to `_raise_error`.
- Deleted `backend/app/api/v1/errors.py`.
- Targeted tests and lint pass.
- Full `pytest -q` timed out after 604 seconds.
