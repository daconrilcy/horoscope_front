# Dev Log

## Preflight

- Initial `git status --short`: clean.
- Current branch: not changed by this execution.
- Existing dirty files: none before capsule generation.
- Capsule generated: yes, under `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/generated/`.
- AGENTS considered: root `AGENTS.md`; no nested `AGENTS.md` found under `backend`, `frontend`, or `_condamad`.

## Implementation notes

- Repository already contained the core CS-173 implementation when inspected: user localization columns, settings fields, languages route, frontend client, Header selector, migration, and initial tests.
- Review found stale frontend behavior and incomplete evidence.
- Backend fixes added centralized SQL error handling for settings/languages and alpha-2 country validation.
- Frontend fixes were implemented through `condamad-frontend-dev` ownership for `frontend/**`.

## Review findings

| Finding | Decision | Resolution |
|---|---|---|
| Source review: `detectLang()` prioritized `localStorage` before browser language. | accepted | `detectLang()` now uses browser language before cached storage unless there is an active explicit session override. |
| Source/story review: account preference applied without checking API language options. | accepted | `LanguageSelector` checks the API-backed option set before applying `default_language_code`. |
| Story/technical review: language labels came from `LANGUAGE_NAMES`. | accepted | labels now use `language.name` from `/v1/reference-data/languages`. |
| Story review: selecting a language could be reverted by stale settings. | accepted | active language override preserves the explicit selection while mutation/refetch catches up. |
| Technical review: country parsing failed BCP47 script locales. | accepted | frontend uses `Intl.Locale().region` with fallback subtag scan; backend validates alpha-2. |
| Technical review: SQL errors not centralized. | accepted | languages lookup and settings persistence return canonical API error envelopes. |
| Technical review: landing navbar has another language control. | rejected | out of CS-173 scope; story canonical owner for this change is Header top menu. |
| Evidence files incomplete. | accepted | traceability, validation plan, final evidence, and review evidence were filled. |

## Commands run

| Command | Result | Notes |
|---|---|---|
| `pytest -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py` | FAIL | 8 tests deselected without `--long`; repository hook excludes integration tests from fast runs. |
| `pytest --long -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py` | PASS | 9 targeted integration tests passed after backend fixes. |
| `ruff format .` | PASS | backend formatting applied, final run clean. |
| `ruff check .` | PASS | backend lint clean. |
| `npm run test -- Header` | PASS | 10 tests passed. |
| `npm run test -- astrology-i18n` | PASS | 70 tests passed. |
| `npm run lint` | PASS | TypeScript lint script passed. |
| `rg -n "style=" src/layouts/components src/api/languages.ts` | PASS | no hits. |
| `rg -n "fetch\(|axios\." src/layouts/components src/api/languages.ts` | PASS | no hits. |
| `rg -n "\bany\b" src/layouts/components/LanguageSelector.tsx src/i18n/astrology.ts src/api/languages.ts` | PASS | no hits. |
| OpenAPI settings/languages assertion | PASS | route and settings fields present. |
| `git diff --check` | PASS | no whitespace errors; Git emitted line-ending warnings only. |

## Final `git status --short`

Recorded in `generated/10-final-evidence.md` after final validation.
