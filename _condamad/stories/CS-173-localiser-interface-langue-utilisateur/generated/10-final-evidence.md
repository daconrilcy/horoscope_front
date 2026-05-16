# Final Evidence — CS-173-localiser-interface-langue-utilisateur

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Final status: done after clean review
- Story key: CS-173-localiser-interface-langue-utilisateur
- Source story: `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/00-story.md`
- Capsule path: `_condamad/stories/CS-173-localiser-interface-langue-utilisateur`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/00-story.md`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: root `AGENTS.md`; no nested `AGENTS.md` under `backend`, `frontend`, or `_condamad`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | source story present |
| `generated/01-execution-brief.md` | yes | yes | PASS | generated execution brief present |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 mapped |
| `generated/04-target-files.md` | yes | yes | PASS | generated target map present |
| `generated/06-validation-plan.md` | yes | yes | PASS | commands updated to story scope |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-003/RG-004/RG-083/RG-108 recorded |
| `generated/10-final-evidence.md` | yes | yes | PASS | final evidence complete |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/api/v1/routers/public/reference_data.py`, `backend/app/services/api_contracts/public/reference_data.py`, `frontend/src/api/languages.ts`, `frontend/src/layouts/components/LanguageSelector.tsx` | `pytest --long -q app/tests/integration/test_reference_languages_api.py`; OpenAPI assertion; `npm run test -- Header` | PASS | API reads `LanguageModel`; frontend labels use API `name`. |
| AC2 | `backend/app/infra/db/models/user.py`, `backend/migrations/versions/20260516_0119_add_user_detected_locale.py`, `backend/app/api/v1/routers/public/users.py`, `backend/app/services/api_contracts/public/users.py` | `pytest --long -q app/tests/integration/test_users_settings.py`; OpenAPI assertion; `npm run test -- Header` BCP47 test | PASS | Locale, country and timezone are persisted; country code is alpha-2 validated. |
| AC3 | `frontend/src/layouts/components/Header.tsx`, `frontend/src/layouts/components/LanguageSelector.tsx`, `frontend/src/i18n/astrology.ts`, `frontend/src/api/userSettings.ts` | `npm run test -- Header`; `npm run test -- astrology-i18n`; `npm run lint` | PASS | Browser language is default, account preference overrides only when DB-backed option exists, selection persists through settings mutation. |
| AC4 | `frontend/src/layouts/components/Header.css`, `frontend/src/layouts/components/Header.tsx`, `frontend/src/layouts/components/LanguageSelector.tsx` | `rg -n "style=" src/layouts/components src/api/languages.ts` returned no hits; `npm run test -- Header` | PASS | No inline style added. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/api/v1/routers/public/reference_data.py` | modified | Return centralized API error if languages lookup fails. | AC1 |
| `backend/app/api/v1/routers/public/users.py` | modified | Validate country code and centralize settings persistence SQL errors. | AC2 |
| `backend/app/tests/integration/test_users_settings.py` | modified | Cover invalid detected country code. | AC2 |
| `frontend/src/i18n/astrology.ts` | modified | Browser locale default before storage cache; explicit selection/account override remains reactive. | AC3 |
| `frontend/src/layouts/components/LanguageSelector.tsx` | modified | Use API labels, require API-backed account language, parse country robustly. | AC1, AC2, AC3, AC4 |
| `frontend/src/tests/astrology-i18n.test.ts` | modified | Cover browser-before-cache language detection. | AC3 |
| `frontend/src/tests/layout/Header.test.tsx` | modified | Cover API labels, account preference filtering, BCP47 country extraction, selection persistence. | AC1, AC2, AC3, AC4 |
| `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/generated/*` | added/modified | Persistent CONDAMAD evidence. | AC1-AC4 |
| `_condamad/stories/story-status.md` | modified | Mark story done after clean review. | AC1-AC4 |

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/integration/test_users_settings.py`: added invalid country code case.
- `frontend/src/tests/layout/Header.test.tsx`: added API label, account preference, missing API option, and BCP47 country cases.
- `frontend/src/tests/astrology-i18n.test.ts`: updated language detection priority coverage.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py` | `backend` | FAIL | 1 | 8 tests deselected because integration tests require `--long`. |
| `pytest --long -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py` | `backend` | PASS | 0 | 9 tests passed. |
| `ruff format .` | `backend` | PASS | 0 | final run clean after formatting one touched file. |
| `ruff check .` | `backend` | PASS | 0 | all checks passed. |
| `python -c "from app.main import app; schema=app.openapi(); assert '/v1/reference-data/languages' in schema['paths']; props=schema['components']['schemas']['UserSettingsData']['properties']; assert {'astrologer_profile','default_astrologer_id','default_language_code','detected_locale','detected_country_code','detected_timezone'} <= set(props); print('openapi settings/languages OK')"` | `backend` | PASS | 0 | OpenAPI route and settings fields present. |
| `npm run test -- Header` | `frontend` | PASS | 0 | 10 tests passed. |
| `npm run test -- astrology-i18n` | `frontend` | PASS | 0 | 70 tests passed. |
| `npm run lint` | `frontend` | PASS | 0 | TypeScript lint script passed. |
| `rg -n "style=" src/layouts/components src/api/languages.ts` | `frontend` | PASS | 1 | no hits. |
| `rg -n "fetch\(|axios\." src/layouts/components src/api/languages.ts` | `frontend` | PASS | 1 | no hits. |
| `rg -n "\bany\b" src/layouts/components/LanguageSelector.tsx src/i18n/astrology.ts src/api/languages.ts` | `frontend` | PASS | 1 | no hits. |
| `git diff --check` | repository root | PASS | 0 | no whitespace errors; line-ending warnings only. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-173-localiser-interface-langue-utilisateur` | repository root | PASS | 0 | CONDAMAD validation PASS. |
| `Start-Process -FilePath 'npm.cmd' -ArgumentList @('run','dev','--','--host','127.0.0.1','--port','5173') ...` | repository root | PASS | 0 | Vite started; 5173 was busy, server is listening on `http://127.0.0.1:5174/`. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Global backend `pytest --long -q` | no | User asked not to use the `--long` version when running all tests; this execution ran only targeted `--long` integration files. | Wider backend regressions outside CS-173 not covered. | Targeted backend integration tests, OpenAPI assertion, `ruff check .`. |
| Full frontend `npm run test` | no | Bounded story; targeted Header and i18n tests plus lint covered changed frontend behavior. | Wider frontend regressions outside Header/i18n not covered. | `npm run test -- Header`, `npm run test -- astrology-i18n`, `npm run lint`. |
| Browser visual smoke | no | Browser automation tool was not available in the active tool list. | Runtime visual inspection not captured. | Vite dev server started on `http://127.0.0.1:5174/`, component tests, lint, OpenAPI import check, static guards. |

## DRY / No Legacy evidence

- Backend language catalogue uses `LanguageModel`; no backend language constant was introduced.
- Frontend language labels come from `/v1/reference-data/languages`; local frontend data is limited to supported interface codes and flags.
- Account language is applied only if present in the API-backed options.
- Direct HTTP scan in top-menu surfaces has no hits.
- Inline style scan in top-menu surfaces has no hits.
- `RG-003`, `RG-004`, `RG-083`, and `RG-108` evidence recorded in `generated/07-no-legacy-dry-guardrails.md`.

## Diff review

- `git diff --stat`: story-scoped backend API/tests, frontend Header/i18n/tests, and CONDAMAD evidence/status files.
- `git diff --check`: PASS.
- Rejected review finding: existing landing navbar language control is outside CS-173 because this story explicitly owns Header top-menu integration.

## Final worktree status

```text
 M _condamad/stories/CS-173-localiser-interface-langue-utilisateur/00-story.md
 M _condamad/stories/story-status.md
 M backend/app/api/v1/routers/public/reference_data.py
 M backend/app/api/v1/routers/public/users.py
 M backend/app/tests/integration/test_users_settings.py
 M frontend/src/i18n/astrology.ts
 M frontend/src/layouts/components/LanguageSelector.tsx
 M frontend/src/tests/astrology-i18n.test.ts
 M frontend/src/tests/layout/Header.test.tsx
?? _condamad/stories/CS-173-localiser-interface-langue-utilisateur/generated/
```

Pending story changes remain uncommitted by request; no commit or push was requested.

## Remaining risks

- No remaining blocking risk identified.
- Residual validation risk: full backend and frontend suites were not run; targeted story validation passed.

## Suggested reviewer focus

- Confirm the account-vs-browser language priority in `LanguageSelector.tsx` and `astrology.ts`.
- Confirm DB-backed language names and alpha-2 detected-country validation satisfy product expectations.
- Confirm rejected landing navbar scope decision is acceptable for CS-173.
