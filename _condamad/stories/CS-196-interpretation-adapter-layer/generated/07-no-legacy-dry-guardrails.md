# CS-196 No Legacy / DRY Guardrails

- Les seuils et priorites proviennent des tables `astral_interpretation_*`.
- Le domaine ne lit pas SQLAlchemy et n'importe ni infra, ni services, ni API.
- Le serializer projette `NatalResult.interpretation_adapter` sans appeler le moteur.
- Aucun mapping local de signaux/themes/priorites dans `interpretation_adapters`.
- Aucun texte redige, LLM, persona, horoscope ou matching.
