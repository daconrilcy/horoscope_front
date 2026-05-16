# Implementation Plan

## Initial repository findings

- The repository already contained most CS-173 runtime code when execution began: DB model columns, migration, settings API fields, languages API, Header selector, API client, and initial tests.
- Generated CONDAMAD evidence was missing and the story was still `ready-to-dev`.
- Independent review found stale frontend behavior, incomplete source-of-truth usage, weak country validation, and non-centralized SQL error handling.

## Proposed changes

- Keep existing backend contract shape and add hardening around detected country and SQL errors.
- Keep existing Header integration and converge `LanguageSelector` on API-backed language names and API-backed account preference validation.
- Preserve browser locale as default and let account settings override after loading.
- Fill CONDAMAD evidence and mark the story done after clean review.

## Files to modify

- Backend router hardening: `reference_data.py`, `users.py`.
- Backend targeted test: `test_users_settings.py`.
- Frontend language behavior: `astrology.ts`, `LanguageSelector.tsx`.
- Frontend targeted tests: `Header.test.tsx`, `astrology-i18n.test.ts`.
- Capsule evidence and story status files.

## Files to delete

- None.

## Tests to add or update

- Backend invalid detected country code integration test.
- Header tests for API labels, account preference present/missing in API options, selection persistence, and BCP47 country extraction.
- i18n test for browser language priority over cached storage.

## Risk assessment

- Risk: existing landing navbar still has an independent language control. Decision: out of CS-173 scope because the story canonical owner is Header top menu.
- Risk: full regression suites were not run. Mitigation: targeted backend/frontend tests, lint, OpenAPI check, and static guards passed.

## Rollback strategy

- Revert the bounded router/test/frontend/evidence changes from this story if validation regresses.
