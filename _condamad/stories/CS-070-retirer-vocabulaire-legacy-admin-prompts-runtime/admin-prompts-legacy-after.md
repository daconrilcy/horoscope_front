# Admin Prompts legacy after

| Item | Decision | Proof | Risk |
|---|---|---|---|
| i18n module | renamed to `adminPromptsArchive.ts` without shim | targeted rg for `adminPromptsLegacy`, `AdminPromptsLegacyStrings`, `promptsLegacy` in AdminPrompts surface returns zero | low |
| runtime tab/state | renamed to `archive`; `/admin/prompts/archive` route added | `npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style design-system` PASS | low |
| tests/copy/ARIA | canonical archive vocabulary asserted | same command PASS | low |

Story markdown validation and strict lint now pass after reconstructing the missing contract sections in `00-story.md`.
