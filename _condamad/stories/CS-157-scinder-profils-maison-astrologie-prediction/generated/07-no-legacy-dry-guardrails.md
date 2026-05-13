# No Legacy / DRY Guardrails

- `HouseProfileData` must not remain active.
- No alias `HouseProfileData = HousePredictionProfile`.
- Product fields stay in prediction DTOs; astrology profile carries stable house facts only.
