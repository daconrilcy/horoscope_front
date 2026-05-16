# Code Review — CS-173-localiser-interface-langue-utilisateur

## Verdict

CLEAN

## Review iterations

- Iteration 1: independent reviews found frontend priority/source-of-truth issues, backend validation/error handling gaps, and incomplete evidence.
- Fix batch: frontend fixes routed through `condamad-frontend-dev`; backend fixes applied in the main session; evidence files updated.
- Fresh review result: no blocking finding remains after targeted validation.

## Accepted findings fixed

| Category | Finding | Resolution |
|---|---|---|
| Frontend behavior | `localStorage` could beat browser locale before account settings loaded. | Browser locale now defaults first; explicit active selection/account override remains reactive. |
| Frontend behavior | Stale account settings could temporarily override a fresh selection. | Active language override protects the explicit selection while mutation/refetch catches up. |
| Frontend source of truth | Account language applied without checking API language options. | Settings language must be locally supported and present in API-backed options. |
| Frontend source of truth | Language names came from a local constant. | Displayed labels use `language.name` from `/v1/reference-data/languages`. |
| Frontend localization metadata | Country extraction failed BCP47 script locales. | `Intl.Locale().region` plus fallback subtag scan handles `zh-Hant-TW`. |
| Backend validation | Detected country accepted any two characters. | Route rejects non alpha-2 country codes with canonical API envelope. |
| Backend error handling | SQLAlchemy failures could bypass central API error envelope. | Languages lookup and settings persistence now catch SQLAlchemy errors and return canonical envelopes. |
| Evidence | CONDAMAD capsule was incomplete. | Traceability, validation plan, no-legacy evidence, final evidence, and review evidence completed. |

## Rejected findings

| Finding | Decision | Reason |
|---|---|---|
| Refactor existing landing navbar language control to DB-backed selector. | Rejected | Out of CS-173 scope. The story canonical owner for this change is Header top menu: `Header.tsx` and `LanguageSelector.tsx`. |

## Validation evidence

- `pytest --long -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py` — PASS, 9 tests.
- `ruff format .` — PASS.
- `ruff check .` — PASS.
- OpenAPI settings/languages assertion — PASS.
- `npm run test -- Header` — PASS, 10 tests.
- `npm run test -- astrology-i18n` — PASS, 70 tests.
- `npm run lint` — PASS.
- `rg -n "style=" src/layouts/components src/api/languages.ts` — PASS, no hits.
- `rg -n "fetch\(|axios\." src/layouts/components src/api/languages.ts` — PASS, no hits.
- `rg -n "\bany\b" src/layouts/components/LanguageSelector.tsx src/i18n/astrology.ts src/api/languages.ts` — PASS, no hits.
- `git diff --check` — PASS.

## Residual risk

- Full backend and frontend suites were not run; targeted story validation passed.
- No remaining blocking issue identified.
