# Story 61.45 : Triage batch piloté des alertes ops

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux pouvoir appliquer en masse un handling `suppressed` ou `resolved` à un lot d'alertes filtrées,
afin de nettoyer rapidement le backlog des alertes connues, non actionnables ou déjà traitées, tout en conservant la traçabilité complète des décisions.

## Contexte

- **61.39** : alerting idempotent, table `canonical_entitlement_mutation_alert_events`
- **61.40** : retry unitaire, table `canonical_entitlement_mutation_alert_delivery_attempts`
- **61.41** : `GET /alerts` + `GET /alerts/summary` — visibilité ops de la file
- **61.42** : `POST /alerts/retry-batch` — retry en masse des alertes `failed`
- **61.43** : table mutable `canonical_entitlement_mutation_alert_event_handlings`, service `CanonicalEntitlementAlertHandlingService.upsert_handling()`, endpoint `POST /alerts/{alert_event_id}/handle`
- **61.44** : table append-only `canonical_entitlement_mutation_alert_event_handling_events`, historisation complète de chaque changement de handling, règle no-op dans `upsert_handling()`, `request_id` propagé
- **Gap** : on peut traiter une alerte unitairement (61.43) et tracer l'historique (61.44). Il manque la capacité de sortir un lot entier du backlog sans cliquer alerte par alerte. Le pendant batch du retry (61.42) n'existe pas côté triage.

**Décision architecturale :**
- Nouveau service `CanonicalEntitlementAlertBatchHandlingService.batch_handle()`
- Réutilise `CanonicalEntitlementAlertHandlingService.upsert_handling()` — logique no-op et historisation append-only 61.44 héritées automatiquement
- Pas de nouvelle table, pas de nouvelle migration
- Pattern identique à `CanonicalEntitlementAlertBatchRetryService` (61.42)
- **Périmètre** : le triage batch s'applique à toutes les alertes (`sent` compris), pas uniquement aux `failed`. Ce n'est pas un retry mais une qualification ops du backlog global — une alerte `sent` peut être supprimée si elle est reconnue comme non-actionnelle.

---

## Acceptance Criteria

### AC 1 — Service `CanonicalEntitlementAlertBatchHandlingService`

1. Nouveau fichier créé : `backend/app/services/canonical_entitlement_alert_batch_handling_service.py`
2. Dataclass `BatchHandleResult` avec champs :
   - `candidate_count: int`
   - `handled_count: int`
   - `skipped_count: int`
   - `dry_run: bool`
   - `alert_event_ids: list[int]` (IDs des candidats, indépendamment du skip)
3. Classe `CanonicalEntitlementAlertBatchHandlingService` avec méthode statique :
   ```python
   batch_handle(
       db: Session,
       *,
       limit: int,
       handling_status: str,        # "suppressed" | "resolved"
       ops_comment: str | None = None,
       suppression_key: str | None = None,
       dry_run: bool = False,
       request_id: str | None = None,
       handled_by_user_id: int | None = None,
       # filtres (identiques à batch_retry)
       alert_kind: str | None = None,
       audit_id: int | None = None,
       feature_code: str | None = None,
       plan_code: str | None = None,
       actor_type: str | None = None,
       request_id_filter: str | None = None,
       date_from: datetime | None = None,
       date_to: datetime | None = None,
   ) -> BatchHandleResult
   ```
4. Méthode helper privée `_load_batch_candidates(db, *, limit, alert_kind, audit_id, feature_code, plan_code, actor_type, request_id_filter, date_from, date_to)` :
   - Construit la requête sur `CanonicalEntitlementMutationAlertEventModel`
   - Applique les filtres (même logique que `CanonicalEntitlementAlertBatchRetryService._load_batch_candidates`)
   - **Pas de filtre sur `delivery_status`** — toutes les alertes sont candidates, y compris celles en `sent`. Le triage batch est une qualification ops du backlog global, pas un retry : une alerte `sent` peut tout à fait être supprimée si elle est connue non-actionnelle.
   - Ordre `model.id.asc()`, `LIMIT limit`
