# CS-426 Legacy Surface Classification

Commentaire global: cette classification transforme l'inventaire des surfaces natal legacy en decisions de suite explicites.

## Classification rules

- Allowed values: `delete`, `replace`, `readonly`, `keep`, `needs-decision`.
- `readonly` means explicitly non-generative and must not call the LLM provider.
- `needs-decision` requires an owner and expected decision.
- `delete` is a later-story classification only; no physical code deletion is authorized by CS-426.

## Surface decisions

| surface | classification | rationale | owner | expected decision | next story input |
|---|---|---|---|---|---|
| Public `POST /v1/natal/interpretation` adapter | replace | Public active-generation entrypoint passes legacy level, force refresh, and variant context to the service. | Backend API owner | Replace routing target with canonical product contract after Big Bang model exists. | Route acceptance guard must prove no direct legacy use-case selection remains. |
| Public GET/LIST/DELETE/PDF interpretation routes | readonly | Non-generative read/delete/render operations over persisted rows. | Backend API owner | Keep as public readback boundary while excluding rejected/audit internals. | Preserve RG-150/RG-152 readback guards. |
| `NatalInterpretationService.interpret` complete/short selector | replace | Central active-generation selector chooses `natal_interpretation` or `natal_interpretation_short` and injects Basic payload. | Natal generation owner | Replace with contract-specific product routing. | Product contract story must remove legacy keys from public generation path. |
| `NatalInterpretationService._generate_free_short` | replace | Active generation uses `natal_long_free` and persists `variant_code=free_short`. | Natal generation owner | Decide final Free product key and replace contradictory long/free naming. | Free public story must preserve preview behavior without old key. |
| `UserNatalInterpretationModel` persistence writes from generation | replace | Active generation persists chart, variant, answer type, fallback and payload state. | Persistence owner | Keep table until migration target exists, but replace write contract and cache identity. | Migration story must compare against this inventory. |
| Stored payload helpers | keep | Non-generative boundary helpers protect accepted/rejected public payload shape. | Natal generation owner | Keep while public readback remains on existing table. | Continue RG-150/RG-152 coverage. |
| LLM runtime gateway natal branches | replace | Runtime active-generation and fallback mediation still know legacy natal use cases. | LLM runtime owner | Replace use-case family routing with explicit Big Bang product contract inputs. | Runtime guard must reject old keys in public natal generation. |
| `PROMPT_FALLBACK_CONFIGS` fallback catalog | replace | Supported natal prompts must not be owned by fallback defaults. | LLM prompting owner | Move supported natal prompts to audited assembly or delete fallback ownership. | RG-018/RG-021 follow-up. |
| `assembly_resolver.py` `fallback_default` | needs-decision | Admin/config fallback can be valid only if explicitly non-public and audited. | LLM platform owner | Decide admin-only retention versus deletion for supported natal products. | Add audited allowlist or removal story. |
| `canonical_use_case_registry.py` natal V3 entries | replace | Registry still names V3 premium schema for legacy complete natal use cases. | LLM configuration owner | Replace with target schema registry for theme natal products. | Big Bang schema contract story. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | delete | Historical bootstrap for old short and complete prompts. | LLM bootstrap owner | Delete once replacement bootstrap exists. | Destructive seed cleanup story. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | replace | Premium V3 prompt seed can be reused only for premium, not Basic. | LLM bootstrap owner | Split premium-only prompt from Basic target contract. | Prompt contract convergence story. |
| `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | replace | Taxonomy maps Basic to `natal_interpretation` and Free to short legacy key. | Product taxonomy owner | Replace rows with product-contract keys. | Taxonomy migration story. |
| `seed_theme_astral_prompt_contract.py` | needs-decision | Contains Basic prompt payload language but target ownership is not settled by CS-426. | Big Bang product owner | Decide canonical status of `basic_natal_prompt_payload` versus target `theme_natal_basic_reading_v1`. | Product contract naming decision. |
| `backend/scripts/seed_natal_short.py` | delete | Dev seed reintroduces `natal_interpretation_short`. | LLM bootstrap owner | Delete after replacement test seed exists. | Script cleanup story. |
| `backend/scripts/seed_28_4.py` | delete | Historical seed for old complete use case. | LLM bootstrap owner | Delete. | Script cleanup story. |
| `backend/scripts/seed_30_2_astroresponse_v2.py` | delete | Obsolete schema transition seed for old complete use case. | LLM bootstrap owner | Delete. | Script cleanup story. |
| `backend/scripts/seed_30_3_gpt5_prompts.py` | replace | Premium prompt seed can still influence old `natal_interpretation`. | LLM prompting owner | Replace with premium-only target prompt seed or delete. | Prompt seed convergence story. |
| `backend/scripts/seed_66_15_assembly_convergence.py` | replace | Maps product levels to old keys including `natal_long_free` and short legacy. | LLM bootstrap owner | Replace convergence rows with product-contract names. | Assembly convergence cleanup. |
| `backend/scripts/seed_66_20_convergence.py` | replace | Maintains old product/use-case convergence rows. | LLM bootstrap owner | Replace with canonical taxonomy or delete. | Assembly convergence cleanup. |
| `backend/scripts/update_all_prompts_59_5.py` | needs-decision | Broad prompt rewrite script has special handling for `natal_interpretation`. | LLM platform owner | Decide deletion or non-production audited maintenance scope. | Script governance story. |
| `backend/scripts/diagnose_natal_interpretation_duplicates.py` | readonly | Non-generative diagnostic over persisted rows and duplicate keys. | Persistence owner | Keep only if updated with final cache identity. | Diagnostic alignment story. |
| Public route and Free-short tests | keep | Non-generative test-only coverage documents current behavior until target contract tests replace it. | QA/backend owner | Keep as regression evidence during migration. | Update expected keys when public route contract changes. |
| Basic and prompt assembly tests | replace | Non-generative test-only coverage still names legacy prompt/use-case keys. | QA/LLM owner | Replace assertions with Big Bang contract names once implemented. | Test migration story. |
| Frontend `NatalInterpretation.tsx` trigger logic | replace | Active-generation trigger can force short generation after Basic upgrade. | Frontend natal owner | Replace trigger rules with explicit product-state contract. | Frontend Big Bang integration story. |
| Frontend API `fetchNatalInterpretation` and `useNatalInterpretation` | replace | Active-generation client sends `use_case_level` and `force_refresh` to public route. | Frontend API owner | Replace request shape only when backend contract changes. | API contract migration story. |
| Live test report | readonly | Non-generative historical evidence of observed degraded behavior. | CONDAMAD evidence owner | Keep as baseline evidence. | Later destructive stories compare before/after. |
| Big Bang architecture report | readonly | Non-generative architecture input for target model. | CONDAMAD evidence owner | Keep as baseline architecture context. | Later product stories cite target decisions. |
| CS-425 brief | readonly | Non-generative upstream cache/remediation context. | CONDAMAD evidence owner | Keep as dependency context. | Cache invalidation follow-up alignment. |
| `_condamad/run-state.json` | readonly | Non-generative run-state file; deletion or cleanup is explicitly out of scope. | CONDAMAD orchestrator | No CS-426 change; handle only in a dedicated cleanup decision. | Evidence records pre-existing dirty status. |
