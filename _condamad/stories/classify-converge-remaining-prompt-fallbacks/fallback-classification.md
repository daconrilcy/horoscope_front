# Classification des fallbacks prompts restants

Ce fichier conserve l'inventaire avant/apres de `PROMPT_FALLBACK_CONFIGS` pour
la story `classify-converge-remaining-prompt-fallbacks`.

## Before inventory

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `natal_long_free` | fallback prompt | historical-facade | free natal runtime, admin runtime audit | runtime metadata + canonical natal assembly path | delete | Present before implementation in `catalog.py`; `rg` shows first-party consumers but no dedicated governed prompt seed. | Free short natal must rely on DB prompt or explicit assembly/runtime metadata, not fallback prompt text. |
| `natal_interpretation_short` | fallback prompt | canonical-active | natal free interpretation, fallback target contracts | `seed_29_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Seeded prompt and assembly target exist. | Bootstrap without assembly must not reuse hardcoded prompt text. |
| `guidance_daily` | fallback prompt | canonical-active | guidance daily feature | `seed_guidance_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Seeded prompt and assembly target exist. | Missing assembly in production must stay `missing_assembly`. |
| `guidance_weekly` | fallback prompt | canonical-active | guidance weekly feature | `seed_guidance_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Seeded prompt and assembly target exist. | Missing assembly in production must stay `missing_assembly`. |
| `event_guidance` | fallback prompt | canonical-active | guidance event feature | `seed_guidance_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Seeded prompt and assembly target exist. | Missing assembly in production must stay `missing_assembly`. |
| `astrologer_selection_help` | fallback prompt | historical-facade | use-case-first support tests | canonical contract metadata only | delete | Canonical contract exists; no governed prompt seed found in required seeds. | Direct use-case-first callers receive metadata-only config unless DB prompt exists. |
| `test_natal` | fallback prompt | canonical-active | orchestration tests | synthetic fixture | fixture | Only referenced by LLM orchestration/admin tests. | Must not become production routing. |
| `test_guidance` | fallback prompt | canonical-active | orchestration tests | synthetic fixture | fixture | Only referenced by LLM orchestration/compose tests. | Must not become production routing. |

## After inventory

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `natal_long_free` | removed fallback prompt | historical-facade | free natal runtime, admin runtime audit | runtime metadata + canonical natal assembly path | delete | Removed from `PROMPT_FALLBACK_CONFIGS`; guarded by `test_converged_prompt_fallback_keys_do_not_build_config`. | Reviewer should confirm metadata-only bootstrap remains acceptable for direct non-assembly calls. |
| `natal_interpretation_short` | removed fallback prompt | canonical-active | natal free interpretation, fallback target contracts | `seed_29_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Removed from `PROMPT_FALLBACK_CONFIGS`; guarded by targeted pytest. | None beyond seed/assembly availability. |
| `guidance_daily` | removed fallback prompt | canonical-active | guidance daily feature | `seed_guidance_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Removed from `PROMPT_FALLBACK_CONFIGS`; guarded by targeted pytest. | None beyond seed/assembly availability. |
| `guidance_weekly` | removed fallback prompt | canonical-active | guidance weekly feature | `seed_guidance_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Removed from `PROMPT_FALLBACK_CONFIGS`; guarded by targeted pytest. | None beyond seed/assembly availability. |
| `event_guidance` | removed fallback prompt | canonical-active | guidance event feature | `seed_guidance_prompts.py` + `seed_66_20_taxonomy.py` assembly | migrate-to-assembly | Removed from `PROMPT_FALLBACK_CONFIGS`; guarded by targeted pytest. | None beyond seed/assembly availability. |
| `astrologer_selection_help` | removed fallback prompt | historical-facade | use-case-first support tests | canonical contract metadata only | delete | Removed from `PROMPT_FALLBACK_CONFIGS`; guarded by targeted pytest. | Direct use-case-first callers must provide DB prompt if real prompt text is needed. |
| `test_natal` | remaining fallback prompt | canonical-active | orchestration tests | synthetic fixture | fixture | Still present in `PROMPT_FALLBACK_CONFIGS`; exact allowlist test covers it. | Must remain test-only. |
| `test_guidance` | remaining fallback prompt | canonical-active | orchestration tests | synthetic fixture | fixture | Still present in `PROMPT_FALLBACK_CONFIGS`; exact allowlist test covers it. | Must remain test-only. |

## Comparison

Allowed differences:

- `natal_long_free`, `natal_interpretation_short`, `guidance_daily`, `guidance_weekly`, `event_guidance` and `astrologer_selection_help` were removed from `PROMPT_FALLBACK_CONFIGS`.
- `test_natal` and `test_guidance` remain as exact synthetic fixtures.

Executable invariant:

- Every remaining fallback key is classified in this file and belongs to the exact fixture allowlist.
- `build_fallback_use_case_config` returns `None` for every removed canonical or near-nominal key.
