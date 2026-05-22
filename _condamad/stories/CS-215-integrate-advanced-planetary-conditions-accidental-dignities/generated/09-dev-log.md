<!-- Journal developpement CS-215. -->

# Dev Log

## Preflight

- Initial dirty files: `_condamad/stories/regression-guardrails.md`,
  `_condamad/stories/story-status.md`, dossier CS-215 non suivi.
- Applicable AGENTS: `AGENTS.md`.
- Gate de suffisance: PASS. Story mono-domaine, AC finis, preuves avant/apres,
  guard `RG-142`, scans et validation complete.

## Implementation Notes

- Ajout du contrat `AccidentalDignityModifier`.
- Ajout des profils V1 et du moteur de conversion dans `dignities`.
- Branchement optionnel de `AdvancedPlanetaryConditionsResult` au scoring.
- Premier essai d'injection dans `accidental_breakdown` a expose un risque de
  KeyError dans les poids runtime historiques. Correction retenue: champ dedie
  `advanced_condition_modifiers`, score additionne separement et exclusion
  explicite du dump/schema public.
- Revue iteration 1: correction AC7 pour `direction=STATIONARY` avec
  `is_retrograde=True`; retrait d'un patch hors domaine `condition/`.

## Validation Summary

- Tests cibles nouveaux: PASS.
- Tests regressions CS-208 a CS-214: PASS.
- Scans interdits: zero-hit.
- `ruff format backend`: PASS, 1505 files left unchanged.
- `ruff check backend`: PASS.
- `ruff check .`: PASS.
- `pytest -q`: PASS, 2932 passed, 1 skipped, 1177 deselected.

## Feedback Loop

No-propagation: les corrections de revue sont locales a CS-215 et deja
capturees par les tests d'integration et la preuve Pydantic d'exclusion
publique.
