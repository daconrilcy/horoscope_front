# Story CS-177 finaliser-i18n-astrologique-backend: Finaliser la localisation backend des libelles astrologiques

Status: done

## Objective

Étendre la localisation backend au-delà des seuls signes. La story supprime les
libellés FR codés en dur pour planètes, aspects, phases lunaires et export PDF
ciblé, puis conserve un seul resolver durable.

## Domain Boundary

Domain: `backend/app/services/reference_data`.

In scope:

- Étendre `AstrologyLabels` aux familles de labels consommées.
- Remplacer les constantes FR ciblées dans les services backend consommateurs.
- Traiter explicitement l'exception PDF `SIGN_LABELS`.
- Ajouter des tests de localisation et des scans anti-retour.

Out of scope:

- Traduire ou réécrire les contenus éditoriaux longs.
- Modifier les calculs astrologiques purs.
- Modifier les bundles i18n frontend.
- Ajouter une nouvelle langue non seedée.

Explicit non-goals:

- Ne pas introduire de resolver dans `backend/app/domain/astrology`.
- Ne pas créer de fallback de langue différent par consommateur.
- Ne pas conserver `PLANET_NAMES_FR`, `ASPECT_NAMES_FR`, `SIGN_LABELS` comme sources nominales sur les surfaces corrigées.
- Ne pas changer les invariants `RG-108` et `RG-109`.

## Required Contracts

- Runtime source of truth: tables `languages`, `astral_sign_translations`, `astral_planet_translations`, `astral_aspect_translations`, `astral_house_translations`.
- Baseline before: `_condamad/stories/CS-177-finaliser-i18n-astrologique-backend/i18n-backend-before.md`.
- Baseline after: `_condamad/stories/CS-177-finaliser-i18n-astrologique-backend/i18n-backend-after.md`.
- Reintroduction guard: `test_astrology_localization_guardrails.py` et scans des symboles interdits.

## Contract Shape

`AstrologyLabels` doit exposer:

- `sign_labels: dict[str, str]`
- `planet_labels: dict[str, str]`
- `aspect_labels: dict[str, str]`
- `house_labels: dict[str, str]`
- `effective_language_code: str`

## Regression Guardrails

Applicable:

- `RG-108` - les vocabulaires métier DB-backed ne sont pas recréés localement.
- `RG-109` - les labels de signes passent par le resolver canonique.
- `RG-107` - les contrats runtime astrology ne portent pas de dicts libres de traduction.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le resolver couvre les familles DB ciblées. | `pytest -q app/tests/unit/test_astrology_translation_resolver.py` |
| AC2 | Les mappings FR ciblés disparaissent. | `rg -n "PLANET_NAMES_FR\|ASPECT_NAMES_FR" app/services/chart app/services/llm_generation` |
| AC3 | `astro_context_builder.py` consomme des labels localisés ou a un owner exact. | `pytest -q app/tests/unit/test_astro_context_builder.py` |
| AC4 | L'exception PDF `SIGN_LABELS` est supprimée ou bloquée par décision. | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` |
| AC5 | `app/domain/astrology` reste sans dépendance traduction. | `rg -n "AstrologyTranslationResolver\|LanguageModel" app/domain/astrology` |

## Implementation Tasks

- Capturer l'inventaire i18n backend.
- Étendre le resolver canonique.
- Migrer les consommateurs ciblés chart, natal context et astro context.
- Supprimer ou bloquer explicitement le PDF `SIGN_LABELS`.
- Valider et écrire l'après.

## Files to Inspect First

- `backend/app/services/reference_data/astrology_translation_resolver.py`
- `backend/app/services/reference_data/translation_seed_service.py`
- `backend/app/infra/db/models/translation_reference.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/natal/astro_context_builder.py`
- `backend/app/services/natal/pdf_export_service.py`
- `backend/app/tests/unit/test_astrology_translation_resolver.py`

## Expected Files to Modify

- `backend/app/services/reference_data/astrology_translation_resolver.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/shared/natal_context.py`
- `backend/app/services/natal/astro_context_builder.py`
- `backend/app/services/natal/pdf_export_service.py`
- Tests unitaires associés.

## Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py
pytest -q app/tests/unit/test_natal_context_localization.py app/tests/unit/test_astro_context_builder.py
pytest -q app/tests/unit/test_astrology_localization_guardrails.py
rg -n "PLANET_NAMES_FR|ASPECT_NAMES_FR|SIGN_LABELS|SIGN_NAMES_FR|\bSIGNS\s*=\s*\[" app/services app/domain/astrology -g "*.py"
rg -n "AstrologyTranslationResolver|translation_reference|LanguageModel" app/domain/astrology -g "*.py"
```
