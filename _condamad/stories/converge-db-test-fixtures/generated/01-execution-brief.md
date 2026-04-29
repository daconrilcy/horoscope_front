# Execution Brief

- Story key: `converge-db-test-fixtures`
- Objective: converger le harnais DB des tests backend vers un accès explicite via helper/fixture de test, sans modifier le comportement applicatif.
- Boundaries: migrations Alembic, modèles SQLAlchemy et frontend hors scope.
- Non-goals: migration exhaustive de tous les imports directs, suppression complète du monkeypatch global `backend/app/tests/conftest.py`, création d'un dossier racine sous `backend/`.
- Required preflight: lire `AGENTS.md`, `00-story.md`, `_condamad/stories/regression-guardrails.md`, l'état git et les conftests DB backend.
- Write rules: petit delta, aucun alias de compatibilité, allowlist persistée pour exceptions restantes, helper canonique sous les arbres de tests existants.
- Done conditions: inventaires avant/après persistés, lot représentatif migré, garde anti-réintroduction active, tests ciblés et lint exécutés dans le venv.
- Halt conditions: rupture de l'alignement SQLite/Alembic, besoin de dépendance nouvelle, suppression du monkeypatch global qui casse des suites non migrées.
