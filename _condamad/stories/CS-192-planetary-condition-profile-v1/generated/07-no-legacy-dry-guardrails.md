<!-- Garde No Legacy / DRY pour CS-192. -->

# CS-192 No Legacy / DRY Guardrails

## Interdits

- Import DB/API/services/prediction depuis `backend/app/domain/astrology/condition/**`.
- Symboles ou textes LLM/prompt/interpretation dans la couche condition.
- Mappings locaux de poids conditionnels ou niveaux sous forme de registre
  concurrent.
- Table `astral_chart_planet_condition_profiles`.
- Recalcul dans `json_builder.py`.

## Preuves attendues

- Tests du service condition.
- Tests runtime repository et migration.
- Tests payload natal et chart JSON.
- Garde architecture RG-119.
- Scans zero-hit cibles documentes dans l'evidence.