5. **Règle no-op batch** : avant d'appeler `upsert_handling()` pour un candidat, vérifier si un handling existant a déjà le même `handling_status`, `ops_comment` et `suppression_key` → si oui, incrémenter `skipped_count` sans appeler le service
6. **Mode `dry_run`** : charger les candidats, charger les handlings existants, calculer les no-ops exactement comme en mode normal, retourner les compteurs réels `handled_count` et `skipped_count` — sans appeler `upsert_handling()` ni écrire en DB. Le dry_run doit refléter fidèlement ce que ferait le run réel.
7. **Mode normal** : appeler `CanonicalEntitlementAlertHandlingService.upsert_handling()` pour chaque candidat non-skippé, accumuler `handled_count` / `skipped_count`. `upsert_handling()` appelle lui-même `db.flush()` en interne — pas de flush supplémentaire dans le service batch.
8. Pas de `db.commit()` dans le service — le commit est dans le router.
9. Pas d'import circulaire (le service n'importe pas le router)

### AC 2 — Endpoint `POST /v1/ops/entitlements/mutation-audits/alerts/handle-batch`

10. Ajouté dans `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
11. Rôle requis : `ops` ou `admin` (via `_ensure_ops_role()`)
12. Rate limit via `_enforce_limits()` avec l'opération `"batch_handle_alerts"`
13. Nouveau schéma Pydantic `BatchHandleRequestBody` :
    ```python
    class BatchHandleRequestBody(BaseModel):
        model_config = ConfigDict(populate_by_name=True)

        limit: int = Field(..., ge=1, le=200)
        handling_status: Literal["suppressed", "resolved"]
        dry_run: bool = False
        ops_comment: str | None = None
        suppression_key: str | None = None
        # filtres
        alert_kind: str | None = None
        audit_id: int | None = None
        feature_code: str | None = None
        plan_code: str | None = None
        actor_type: str | None = None
        request_id_filter: str | None = Field(default=None, alias="request_id")
        date_from: datetime | None = None
        date_to: datetime | None = None
    ```
14. Nouveau schéma Pydantic `BatchHandleResultData` :
    ```python
    class BatchHandleResultData(BaseModel):
        candidate_count: int
        handled_count: int
        skipped_count: int
        dry_run: bool
        alert_event_ids: list[int]
    ```
15. Nouveau schéma Pydantic `BatchHandleApiResponse(BaseModel)` : `data: BatchHandleResultData`, `meta: ResponseMeta`
16. L'endpoint appelle `CanonicalEntitlementAlertBatchHandlingService.batch_handle()` (import local dans la fonction, pattern identique à `batch_retry_alerts`)
17. `db.commit()` uniquement si `not body.dry_run`
18. Retourne HTTP 200
19. Réponse : `{"data": {...BatchHandleResultData...}, "meta": {"request_id": ...}}`

### AC 3 — Ordre des routes dans le router

20. Dans `ops_entitlement_mutation_audits.py`, l'endpoint est inséré dans cet ordre exact :
    1. `GET /mutation-audits/alerts/summary` (61.41)
    2. `GET /mutation-audits/alerts` (61.41)
    3. `POST /mutation-audits/alerts/retry-batch` (61.42)
    4. `POST /mutation-audits/alerts/handle-batch` ← **ajout 61.45** (DOIT être avant `{alert_event_id}/handle`)
    5. `POST /mutation-audits/alerts/{alert_event_id}/handle` (61.43)
    6. `GET /mutation-audits/alerts/{alert_event_id}/handling-history` (61.44)
    7. `GET /mutation-audits/alerts/{alert_event_id}/attempts` (61.40)
    8. `POST /mutation-audits/alerts/{alert_event_id}/retry` (61.40)

    **CRITIQUE** : FastAPI matche les routes dans l'ordre de déclaration. `handle-batch` est un path statique — il DOIT être déclaré AVANT `{alert_event_id}/handle` sinon FastAPI capturera `"handle-batch"` comme valeur de `alert_event_id` et tentera un cast en `int`, résultant en une erreur 422. Voir le même pattern : `retry-batch` déclaré avant `{alert_event_id}/retry`.

### AC 4 — Tests unitaires

21. Fichier créé : `backend/app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py`
22. Tests à implémenter :
    - `test_batch_handle_returns_correct_candidate_count` — candidats chargés et comptés
    - `test_batch_handle_dry_run_does_not_call_upsert` — dry_run : pas d'appel à `upsert_handling`, compteurs `handled_count`/`skipped_count` reflètent fidèlement l'état réel (no-op calculé, pas de DB write)
    - `test_batch_handle_calls_upsert_for_each_candidate` — mode normal, N candidats → N appels à `upsert_handling`
    - `test_batch_handle_skips_already_handled_with_same_state` — candidat avec handling identique → skippé, pas d'appel à `upsert_handling`
    - `test_batch_handle_processes_when_status_differs` — candidat avec handling différent → traité
    - `test_batch_handle_processes_when_comment_differs` — ops_comment différent → traité
    - `test_batch_handle_passes_request_id_to_upsert` — `request_id` propagé dans chaque appel à `upsert_handling`
    - `test_batch_handle_passes_handled_by_user_id` — `handled_by_user_id` propagé
    - `test_batch_handle_limit_is_respected` — limit=2 avec 5 candidats → 2 traités
    - `test_batch_handle_does_not_commit` — `db.commit()` non appelé dans le service (commit délégué au router)

### AC 5 — Tests d'intégration

23. Fichier créé : `backend/app/tests/integration/test_ops_alert_batch_handle_api.py`
24. Tests à implémenter :
    - `test_batch_handle_suppresses_failed_alerts` — POST handle-batch avec `handling_status=suppressed`, vérifie état dans DB
    - `test_batch_handle_resolves_failed_alerts` — idem avec `resolved`
    - `test_batch_handle_dry_run_does_not_persist` — dry_run=True, aucune ligne dans `handlings`
    - `test_batch_handle_skips_already_handled_same_state` — candidat déjà suppressed avec même comment/key → `skipped_count==1`, `handled_count==0`
    - `test_batch_handle_rehandles_when_state_changes` — candidat déjà suppressed, batch avec `resolved` → traité (nouveau handling + event d'historique)
    - `test_batch_handle_limit_is_respected` — 5 alertes disponibles, limit=2 → 2 traitées
    - `test_batch_handle_appends_history_events_for_each_handled` — après batch, table `handling_events` a N entrées (une par alerte traitée)
    - `test_batch_handle_no_history_event_on_skip` — skip → pas d'event dans `handling_events`
    - `test_batch_handle_requires_ops_role` — 403 si rôle user
    - `test_batch_handle_unauthenticated_returns_401` — 401 sans token
    - `test_batch_handle_returns_429_when_rate_limited` — 429 si rate limit
    - `test_batch_handle_filter_by_alert_kind` — filtre alert_kind restreint les candidats
    - `test_batch_handle_filter_by_feature_code` — filtre feature_code
    - `test_batch_handle_response_schema` — vérifie structure `data.candidate_count`, `data.handled_count`, `data.skipped_count`, `data.dry_run`, `data.alert_event_ids`
    - `test_batch_handle_returns_422_when_limit_missing` — 422 si `limit` absent du body
    - `test_batch_handle_returns_422_for_invalid_handling_status` — 422 si `handling_status` n'est pas `suppressed` ou `resolved`
    - `test_batch_retry_still_excludes_suppressed_after_61_45` — non-régression : batch_retry exclut toujours les suppressed

### AC 6 — Non-régression

25. Aucune modification des endpoints existants (61.39–61.44).
26. Interface HTTP de `POST /alerts/{alert_event_id}/handle` **inchangée**.
27. `CanonicalEntitlementAlertHandlingService` non modifié.
28. `CanonicalEntitlementAlertQueryService` non modifié.
29. `CanonicalEntitlementAlertBatchRetryService` non modifié.
30. Tests 61.40–61.44 restent verts.

### AC 7 — Documentation

31. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.45 — Triage batch des alertes"** : endpoint, body, résultat agrégé, règle no-op batch.
32. `backend/README.md` mis à jour avec mention de l'endpoint batch handle.

---

## Tasks / Subtasks

- [x] AC 1 — Service batch handling
  - [x] Créer `backend/app/services/canonical_entitlement_alert_batch_handling_service.py`
  - [x] Dataclass `BatchHandleResult` (candidate_count, handled_count, skipped_count, dry_run, alert_event_ids)
  - [x] Méthode `_load_batch_candidates()` sans filtre delivery_status
  - [x] Logique pre-check no-op : charger handlings existants pour tous les candidats, comparer 3 champs
  - [x] Méthode `batch_handle()` : no-op check partagé dry_run/normal, boucle upsert conditionnelle (`if not dry_run`), compteurs fidèles dans les deux modes

- [x] AC 2+3 — Endpoint + schémas dans le router
  - [x] Ajouter schémas `BatchHandleRequestBody`, `BatchHandleResultData`, `BatchHandleApiResponse` dans le router
  - [x] Ajouter endpoint `POST /mutation-audits/alerts/handle-batch` **avant** `{alert_event_id}/handle`
  - [x] Import local de `CanonicalEntitlementAlertBatchHandlingService` dans l'endpoint
  - [x] `db.commit()` uniquement si `not body.dry_run`
  - [x] Rate limit operation `"batch_handle_alerts"`

- [x] AC 4 — Tests unitaires
  - [x] Créer `backend/app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py` (10 tests)

- [x] AC 5 — Tests d'intégration
  - [x] Créer `backend/app/tests/integration/test_ops_alert_batch_handle_api.py` (17 tests)
  - [x] Importer les helpers depuis `test_ops_review_queue_alerts_retry_api.py`

- [x] AC 7 — Documentation
  - [x] Mettre à jour `backend/docs/entitlements-canonical-platform.md`
  - [x] Mettre à jour `backend/README.md`

---

## Dev Notes

### Architecture — fichiers concernés

```
# NOUVEAUX
backend/app/services/canonical_entitlement_alert_batch_handling_service.py
backend/app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py
backend/app/tests/integration/test_ops_alert_batch_handle_api.py

