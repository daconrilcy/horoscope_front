# Threaded DB Evidence After

## Correction appliquee

`PredictionComputeRunner.run_with_timeout` charge maintenant le contexte prediction avant de soumettre `orchestrator.run` au `ThreadPoolExecutor`.

Le worker recoit un `ctx_loader` pur qui:

- compare la demande moteur au triplet precharge `(reference_version, ruleset_version, local_date)`;
- retourne le contexte precharge;
- ne reference pas `db`.

## Timeout

Le timeout conserve l'erreur controlee:

```python
DailyPredictionServiceError(
    "timeout",
    "Calcul trop long — service temporairement dégradé",
)
```

Le shutdown de l'executor utilise `wait=False` afin que le chemin timeout rende la main sans attendre la fin du worker.

## Preuve runtime et garde anti-retour

`backend/app/tests/unit/test_prediction_compute_runner.py` couvre:

- le chargement du contexte dans le thread appelant;
- la restitution du contexte precharge dans le worker;
- l'absence d'appel `db.expire_all()` au timeout;
- une garde AST qui echoue si `ctx_loader` reference de nouveau `db`.
