# CS-196 Execution Brief

## Scope

- Implementer la couche backend pure `interpretation_adapters`.
- Ajouter les tables/seeds `astral_interpretation_*`.
- Charger les references dans `AstrologyRuntimeReference`.
- Brancher `NatalResult.interpretation_adapter` apres `dominant_planets`.
- Exposer une projection JSON stricte sans recalcul.

## Out of Scope

- Aucun texte narratif.
- Aucun appel LLM.
- Aucun assemblage de prompt.
- Aucun comportement UI.
