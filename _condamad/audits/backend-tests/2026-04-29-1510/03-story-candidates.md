# Story Candidates - backend-tests

## SC-101 - Converger le harnais DB de tests

- Source finding: F-101
- Suggested story title: Replace direct `SessionLocal` test imports with an explicit DB fixture
- Suggested archetype: test-harness-convergence
- Primary domain: backend tests DB harness
- Required contracts: SQLite alignment fixture, Alembic head check, no direct production `SessionLocal` imports in tests
- Draft objective: migrer les tests DB vers une session de test explicite et supprimer la redirection globale de `backend/app/tests/conftest.py`.
- Must include: inventaire des 89 fichiers; helper/fixture canonique; migration par lots; preuve que `ensure_configured_sqlite_file_matches_alembic_head` continue de couvrir les fichiers SQLite pertinents.
- Validation hints: `pytest -q app/tests/unit/test_backend_db_test_harness.py`; tests integration DB representatifs; `pytest --collect-only -q --ignore=.tmp-pytest`; scan zero-hit sur imports directs `SessionLocal`.
- Blockers: risque eleve de blast radius, a traiter par lots bornes.

## SC-102 - Guarder la topologie canonique des tests backend

- Source finding: F-102
- Suggested story title: Document and enforce backend pytest test roots
- Suggested archetype: test-suite-topology-convergence
- Primary domain: backend tests topology
- Required contracts: `backend/pyproject.toml` testpaths, monorepo architecture, no hidden test roots
- Draft objective: rendre explicite quelles racines de tests sont autorisees et bloquer toute nouvelle racine non collectee.
- Must include: registre de topologie; garde AST/path; comparaison statique entre `rg --files backend -g test_*.py` et les racines autorisees; preuve que toutes les racines collectees sont intentionnelles.
- Validation hints: `pytest -q app/tests/unit/test_backend_test_topology.py`; `pytest --collect-only -q --ignore=.tmp-pytest`.
- Blockers: decision si `backend/tests/*` est canonique durable ou suite specialisee.

## SC-103 - Corriger la garde anti import croise

- Source finding: F-103
- Suggested story title: Make cross-test import guard cover both backend test roots
- Suggested archetype: reintroduction-guard-fix
- Primary domain: backend tests helpers
- Required contracts: zero imports depuis modules executables `test_*.py`, coverage de `backend/app/tests` et `backend/tests`
- Draft objective: corriger `test_backend_test_helper_imports.py` pour scanner les deux racines reelles.
- Must include: correction de `BACKEND_ROOT`; assertion que `TEST_ROOTS` contient `backend/app/tests` et `backend/tests`; scan zero-hit conserve.
- Validation hints: `pytest -q app/tests/unit/test_backend_test_helper_imports.py`; scan rg cross-test imports.
- Blockers: aucun.

## SC-104 - Decider l'ownership des tests qualite/ops

- Source finding: F-104
- Suggested story title: Classify backend ops and quality checks
- Suggested archetype: quality-suite-ownership-decision
- Primary domain: quality/ops tests
- Required contracts: CI test jobs, backend pytest scope, PowerShell script checks
- Draft objective: decider si les tests docs/scripts/secrets/security restent dans pytest backend, deviennent une suite marquee, ou passent dans un job qualite separe.
- Must include: inventaire des tests concernes; cout d'execution; dependances OS; decision persistante; adaptation des commandes README/CI si necessaire.
- Validation hints: `pytest -q -m ...` selon decision; execution des scripts PowerShell cibles si deplaces.
- Blockers: decision utilisateur/CI.

## SC-105 - Migrer ou borner les tests `LLMNarrator` deprecies

- Source finding: F-105
- Suggested story title: Replace deprecated `LLMNarrator` tests with canonical adapter coverage
- Suggested archetype: deprecation-guard-convergence
- Primary domain: prediction tests
- Required contracts: narration horoscope, adapter canonique, absence de warnings non classes
- Draft objective: eliminer les 7 warnings ou les classer comme compatibilite temporaire documentee.
- Must include: decision keep/migrate; tests equivalents sur `AIEngineAdapter.generate_horoscope_narration` si migration; assertion que la suite ne produit plus ces warnings.
- Validation hints: `pytest -q tests/unit/prediction/test_llm_narrator.py`; `pytest -q -W error::DeprecationWarning tests/unit/prediction`.
- Blockers: confirmer si `LLMNarrator` doit rester supporte temporairement.
