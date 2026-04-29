# Mapping durable des guards story-numbered

Ce registre classe chaque fichier `test_story_*.py` trouve dans le baseline avant.
Tous les fichiers du baseline sont maintenant migres vers des noms durables; aucun
fichier backend actif ne doit encore correspondre a `test_story_*.py`.

| File | Classification | Invariant | Canonical target | Decision |
|---|---|---|---|---|
| `backend/app/tests/integration/test_story_61_62_decommission.py` | migrated | API decommission contract | `backend/app/tests/integration/test_decommissioned_endpoints_contract.py` | renomme sans changement d'assertions |
| `backend/app/tests/test_story_61_58_full.py` | migrated | Full reconciliation chain | `backend/app/tests/test_full_reconciliation_chain.py` | renomme sans changement d'assertions |
| `backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py` | migrated | RG-005 services LLM boundary | `backend/app/tests/unit/test_backend_services_llm_structure_guard.py` | renomme sans changement d'assertions |
| `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py` | migrated | RG-005 entitlement namespace boundary | `backend/app/tests/unit/test_backend_entitlement_structure_guard.py` | renomme sans changement d'assertions |
| `backend/app/tests/unit/test_story_70_23_services_structure_guard.py` | migrated | RG-005 services namespace boundary | `backend/app/tests/unit/test_backend_services_structure_guard.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_21_governance.py` | migrated | LLM governance registry | `backend/tests/integration/test_llm_governance_registry.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_22_provider_locking.py` | migrated | LLM provider locking | `backend/tests/integration/test_llm_provider_locking.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py` | migrated | Evaluation matrix daily paths | `backend/tests/integration/test_evaluation_matrix_daily_paths.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_25_observability.py` | migrated | RG-007 LLM observability | `backend/tests/integration/test_llm_observability_integration.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_26_documentation_governance.py` | migrated | Documentation governance | `backend/tests/integration/test_llm_documentation_governance.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_27_integrated_propagation.py` | migrated | LLM integrated propagation | `backend/tests/integration/test_llm_integrated_propagation.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_29_extinction.py` | migrated | Legacy extinction guard | `backend/tests/integration/test_llm_legacy_extinction.py` | renomme avec noms de fonctions durables |
| `backend/tests/integration/test_story_66_30_suppression.py` | migrated | Runtime suppression telemetry | `backend/tests/integration/test_llm_runtime_suppression.py` | renomme avec noms de fonctions durables |
| `backend/tests/integration/test_story_66_36_admin_integration.py` | migrated | Admin LLM integration | `backend/tests/integration/test_admin_llm_integration.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_36_golden_regression.py` | migrated | Golden regression outputs | `backend/tests/integration/test_llm_golden_regression.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_38_doc_conformity.py` | migrated | Doc conformity contract | `backend/tests/integration/test_llm_doc_conformity.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_39_doc_conformity_hardening.py` | migrated | Doc conformity hardening | `backend/tests/integration/test_llm_doc_conformity_hardening.py` | renomme avec auto-reference mise a jour |
| `backend/tests/integration/test_story_66_40_legacy_residual.py` | migrated | Legacy residual governance | `backend/tests/integration/test_llm_legacy_residual_governance.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_41_semantic_conformity.py` | migrated | Semantic conformity runtime | `backend/tests/integration/test_llm_semantic_conformity.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_66_43_provider_runtime_chaos.py` | migrated | Provider runtime chaos | `backend/tests/integration/test_llm_provider_runtime_chaos.py` | renomme avec noms de fonctions durables |
| `backend/tests/integration/test_story_70_17_llm_db_cleanup_registry.py` | migrated | LLM DB cleanup registry | `backend/tests/integration/test_llm_db_cleanup_registry.py` | renomme sans changement d'assertions |
| `backend/tests/integration/test_story_70_18_llm_db_invariants.py` | migrated | LLM DB invariants | `backend/tests/integration/test_llm_db_invariants.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_10_persona_boundary.py` | migrated | Persona boundary | `backend/tests/llm_orchestration/test_persona_boundary.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_11_execution_profiles.py` | migrated | Execution profiles | `backend/tests/llm_orchestration/test_execution_profiles.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_12_length_budgets.py` | migrated | Length budgets | `backend/tests/llm_orchestration/test_length_budgets.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_13_placeholders.py` | migrated | Placeholder validation | `backend/tests/llm_orchestration/test_placeholder_validation.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_14_context_quality.py` | migrated | Context quality | `backend/tests/llm_orchestration/test_context_quality.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_15_convergence.py` | migrated | LLM orchestration convergence | `backend/tests/llm_orchestration/test_llm_convergence.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_17_architecture_guards.py` | migrated | LLM orchestration architecture | `backend/tests/llm_orchestration/test_architecture_guards.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_18_stable_profiles.py` | migrated | Stable profile resolution | `backend/tests/llm_orchestration/test_stable_profiles.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_19_narrator_migration.py` | migrated | Narrator migration | `backend/tests/llm_orchestration/test_narrator_migration.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_20_convergence.py` | migrated | LLM convergence | `backend/tests/llm_orchestration/test_runtime_convergence.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_23_taxonomy.py` | migrated | Execution profile taxonomy | `backend/tests/llm_orchestration/test_execution_profile_taxonomy.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_28_closure.py` | migrated | LLM closure | `backend/tests/llm_orchestration/test_llm_closure.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_42_prompt_governance_registry.py` | migrated | Prompt governance registry | `backend/tests/llm_orchestration/test_prompt_governance_registry.py` | renomme sans changement d'assertions |
| `backend/tests/llm_orchestration/test_story_66_9_unification.py` | migrated | LLM unification | `backend/tests/llm_orchestration/test_llm_unification.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_66_27_injector_extension.py` | migrated | Template injector extension | `backend/tests/unit/test_template_injector_extension.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_70_13_bootstrap.py` | migrated | Canonical LLM bootstrap | `backend/tests/unit/test_canonical_llm_bootstrap.py` | renomme avec nom de fonction durable |
| `backend/tests/unit/test_story_70_14_transition_guards.py` | migrated | RG-001 historical facade transition | `backend/tests/unit/test_historical_facade_transition_guards.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_70_18_backend_structure_guard.py` | migrated | Backend structure perimeter | `backend/tests/unit/test_backend_structure_guard.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_70_18_datetime_provider_guard.py` | migrated | Datetime provider centralization | `backend/tests/unit/test_datetime_provider_guard.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py` | migrated | LLM canonical perimeter | `backend/tests/unit/test_llm_canonical_perimeter.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_70_18_llm_model_namespace_guard.py` | migrated | LLM model namespace | `backend/tests/unit/test_llm_model_namespace_guard.py` | renomme sans changement d'assertions |
| `backend/tests/unit/test_story_70_18_llm_sensitive_model_validators.py` | migrated | LLM model validators | `backend/tests/unit/test_llm_sensitive_model_validators.py` | renomme sans changement d'assertions |
