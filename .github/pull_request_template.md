# Pull Request

## Description
<!-- Résumé des changements -->

## Maintenance du Pipeline LLM (Gouvernance obligatoire)

Cette PR modifie-t-elle la structure, les providers, les fallbacks ou la composition canonique du pipeline ?

- [ ] **OUI** : J'ai mis à jour [docs/llm-prompt-generation-by-feature.md](docs/llm-prompt-generation-by-feature.md).
- [ ] **NON / JUSTIFICATION** : Ce document reste valide sans changement. 
  Motif autorisé (cocher un seul) :
  - [ ] `REF_ONLY` : Refactoring local sans impact sur la structure ou la doctrine.
  - [ ] `FIX_TYPO` : Correction de typos ou de wording sans changement de sens.
  - [ ] `TEST_ONLY` : Uniquement des changements de tests ou de mocks.
  - [ ] `DOC_ONLY` : Cette PR est elle-même une mise à jour documentaire.
  - [ ] `NON_LLM` : Les fichiers touchés n'impactent pas le pipeline LLM (ex: scripts ops).

### Rappel des zones à impact obligatoire
La revue de la documentation est requise pour toute modification de :
- `_resolve_plan()`, `execute_request()`, `_call_provider()`, `_handle_repair_or_fallback()`.
- `_build_messages()`, `PromptRenderer`, `PromptAssemblyConfig`, `context_quality`, `ContextQualityInjector`, budgets de longueur.
- `ProviderParameterMapper`, `FallbackGovernanceRegistry`, `NOMINAL_SUPPORTED_PROVIDERS`.
- Taxonomie canonique `feature/subfeature/plan`, résolution `ExecutionProfile`.

## Checklist
- [ ] Les tests passent (`pytest -q`)
- [ ] Le linting est OK (`ruff check backend`)
- [ ] Le quality gate a été exécuté (`.\scripts\quality-gate.ps1`)
