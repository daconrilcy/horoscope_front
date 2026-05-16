# Story CS-178 documenter-zodiaque-ayanamsa-runtime: Documenter le contrat tropical sidereal ayanamsa du runtime natal

Status: done

## Objective

Créer une documentation technique canonique pour le contrat entre
`sign_from_longitude`, le choix tropical/sidéral, l'ayanamsa et le flux natal.
La doc doit expliciter que `sign_from_longitude` mappe une longitude déjà
calculée par tranches de 30 degrés. Le zodiaque et l'ayanamsa sont appliqués en
amont.

## Domain Boundary

Domain: `backend/docs`.

In scope:

- Ajouter ou mettre à jour une page de documentation backend canonique sur le contrat zodiacal.
- Citer les fichiers de code propriétaires et tests de preuve.
- Ajouter une garde documentaire si les tests docs existants la permettent.
- Mettre à jour les références README/docs uniquement si le registre docs l'exige.

Out of scope:

- Modifier les calculs `sign_from_longitude`, `calculate_planets` ou `NatalCalculationService`.
- Modifier OpenAPI ou les routes API.
- Ajouter un nouveau mode zodiacal.
- Modifier le frontend.

Explicit non-goals:

- Ne pas introduire de helper concurrent pour calculer les signes.
- Ne pas changer le fallback d'ayanamsa.
- Ne pas déplacer la logique sidérale hors `ephemeris_provider.py`.
- Ne pas changer les invariants `RG-092`, `RG-106`, `RG-107` et `RG-108`.

## Required Contracts

- Runtime source of truth: `zodiac.py`, `ephemeris_provider.py`, `calculation_service.py` et tests existants.
- Baseline before: `_condamad/stories/CS-178-documenter-zodiaque-ayanamsa-runtime/zodiac-doc-before.md`.
- Baseline after: `_condamad/stories/CS-178-documenter-zodiaque-ayanamsa-runtime/zodiac-doc-after.md`.
- Canonical doc: `backend/docs/astrology-zodiac-runtime-contract.md`.

## Regression Guardrails

Applicable:

- `RG-092` - référentiels structurels non recréés.
- `RG-106` - calculateurs astrology branchés sur les sources canoniques.
- `RG-107` - pas de payload libre ou fallback implicite dans le flux natal.
- `RG-108` - pas de vocabulaire métier local concurrent.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La doc explique le flux service vers provider vers longitude vers signe. | `rg -n "ephemeris_provider" backend/docs/astrology-zodiac-runtime-contract.md` |
| AC2 | La doc dit que `sign_from_longitude` n'applique pas l'ayanamsa. | `rg -n "n'applique pas l'ayanamsa" backend/docs/astrology-zodiac-runtime-contract.md` |
| AC3 | Les tests tropical/sidéral/ayanamsa sont cités avec commandes exactes. | `pytest -q tests/unit/domain/astrology/test_zodiac.py` |
| AC4 | Aucun helper concurrent longitude vers signe ou ayanamsa n'est ajouté. | `rg -n "ZODIAC_SIGNS\|ayanamsa.*sign_from_longitude" app/domain/astrology` |

## Implementation Tasks

- Identifier l'emplacement canonique de documentation.
- Rédiger le contrat zodiacal.
- Ajouter les preuves et commandes.
- Vérifier l'absence de duplication.

## Files to Inspect First

- `backend/app/domain/astrology/zodiac.py`
- `backend/app/domain/astrology/ephemeris_provider.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/tests/unit/test_ephemeris_provider.py`
- `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py`
- `backend/tests/unit/domain/astrology/test_zodiac.py`
- `backend/docs/ownership-index.md`

## Expected Files to Modify

- `backend/docs/astrology-zodiac-runtime-contract.md`
- `backend/docs/ownership-index.md` si requis par les guards docs.

## Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_zodiac.py app/tests/unit/test_ephemeris_provider.py
pytest -q app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_calculation_service.py
pytest -q app/tests/unit/test_backend_docs_ownership.py
rg -n "def .*sign.*longitude|ZODIAC_SIGNS|ayanamsa.*sign_from_longitude|set_sid_mode" app/domain/astrology app/services/natal -g "*.py"
```
