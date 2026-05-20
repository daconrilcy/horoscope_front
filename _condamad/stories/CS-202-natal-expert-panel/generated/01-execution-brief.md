# Execution Brief - CS-202-natal-expert-panel

## Objective

Afficher un panneau expert du theme natal dans la page `/natal`, en consommant
uniquement le JSON public existant expose par le backend depuis CS-201.

## Boundaries

- Domaine unique: `frontend`.
- Backend, migrations, seeds, `json_builder.py`, routes API et persistence hors
  scope.
- Toute tranche frontend passe par le contrat `condamad-frontend-dev`.
- Le panneau peut formater, trier et grouper pour l'affichage, mais uniquement
  depuis les champs explicites du payload public.

## Non-goals

- Aucun calcul de secte, hayz, out-of-sect, joies, dignites, dominantes,
  signaux ou interpretation cote React.
- Aucun alias legacy, fallback doctrinal, shim ou compatibilite transitoire.
- Aucun style inline et aucune nouvelle dependance.

## Required guardrails

- Appliquer `RG-129` et les invariants associes `RG-118` a `RG-128`.
- Executer les scans frontend interdits de `00-story.md` section 20.
- Prouver que les chemins backend interdits ne changent pas.

## Completion definition

- AC1 a AC12 passent avec preuves code et validation.
- Les fichiers d'evidence before/after/validation existent.
- Les tests frontend cibles, lint/build frontend, scans interdits et regressions
  backend CS-201 sont executes ou bloques avec raison explicite.
- `generated/10-final-evidence.md` et `_condamad/stories/story-status.md` sont
  synchronises.
