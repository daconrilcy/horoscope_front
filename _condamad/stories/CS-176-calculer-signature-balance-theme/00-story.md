# Story CS-176 calculer-signature-balance-theme: Calculer la balance et la signature globale du theme natal

Status: done

## Objective

Ajouter un calcul canonique de balance et signature globale du thème natal.
Il produit les dominances élémentaires, modales, signes dominants, planètes
dominantes et maisons dominantes depuis les runtime astrology existants.
Le résultat reste déterministe, testé, sans narration ni logique prediction.

## Domain Boundary

Domain: `backend/app/domain/astrology/interpretation`.

In scope:

- Ajouter des contrats de balance/signature astrologique pure.
- Calculer éléments, modalités, signes, planètes et maisons dominants depuis les runtime existants.
- Brancher le résultat dans le flux natal de façon additive.
- Ajouter des tests unitaires déterministes.

Out of scope:

- Générer du texte LLM ou des prompts.
- Modifier les algorithmes Swiss Ephemeris.
- Ajouter une UI frontend.
- Créer une table DB de scoring produit.

Explicit non-goals:

- Ne pas recalculer les maisons ou aspects depuis le serializer chart.
- Ne pas lire directement les tables SQL depuis le calculateur.
- Ne pas remplacer `HouseStrengthEvaluator` ni `DominantAspectEvaluator`.
- Ne pas changer les invariants `RG-095`, `RG-096`, `RG-101`, `RG-107` et `RG-108`.

## Required Contracts

- Runtime source of truth: `SignRuntimeData`, `HouseStrengthRuntimeData`, `DominantAspectRuntimeData` et `AstrologyRuntimeReference.signs`.
- Baseline before: `_condamad/stories/CS-176-calculer-signature-balance-theme/chart-signature-before.md`.
- Baseline after: `_condamad/stories/CS-176-calculer-signature-balance-theme/chart-signature-after.md`.
- Allowed difference: ajout additif de `chart_balance` et/ou `chart_signature` si projection publique retenue.

## Contract Shape

Le contrat doit exposer:

- `elements`
- `modalities`
- `dominant_signs`
- `dominant_planets`
- `dominant_houses`
- `synthesis`
- `version`

Les scores sont normalisés et les égalités ont un tie-break documenté.

## Regression Guardrails

Applicable:

- `RG-095` - pas de dépendance astrology vers prediction.
- `RG-096` - `HouseStrengthRuntimeData` reste la source des scores de maisons.
- `RG-101` - les aspects dominants gardent leur owner.
- `RG-107` - pas de payload métier libre non typé.
- `RG-108` - pas de vocabulaire métier recréé localement.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Un contrat typé couvre la signature globale. | `pytest -q tests/unit/domain/astrology/test_chart_signature_runtime_data.py` |
| AC2 | Le calculateur classe les dominances avec tie-break documenté. | `pytest -q tests/unit/domain/astrology/test_chart_signature.py` |
| AC3 | La signature réutilise les évaluateurs existants. | `pytest -q tests/unit/domain/astrology/test_chart_signature.py` |
| AC4 | `json_builder.py` projette sans recalculer les scores. | `rg -n "element.*score\|dominant_sign" app/services/chart -g "*.py"` |
| AC5 | Les gardes maisons/aspects/frontière prediction restent vertes. | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` |

## Implementation Tasks

- Capturer le baseline chart actuel.
- Définir les contrats de signature.
- Implémenter le calculateur.
- Brancher la signature dans le flux natal ou chart.
- Ajouter tests, scans et baseline après.

## Files to Inspect First

- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/interpretation/dominant_aspects.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/services/chart/json_builder.py`

## Expected Files to Modify

- `backend/app/domain/astrology/runtime/chart_signature_runtime_data.py`
- `backend/app/domain/astrology/interpretation/chart_signature.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py` si projection publique additive.
- `backend/tests/unit/domain/astrology/test_chart_signature_runtime_data.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`

## Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_chart_signature_runtime_data.py tests/unit/domain/astrology/test_chart_signature.py
pytest -q tests/unit/domain/astrology/test_house_strength.py tests/unit/domain/astrology/test_dominant_aspects.py
pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_prediction_boundary.py
rg -n "ELEMENTS|MODALITIES|SIGN_WEIGHTS|app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
rg -n "element.*score|modality.*score|dominant_sign|dominant_planet" app/services/chart -g "*.py"
```
