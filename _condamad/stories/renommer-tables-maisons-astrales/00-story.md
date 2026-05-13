# Renommer les tables SQL des maisons astrales

## Objectif

Renommer les tables SQL suivantes sans changer les contrats runtime JSON ni les noms de champs métier Python :

- `houses` -> `astral_houses`
- `house_profiles` -> `astral_prediction_daily_house_profiles`
- `house_category_weights` -> `astral_house_category_weights`

## Contexte

La documentation `docs/tables-maisons-et-roles.md` décrit le rôle des tables liées aux maisons astrologiques. Le renommage doit aligner le vocabulaire SQL avec les noms déjà normalisés côté planètes et signes, tout en gardant les objets métier `HouseModel`, `HouseProfileModel` et `HouseCategoryWeightModel`.

## Acceptance Criteria

1. Les modèles SQLAlchemy pointent vers les trois noms de tables canoniques et leurs clés étrangères maison utilisent `astral_houses.id`.
2. Une migration Alembic renomme les trois tables en conservant les données, les contraintes et les index utiles, avec downgrade vers les anciens noms.
3. Les migrations/tests de référence attendent les nouveaux noms et prouvent que les anciens noms SQL ne restent pas actifs au head.
4. La documentation `docs/tables-maisons-et-roles.md` décrit les nouveaux noms SQL sans présenter les anciens noms comme noms actifs.
5. Les tests ciblés du périmètre migrations/référentiels passent; la suite complète n'est pas lancée conformément à la demande utilisateur.

## Contraintes

- Ne pas ajouter de shim, alias ou double table active.
- Ne pas renommer les champs JSON `houses` du payload thème natal.
- Ne pas lancer toute la suite de tests.
- Toute commande Python doit être exécutée après activation de `.\.venv\Scripts\Activate.ps1`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-092` - les référentiels astrologiques stables restent non versionnés; le renommage `houses` ne doit pas réintroduire `reference_version_id`.
  - `RG-093` - la normalisation des noms SQL astral reste cohérente avec les tables `astral_signs` et profils associés.
- Required regression evidence:
  - Tests ciblés de migrations/référentiels.
  - Scan ciblé des anciens noms SQL dans `backend/app` et les tests actifs.
- Allowed differences:
  - Les anciens noms restent autorisés uniquement dans les migrations historiques, le downgrade de la nouvelle migration, les scans de garde et les artefacts CONDAMAD.
