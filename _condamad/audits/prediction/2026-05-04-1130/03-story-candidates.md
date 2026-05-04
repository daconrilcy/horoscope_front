<!-- Propositions de stories issues du recontrole CONDAMAD prediction. -->

# Story Candidates

## SC-001

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Supprimer physiquement le namespace racine `app.prediction`
- Suggested archetype: namespace-extinction
- Primary domain: `backend/app/prediction`
- Required contracts: no-legacy-dry-audit-contract, dependency-direction-audit, test-guard-coverage-audit
- Draft objective: Orchestrer la migration finale des fichiers restants et supprimer `backend/app/prediction` sans facade, alias, fallback ni re-export.
- Must include: inventaire avant/apres, zero-hit `rg "app\.prediction" backend/app backend/tests`, suppression `__init__.py`, mise a jour RG-032 vers une garde zero fichier, aucun nouveau dossier racine backend.
- Validation hints: `rg --files backend/app/prediction`; `rg -n "from app\.prediction|import app\.prediction" backend/app backend/tests -g "*.py"`; suite prediction cible; diff imports.
- Blockers: decider l'owner final de la projection publique et des DTO persisted avant suppression.

## SC-002

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Migrer le moteur pur prediction sous `domain/prediction`
- Suggested archetype: domain-purity-convergence
- Primary domain: `backend/app/domain/prediction`
- Required contracts: domain-purity-audit-contract, no-legacy-dry-audit-contract
- Draft objective: Deplacer le calcul pur, les schemas metier et les policies deterministes hors de `app.prediction` vers `app.domain.prediction`.
- Must include: migration imports internes, absence FastAPI/SQLAlchemy/settings/LLM runtime, tests unitaires moteur inchanges, guard zero import inverse depuis `domain` vers `services/api/infra`.
- Validation hints: `rg -n "fastapi|sqlalchemy|Session|settings|AIEngineAdapter|from app\.infra|from app\.api" backend/app/domain/prediction -g "*.py"`; tests `test_engine_orchestrator.py`, `test_transit_*`, `test_public_*`.
- Blockers: confirmer que le moteur pur vit bien sous `backend/app/domain/prediction` et non sous un autre sous-package metier.

## SC-003

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Reclasser les DTO persisted prediction hors du namespace legacy
- Suggested archetype: data-model-boundary-convergence
- Primary domain: `backend/app/infra/db/repositories`, `backend/app/domain/prediction`
- Required contracts: data-model-boundary-audit, service-boundary-audit-contract
- Draft objective: Donner un owner stable aux DTO/read models `PersistedPredictionSnapshot`, scores, time blocks, turning points et `CalibrationData`.
- Must include: decision par type `domain-pure` ou `infra-read-model`, migration des imports repositories/services/tests, absence de double implementation active, aucun shim `app.prediction.persisted_*`.
- Validation hints: `rg -n "app\.prediction\.persisted|app\.prediction\.context" backend/app backend/tests -g "*.py"`; tests persistence, relative scoring et API daily.
- Blockers: choisir si les read models persisted representent un contrat domaine pur ou un contrat infra DB.

## SC-004

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Decoupler les routeurs API du namespace `app.prediction`
- Suggested archetype: api-adapter-boundary-convergence
- Primary domain: `backend/app/api/v1/routers/public/predictions.py`, `backend/app/api/v1/routers/internal/llm/qa.py`
- Required contracts: api-adapter-audit-contract, service-boundary-audit-contract
- Draft objective: Faire consommer aux routeurs uniquement les services prediction et les contrats API canoniques, sans import direct `app.prediction`.
- Must include: remplacement `PublicPredictionAssembler` et snapshots par owner canonique, conservation OpenAPI, gestion d'erreurs inchangee, zero import `app.prediction` sous `backend/app/api`.
- Validation hints: tests `test_daily_prediction_api.py`, `test_horoscope_daily_variant_narration.py`; scan `rg -n "app\.prediction" backend/app/api -g "*.py"`.
- Blockers: confirmer si la projection publique cible vit sous `services/prediction` ou `services/api_contracts/public`.

## SC-005

- Candidate ID: SC-005
- Source finding: F-005
- Suggested story title: Remplacer la garde anti-croissance par une garde d'extinction prediction
- Suggested archetype: architecture-guard-hardening
- Primary domain: `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- Required contracts: no-legacy-dry-audit-contract, test-guard-coverage-audit
- Draft objective: Transformer l'allowlist temporaire CS-012 en garde finale: aucun fichier sous `backend/app/prediction` et aucun import `app.prediction` dans le runtime ou les tests collectes.
- Must include: migration des fixtures/tests vers owners canoniques, suppression ou archivage explicite de l'allowlist, exceptions uniquement pour artefacts historiques `_condamad`, preservation RG-026 a RG-033.
- Validation hints: `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; `rg --files backend/app/prediction`; `rg -n "from app\.prediction|import app\.prediction" backend/app backend/tests -g "*.py"`.
- Blockers: cette story doit venir apres SC-002 a SC-004 ou etre une story finale d'integration.
