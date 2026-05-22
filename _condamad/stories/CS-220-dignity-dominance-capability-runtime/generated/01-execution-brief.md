# Execution Brief - CS-220-dignity-dominance-capability-runtime

## Primary objective

Migrer les entrees et payloads internes dignity/dominance vers `NatalResult.chart_objects`, sans changer les calculateurs historiques ni les sorties publiques.

## Boundaries

- Modifier uniquement le domaine backend astrology, les tests associes et les preuves CONDAMAD.
- Garder `PlanetDignityScoringService`, `PlanetDominanceEngine`, `NatalResult.dignities` et `NatalResult.dominant_planets` comme surfaces historiques.
- Ne pas toucher API, JSON public, frontend, DB, migrations ou dependances.

## Write rules

- Selectionner les candidats via `supports_dignities` et `supports_dominance`, pas par `object_type`.
- Projeter les resultats historiques vers des payloads immuables sans recalculer les scores.
- Enrichir `chart_objects` par nouvelles instances.
- Ajouter tests unitaires, integration natal et guards d'architecture.

## Done when

- Tous les AC de `03-acceptance-traceability.md` ont une preuve code et validation.
- `evidence/validation.md` et `generated/10-final-evidence.md` sont complets.
- `_condamad/stories/story-status.md` est synchronise.
