<!-- Synthese executive du recontrole CONDAMAD prediction. -->

# Executive Summary

Audit cible: `backend/app/prediction`

Conclusion: les stories de l'audit precedent sont bien mises en oeuvre. Les guards passent, les dependances infra interdites ne sont pas revenues sous `app.prediction`, la projection publique est redevenue deterministe, le bug `astro_foundation` est couvert, et la session DB du calcul threade est protegee par tests. Le dossier `backend/app/prediction` reste toutefois present et actif: il contient encore 39 fichiers Python et 16 templates.

Findings:

- High: 2
- Medium: 3
- Info: 1
- Story candidates: 5

Top risks:

1. `backend/app/prediction` reste une racine runtime, donc la suppression physique n'est pas encore possible.
2. Le moteur pur n'a pas encore ete migre sous `backend/app/domain/prediction`.
3. L'infra DB et l'API importent encore des DTO/projections depuis `app.prediction`.
4. Les tests et guards referencent encore l'ancien namespace; ils doivent etre migres avant une garde zero-hit.

Chemin recommande:

1. Migrer le moteur pur vers `domain/prediction`.
2. Reclasser les DTO persisted entre `domain` et `infra`.
3. Decoupler les routeurs API de `app.prediction`.
4. Migrer l'editorial/templates et `astrologer_prompt_builder` vers leurs owners service/LLM.
5. Remplacer l'allowlist anti-croissance par une garde d'extinction, puis supprimer le dossier.

Validation applicative executee:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py tests/unit/prediction/test_public_astro_foundation.py
```

Resultat: `40 passed`.
