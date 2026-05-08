<!-- Brief d'execution genere pour guider la mise en oeuvre CS-111. -->

# Execution Brief CS-111

- Story key: `CS-111-retirer-redecider-exception-inline-style-twocolumnlayout`
- Objective: supprimer l'exception inline style de `TwoColumnLayout` et converger les surfaces `--sidebar-width` remediables.
- Boundary: `TwoColumnLayout.*`, allowlists inline/design-system, `ChatPage.css`, token namespace registry, preuves CS-111.
- Non-goals: pas de refonte des pages, pas de route change, pas de nouvelle dependency.
- Guardrails: `RG-047`, `RG-050`, `RG-068`.
- Done: AC1-AC5 en `PASS`, sans decision arbitraire requise car aucun besoin runtime arbitraire n'est prouve.
