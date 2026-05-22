# CS-214 Implementation Plan

1. Creer un orchestrateur pur qui extrait les longitudes, appelle les
   calculateurs CS-209 a CS-213, construit les bundles et agrege les signaux.
2. Creer une factory de signaux techniques pour proximite solaire, mouvement,
   relation solaire, visibilite et phase lunaire globale.
3. Exporter les symboles publics depuis `planetary_conditions.__init__`.
4. Ajouter le champ runtime optionnel a `NatalResult` et appeler
   l'orchestrateur depuis les positions et vitesses deja calculees.
5. Ajouter les tests runtime et integration natal.
6. Executer lint, tests, scans RG-141 et validation de story.

## No Legacy

Aucun shim, alias, fallback, second owner ou dependance nouvelle. Le bloc
runtime est volontairement exclu de la projection JSON Pydantic.
