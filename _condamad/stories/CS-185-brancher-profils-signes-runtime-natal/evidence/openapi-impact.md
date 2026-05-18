# OpenAPI Impact - CS-185

## Resultat

Aucune route FastAPI, schema API explicite, serializer public ou client
frontend n'a ete modifie dans cette story.

## Details

- Les changements portent sur le chargement DB runtime et les dataclasses
  internes `SignReferenceData` / `SignRuntimeData`.
- Le payload public `ReferenceRepository.get_reference_data()` conserve
  `signs[]` sous forme `{code, name}`.
- Les profils enrichis sont injectes uniquement dans
  `AstrologyRuntimeReferenceRepository.load()` via un chargement runtime dedie.
- `backend/app/services/chart/json_builder.py` n'a pas ete modifie.
- Aucune projection publique additive de `chart_balance` ou `chart_signature`
  n'a ete ajoutee.
- Aucun type frontend n'a ete modifie.

Conclusion: pas de changement OpenAPI intentionnel pour CS-185.