# MODIFIÉS
backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
  → +BatchHandleRequestBody, BatchHandleResultData, BatchHandleApiResponse (schémas)
  → +POST /mutation-audits/alerts/handle-batch (entre retry-batch et {alert_event_id}/handle)

backend/docs/entitlements-canonical-platform.md
backend/README.md

# PAS DE MIGRATION — pas de nouvelle table
```

### Modèle de service — structure exacte à reproduire

Reproduire **exactement** le pattern de `CanonicalEntitlementAlertBatchRetryService` :

```python
# backend/app/services/canonical_entitlement_alert_batch_handling_service.py
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
from app.services.canonical_entitlement_alert_handling_service import (
    CanonicalEntitlementAlertHandlingService,
)

logger = logging.getLogger(__name__)


@dataclass
class BatchHandleResult:
    candidate_count: int
    handled_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int] = field(default_factory=list)


class CanonicalEntitlementAlertBatchHandlingService:
    @staticmethod
    def batch_handle(
        db: Session,
        *,
        limit: int,
        handling_status: str,
        ops_comment: str | None = None,
        suppression_key: str | None = None,
        dry_run: bool = False,
        request_id: str | None = None,
        handled_by_user_id: int | None = None,
        alert_kind: str | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> BatchHandleResult:
        candidates = CanonicalEntitlementAlertBatchHandlingService._load_batch_candidates(
            db, limit=limit, alert_kind=alert_kind, audit_id=audit_id,
            feature_code=feature_code, plan_code=plan_code, actor_type=actor_type,
            request_id_filter=request_id_filter, date_from=date_from, date_to=date_to,
        )
        alert_event_ids = [event.id for event in candidates]
        candidate_count = len(candidates)

        # Pré-charger les handlings existants pour détecter les no-ops (1 requête IN)
        existing_handlings: dict[int, CanonicalEntitlementMutationAlertEventHandlingModel] = {}
        if alert_event_ids:
            result = db.execute(
                select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
                    CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id.in_(alert_event_ids)
                )
            )
            for h in result.scalars().all():
                existing_handlings[h.alert_event_id] = h

        handled_count = 0
        skipped_count = 0

        for event in candidates:
            existing = existing_handlings.get(event.id)
            is_noop = (
                existing is not None
                and existing.handling_status == handling_status
                and existing.ops_comment == ops_comment
                and existing.suppression_key == suppression_key
            )
            if is_noop:
                skipped_count += 1
                continue

            if not dry_run:
                CanonicalEntitlementAlertHandlingService.upsert_handling(
                    db,
                    alert_event_id=event.id,
                    handling_status=handling_status,
                    handled_by_user_id=handled_by_user_id,
                    ops_comment=ops_comment,
                    suppression_key=suppression_key,
                    request_id=request_id,
                )
            handled_count += 1

        return BatchHandleResult(
            candidate_count=candidate_count,
            handled_count=handled_count,
            skipped_count=skipped_count,
            dry_run=dry_run,
            alert_event_ids=alert_event_ids,
        )

    @staticmethod
    def _load_batch_candidates(
        db: Session,
        *,
        limit: int,
        alert_kind: str | None,
        audit_id: int | None,
        feature_code: str | None,
        plan_code: str | None,
        actor_type: str | None,
        request_id_filter: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[CanonicalEntitlementMutationAlertEventModel]:
        model = CanonicalEntitlementMutationAlertEventModel
        query = select(model)
        # PAS de filtre delivery_status — toutes les alertes sont candidates (contrairement à batch_retry)
        if alert_kind is not None:
            query = query.where(model.alert_kind == alert_kind)
        if audit_id is not None:
            query = query.where(model.audit_id == audit_id)
        if feature_code is not None:
            query = query.where(model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            query = query.where(model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            query = query.where(model.actor_type_snapshot == actor_type)
        if request_id_filter is not None:
            query = query.where(model.request_id == request_id_filter)
        if date_from is not None:
            query = query.where(model.created_at >= date_from)
        if date_to is not None:
            query = query.where(model.created_at <= date_to)
        query = query.order_by(model.id.asc()).limit(limit)
        return list(db.scalars(query).all())
```

### Endpoint dans le router — schémas et placement exact

**Schémas à ajouter** (après `BatchRetryApiResponse`, avant `AlertHandlingState`) :

```python
class BatchHandleRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., ge=1, le=200)
    handling_status: Literal["suppressed", "resolved"]
    dry_run: bool = False
    ops_comment: str | None = None
    suppression_key: str | None = None
    alert_kind: str | None = None
    audit_id: int | None = None
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    request_id_filter: str | None = Field(default=None, alias="request_id")
    date_from: datetime | None = None
    date_to: datetime | None = None


class BatchHandleResultData(BaseModel):
    candidate_count: int
    handled_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int]


class BatchHandleApiResponse(BaseModel):
    data: BatchHandleResultData
    meta: ResponseMeta
```

**Endpoint** :

```python
@router.post(
    "/mutation-audits/alerts/handle-batch",
    response_model=BatchHandleApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"description": "Validation error"},
        429: {"model": ErrorEnvelope},
    },
)
def batch_handle_alerts(
    body: BatchHandleRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_batch_handling_service import (
        CanonicalEntitlementAlertBatchHandlingService,
    )

    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="batch_handle_alerts",
        )
    ) is not None:
        return err

    result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
        db,
        limit=body.limit,
        handling_status=body.handling_status,
        ops_comment=body.ops_comment,
        suppression_key=body.suppression_key,
        dry_run=body.dry_run,
        request_id=request_id,
        handled_by_user_id=current_user.id,
        alert_kind=body.alert_kind,
        audit_id=body.audit_id,
        feature_code=body.feature_code,
        plan_code=body.plan_code,
        actor_type=body.actor_type,
        request_id_filter=body.request_id_filter,
        date_from=body.date_from,
        date_to=body.date_to,
    )

    if not body.dry_run:
        db.commit()

    return {
        "data": {
            "candidate_count": result.candidate_count,
            "handled_count": result.handled_count,
            "skipped_count": result.skipped_count,
            "dry_run": result.dry_run,
            "alert_event_ids": result.alert_event_ids,
        },
        "meta": {"request_id": request_id},
    }
