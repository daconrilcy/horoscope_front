# Guard before - CS-018

## Baseline source

Historical baseline for the guard replaced by this story:

- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`

## Baseline behavior

CS-012 used a persistent allowlist to classify the then-existing Python files
under `backend/app/prediction`. That guard was an anti-growth guard: it could
detect new unclassified files but did not prove namespace extinction.

## Historical allowed files

The CS-012 artifact listed the former `backend/app/prediction/*.py` inventory,
including the root package, engine modules, public projection modules,
persistence DTOs and schema modules.

## Replacement requirement

CS-018 replaces that model with a final invariant:

- `backend/app/prediction` must not exist.
- `app.prediction` must not be imported by runtime code or collected tests.
- The CS-012 allowlist remains historical evidence only.
