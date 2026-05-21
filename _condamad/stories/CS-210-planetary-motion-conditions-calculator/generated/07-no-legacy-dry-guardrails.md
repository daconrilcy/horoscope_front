# No Legacy / DRY Guardrails - CS-210

## Canonical Owners

- Profil de mouvement: `planetary_conditions/contracts.py`.
- Catalogue par defaut: `planetary_conditions/planetary_motion_profiles.py`.
- Calcul pur: `planetary_conditions/planetary_motion_calculator.py`.
- Tests: `backend/tests/unit/domain/astrology/planetary_conditions`.

## Forbidden

- Shim, alias, fallback, compatibilite, second calculateur.
- Integration API, DB, services chart, JSON public, frontend ou `NatalResult`.
- Scoring, texte narratif, prompt, LLM ou dependance externe.

## Required Evidence

- Tests unitaires comportementaux.
- Scans zero-hit sur imports et symboles interdits.
- Diff adjacent vide.
- `RG-135`, `RG-136`, `RG-137` consultes et inchanges.
