<!-- Plan d'implementation suivi pour CS-215. -->

# Implementation Plan

1. Ajouter le contrat immutable `AccidentalDignityModifier`.
2. Ajouter les profils V1 centralises dans `advanced_condition_modifier_profiles.py`.
3. Ajouter le moteur pur `calculate_advanced_condition_modifiers`.
4. Brancher `AdvancedPlanetaryConditionsResult` dans `PlanetDignityScoringService`.
5. Passer le resultat CS-214 depuis `natal_calculation.py`.
6. Ajouter tests unitaires moteur et integration scoring.
7. Executer tests, scans, lint, regression globale et preuves CONDAMAD.

Decision de conception: les modificateurs sont exposes dans le champ dedie
`PlanetDignityResult.advanced_condition_modifiers` et additionnes a
`accidental_score` / `total_score`. Ils ne sont pas injectes dans
`accidental_breakdown`, car ce breakdown est consomme par les poids runtime
historiques et attend des codes de dignite deja presents dans le referentiel.
