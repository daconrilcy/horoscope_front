# Admin Prompts legacy removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `adminPromptsLegacy.ts` | file | historical-facade | AdminPrompts i18n imports | `adminPromptsArchive.ts` | delete | file renamed, no re-export | low |
| `AdminPromptsLegacyStrings` | type | historical-facade | page/tests | `AdminPromptsArchiveStrings` | replace-consumer | targeted scan zero | low |
| `promptsLegacy` | property | historical-facade | page aggregation | `promptsArchive` | replace-consumer | targeted scan zero | low |
| tab value `legacy` | state | historical-facade | route/page state | `archive` | replace-consumer | route test PASS | low |
