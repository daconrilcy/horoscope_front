# Audit de suppression

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `backend/app/prediction` | module | historical-facade | Services, API, infra, jobs, tests avant migration | `backend/app/domain/prediction` | delete | `rg --files app/prediction` zero fichier car chemin absent | Reintroduction du package legacy. |
| `backend/app/prediction/__init__.py` | file | historical-facade | Imports package legacy avant migration | `backend/app/domain/prediction/__init__.py` | move-delete old path | `importlib.util.find_spec('app.prediction') is None` | Package legacy redeviendrait importable si recreate. |
| Engine pur prediction | module group | canonical-active | `app/services/prediction/engine_orchestrator.py`, tests moteur | `backend/app/domain/prediction` | move | Tests `test_engine_orchestrator.py` PASS | La granularite d'owner plus fine reste a revoir dans les stories CS-015 a CS-017. |
| Read models persisted | DTO group | canonical-active | repositories, services, API, tests | `backend/app/domain/prediction` pour cette convergence physique | move | Scans zero import `app.prediction`; integration API PASS | Owner infra plus precis prevu par CS-016, non bloqueur pour extinction physique. |
| Projection publique | module group | canonical-active | routeurs publics/internes, services, tests | `backend/app/domain/prediction/public_projection.py` | move | Tests API PASS; scans zero import legacy | Owner API/contrat plus precis prevu par CS-017, non bloqueur pour suppression du namespace. |
| Consumers `app.prediction.*` | import path | active_legacy_removed | Tous les fichiers Python scannes sous `backend/app` et `backend/tests` | `app.domain.prediction.*` | replace-consumer | `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` zero-hit | Drift d'import hors scope si des consommateurs externes non documentes existent. |

## Decision

La suppression physique est complete cote depot: aucun consommateur interne actif ne depend encore de `app.prediction`. Aucune facade, alias, fallback, wrapper ou re-export n'a ete conserve.
