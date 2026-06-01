# Frontend Removal Audit — CS-439

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `mapProductActionDataToInterpretation` | symbol | historical-facade | `useNatalInterpretation` modern product action | `normalizeThemeNatalReadingPublicPayload` accepting only `theme_natal*` public schema data | delete | `adapter-symbol-after.txt` zero-hit | Old DTO remap returns if guard weakens. |
| `NatalInterpretationResult` modern target | type | historical-facade | public reading hook and by-id typing | `ThemeNatalReadingPublicPayload` | replace-consumer | `adapter-symbol-after.txt` zero-hit | Old envelope becomes nominal again if type name returns. |
| `isNatalInterpretationResult` | symbol | historical-facade | old compatibility acceptance in product-action response | no compatibility guard; non-theme data returns `null` | delete | `adapter-symbol-after.txt` zero-hit | Silent old envelope fallback returns. |
| `natal_long_free` branch | symbol | historical-facade | public UI history selection and tests | schema/action driven `theme_natal_preview` fixtures and product state | delete | `frontend-legacy-after.txt` denylist-only hit | Free long rows could be selected as modern readings. |
| `natal_interpretation_short` fixture | symbol | historical-facade | public UI tests | `theme_natal_preview` fixtures | delete | `frontend-legacy-after.txt` denylist-only hit | Positive legacy fixture remains. |
| `variant_code` entitlement display | field | canonical-active | `/natal` entitlement gates | `NatalChartPage.tsx` and `NatalAstrologerMode.tsx` gate/display reads | keep | `variant-code-after.txt` classified hits | None for command construction; review remaining hits as gates only. |
| `variant_code` command use | field | historical-facade | product action body construction | `ThemeNatalReadingCommandRequest.action` | delete | `natalChartApi.test.tsx` and `variant-code-after.txt` | Product command drift if field is reintroduced. |
| unknown external old DTO consumer | symbol | non-domain for this story | no first-party public reading consumer kept | public `theme_natal` payload | no blocker | bounded scans and targeted tests | Historical rows may no longer render as modern readings; allowed story delta. |
