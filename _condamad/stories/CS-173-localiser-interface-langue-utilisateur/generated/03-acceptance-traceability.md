# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les langues disponibles pour l'interface sont lues depuis la table `languages`. | `LanguageModel` lu par `/v1/reference-data/languages`, contrat `LanguagesApiResponse`, client `frontend/src/api/languages.ts`. | `pytest --long -q app/tests/integration/test_reference_languages_api.py`, OpenAPI check, tests Header avec labels API. | PASS |
| AC2 | Le compte utilisateur persiste la localisation détectée optionnelle. | Colonnes utilisateur, migration, champs settings GET/PATCH, validation alpha-2 du pays. | `pytest --long -q app/tests/integration/test_users_settings.py`, OpenAPI check, test Header locale `zh-Hant-TW`. | PASS |
| AC3 | Le Header persiste le choix utilisateur via le bouton de langue. | `Header.tsx` intègre `LanguageSelector`; sélection via API languages + `useUpdateUserSettings`; préférence compte appliquée seulement si présente dans les options API. | `npm run test -- Header`, `npm run test -- astrology-i18n`, `npm run lint`. | PASS |
| AC4 | Aucun style inline n'est ajouté dans les composants du top menu. | Styles dans `Header.css`; aucun `style=` dans `Header.tsx`, `LanguageSelector.tsx` ou `api/languages.ts`. | `rg -n "style=" src/layouts/components src/api/languages.ts` sans hit. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
