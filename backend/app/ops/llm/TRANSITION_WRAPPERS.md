# Registre wrappers transitoires LLM

Ce registre suit les wrappers de compatibilite introduces pendant la convergence vers les chemins canoniques.

## Regles

- Un wrapper transitoire n est pas un point d extension permanent.
- Toute nouvelle evolution doit cibler le chemin canonique, pas le wrapper.
- Chaque wrapper doit avoir un **critere de sortie** clair.

## Wrappers actifs

| Wrapper transitoire | Cible canonique | Raison | Critere de sortie |
| --- | --- | --- | --- |
| `backend/scripts/build_llm_release_candidate.py` | `app.ops.llm.release.build_release_candidate` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_golden_evidence.py` | `app.ops.llm.release.build_golden_evidence` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_qualification_evidence.py` | `app.ops.llm.release.build_qualification_evidence` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_smoke_evidence.py` | `app.ops.llm.release.build_smoke_evidence` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/scripts/build_llm_release_readiness_report.py` | `app.ops.llm.release.build_release_readiness_report` | Compatibilite CI/outils existants | Aucun appel restant vers le script legacy dans CI et docs |
| `backend/app/application/llm/ai_engine_adapter.py` (re-export) | `app.services.ai_engine_adapter` (implementation courante) | Chemin canonique application expose sans rupture | L implementation est deplacee dans `app/application/llm` et les imports legacy sont retires |
| `backend/app/api/v1/routers/admin/llm/*.py` (wrappers namespace) | Routers `admin_llm*` historiques | Stabiliser le namespace canonique API sans big-bang | Les routers historiques `admin_llm*.py` sont absorbes/remplaces, puis wrappers supprimes |
| `backend/app/domain/llm/*` (wrappers ponts) | Modules `llm_orchestration` et `prompts` historiques | Offrir des points d entree domaine canoniques | Les implementations sont effectivement migrees sous `domain/llm/*`, puis re-exports retires |
| `backend/app/infrastructure/db/models/llm_*.py` (re-exports) | `app.infra.db.models.*` historiques | Convergence progressive vers chemins DB canoniques | Plus aucun import actif vers `app.infra.db.models.llm_*` |

## Checklist de sortie (a appliquer avant suppression)

- Les imports applicatifs ont ete migres vers la cible canonique.
- Les scripts CI/CD et outils dev pointent la cible canonique.
- La documentation de reference ne cite plus le wrapper.
- Les tests de non-regression passent sans le wrapper.
