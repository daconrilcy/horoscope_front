# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/00-story.md`
- `backend/app/infra/db/models/user.py`
- `backend/app/api/v1/routers/public/users.py`
- `backend/app/services/api_contracts/public/users.py`
- `backend/app/api/v1/routers/public/reference_data.py`
- `backend/app/services/api_contracts/public/reference_data.py`
- `backend/migrations/versions/20260516_0119_add_user_detected_locale.py`
- `frontend/src/layouts/components/Header.tsx`
- `frontend/src/layouts/components/Header.css`
- `frontend/src/layouts/components/LanguageSelector.tsx`
- `frontend/src/api/languages.ts`
- `frontend/src/api/userSettings.ts`
- `frontend/src/i18n/astrology.ts`

## Required searches before editing

```powershell
rg -n "detected_locale|detected_country_code|detected_timezone|default_language_id" backend/app backend/migrations backend/app/tests
rg -n "LanguageSelector|chooseLanguage|SUPPORTED_LANGS" frontend/src
rg -n "style=" frontend/src/layouts/components frontend/src/api/languages.ts
rg -n "fetch\(|axios\." frontend/src/layouts/components frontend/src/api/languages.ts
```

## Modified files

- `backend/app/api/v1/routers/public/reference_data.py`
- `backend/app/api/v1/routers/public/users.py`
- `backend/app/tests/integration/test_users_settings.py`
- `frontend/src/i18n/astrology.ts`
- `frontend/src/layouts/components/LanguageSelector.tsx`
- `frontend/src/tests/astrology-i18n.test.ts`
- `frontend/src/tests/layout/Header.test.tsx`
- `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/00-story.md`
- `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/generated/*`
- `_condamad/stories/story-status.md`

## Inspected but not modified

- `backend/app/infra/db/models/user.py`
- `backend/app/services/api_contracts/public/users.py`
- `backend/app/services/api_contracts/public/reference_data.py`
- `backend/migrations/versions/20260516_0119_add_user_detected_locale.py`
- `frontend/src/layouts/components/Header.tsx`
- `frontend/src/layouts/components/Header.css`
- `frontend/src/api/languages.ts`
- `frontend/src/api/userSettings.ts`
- `backend/app/tests/integration/test_reference_languages_api.py`

## Forbidden or high-risk files

- `backend/app/domain/astrology/**` — out of scope.
- `frontend/src/App.css` — Header owns its styles through `Header.css`.
- `docs/db_seeder/languages.json` — seed source inspected but not changed.
