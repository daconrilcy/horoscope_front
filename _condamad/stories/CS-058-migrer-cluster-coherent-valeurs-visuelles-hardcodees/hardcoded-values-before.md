# Hardcoded values before CS-058

Chosen cluster: prediction cards and adjacent prediction summary cards.
Files: `PeriodCard.css`, `KeyPointCard.css`, `CategoryGrid.css`, `DayPredictionCard.css`, `TurningPointCard.css`.

| File | Initial local values | Classification | Decision |
|---|---|---|---|
| `PeriodCard.css` | local radius/shadow/gap/font/fallback literals | design-system replaceable subset | migrate subset to existing tokens |
| `KeyPointCard.css` | radius, icon padding, font sizes, shadow fallback | design-system replaceable subset | migrate subset to existing tokens |
| `CategoryGrid.css` | no inline color classes yet | missing CSS ownership for dynamic visual tones | add finite modifier classes |
| `DayPredictionCard.css` | no tone background classes yet | missing CSS ownership for dynamic visual tones | add finite modifier classes |
| `TurningPointCard.css` | visual badge values coupled to TSX | CSS ownership missing | move finite badge classes to CSS |

No new token or typography role required; existing tokens/classes were sufficient for this bounded cluster.
