# Story CS-161 ajouter-profils-interpretation-maisons: Ajouter les profils d'interpretation editoriale des maisons

Status: done

## 1. Objective

Creer un referentiel SQL dedie aux profils d'interpretation editoriale des maisons astrologiques, versionne par `reference_version_id`, rattache au vocabulaire stable `astral_houses`, multilingue et extensible par tradition.

## 2. Trigger / Source

- Source type: user-request
- Source reference: demande utilisateur du 2026-05-14 sur la table `house_interpretation_profiles`.
- Reason for change: separer le vocabulaire canonique des maisons, les profils techniques de prediction, les poids produit et le vocabulaire editorial utilise par l'interpretation et les prompts IA.

## 3. Domain Boundary

- Domain: backend referentiels astrologiques editoriaux.
- In scope:
  - ajouter la table `house_interpretation_profiles`;
  - ajouter le modele SQLAlchemy correspondant;
  - relier la table a `reference_versions` et `astral_houses`;
  - garantir une unicite par version, maison, langue et tradition;
  - couvrir la migration et le modele par tests.
- Out of scope:
  - alimenter les 12 lignes de contenu editorial;
  - exposer une API;
  - consommer ce vocabulaire dans le runtime astrologique ou le scoring prediction;
  - modifier `HouseRuntimeData`, `HouseProfileModel` ou `HouseCategoryWeightModel`.

## 4. Separation cible

```text
astral_houses
= vocabulaire canonique stable

astral_prediction_daily_house_profiles
= parametrage astrologique/predictif technique

astral_house_category_weights
= routage produit vers les categories

house_interpretation_profiles
= vocabulaire editorial pour interpretation et prompts IA
```

## 5. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La table `house_interpretation_profiles` existe avec les colonnes editoriales demandees et des champs JSON stockes comme texte JSON. | Test de migration inspectant le schema Alembic head. |
| AC2 | La table est versionnee par `reference_version_id`, reference `astral_houses.id`, et impose l'unicite `(reference_version_id, house_id, language, tradition)`. | Tests SQLAlchemy modele + migration. |
| AC3 | Le modele ne modifie pas le runtime astrologique, les profils maison prediction ou les poids produit. | Tests de noms de tables existants + scans anti-consommation dans `domain/astrology`. |

## 6. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - ne pas recreer de table generique `astro_characteristics`.
  - `RG-092` - `astral_houses` reste un referentiel stable non versionne.
  - `RG-093` - ne pas toucher aux profils et maitrises des signes.
  - `RG-095` - ne pas introduire de symboles produit dans `domain/astrology`.
- Required regression evidence:
  - tests de migration des referentiels;
  - scan cible `domain/astrology`;
  - tests de modele reference/prediction existants.
- Allowed differences:
  - nouvelle table editoriale versionnee distincte de `astral_houses`.

## 7. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py
ruff check .
rg -n "house_interpretation_profiles|HouseInterpretationProfileModel" app/domain/astrology -g "*.py"
```

## 8. Dev Agent Instructions

- Implementer uniquement cette story.
- Ne pas ajouter de consommation runtime ou API.
- Ne pas modifier les tables structurelles `astral_houses`, `astral_signs`, `astral_planets`, `aspects` ou `astro_points`.
- Ne pas toucher au fichier non suivi `docs/recherches astro/house_interpretation_vocabulary.json` sans demande explicite.
