# Registre wrappers transitoires LLM

Ce registre suit les wrappers de compatibilite introduces pendant la convergence vers les chemins canoniques (story 70-15 et suivantes).

## Regles

- Un wrapper transitoire n est pas un point d extension permanent.
- Toute nouvelle evolution doit cibler le chemin canonique, pas le wrapper.
- Chaque wrapper doit avoir un **critere de sortie** clair.

## Wrappers actifs

| Wrapper transitoire | Cible canonique | Raison | Critere de sortie |
| --- | --- | --- | --- |
| `backend/app/services/ai_engine_adapter.py` | `app.application.llm.ai_engine_adapter` | Compatibilite imports historiques services | Zero import production vers `app.services.ai_engine_adapter` ; tests migres |
| `backend/app/llm_orchestration/gateway.py` | `app.domain.llm.runtime.gateway` | Compatibilite imports et patches tests sur namespace historique | Imports runtime/admin pointent `domain.llm.runtime.gateway` ; shim reduit a reexports minimaux |
| `backend/app/llm_orchestration/services/*.py` (shims runtime/prompting/configuration listes ci-dessous) | `app.domain.llm.runtime.*` ou `app.domain.llm.configuration.*` ou `app.domain.llm.prompting.*` | Compatibilite chemins historiques | Aucun import actif hors tests vers ces modules shim |
| `backend/app/llm_orchestration/prompt_version_lookup.py` | `app.domain.llm.configuration.prompt_version_lookup` | Compatibilite | Suppression apres migration des derniers imports |
| `backend/app/llm_orchestration/providers/provider_runtime_manager.py` | `app.domain.llm.runtime.provider_runtime_manager` | Compatibilite | Idem |
| `backend/app/llm_orchestration/prompt_governance_registry.py` | `app.domain.llm.governance.prompt_governance_registry` | Compatibilite imports gouvernance historiques | Suppression apres migration complete des imports runtime/admin/coherence |
| `backend/app/llm_orchestration/legacy_residual_registry.py` | `app.domain.llm.governance.legacy_residual_registry` | Compatibilite imports residual legacy historiques | Suppression apres migration complete des imports runtime/ops/doc |
| `backend/scripts/build_llm_release_candidate.py` | `app.ops.llm.release.build_release_candidate` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_golden_evidence.py` | `app.ops.llm.release.build_golden_evidence` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_qualification_evidence.py` | `app.ops.llm.release.build_qualification_evidence` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_smoke_evidence.py` | `app.ops.llm.release.build_smoke_evidence` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_release_readiness_report.py` | `app.ops.llm.release.build_release_readiness_report` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/app/api/v1/routers/admin/llm/*.py` (wrappers namespace) | Routers `admin_llm*` historiques | Stabiliser le namespace canonique API sans big-bang | Les routers historiques `admin_llm*.py` sont absorbes/remplaces, puis wrappers supprimes |
| `backend/app/infrastructure/db/models/llm_*.py` (re-exports) | `app.infra.db.models.*` historiques | Convergence progressive vers chemins DB canoniques | Plus aucun import actif vers `app.infra.db.models.llm_*` |

### Shims `llm_orchestration/services` et provider (post 70-15)

Fichiers reduits a un reexport vers le domaine canonique : `context_quality_injector`, `length_budget_injector`, `provider_parameter_mapper`, `output_validator`, `fallback_governance`, `prompt_renderer`, `persona_composer`, `assembly_resolver`, `assembly_registry`, `assembly_admin_service`, `execution_profile_registry`.

## Checklist de sortie (a appliquer avant suppression)

- Les imports applicatifs ont ete migres vers la cible canonique.
- Les scripts CI/CD et outils dev pointent la cible canonique.
- La documentation de reference ne cite plus le wrapper.
- Les tests de non-regression passent sans le wrapper.