```

**PLACEMENT DANS LE ROUTER** : insérer cet endpoint **après** le handler de `retry-batch` et **avant** le handler de `{alert_event_id}/handle` (ligne ~1207 du fichier actuel). La déclaration avant le path-param est obligatoire pour FastAPI.

### Pre-check no-op en batch — justification du pattern

Le pre-check avant la boucle (charger tous les handlings existants en une requête IN) est préféré à l'appel naïf à `upsert_handling()` pour chaque candidat car :
1. Réduit le nombre de requêtes SQL (1 IN vs N SELECT dans la boucle)
2. Permet de compter `skipped_count` avec précision — `upsert_handling()` retourne le record même en cas de no-op, sans indicateur de skip
3. Le comportement no-op de `upsert_handling()` (éviter INSERT d'event si rien ne change) reste la ligne de défense au niveau service ; le pre-check est une optimisation batch en amont

**Note** : comme `upsert_handling()` implémente lui-même la règle no-op depuis 61.44, les appels qui passeraient par erreur (race condition) ne créeraient pas de doublons dans l'historique.

### Tests unitaires — pattern de référence

Fichier de référence pour le pattern de tests unitaires du service :
`backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py`

- `Base.metadata.drop_all(bind=engine)` + `Base.metadata.create_all(bind=engine)` en setup
- `SessionLocal()` directement
- Mocker `CanonicalEntitlementAlertHandlingService.upsert_handling` pour tester le service batch isolément (vérifier combien de fois il est appelé, avec quels args)

### Tests d'intégration — helpers à importer

```python
from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
    _cleanup_tables,
    _register_user_with_role_and_token,
    _seed_alert_event,
    _seed_audit,
)
```

Pattern identique à `test_ops_alert_event_handle_api.py` (61.43) et `test_ops_alert_event_handling_history_api.py` (61.44).

Pour vérifier les events d'historique dans les tests d'intégration :
```python
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling_event import (
    CanonicalEntitlementMutationAlertEventHandlingEventModel,
)
# ...
with SessionLocal() as db:
    events = db.scalars(
        select(CanonicalEntitlementMutationAlertEventHandlingEventModel)
        .where(CanonicalEntitlementMutationAlertEventHandlingEventModel.alert_event_id == alert_event_id)
    ).all()
    assert len(events) == 1
