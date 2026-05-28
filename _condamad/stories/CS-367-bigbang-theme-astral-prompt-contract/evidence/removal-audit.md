# CS-367 - Removal Audit

<!-- Commentaire global: cet audit classe les anciennes surfaces theme_astral avant cloture de la bascule bigbang. -->

## Scope

- Story: `CS-367-bigbang-theme-astral-prompt-contract`
- Source brief: `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md`
- Classification date: `2026-05-28`
- Closure mode: full-closure for the active `theme_astral` provider prompt path.

## Classification Table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `theme_astral_prompt_v1` | prompt contract | canonical-active | gateway, seed, tests | itself | keep | canonical scan and tests | none |
| `theme_astral_llm_input_v1` | provider input | canonical-active | gateway, examples, tests | itself | keep | canonical and shape scans | none |
| `chart_json` for `theme_astral` | legacy carrier | historical-facade | no canonical owner | target input data | replace-consumer | rejection test and scan | low |
| `natal_data` for `theme_astral` | legacy carrier | historical-facade | no canonical owner | target input data | replace-consumer | rejection test and scan | low |
| `llm_astrology_input_v1` for `theme_astral` | legacy carrier | historical-facade | natal/historical only | target input | replace-consumer | rejection and guard tests | low |
| `natal_interpretation_short` | old use case | historical-facade | natal only | target prompt | replace-consumer | architecture guard | low |
| `NATAL_SHORT_PROMPT` | old prompt seed | historical-facade | natal seed only | theme seed | keep | scoped scan | medium |
| `NATAL_COMPLETE_PROMPT` | old prompt seed | historical-facade | natal seed only | theme seed | keep | scoped scan | medium |
| Old plan theme examples | examples | dead | no active examples | stable examples | delete | shape proof | none |
| Legacy theme tests/mocks | tests | historical-facade | replaced by CS-367 | new tests | replace-consumer | targeted and full tests | none |

## Decision Notes

- No `external-active` or `needs-user-decision` candidate was found for the active `theme_astral` provider prompt path.
- Remaining legacy tokens are natal-specific, admin sample, historical documentation, or guard evidence; they are not active `theme_astral` provider inputs.
- No compatibility shim, alias, fallback path, or wrapper was introduced for `theme_astral`.
