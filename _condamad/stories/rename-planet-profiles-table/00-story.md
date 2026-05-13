# Renommer la table des profils planetaires de prediction quotidienne

## Goal

Renommer la table SQL `planet_profiles` en `astral_prediction_daily_planet_profiles` pour clarifier qu'elle appartient au moteur de prediction quotidienne et non au calcul du theme astral.

## Context

L'analyse precedente a confirme que cette table n'intervient pas dans le calcul du theme astral. Elle sert au scoring, aux orbes et aux profils de planetes dans le moteur de prediction journaliere.

## Acceptance Criteria

| ID | Requirement |
|---|---|
| AC1 | Le modele SQLAlchemy `PlanetProfileModel` pointe vers la table canonique `astral_prediction_daily_planet_profiles`. |
| AC2 | Une migration Alembic renomme la table existante depuis `planet_profiles` sans perte de donnees et conserve les index/contraintes utiles. |
| AC3 | Les tests et assertions de schema attendent le nouveau nom de table. |
| AC4 | Les references documentaires actives mentionnent le nouveau nom et ne presentent plus `planet_profiles` comme table SQL active. |
| AC5 | Les anciennes references `planet_profiles` restantes sont limitees aux attributs runtime Python, noms de fonctions, artefacts historiques ou logique de migration necessaire. |

## Non-goals

- Ne pas renommer les attributs Python `PredictionContext.planet_profiles` ni les fonctions `get_planet_profiles`.
- Ne pas changer le calcul, le seed metier, les donnees, les poids ou les DTO.
- Ne pas modifier le frontend.
- Ne pas toucher aux changements utilisateur preexistants hors du scope.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-092` - les tables structurelles `planets`, `houses`, `aspects`, `astro_points` restent non versionnees; la story touche une table parametrique qui reference `planets`.
  - `RG-093` - les tables astrales recemment normalisees ne doivent pas regresser; la story touche la documentation et les seeds voisins.
- Required regression evidence:
  - Tests repository/migrations/seeds lies aux references astrologiques.
  - Scan cible de l'ancien nom de table.
- Allowed differences:
  - Les migrations historiques peuvent conserver l'ancien nom lorsqu'elles decrivent l'etat historique avant la migration de renommage.