```

### Différences clés avec `CanonicalEntitlementAlertBatchRetryService`

| Aspect | Batch Retry (61.42) | Batch Handle (61.45) |
|---|---|---|
| Filtre initial | `delivery_status == "failed"` | Aucun filtre sur `delivery_status` |
| Exclut | Alertes `suppressed`/`resolved` | Alertes déjà dans l'état cible (no-op check) |
| Action | `_deliver_webhook()` + `attempt` INSERT | `upsert_handling()` → `handlings` upsert + `handling_events` INSERT |
| Résultat | `retried_count`, `sent_count`, `failed_count` | `handled_count`, `skipped_count` |
| Compteurs dry_run | `retried_count = candidate_count` | compteurs réels calculés (`handled_count` + `skipped_count` corrects), sans écriture DB |
| `limit` max | 100 | 200 (triage plus volumineux) |

### Convention de nommage

| Élément | Nom |
|---|---|
| Fichier service | `canonical_entitlement_alert_batch_handling_service.py` |
| Classe service | `CanonicalEntitlementAlertBatchHandlingService` |
| Méthode principale | `batch_handle()` |
| Dataclass résultat | `BatchHandleResult` |
| Schéma body | `BatchHandleRequestBody` |
| Schéma résultat | `BatchHandleResultData` |
| Schéma réponse | `BatchHandleApiResponse` |
| Opération rate limit | `"batch_handle_alerts"` |
| URL endpoint | `/mutation-audits/alerts/handle-batch` |

### Références

- [Source: service batch retry — pattern à reproduire] `backend/app/services/canonical_entitlement_alert_batch_retry_service.py`
- [Source: service handling — méthode `upsert_handling()` à réutiliser] `backend/app/services/canonical_entitlement_alert_handling_service.py`
- [Source: router — schémas et endpoints alerts, placement] `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` (lignes ~233–274 pour schémas batch retry, ligne ~1144 pour placement)
- [Source: tests intégration 61.43 — pattern helpers] `backend/app/tests/integration/test_ops_alert_event_handle_api.py`
- [Source: tests unitaires 61.43] `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py`
- [Source: modèle alerte] `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py`
- [Source: modèle handling mutable] `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling.py`
- [Source: modèle handling events append-only] `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling_event.py`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py app/tests/integration/test_ops_alert_batch_handle_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/api/v1/routers/ops_entitlement_mutation_audits.py app/services/canonical_entitlement_alert_batch_handling_service.py app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py app/tests/integration/test_ops_alert_batch_handle_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/api/v1/routers/ops_entitlement_mutation_audits.py app/services/canonical_entitlement_alert_batch_handling_service.py app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py app/tests/integration/test_ops_alert_batch_handle_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py app/tests/unit/test_canonical_entitlement_alert_handling_service.py app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py app/tests/integration/test_ops_review_queue_alerts_retry_api.py app/tests/integration/test_ops_alert_event_handle_api.py app/tests/integration/test_ops_alert_event_handling_history_api.py app/tests/integration/test_ops_alert_batch_handle_api.py`

