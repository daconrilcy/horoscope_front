# Baseline apres CS-176

- `ChartBalanceRuntimeData` et `ChartSignatureRuntimeData` existent sous `domain/astrology/runtime`.
- `ChartSignatureCalculator` consomme `SignRuntimeData`, `HouseStrengthRuntimeData` et `AspectRuntimeData`.
- `NatalResult.chart_balance` est additif.
- `build_chart_json` projette `chart_balance` et `chart_signature` sans recalculer les scores.
