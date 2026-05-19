# CS-190 - Seeder les dignites astrales et exposer les persistances runtime

## Goal

Seeder les JSON de dignites astrales ajoutes/modifies dans `docs/db_seeder/astrology`, ajouter les tables au seed backend, puis creer les modeles SQLAlchemy et repositories necessaires.

## Acceptance Criteria

- AC1: Les nouveaux JSON de dignites essentielles, accidentelles, termes, faces, triplicites, profils, poids et resultats runtime sont representes par des modeles SQLAlchemy.
- AC2: Les tables de reference sont alimentees depuis les JSON par le seed backend existant de reference data.
- AC3: Les tables runtime/audit, notamment `astral_chart_planet_dignity_results`, ont un modele et un repository sans donnees seed obligatoires.
- AC4: Les contraintes relationnelles et uniques demandees sont presentes cote DB quand elles sont pertinentes.
- AC5: Des tests ciblés prouvent la migration, le seed et les repositories.

## Constraints

- Respecter le venv pour toute commande Python.
- Ne pas creer de `requirements.txt`.
- Ne pas ajouter de dossier racine sous `backend/`.
- Garder un delta coherent, sans wrapper de compatibilite ni fallback silencieux.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-011` - les tests backend DB doivent utiliser le harnais canonique.
  - `RG-014` - les tests ajoutes doivent avoir des assertions utiles.
- Non-applicable invariants: frontend/API route/LLM guardrails non touches.
