# Execution Brief

- Story key: `CS-161-ajouter-profils-interpretation-maisons`
- Objective: ajouter le referentiel SQL editorial `house_interpretation_profiles`.
- Boundaries: backend DB models, Alembic migration, tests de schema et preuves CONDAMAD.
- Non-goals: seed complet, API, runtime astrology, scoring prediction, frontend.
- Preflight: lire `AGENTS.md`, `regression-guardrails.md`, modeles reference/prediction, migrations recentes.
- Write rules: petit delta, aucun shim, aucune table runtime, aucune dependance produit dans `domain/astrology`.
- Done: AC1-AC3 prouves par tests, lint, scan negatif et evidence finale.
- Halt: conflit de revision Alembic, besoin de contenu editorial produit, ou modification requise du runtime.
