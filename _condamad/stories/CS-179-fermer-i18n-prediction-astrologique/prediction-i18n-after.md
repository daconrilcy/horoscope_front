# Prediction I18n After

## Scope

- Domain: `backend/app/domain/prediction`
- Captured after CS-179 implementation.

## Runtime ownership

| Responsibility | Runtime owner | Prediction behavior |
|---|---|---|
| Sign labels | `AstrologyTranslationResolver` through injected `PredictionAstroLabels` | `PublicAstroVocabulary.sign()` normalizes technical codes and delegates label resolution. |
| Planet labels | `AstrologyTranslationResolver` through injected `PredictionAstroLabels` | `PublicAstroVocabulary.planet()` normalizes runtime codes and delegates label resolution. |
| Aspect labels | `AstrologyTranslationResolver` through injected `PredictionAstroLabels` | `PublicAstroVocabulary.aspect()` delegates label resolution. |
| House labels | `AstrologyTranslationResolver` through injected `PredictionAstroLabels` | `PublicAstroVocabulary.house()` delegates label resolution. |
| Event kinds | Runtime event type | Prediction exposes technical event type instead of owning local FR effect labels. |
| Fixed stars | Non DB-backed proper-name display data | Prediction keeps technical proper names and longitudes, not DB-backed translation mappings. |
| Aspect tonality | Prediction display metadata, non DB-backed | `_ASPECT_TONES` is classified as the existing public tonality metadata, not an aspect name translation; guard coverage prevents new aspect mapping names beside this classified metadata. |

## After scans

| Command | Result | Classification |
|---|---|---|
| `rg -n "PLANET_NAMES_FR\|SIGN_NAMES_FR\|SIGN_LABELS_FR\|PLANET_CODE_LABELS" app/domain/prediction -g "*.py"` | zero active hits | PASS |
| `rg -n "ASPECT_LABELS\|HOUSE_SIGNIFICATIONS\|EFFECT_LABELS" app/domain/prediction -g "*.py"` | zero active hits | PASS |
| `rg -n "get_planet_name_fr\|get_sign_name_fr\|get_aspect_label\|get_effect_label" app/domain/prediction -g "*.py"` | zero active hits | PASS |
| `rg -n "AstrologyTranslationResolver\|astrology_translation_resolver\|LanguageModel\|from app\.services" app/domain/prediction -g "*.py"` | zero active hits | PASS |

## Guard evidence

- `backend/app/tests/unit/test_astrology_localization_guardrails.py` includes a prediction-specific guard for forbidden local label mappings.
- `RG-110` remains registered in `_condamad/stories/regression-guardrails.md`.

## Known residual in-domain work: none

No active DB-backed sign, planet, aspect, house or effect label mapping remains under `backend/app/domain/prediction`.
