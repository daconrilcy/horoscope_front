# Inventaire apres - tests backend story-numbered

Comparison command: `rg --files backend -g 'test_story_*.py'`.

Total apres migration complete: 0 fichier.

Difference autorisee: les 44 fichiers du baseline ont ete renommes vers des noms
durables et restent references dans `story-guard-mapping.md`.

| Old file | Canonical file |
|---|---|
| `backend/app/tests/integration/test_story_61_62_decommission.py` | `backend/app/tests/integration/test_decommissioned_endpoints_contract.py` |
| `backend/app/tests/test_story_61_58_full.py` | `backend/app/tests/test_full_reconciliation_chain.py` |
| `backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py` | `backend/app/tests/unit/test_backend_services_llm_structure_guard.py` |
| `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py` | `backend/app/tests/unit/test_backend_entitlement_structure_guard.py` |
| `backend/app/tests/unit/test_story_70_23_services_structure_guard.py` | `backend/app/tests/unit/test_backend_services_structure_guard.py` |
| `backend/tests/integration/test_story_66_21_governance.py` | `backend/tests/integration/test_llm_governance_registry.py` |
| `backend/tests/integration/test_story_66_22_provider_locking.py` | `backend/tests/integration/test_llm_provider_locking.py` |
| `backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py` | `backend/tests/integration/test_evaluation_matrix_daily_paths.py` |
| `backend/tests/integration/test_story_66_25_observability.py` | `backend/tests/integration/test_llm_observability_integration.py` |
| `backend/tests/integration/test_story_66_26_documentation_governance.py` | `backend/tests/integration/test_llm_documentation_governance.py` |
| `backend/tests/integration/test_story_66_27_integrated_propagation.py` | `backend/tests/integration/test_llm_integrated_propagation.py` |
| `backend/tests/integration/test_story_66_29_extinction.py` | `backend/tests/integration/test_llm_legacy_extinction.py` |
| `backend/tests/integration/test_story_66_30_suppression.py` | `backend/tests/integration/test_llm_runtime_suppression.py` |
| `backend/tests/integration/test_story_66_36_admin_integration.py` | `backend/tests/integration/test_admin_llm_integration.py` |
| `backend/tests/integration/test_story_66_36_golden_regression.py` | `backend/tests/integration/test_llm_golden_regression.py` |
| `backend/tests/integration/test_story_66_38_doc_conformity.py` | `backend/tests/integration/test_llm_doc_conformity.py` |
| `backend/tests/integration/test_story_66_39_doc_conformity_hardening.py` | `backend/tests/integration/test_llm_doc_conformity_hardening.py` |
| `backend/tests/integration/test_story_66_40_legacy_residual.py` | `backend/tests/integration/test_llm_legacy_residual_governance.py` |
| `backend/tests/integration/test_story_66_41_semantic_conformity.py` | `backend/tests/integration/test_llm_semantic_conformity.py` |
| `backend/tests/integration/test_story_66_43_provider_runtime_chaos.py` | `backend/tests/integration/test_llm_provider_runtime_chaos.py` |
| `backend/tests/integration/test_story_70_17_llm_db_cleanup_registry.py` | `backend/tests/integration/test_llm_db_cleanup_registry.py` |
| `backend/tests/integration/test_story_70_18_llm_db_invariants.py` | `backend/tests/integration/test_llm_db_invariants.py` |
| `backend/tests/llm_orchestration/test_story_66_10_persona_boundary.py` | `backend/tests/llm_orchestration/test_persona_boundary.py` |
| `backend/tests/llm_orchestration/test_story_66_11_execution_profiles.py` | `backend/tests/llm_orchestration/test_execution_profiles.py` |
| `backend/tests/llm_orchestration/test_story_66_12_length_budgets.py` | `backend/tests/llm_orchestration/test_length_budgets.py` |
| `backend/tests/llm_orchestration/test_story_66_13_placeholders.py` | `backend/tests/llm_orchestration/test_placeholder_validation.py` |
| `backend/tests/llm_orchestration/test_story_66_14_context_quality.py` | `backend/tests/llm_orchestration/test_context_quality.py` |
| `backend/tests/llm_orchestration/test_story_66_15_convergence.py` | `backend/tests/llm_orchestration/test_llm_convergence.py` |
| `backend/tests/llm_orchestration/test_story_66_17_architecture_guards.py` | `backend/tests/llm_orchestration/test_architecture_guards.py` |
| `backend/tests/llm_orchestration/test_story_66_18_stable_profiles.py` | `backend/tests/llm_orchestration/test_stable_profiles.py` |
| `backend/tests/llm_orchestration/test_story_66_19_narrator_migration.py` | `backend/tests/llm_orchestration/test_narrator_migration.py` |
| `backend/tests/llm_orchestration/test_story_66_20_convergence.py` | `backend/tests/llm_orchestration/test_runtime_convergence.py` |
| `backend/tests/llm_orchestration/test_story_66_23_taxonomy.py` | `backend/tests/llm_orchestration/test_execution_profile_taxonomy.py` |
| `backend/tests/llm_orchestration/test_story_66_28_closure.py` | `backend/tests/llm_orchestration/test_llm_closure.py` |
| `backend/tests/llm_orchestration/test_story_66_42_prompt_governance_registry.py` | `backend/tests/llm_orchestration/test_prompt_governance_registry.py` |
| `backend/tests/llm_orchestration/test_story_66_9_unification.py` | `backend/tests/llm_orchestration/test_llm_unification.py` |
| `backend/tests/unit/test_story_66_27_injector_extension.py` | `backend/tests/unit/test_template_injector_extension.py` |
| `backend/tests/unit/test_story_70_13_bootstrap.py` | `backend/tests/unit/test_canonical_llm_bootstrap.py` |
| `backend/tests/unit/test_story_70_14_transition_guards.py` | `backend/tests/unit/test_historical_facade_transition_guards.py` |
| `backend/tests/unit/test_story_70_18_backend_structure_guard.py` | `backend/tests/unit/test_backend_structure_guard.py` |
| `backend/tests/unit/test_story_70_18_datetime_provider_guard.py` | `backend/tests/unit/test_datetime_provider_guard.py` |
| `backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py` | `backend/tests/unit/test_llm_canonical_perimeter.py` |
| `backend/tests/unit/test_story_70_18_llm_model_namespace_guard.py` | `backend/tests/unit/test_llm_model_namespace_guard.py` |
| `backend/tests/unit/test_story_70_18_llm_sensitive_model_validators.py` | `backend/tests/unit/test_llm_sensitive_model_validators.py` |
