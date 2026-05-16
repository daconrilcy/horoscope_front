# Prediction I18n Before

## Scope

- Domain: `backend/app/domain/prediction`
- Captured before implementation work on CS-179.

## Baseline scan

| Command | Result |
|---|---|
| `rg -n "get_planet_name_fr|get_sign_name_fr|get_aspect_label|get_effect_label|HOUSE_SIGNIFICATIONS|ASPECT_TONALITY|get_fixed_star_name_fr|PLANET_CODE_LABELS|SIGN_LABELS_FR" backend/app/domain/prediction backend/tests/unit/prediction backend/app/tests/unit/test_astrology_localization_guardrails.py -g "*.py"` | Active hits in `public_astro_vocabulary.py`, `public_projection.py`, `public_astro_daily_events.py`, `astrologer_prompt_builder.py`. |

## Removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| Local planet labels in `public_astro_vocabulary.py` | mapping | historical-facade | Public projection, daily events, prompt builder | Injected labels from `AstrologyTranslationResolver` contract | replace-consumer | Direct imports found by scan | Labels may become technical when no contract is injected in unit-level direct use. |
| Local sign labels in `public_astro_vocabulary.py` | mapping | historical-facade | Public projection, daily events, prompt builder | Injected labels from `AstrologyTranslationResolver` contract | replace-consumer | Direct imports found by scan | Short sign aliases must normalize to canonical sign codes. |
| Local aspect labels in `public_astro_vocabulary.py` | mapping | historical-facade | Public projection, daily events | Injected labels from `AstrologyTranslationResolver` contract | replace-consumer | Direct imports found by scan | Aspect payload shape must stay stable. |
| Local house significations in `public_astro_vocabulary.py` | mapping | historical-facade | Astro foundation activated houses | Injected house labels plus existing public domain labels | replace-consumer | Direct import found by scan | House domain text may follow public domain labels instead of local house prose. |
| Local effect labels in `public_astro_vocabulary.py` | mapping | historical-facade | Astro foundation effect labels | Technical event type from runtime event | replace-consumer | Direct import found by scan | Display label becomes technical for non DB-backed event type. |
| Prompt builder planet and sign labels | mapping | historical-facade | Daily horoscope prompt context | Injected label contract | replace-consumer | Direct constants found by scan | Historical two-letter planet codes require canonical-code normalization. |

## Consumer list

- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/app/domain/prediction/astrologer_prompt_builder.py`

## Decision

- Full closure is implementable without user decision because DB-backed labels route through the existing resolver and non DB-backed event kinds can remain technical runtime codes.
