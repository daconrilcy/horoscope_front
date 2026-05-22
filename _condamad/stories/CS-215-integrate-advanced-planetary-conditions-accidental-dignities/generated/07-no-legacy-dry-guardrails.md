<!-- Guardrails No Legacy / DRY pour CS-215. -->

# No Legacy / DRY Guardrails

## Canonical Ownership

- Conditions avancees factuelles: `backend/app/domain/astrology/planetary_conditions`.
- Conversion condition -> score accidentel: `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`.
- Profils de deltas: `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`.
- Agregation score: `PlanetDignityScoringService`.

## Forbidden

- Recalculer proximite solaire, mouvement, relation solaire, visibilite ou phase lunaire.
- Ajouter fallback, shim, alias, re-export legacy ou second moteur de scoring.
- Lire API, DB, infra, services chart, frontend ou LLM depuis les nouveaux modules.
- Modifier les calculateurs `planetary_conditions`.

## Evidence Required

- Tests cibles du moteur et de l'integration.
- Scans zero-hit sur dependances interdites, termes interdits et duplication.
- Diff adjacent vide sur API/DB/frontend/projection publique/calculateurs amont.
- `RG-142` cite et valide.

## Result

- Aucun fallback, shim, alias, legacy path ou duplication active introduit.
- Le choix d'un champ dedie `advanced_condition_modifiers` evite de polluer les
  poids runtime historiques tout en ajoutant les deltas au score accidentel.
