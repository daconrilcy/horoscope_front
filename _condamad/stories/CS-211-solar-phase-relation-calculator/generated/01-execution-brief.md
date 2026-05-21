# Execution Brief - CS-211 solar-phase-relation-calculator

## Primary objective

Implementer uniquement le calculateur domaine pur de relation solaire
oriental/occidental sous
`backend/app/domain/astrology/planetary_conditions`.

## Boundaries

- Ajouter `SolarPhaseRelationThresholds` au contrat canonique si absent.
- Ajouter `solar_phase_relation_calculator.py`.
- Exporter les fonctions publiques depuis le package `planetary_conditions`.
- Ajouter les tests unitaires du calculateur et du contrat de seuil.
- Ne pas integrer dans `NatalResult`, JSON public, API, DB, frontend ou moteurs
  adjacents.

## Done conditions

- Tous les AC de `00-story.md` ont une preuve code et validation.
- Les tests cibles, `ruff format .`, `ruff check .`, `pytest -q`, les scans
  anti-derives et validations de story sont executes dans le venv.
- `generated/10-final-evidence.md` et `generated/11-code-review.md` sont
  complets.
- `_condamad/stories/story-status.md` est synchronise.

## Halt conditions

- Contrat CS-208 incompatible avec `SolarPhaseRelationThresholds`.
- Besoin d'une dependance, integration adjacente ou exception non prevue.
- Validation requise en echec sans correctif borne.
