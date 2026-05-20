# CS-198 Implementation Plan

1. Ajouter `PlanetSectCondition` dans les contrats de dignites avec validation stricte.
2. Ajouter un calculateur pur qui lit uniquement les regles runtime
   `in_sect`/`out_of_sect` et le `ChartSectResult`.
3. Brancher le calcul dans `PlanetDignityScoringService`, apres le calcul
   unique de `ChartSectResult`.
4. Projeter `sect_condition` dans `json_builder.py` sans import de calculateur.
5. Mettre a jour les tests de contrat, scoring, projection, persistance et
   repository runtime.
6. Executer tests, scans anti-reintroduction, lint et format.

Rollback: retirer le nouveau contrat, le calculateur, le champ
`sect_condition`, les assertions associees et les artefacts CS-198.
