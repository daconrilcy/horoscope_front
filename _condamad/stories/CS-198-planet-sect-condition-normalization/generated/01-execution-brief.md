# CS-198 Execution Brief

## Objectif

Exposer `dignities.planets[planet_code].sect_condition` comme contrat explicite
derive une seule fois depuis `ChartSectResult` et les regles runtime
`in_sect` / `out_of_sect`.

## Bornes

- Domaine unique: `backend/app/domain/astrology/dignities`.
- Projection publique uniquement dans `backend/app/services/chart/json_builder.py`.
- Aucun changement frontend, route API, migration ou moteur hayz/rejoicing.
- Aucun mapping local de planetes diurnes/nocturnes.

## Conditions d'arret

- Stopper si aucune source runtime de secte planetaire n'existe.
- Stopper si les validations ciblees echouent sans correction sure.
- Ne pas toucher les modifications preexistantes CS-197, guardrails et statut
  sauf synchronisation explicite de la ligne CS-198.

## Done

- Contrat `PlanetSectCondition` immutable.
- Calculateur pur `PlanetSectConditionCalculator`.
- Projection JSON additive `sect_condition`.
- Tests, scans et preuves persistantes presents.
