# Execution Brief

- Story key: `supprimer-astro-characteristics`
- Objective: retirer la table generique `astro_characteristics` du runtime backend, des seeds, du clonage et du contrat public.
- Boundaries: backend DB models, repository reference data, Alembic migrations, backend tests, capsule CONDAMAD, registry guardrail si un invariant durable est cree.
- Non-goals: pas de nouvelle table d'overrides, pas de refonte du moteur natal, pas de compatibilite.
- Preflight: verifier `git status --short`, lire `AGENTS.md`, lire `_condamad/stories/regression-guardrails.md`, inspecter les usages via `rg`.
- Write rules: plus petit delta coherent, aucune modification frontend, aucune suppression de fichiers hors migration/test/code directement lies.
- Done: ACs tracees, tests et scans executés avec venv active pour Python, final evidence complete, status story mis a jour.
- Halt: migration Alembic contradictoire, tests DB non reparables sans decision externe, besoin d'une nouvelle dependance.
