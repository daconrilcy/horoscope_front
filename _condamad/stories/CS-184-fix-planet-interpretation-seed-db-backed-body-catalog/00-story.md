# CS-184 - Fix planet interpretation seed and DB-backed body catalog

## Source

Demande utilisateur du 2026-05-18:

- `astral_planet_interpretation_profiles` doit être seedée depuis `docs/db_seeder/astrology/astral_planet_interpretation_profiles.json`.
- `PLANET_BODY_TYPES` et `ASTROLOGICAL_ANGLE_POINT_CODES` ne doivent pas revenir dans `backend/app/domain/prediction/aspect_reference.py`.
- Les types planétaires doivent venir de `astral_planet_definitions`.
- Les points angulaires doivent venir de `astral_angle_points`.
- Vérifier qu'un guardrail empêche la réintroduction de constantes hardcodées quand la valeur existe en table.

## Acceptance Criteria

1. Le seed backend alimente `astral_planet_interpretation_profiles` depuis le JSON documentaire.
2. Les règles d'orbes prediction ne s'appuient plus sur des constantes hardcodées de familles planétaires ou de points angulaires.
3. Le contexte prediction expose les définitions planétaires et les points angulaires nécessaires au runtime.
4. Un test de garde échoue si les constantes interdites sont réintroduites.
5. Les tests ciblés de seed, API daily et seed v2 passent.
