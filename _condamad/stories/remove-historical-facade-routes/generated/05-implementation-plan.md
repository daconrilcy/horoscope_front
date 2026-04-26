# Implementation Plan

## Findings

- `/v1/ai` is mounted from `backend/app/main.py` and mirrored in `backend/tests/evaluation/__init__.py`.
- The dedicated `/v1/ai` modules are `backend/app/api/v1/routers/public/ai.py`, `backend/app/api/v1/router_logic/public/ai.py`, and `backend/app/api/v1/schemas/ai.py`.
- First-party chat and guidance clients already use `/v1/chat/*` and `/v1/guidance/*`.
- Admin generation exports still expose `use_case_compat` via service model, CSV/JSON fields and deprecation headers.
- Frontend routing still declares `/admin/prompts/legacy`; tests assert that legacy route as nominal behavior.

## Patch sequence

1. Produce deterministic audit and audit validator.
2. Remove `/v1/ai` registration and dedicated modules.
3. Remove `use_case_compat` from export row contract, export headers, CSV fields, UI notice and tests.
4. Remove admin audit legacy states from backend and frontend nominal types.
5. Remove frontend legacy prompt route and update routing tests.
6. Add/update architecture and OpenAPI guards.
7. Run targeted validation, lint, negative scans and final diff review.

## No Legacy stance

Removed surfaces are deleted. No redirect, alias, compatibility module, wrapper, or fallback route is allowed.

## Rollback

Use git diff to revert only story-owned changes if a blocker appears; do not touch pre-existing `backend/horoscope.db`.
