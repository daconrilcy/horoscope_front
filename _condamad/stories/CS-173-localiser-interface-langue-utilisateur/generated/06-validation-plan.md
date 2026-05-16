# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Backend root: `backend`
- Frontend root: `frontend`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- User constraint: do not run the global test suite with `--long`; targeted integration tests may use `--long` because the repository deselects integration tests otherwise.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend settings and languages contracts | `pytest --long -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py` | `backend` | yes | all targeted integration tests pass |
| Frontend Header language selector | `npm run test -- Header` | `frontend` | yes | Header tests pass |
| Frontend language detection | `npm run test -- astrology-i18n` | `frontend` | yes | i18n detection tests pass |
| OpenAPI contract | `python -c "from app.main import app; schema=app.openapi(); assert '/v1/reference-data/languages' in schema['paths']; props=schema['components']['schemas']['UserSettingsData']['properties']; assert {'astrologer_profile','default_astrologer_id','default_language_code','detected_locale','detected_country_code','detected_timezone'} <= set(props); print('openapi settings/languages OK')"` | `backend` | yes | route and settings fields are exposed |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Inline style guard | `rg -n "style=" src/layouts/components src/api/languages.ts` | `frontend` | yes | no hits |
| Direct HTTP guard | `rg -n "fetch\(|axios\." src/layouts/components src/api/languages.ts` | `frontend` | yes | no hits |
| Type escape guard | `rg -n "\bany\b" src/layouts/components/LanguageSelector.tsx src/i18n/astrology.ts src/api/languages.ts` | `frontend` | yes | no hits |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend format | `ruff format .` | `backend` | yes | no formatting drift remains |
| Backend lint | `ruff check .` | `backend` | yes | no lint errors |
| Frontend type/lint | `npm run lint` | `frontend` | yes | TypeScript lint script passes |
| Diff whitespace | `git diff --check` | repository root | yes | no whitespace or conflict marker errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend fast suite | `pytest -q` | `backend` | no | skipped: targeted story tests plus lint were run; global fast suite not required for this bounded story |
| Full frontend suite | `npm run test` | `frontend` | no | skipped: targeted Header and i18n suites plus lint were run |

## Rule for skipped commands

Skipped commands must be recorded with reason, risk, and compensating evidence in `generated/10-final-evidence.md`.
