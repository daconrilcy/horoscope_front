# No Legacy / DRY Guardrails

## Applicable guardrails

| Guardrail | Evidence |
|---|---|
| RG-003 | `/v1/reference-data/languages` is mounted through the canonical API v1 router registry and appears in OpenAPI. |
| RG-004 | Settings persistence and languages lookup now use centralized API error envelopes on SQLAlchemy failures. |
| RG-083 | Header language UI uses `Header.css`; `rg -n "style=" src/layouts/components src/api/languages.ts` has no hits. |
| RG-108 | Backend reads `LanguageModel`; frontend displays names from the API response and filters only on supported interface bundles. |

## Forbidden patterns checked

- No backend hardcoded language catalogue was introduced.
- No direct `fetch` or `axios` call was introduced in `Header.tsx`, `LanguageSelector.tsx`, or `api/languages.ts`.
- No inline style was introduced in top-menu components.
- No compatibility wrapper, transitional alias, shim, or duplicate active Header language selector was introduced.

## Review decisions

- Accepted: frontend must not apply a saved account language unless that code is present in API language options.
- Accepted: frontend labels must come from `/v1/reference-data/languages`.
- Accepted: browser locale is the default before account settings load; account setting overrides once loaded.
- Accepted: country code must be derived robustly from BCP47 locales and validated backend-side as alpha-2.
- Rejected as out of scope: refactoring the existing landing navbar language control. CS-173 scopes canonical top-menu integration to `Header.tsx` / `LanguageSelector.tsx`.
