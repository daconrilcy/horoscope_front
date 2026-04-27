# Implementation Plan

## Findings

- `backend/app/api/v1/errors.py` was the old active facade for API error responses.
- Many services imported `api_error_response` and returned HTTP responses.
- Existing main exception handlers duplicated the envelope shape.

## Approach

- Add `ApplicationError` under `app.core.exceptions`.
- Add canonical API error contracts, catalog, handlers, and raising helper under `app.api.errors`.
- Replace service HTTP response construction with raised `ApplicationError`.
- Delete `app.api.v1.errors` instead of preserving a re-export.
- Add architecture guards and integration tests.

## Rollback

- Revert the package addition, service helper rename, main handler changes, and deleted `backend/app/api/v1/errors.py`.
