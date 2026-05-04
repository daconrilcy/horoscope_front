# Threaded DB Baseline Before

## Etat initial

`backend/app/services/prediction/compute_runner.py` construit `ctx_loader` dans `run_with_timeout` avec une fermeture sur la session SQLAlchemy appelante:

```python
def ctx_loader(ref: str, rule: str, dt: date) -> object:
    return self.context_loader.load(db, ref, rule, dt)
```

Ce loader est injecte dans `EngineOrchestrator`, puis `orchestrator.run` est soumis a `ThreadPoolExecutor`.

## Risque

Si le calcul depasse le timeout, le worker peut continuer a utiliser le loader injecte. La session `db` appartient pourtant au thread appelant et ne doit pas etre consommee par un worker survivant.

## Invariant attendu apres correction

Le contexte prediction est soit precharge hors thread, soit charge par une session worker dediee. La session appelante ne doit plus etre capturee par le callable execute dans le worker.
