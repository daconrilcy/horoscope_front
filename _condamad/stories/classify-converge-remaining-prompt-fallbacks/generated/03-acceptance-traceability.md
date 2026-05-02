# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `fallback-classification.md` liste les 8 cles imposees. | Ajouter l'audit persistant avec inventaire avant/apres et decisions. | `test_fallback_classification_audit_covers_every_reviewed_key`; revue de l'audit. | PASS |
| AC2 | Les cles migrees ou supprimees ne construisent plus de fallback config. | Supprimer les 6 prompts fallback non-fixtures de `PROMPT_FALLBACK_CONFIGS`; ajouter les guards builder. | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py`; scan `rg`. | PASS |
| AC3 | Les cles `fixture` ou `bootstrap-non-prod` sont exactes. | Restreindre `PROMPT_FALLBACK_CONFIGS` a `test_natal` et `test_guidance`; audit fixture exact. | `test_prompt_fallback_config_exceptions_are_exact`; audit `fallback-classification.md`. | PASS |
| AC4 | Aucune nouvelle cle canonique fallback n'est admise sans decision. | Guard exact allowlist + audit coverage test + interdiction des cles canoniques convergees. | `test_fallback_classification_audit_covers_every_reviewed_key`; `test_converged_prompt_fallback_keys_do_not_build_config`. | PASS |
| AC5 | Le gateway production conserve l'erreur `missing_assembly`. | Aucun changement gateway; validation du contrat existant. | `pytest -q tests/llm_orchestration/test_assembly_resolution.py`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