### Completion Notes List

- Implémentation du service `CanonicalEntitlementAlertBatchHandlingService` avec préchargement des handlings existants, règle no-op batch et support `dry_run` fidèle sans écriture.
- Ajout de l'endpoint `POST /v1/ops/entitlements/mutation-audits/alerts/handle-batch` avec schémas Pydantic dédiés, rate limit `batch_handle_alerts` et placement avant `/{alert_event_id}/handle`.
- Ajout des suites de tests unitaires et d'intégration couvrant le batch handling, les skips no-op, l'historisation append-only et la non-régression sur `retry-batch`.
- Documentation backend mise à jour pour l'endpoint batch handle, son body, sa réponse agrégée et la règle no-op batch.
- Double revue `bmad-code-review` effectuée après implémentation; aucun écart fonctionnel restant vis-à-vis du cahier des charges de la story.

### File List

- _bmad-output/implementation-artifacts/61-45-triage-batch-pilote-alertes-ops.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/services/canonical_entitlement_alert_batch_handling_service.py
- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/tests/unit/test_canonical_entitlement_alert_batch_handling_service.py
- backend/app/tests/integration/test_ops_alert_batch_handle_api.py
- backend/docs/entitlements-canonical-platform.md
- backend/README.md

### Change Log

- 2026-03-29: Implémentation initiale de la story 61.45 (service batch handle, endpoint API, tests unitaires/intégration, documentation).
- 2026-03-29: Double passage de revue adversariale et clôture de la story en `done`.
