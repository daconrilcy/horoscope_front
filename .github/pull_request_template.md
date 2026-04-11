# Pull Request

## Description
<!-- Résumé des changements -->

## Maintenance du Pipeline LLM (Gouvernance obligatoire)

Cette PR modifie-t-elle la structure, les providers, les fallbacks ou la composition canonique du pipeline ?

- [ ] **OUI** : J'ai mis à jour [docs/llm-prompt-generation-by-feature.md](docs/llm-prompt-generation-by-feature.md).
- [ ] **NON / JUSTIFICATION** : Ce document reste valide sans changement car :
  > <!-- Justification ici (ex: refactoring local sans impact structurel) -->

### Rappel des zones à impact obligatoire
La revue de la documentation est requise pour toute modification de :
- `_resolve_plan()`, `execute_request()`, `_call_provider()`, `_handle_repair_or_fallback()`.
- `_build_messages()`, `PromptRenderer`, `PromptAssemblyConfig`, `ContextQualityInjector`, budgets de longueur.
- `ProviderParameterMapper`, `FallbackGovernanceRegistry`, `NOMINAL_SUPPORTED_PROVIDERS`.
- Taxonomie canonique `feature/subfeature/plan`, résolution `ExecutionProfile`.

## Checklist
- [ ] Les tests passent (`pytest -q`)
- [ ] Le linting est OK (`ruff check backend`)
- [ ] Le quality gate a été exécuté (`.\scripts\quality-gate.ps1`)
