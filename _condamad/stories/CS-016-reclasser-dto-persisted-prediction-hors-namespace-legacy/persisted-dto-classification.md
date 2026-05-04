# Classification DTO persisted prediction

## Decision

Les DTO persisted prediction sont classes comme contrats purs partages par le domaine prediction et les adapters de persistence. Leur owner canonique est `backend/app/domain/prediction`.

## Types classes

| Type | Owner canonique | Classification | Justification | Surface non canonique |
|---|---|---|---|---|
| `PersistedPredictionSnapshot` | `app.domain.prediction.persisted_snapshot` | `domain-pure` | Snapshot typé consommé par services, projection publique, API et repositories sans dépendance SQLAlchemy. | `app.prediction.persisted_snapshot` |
| `PersistedCategoryScore` | `app.domain.prediction.persisted_snapshot` | `domain-pure` | Read model de score sérialisé sans ORM, nécessaire à la projection déterministe. | `app.prediction.persisted_snapshot` |
| `PersistedTurningPoint` | `app.domain.prediction.persisted_snapshot` | `domain-pure` | Read model de turning point sans ORM, utilisé hors infra DB. | `app.prediction.persisted_snapshot` |
| `PersistedTimeBlock` | `app.domain.prediction.persisted_snapshot` | `domain-pure` | Read model de bloc horaire sans ORM, utilisé hors infra DB. | `app.prediction.persisted_snapshot` |
| `PersistedRelativeScore` | `app.domain.prediction.persisted_relative_score` | `domain-pure` | Métriques relatives exploitées par le calcul et la projection, sans dépendance infra. | `app.prediction.persisted_relative_score` |
| `PersistedUserBaseline` | `app.domain.prediction.persisted_baseline` | `domain-pure` | Baseline typée retournée par le repository puis consommée par les services de scoring. | `app.prediction.persisted_baseline` |
| `V3Granularity` | `app.domain.prediction.persisted_baseline` | `domain-pure` | Enum de granularité métier partagé par calcul et persistance. | `app.prediction.persisted_baseline` |
| `CalibrationData` | `app.domain.prediction.context` | `domain-pure` | Contrat de calibration consommé par calibrateur, contexte chargé et repositories de référence. | `app.prediction.context` |

## No Legacy

- Aucun owner infra séparé n'est créé pour éviter deux DTO actifs.
- Aucun module `app.prediction.persisted_*` ou `app.prediction.context` n'est conservé comme shim.
- Les repositories DB importent directement les DTO depuis `app.domain.prediction`.
