# Story CS-175 creer-runtime-canonique-signes: Creer le runtime canonique des signes du theme natal

Status: done

## Objective

Créer un contrat `SignRuntimeData` dans `backend/app/domain/astrology/runtime`.
Il porte les faits calculés d'un signe natal: occupants, poids, dominance,
dignités actives et rôle de synthèse. Le runtime signe reste astrologique pur,
réutilisable par les services chart et futurs calculateurs de signature.

## Domain Boundary

Domain: `backend/app/domain/astrology/runtime`.

In scope:

- Ajouter les dataclasses runtime de signe sous `domain/astrology/runtime`.
- Ajouter un builder domaine qui agrège les placements natals par signe.
- Exposer le runtime signe depuis `NatalResult` ou son flux canonique.
- Ajouter des tests unitaires domaine pour le contrat et le builder.

Out of scope:

- Calculer la signature globale du thème.
- Modifier les prompts LLM, la prédiction ou le frontend.
- Ajouter une nouvelle table DB ou un nouveau seed.

Explicit non-goals:

- Ne pas modifier l'ordre zodiacal de `zodiac.py`.
- Ne pas créer de mapping local concurrent de signes, planètes ou dignités.
- Ne pas importer `app.domain.prediction`, `app.services.prediction` ou `app.api` depuis `domain/astrology`.
- Ne pas changer les invariants `RG-095`, `RG-107`, `RG-108` et `RG-109`.

## Required Contracts

- Runtime source of truth: placements natals, `AstrologyRuntimeReference.signs`, `DignityReferenceSet` et `sign_from_longitude`.
- Baseline: `_condamad/stories/CS-175-creer-runtime-canonique-signes/baseline-natal-runtime-before.md`.
- After evidence: `_condamad/stories/CS-175-creer-runtime-canonique-signes/baseline-natal-runtime-after.md`.
- Allowed difference: ajout d'une surface runtime `signs_runtime` ou équivalent canonique documenté.

## Contract Shape

`SignRuntimeData` doit exposer:

- `sign: str`
- `occupants: tuple[SignOccupantRuntimeData, ...]`
- `weight: float`
- `dominant: bool`
- `active_dignities: tuple[SignDignityRuntimeData, ...]`
- `synthesis_role: str | None`
- `reasons: tuple[SignDominanceReason, ...]`

## Regression Guardrails

Applicable:

- `RG-095` - le domaine astrology ne dépend pas de prediction.
- `RG-107` - les données métier astrology ne traversent pas comme `dict` libres.
- `RG-108` - les vocabulaires DB-backed ne sont pas recréés localement.
- `RG-109` - les labels de signes restent hors runtime pur.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `SignRuntimeData` expose le shape complet attendu. | `pytest -q tests/unit/domain/astrology/test_sign_runtime_data.py` |
| AC2 | Le builder produit douze signes ordonnés sans constante locale. | `pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py` |
| AC3 | Les dignités actives viennent de `DignityReferenceSet`. | `rg -n "SIGN_DIGNIT\|DIGNITIES_BY_SIGN" app/domain/astrology` |
| AC4 | Le flux natal reste compatible. | `pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_calculation_service.py` |
| AC5 | La frontière `domain/astrology` vers prediction reste fermée. | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` |

## Implementation Tasks

- Capturer le baseline runtime natal.
- Ajouter `sign_runtime_data.py` et les exports runtime.
- Ajouter `sign_runtime_builder.py`.
- Brancher le flux natal sans casser le JSON public.
- Exécuter tests, scans et produire le baseline après.

## Files to Inspect First

- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/services/chart/json_builder.py`

## Expected Files to Modify

- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`

## Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_sign_runtime_data.py tests/unit/domain/astrology/test_sign_runtime_builder.py
pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_astrology_prediction_boundary.py
rg -n "SIGNS\s*=\s*\[|SIGN_NAMES_FR|app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
```
