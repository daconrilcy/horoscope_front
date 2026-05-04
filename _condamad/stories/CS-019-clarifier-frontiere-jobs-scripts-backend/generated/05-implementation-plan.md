# Implementation Plan — CS-019

1. Capturer la classification de chaque fichier initial sous `app.jobs`.
2. Deplacer les helpers calibration/QA vers `app.services.calibration`.
3. Deplacer les entrypoints batch planifiables sous `app.scheduled_tasks`.
4. Ajouter des wrappers CLI minces sous `backend/scripts`.
5. Mettre a jour les tests vers les owners canoniques.
6. Ajouter une garde AST/path contre la reintroduction de `app.jobs` et de non-taches planifiables.
7. Executer les tests cibles, scans No Legacy, lint et validateurs CONDAMAD.
