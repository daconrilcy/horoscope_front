# Legacy style after CS-059

Scan command: `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css` from `frontend`.

Registry after: 5 rows remain: 2 admin external-active selector rows and 3 compatibility token alias rows.
Deleted: 12 chat selector-family rows and corresponding `App.css` legacy selector blocks.

| File | Result | Evidence |
|---|---|---|
| `frontend/src/App.css` | chat legacy selector blocks removed | no `legacy` hits remain in `src/App.css` |
| `frontend/src/styles/legacy-style-surface-registry.md` | chat rows removed | registry keeps only admin external-active and token aliases |
| `frontend/src/pages/admin/AdminPromptsPage.css` | unchanged external-active surface | admin legacy hits remain intentionally blocked |
| `frontend/src/styles/theme.css` / token aliases | unchanged compatibility surface | broad active consumers remain; no alias deleted in this batch |

Validation: `npm run test -- css-fallback design-system theme-tokens inline-style legacy-style visual-smoke` PASS; `npm run lint` PASS.
