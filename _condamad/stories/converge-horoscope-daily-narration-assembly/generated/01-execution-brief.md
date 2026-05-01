# Execution Brief - converge-horoscope-daily-narration-assembly

## Primary objective

Move durable horoscope daily narration instructions out of
`AstrologerPromptBuilder` and into the governed `horoscope_daily/narration`
assembly path.

## Boundaries

- Keep `AstrologerPromptBuilder` as a daily context payload builder only.
- Put durable output, style, length, and anti-generic instructions in assembly
  owned surfaces.
- Preserve `daily_synthesis` post-gateway sentence validation in
  `horoscope_daily/narration_service.py`.
- Do not modify public horoscope daily JSON contracts.
- Do not add narrative logic to `AIEngineAdapter`.

## Done when

- AC1 through AC4 have code and validation evidence.
- Prompt builder before/after artifacts exist.
- Reintroduction guards fail on forbidden builder/adaptor markers.
- Targeted tests, lint, format, story validation, and negative scans are
  recorded in `10-final-evidence.md`.
