<!-- Registre des constats pour le recontrole CONDAMAD du domaine prediction. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | boundary-violation | `backend/app/prediction` | E-003, E-007, E-008, E-010, E-014 | Le dossier racine `app.prediction` reste une surface runtime active. Il est stabilise, mais pas supprimable en l'etat. | Migrer les fichiers restants vers `domain`, `services`, `infra`, `api/contracts` et `ops`, puis supprimer le dossier sans shim ni re-export. | yes |
| F-002 | High | High | missing-canonical-owner | moteur prediction pur | E-003, E-007, E-010 | Le moteur pur est appele depuis `services/prediction`, mais son owner physique reste le namespace legacy `app.prediction`. | Creer/migrer vers `backend/app/domain/prediction` avec imports internes canonicalises et tests de non-retour vers `app.prediction`. | yes |
| F-003 | Medium | High | dependency-direction-violation | `backend/app/infra/db/repositories` | E-008, E-009 | L'infra DB depend encore de DTO/read models situes dans le namespace a supprimer, ce qui bloque l'extinction du dossier. | Deplacer ou dedoubler proprement les DTO de persistence vers un owner canonique infra ou domaine, sans facade de compatibilite. | yes |
| F-004 | Medium | High | boundary-violation | routeurs API prediction / internal LLM QA | E-008, E-013 | Les routeurs importent encore directement la projection et les snapshots depuis `app.prediction`; la couche API reste couplee au namespace a supprimer. | Faire passer les routeurs par `services/prediction` et/ou `services/api_contracts`, puis verifier zero import `app.prediction` sous `backend/app/api`. | yes |
| F-005 | Medium | High | missing-guard | guards extinction prediction | E-002, E-011, E-014 | Les guards actuels empechent la croissance de `app.prediction`, mais ils autorisent encore l'inventaire actuel; ils ne prouvent pas l'objectif final zero fichier/zero import. | Ajouter une story d'extinction avec migration des tests, nouvelle garde zero-hit et retrait de l'allowlist temporaire. | yes |
| F-006 | Info | High | no-legacy-dry | CS-006 a CS-013 | E-001, E-002, E-004, E-005, E-006, E-012, E-013 | Les stories precedentes ont ete mises en oeuvre et leurs invariants principaux passent; le risque restant est la migration physique, pas une regression de ces stories. | Conserver RG-026 a RG-033 comme non-regression obligatoire pour les stories de suppression du namespace. | no |

## Finding Details

### F-001

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: `backend/app/prediction`
- Evidence: E-003, E-007, E-008, E-010, E-014
- Expected rule: aucune racine applicative `backend/app/prediction` ne doit rester une fois les owners canoniques disponibles.
- Actual state: 39 fichiers Python et 16 templates restent sous `backend/app/prediction`; services, API, infra, jobs et tests importent encore ce namespace.
- Impact: Le dossier racine `app.prediction` reste une surface runtime active. Il est stabilise, mais pas supprimable en l'etat.
- Recommended action: Migrer les fichiers restants vers `domain`, `services`, `infra`, `api/contracts` et `ops`, puis supprimer le dossier sans shim ni re-export.
- Story candidate: yes
- Suggested archetype: namespace-extinction

### F-002

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: moteur prediction pur
- Evidence: E-003, E-007, E-010
- Expected rule: le calcul pur et les invariants metier vivent sous `backend/app/domain`.
- Actual state: `backend/app/services/prediction/engine_orchestrator.py` importe encore le moteur pur depuis `app.prediction.*`; `backend/app/domain/prediction` est absent.
- Impact: Le moteur pur est appele depuis `services/prediction`, mais son owner physique reste le namespace legacy `app.prediction`.
- Recommended action: Creer/migrer vers `backend/app/domain/prediction` avec imports internes canonicalises et tests de non-retour vers `app.prediction`.
- Story candidate: yes
- Suggested archetype: domain-purity-convergence

### F-003

- Severity: Medium
- Confidence: High
- Category: dependency-direction-violation
- Domain: `backend/app/infra/db/repositories`
- Evidence: E-008, E-009
- Expected rule: l'infra DB ne depend pas d'un package legacy appele a disparaitre; les DTO de persistence ont un owner stable.
- Actual state: `daily_prediction_repository.py` et `prediction_schemas.py` importent encore des DTO depuis `app.prediction`.
- Impact: L'infra DB depend encore de DTO/read models situes dans le namespace a supprimer, ce qui bloque l'extinction du dossier.
- Recommended action: Deplacer ou dedoubler proprement les DTO de persistence vers un owner canonique infra ou domaine, sans facade de compatibilite.
- Story candidate: yes
- Suggested archetype: data-model-boundary-convergence

### F-004

- Severity: Medium
- Confidence: High
- Category: boundary-violation
- Domain: routeurs API prediction / internal LLM QA
- Evidence: E-008, E-013
- Expected rule: l'API reste adaptateur HTTP et consomme des services/contrats canoniques, pas le namespace a supprimer.
- Actual state: `public/predictions.py` et `internal/llm/qa.py` importent `PersistedPredictionSnapshot` et `PublicPredictionAssembler` depuis `app.prediction`.
- Impact: Les routeurs importent encore directement la projection et les snapshots depuis `app.prediction`; la couche API reste couplee au namespace a supprimer.
- Recommended action: Faire passer les routeurs par `services/prediction` et/ou `services/api_contracts`, puis verifier zero import `app.prediction` sous `backend/app/api`.
- Story candidate: yes
- Suggested archetype: api-adapter-boundary-convergence

### F-005

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: guards extinction prediction
- Evidence: E-002, E-011, E-014
- Expected rule: apres migration, un guard doit prouver que `backend/app/prediction` et tous les imports `app.prediction` sont absents.
- Actual state: la garde actuelle compare l'inventaire courant a une allowlist; elle protege contre la croissance mais autorise encore le dossier.
- Impact: Les guards actuels empechent la croissance de `app.prediction`, mais ils autorisent encore l'inventaire actuel; ils ne prouvent pas l'objectif final zero fichier/zero import.
- Recommended action: Ajouter une story d'extinction avec migration des tests, nouvelle garde zero-hit et retrait de l'allowlist temporaire.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

### F-006

- Severity: Info
- Confidence: High
- Category: no-legacy-dry
- Domain: CS-006 a CS-013
- Evidence: E-001, E-002, E-004, E-005, E-006, E-012, E-013
- Expected rule: les invariants crees par les stories precedentes restent vrais avant de planifier l'extinction.
- Actual state: les tests cibles passent et les scans de retour infra/legacy/LLM sont zero-hit ou limites aux guards attendus.
- Impact: Les stories precedentes ont ete mises en oeuvre et leurs invariants principaux passent; le risque restant est la migration physique, pas une regression de ces stories.
- Recommended action: Conserver RG-026 a RG-033 comme non-regression obligatoire pour les stories de suppression du namespace.
- Story candidate: no
- Suggested archetype: none
