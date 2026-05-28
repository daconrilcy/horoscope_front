# Owner Map — CS-364

<!-- Commentaire global: cet artefact relie chaque primitive du contrat theme astral a son owner backend canonique. -->

## Mapping des primitives

| Primitive | Owner canonique | Preuve |
|---|---|---|
| `theme_astral_prompt_contract_v1` | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Constante stable et read model actif. |
| `theme_astral_llm_input_v1` | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Schema d'entree Pydantic/JSON et placeholder canonical. |
| `theme_astral_response_contract_v1` | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Schema de sortie et reference `LlmOutputSchemaModel`. |
| `delivery_profile` | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Profondeurs non commerciales `essential` et `deep`. |
| `astrologer_voice` / `persona` | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | Seed `LlmPersonaModel` style-only. |
| `prompt templates` | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | Seed `LlmPromptVersionModel`. |
| `assemblies` | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | Seed `PromptAssemblyConfigModel` par profondeur. |
| `use cases` | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Contrat canonique `theme_astral`. |
| `output schemas` | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Schema canonique version 1. |
| `execution profiles` | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | Seed `LlmExecutionProfileModel`. |
| `resolver` / `runtime` | `backend/app/domain/llm/configuration/theme_astral_contracts.py` | `resolve_active_theme_astral_prompt_contract`. |
| `catalog` / governance | `backend/app/domain/llm/governance/data/prompt_governance_registry.json` | Famille canonique et placeholders declares. |
| `DB` / migration | `backend/tests/integration/test_theme_astral_prompt_contract_migration.py` | Reutilisation des tables LLM existantes, pas de migration ajoutee. |

## Conclusion

La story reutilise les tables LLM existantes et n'introduit pas de registry parallele, de nouveau dossier racine backend, de gateway provider ou de frontend.
