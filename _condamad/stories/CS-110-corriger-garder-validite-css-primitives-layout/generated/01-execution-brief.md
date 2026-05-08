<!-- Brief d'execution genere pour guider la mise en oeuvre CS-110. -->

# Execution Brief CS-110

- Story key: `CS-110-corriger-garder-validite-css-primitives-layout`
- Objective: corriger le padding invalide de `PageLayout.css` et ajouter une garde deterministe de syntaxe CSS pour les layouts.
- Boundary: `frontend/src/layouts/PageLayout.css`, `frontend/src/tests/design-system-guards.test.ts`, preuves CS-110.
- Non-goals: pas de changement de route, pas de nouveau token, pas de dependency, pas de modification des APIs React layout.
- Guardrails: `RG-050`, `RG-068`.
- Done: AC1-AC4 en `PASS`, tests ciblés et lint verts, preuve finale complete.
- Halt: nouvelle dependance CSS parser requise, changement visuel hors padding attendu, ou test frontend non resolu.
