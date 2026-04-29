# Inventaire avant - tests backend story-numbered

Baseline capture: `rg --files backend -g 'test_story_*.py' | Sort-Object`.

Total avant migration: 44 fichiers.

| File | Initial classification hypothesis |
|---|---|
| `backend/app/tests/integration/test_story_61_62_decommission.py` | keep |
| `backend/app/tests/test_story_61_58_full.py` | keep |
| `backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py` | migrated |
| `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py` | migrated |
| `backend/app/tests/unit/test_story_70_23_services_structure_guard.py` | migrated |
| `backend/tests/integration/test_story_66_21_governance.py` | keep |
| `backend/tests/integration/test_story_66_22_provider_locking.py` | keep |
| `backend/tests/integration/test_story_66_24_evaluation_matrix_daily_paths.py` | keep |
| `backend/tests/integration/test_story_66_25_observability.py` | keep |
| `backend/tests/integration/test_story_66_26_documentation_governance.py` | keep |
| `backend/tests/integration/test_story_66_27_integrated_propagation.py` | keep |
| `backend/tests/integration/test_story_66_29_extinction.py` | keep |
| `backend/tests/integration/test_story_66_30_suppression.py` | keep |
| `backend/tests/integration/test_story_66_36_admin_integration.py` | keep |
| `backend/tests/integration/test_story_66_36_golden_regression.py` | keep |
| `backend/tests/integration/test_story_66_38_doc_conformity.py` | keep |
| `backend/tests/integration/test_story_66_39_doc_conformity_hardening.py` | keep |
| `backend/tests/integration/test_story_66_40_legacy_residual.py` | keep |
| `backend/tests/integration/test_story_66_41_semantic_conformity.py` | keep |
| `backend/tests/integration/test_story_66_43_provider_runtime_chaos.py` | keep |
| `backend/tests/integration/test_story_70_17_llm_db_cleanup_registry.py` | keep |
| `backend/tests/integration/test_story_70_18_llm_db_invariants.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_10_persona_boundary.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_11_execution_profiles.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_12_length_budgets.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_13_placeholders.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_14_context_quality.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_15_convergence.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_17_architecture_guards.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_18_stable_profiles.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_19_narrator_migration.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_20_convergence.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_23_taxonomy.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_28_closure.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_42_prompt_governance_registry.py` | keep |
| `backend/tests/llm_orchestration/test_story_66_9_unification.py` | keep |
| `backend/tests/unit/test_story_66_27_injector_extension.py` | keep |
| `backend/tests/unit/test_story_70_13_bootstrap.py` | keep |
| `backend/tests/unit/test_story_70_14_transition_guards.py` | keep |
| `backend/tests/unit/test_story_70_18_backend_structure_guard.py` | keep |
| `backend/tests/unit/test_story_70_18_datetime_provider_guard.py` | keep |
| `backend/tests/unit/test_story_70_18_llm_canonical_perimeter.py` | keep |
| `backend/tests/unit/test_story_70_18_llm_model_namespace_guard.py` | keep |
| `backend/tests/unit/test_story_70_18_llm_sensitive_model_validators.py` | keep |
