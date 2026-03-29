# Story 61.41 : Exposition ops de la file des alertes canoniques et pilotage du retry

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux consulter une liste paginée et filtrable des `canonical_entitlement_mutation_alert_events` avec leur dernier état de delivery et leurs tentatives associées,
afin d'identifier rapidement les alertes en échec, de comprendre leur historique de delivery, et de déclencher un retry ciblé sans passer par SQL.

## Contexte

- **61.39** : alerting idempotent, persistance dans `canonical_entitlement_mutation_alert_events` (table `alert_events`)
- **61.40** : table `canonical_entitlement_mutation_alert_delivery_attempts`, service de retry, endpoints `GET .../alerts/{id}/attempts` et `POST .../alerts/{id}/retry`
- **Gap** : il n'existe aucun endpoint pour lister les alert_events, filtrer par `delivery_status`, identifier les IDs retryables, ou obtenir un résumé de santé de l'alerting sans SQL

## Acceptance Criteria

### AC 1 — Endpoint liste `GET /v1/ops/entitlements/mutation-audits/alerts`

1. Endpoint `GET /mutation-audits/alerts` ajouté dans `ops_entitlement_mutation_audits.py`.
2. Rôle requis : `ops` ou `admin` (via `_ensure_ops_role()`).
3. Rate limit via `_enforce_limits()` avec l'opération `"list_alert_events"` ; retourne 429 si dépassé.
4. Filtres query params acceptés :
   - `alert_kind: str | None = None`
   - `delivery_status: Literal["sent", "failed"] | None = None` — valeurs invalides → 422 natif FastAPI
   - `audit_id: int | None = None`
   - `feature_code: str | None = None`
   - `plan_code: str | None = None`
   - `actor_type: str | None = None`
   - `request_id: str | None = None` (alias interne `request_id_filter` pour éviter conflit avec la variable `request_id` FastAPI)
   - `date_from: datetime | None = None`
   - `date_to: datetime | None = None`
5. Pagination : `page` (défaut 1, ≥ 1), `page_size` (défaut 20, ≥ 1, ≤ 100).
6. Tri fixe : `created_at DESC, id DESC`.
7. Chaque item expose :
   - Tous les champs de `CanonicalEntitlementMutationAlertEventModel` : `id`, `audit_id`, `dedupe_key`, `alert_kind`, `delivery_status`, `delivery_channel`, `delivery_error`, `created_at`, `delivered_at`, `feature_code_snapshot`, `plan_id_snapshot`, `plan_code_snapshot`, `risk_level_snapshot`, `effective_review_status_snapshot`, `actor_type_snapshot`, `actor_identifier_snapshot`, `age_seconds_snapshot`, `sla_target_seconds_snapshot`, `due_at_snapshot`, `request_id`
   - Champs **dérivés** : `attempt_count` (int), `last_attempt_number` (int | None), `last_attempt_status` (str | None), `retryable` (bool)
8. `retryable = (delivery_status == "failed")`.
8b. `attempt_count` compte uniquement les lignes présentes dans `canonical_entitlement_mutation_alert_delivery_attempts`. Un alert event peut donc avoir `delivery_status="failed"` ou `"sent"` avec `attempt_count=0` si aucune tentative historisée n'existe encore (ex. event initial 61.39 sans retry 61.40 déclenché).
9. Réponse : `{ data: { items: [...], total_count: int, page: int, page_size: int }, meta: { request_id } }`.
10. Endpoint strictement **read-only**, aucune écriture DB.

### AC 2 — Endpoint résumé `GET /v1/ops/entitlements/mutation-audits/alerts/summary`

11. Endpoint `GET /mutation-audits/alerts/summary` ajouté dans `ops_entitlement_mutation_audits.py`.
12. Enregistré avant tout endpoint capturant `{alert_event_id}` dans l'ordre de déclaration du router.
13. Rôle requis : `ops` ou `admin`.
14. Rate limit via `_enforce_limits()` avec l'opération `"alert_events_summary"` ; retourne 429 si dépassé.
15. Accepte les **mêmes filtres SQL que l'endpoint liste**, sauf `page` et `page_size` :
    `alert_kind`, `delivery_status`, `audit_id`, `feature_code`, `plan_code`, `actor_type`, `request_id`, `date_from`, `date_to`.
16. Les compteurs sont calculés sur l'**ensemble filtré** via SQL aggregates en une seule requête :
    - `total_count` : count(*)
    - `failed_count` : count where `delivery_status == "failed"`
    - `sent_count` : count where `delivery_status == "sent"`
    - `retryable_count` : strictement égal à `failed_count` (retryable ⟺ failed)
    - `webhook_failed_count` : count where `delivery_channel == "webhook" AND delivery_status == "failed"`
    - `log_sent_count` : count where `delivery_channel == "log" AND delivery_status == "sent"`
17. Réponse : `{ data: { total_count, failed_count, sent_count, retryable_count, webhook_failed_count, log_sent_count }, meta: { request_id } }`.
18. Endpoint strictement **read-only**, aucune écriture DB.

### AC 3 — Service `CanonicalEntitlementAlertQueryService`

18. `backend/app/services/canonical_entitlement_alert_query_service.py` créé.
19. Interface publique :
    ```python
    @staticmethod
    def list_alert_events(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        alert_kind: str | None = None,
        delivery_status: Literal["sent", "failed"] | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[AlertEventRow], int]: ...

    @staticmethod
    def get_summary(
        db: Session,
        *,
        alert_kind: str | None = None,
        delivery_status: Literal["sent", "failed"] | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AlertSummaryResult: ...
    ```
20. `AlertEventRow` est un dataclass avec les champs : `event` (`CanonicalEntitlementMutationAlertEventModel`), `attempt_count` (int), `last_attempt_number` (int | None), `last_attempt_status` (str | None).
21. `AlertSummaryResult` est un dataclass avec les champs : `total_count`, `failed_count`, `sent_count`, `retryable_count`, `webhook_failed_count`, `log_sent_count` (tous int).
22. `list_alert_events` utilise **deux requêtes** :
    - Requête 1 : filtre + compte total + pagination sur `CanonicalEntitlementMutationAlertEventModel`, tri `created_at DESC, id DESC`
    - Requête 2 : `SELECT alert_event_id, attempt_number, delivery_status FROM canonical_entitlement_mutation_alert_delivery_attempts WHERE alert_event_id IN (ids_de_la_page)` — groupement Python côté service pour calculer `attempt_count`, `last_attempt_number`, `last_attempt_status`
22b. `last_attempt_number` et `last_attempt_status` sont dérivés de la tentative ayant le plus grand `attempt_number` parmi les attempts de cet event (pas "la dernière ligne insérée").
23. `get_summary` exécute une seule requête SQL avec `func.count` + `case` sur l'ensemble filtré pour tous les compteurs.
24. Pas de `db.commit()` ni `db.flush()` dans le service.
25. Pattern identique à `CanonicalEntitlementMutationAuditQueryService` pour la structure générale.

### AC 4 — Schémas Pydantic

26. Les schémas suivants ajoutés dans `ops_entitlement_mutation_audits.py` :

    ```python
    class AlertEventItem(BaseModel):
        id: int
        audit_id: int
        dedupe_key: str
        alert_kind: str
        delivery_status: str
        delivery_channel: str
        delivery_error: str | None = None
        created_at: datetime
        delivered_at: datetime | None = None
        feature_code_snapshot: str
        plan_id_snapshot: int
        plan_code_snapshot: str
        risk_level_snapshot: str
        effective_review_status_snapshot: str | None = None
        actor_type_snapshot: str
        actor_identifier_snapshot: str
        age_seconds_snapshot: int
        sla_target_seconds_snapshot: int | None = None
        due_at_snapshot: datetime | None = None
        request_id: str | None = None
        # Champs dérivés
        attempt_count: int
        last_attempt_number: int | None = None
        last_attempt_status: str | None = None
        retryable: bool

    class AlertEventListData(BaseModel):
        items: list[AlertEventItem]
        total_count: int
        page: int
        page_size: int

    class AlertEventListApiResponse(BaseModel):
        data: AlertEventListData
        meta: ResponseMeta

    class AlertSummaryData(BaseModel):
        total_count: int
        failed_count: int
        sent_count: int
        retryable_count: int
        webhook_failed_count: int
        log_sent_count: int

    class AlertSummaryApiResponse(BaseModel):
        data: AlertSummaryData
        meta: ResponseMeta
    ```

### AC 5 — Ordre critique des routes dans le router

27. Dans `ops_entitlement_mutation_audits.py`, les endpoints 61.41 sont déclarés dans cet ordre :
    1. `GET /mutation-audits/alerts/summary`
    2. `GET /mutation-audits/alerts`
    3. Puis les endpoints 61.40 existants :
       - `GET /mutation-audits/alerts/{alert_event_id}/attempts`
       - `POST /mutation-audits/alerts/{alert_event_id}/retry`
28. Aucun endpoint `GET /mutation-audits/alerts/{alert_event_id}` (detail) n'est ajouté dans cette story.

### AC 6 — Tests unitaires

28. `backend/app/tests/unit/test_canonical_entitlement_alert_query_service.py` créé avec :
    - `test_list_alert_events_empty`
    - `test_list_alert_events_returns_items_with_derived_fields`
    - `test_list_alert_events_filter_by_delivery_status`
    - `test_list_alert_events_filter_by_alert_kind`
    - `test_list_alert_events_filter_by_feature_code`
    - `test_list_alert_events_computes_attempt_count_correctly`
    - `test_list_alert_events_computes_retryable_true_for_failed`
    - `test_list_alert_events_computes_retryable_false_for_sent`
    - `test_get_summary_counts_correctly`

### AC 7 — Tests d'intégration

29. `backend/app/tests/integration/test_ops_alert_events_list_api.py` créé avec :
    - `test_get_alerts_list_empty`
    - `test_get_alerts_list_returns_items_with_derived_fields`
    - `test_get_alerts_list_filter_by_delivery_status_failed`
    - `test_get_alerts_list_filter_by_audit_id`
    - `test_get_alerts_list_filter_by_feature_code`
    - `test_get_alerts_list_pagination`
    - `test_get_alerts_list_requires_ops_role`
    - `test_get_alerts_list_returns_429_when_rate_limited`
    - `test_get_alerts_summary_empty`
    - `test_get_alerts_summary_counts_correctly`
    - `test_get_alerts_summary_requires_ops_role`
30. Les tests 61.39 et 61.40 restent verts (non-régression).

### AC 8 — Non-régression

31. Aucun contrat HTTP des endpoints 61.37–61.40 modifié.
31b. Les endpoints 61.40 `GET /alerts/{alert_event_id}/attempts` et `POST /alerts/{alert_event_id}/retry` conservent strictement leur contrat HTTP (chemin, body, codes de retour, schémas de réponse).
32. Aucune migration Alembic créée.
33. `CanonicalEntitlementAlertService` et `CanonicalEntitlementAlertRetryService` inchangés.
34. Modèles SQLAlchemy existants non modifiés.

### AC 9 — Documentation

35. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.41 — Exposition ops de la file des alertes"** : endpoints liste/summary, schéma réponse, champs dérivés, ordre des routes.
36. `backend/README.md` mis à jour avec mention des endpoints de consultation des alertes.

---

## Tasks / Subtasks

- [x] **Créer `CanonicalEntitlementAlertQueryService`** (AC: 3, 4 partiel)
  - [x] `backend/app/services/canonical_entitlement_alert_query_service.py`
  - [x] Définir `AlertEventRow` et `AlertSummaryResult` dataclasses
  - [x] Implémenter `list_alert_events` (2 requêtes : pagination + attempts batch)
  - [x] Implémenter `get_summary` (SQL aggregates avec `case`)

- [x] **Ajouter les schémas Pydantic** (AC: 4)
  - [x] `AlertEventItem`, `AlertEventListData`, `AlertEventListApiResponse`
  - [x] `AlertSummaryData`, `AlertSummaryApiResponse`
  - [x] Ajout dans `ops_entitlement_mutation_audits.py`

- [x] **Ajouter les endpoints** (AC: 1, 2, 5)
  - [x] `GET /mutation-audits/alerts/summary` — enregistré EN PREMIER
  - [x] `GET /mutation-audits/alerts` — liste paginée + filtrée
  - [x] Vérifier l'ordre de déclaration dans le fichier router

- [x] **Tests unitaires** (AC: 6)
  - [x] `backend/app/tests/unit/test_canonical_entitlement_alert_query_service.py` (9 tests)

- [x] **Tests d'intégration** (AC: 7)
  - [x] `backend/app/tests/integration/test_ops_alert_events_list_api.py` (11 tests)
  - [x] Vérifier non-régression 61.39 et 61.40

- [x] **Documentation** (AC: 9)
  - [x] Section 61.41 dans `backend/docs/entitlements-canonical-platform.md`
  - [x] `backend/README.md`

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest unit`
  - [x] `pytest integration`

---

## Dev Notes

### Architecture : pourquoi deux requêtes dans `list_alert_events`

Ne pas utiliser de LEFT JOIN SQLAlchemy sur les attempts pour le comptage. La table `canonical_entitlement_mutation_alert_delivery_attempts` peut avoir N lignes par event — un JOIN duplique les lignes de l'event parent et complique le comptage total. Le pattern à deux requêtes (paginer les events, puis batch-fetch les attempts des IDs de la page) est plus simple, plus lisible, et performant pour `page_size ≤ 100`.

### Implémentation `list_alert_events` — squelette exact

```python
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)


@dataclass
class AlertEventRow:
    event: CanonicalEntitlementMutationAlertEventModel
    attempt_count: int
    last_attempt_number: int | None
    last_attempt_status: str | None


@dataclass
class AlertSummaryResult:
    total_count: int
    failed_count: int
    sent_count: int
    retryable_count: int
    webhook_failed_count: int
    log_sent_count: int


class CanonicalEntitlementAlertQueryService:
    @staticmethod
    def list_alert_events(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        alert_kind: str | None = None,
        delivery_status: str | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[AlertEventRow], int]:
        Model = CanonicalEntitlementMutationAlertEventModel
        q = select(Model)
        if alert_kind is not None:
            q = q.where(Model.alert_kind == alert_kind)
        if delivery_status is not None:
            q = q.where(Model.delivery_status == delivery_status)
        if audit_id is not None:
            q = q.where(Model.audit_id == audit_id)
        if feature_code is not None:
            q = q.where(Model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            q = q.where(Model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            q = q.where(Model.actor_type_snapshot == actor_type)
        if request_id is not None:
            q = q.where(Model.request_id == request_id)
        if date_from is not None:
            q = q.where(Model.created_at >= date_from)
        if date_to is not None:
            q = q.where(Model.created_at <= date_to)

        # Total count avant pagination
        count_q = select(func.count()).select_from(q.subquery())
        total_count = db.scalar(count_q) or 0

        # Page
        q = (
            q.order_by(Model.created_at.desc(), Model.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        events = list(db.scalars(q).all())

        if not events:
            return [], total_count

        # Batch-fetch attempts pour les events de la page
        event_ids = [e.id for e in events]
        AttemptModel = CanonicalEntitlementMutationAlertDeliveryAttemptModel
        attempts = list(
            db.scalars(
                select(AttemptModel).where(AttemptModel.alert_event_id.in_(event_ids))
            ).all()
        )

        # Grouper par alert_event_id
        attempts_by_event: dict[int, list] = defaultdict(list)
        for a in attempts:
            attempts_by_event[a.alert_event_id].append(a)

        rows = []
        for event in events:
            event_attempts = attempts_by_event.get(event.id, [])
            if event_attempts:
                last = max(event_attempts, key=lambda a: a.attempt_number)
                rows.append(AlertEventRow(
                    event=event,
                    attempt_count=len(event_attempts),
                    last_attempt_number=last.attempt_number,
                    last_attempt_status=last.delivery_status,
                ))
            else:
                rows.append(AlertEventRow(
                    event=event,
                    attempt_count=0,
                    last_attempt_number=None,
                    last_attempt_status=None,
                ))
        return rows, total_count

    @staticmethod
    def get_summary(
        db: Session,
        *,
        alert_kind: str | None = None,
        delivery_status: str | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AlertSummaryResult:
        from sqlalchemy import case
        Model = CanonicalEntitlementMutationAlertEventModel
        # Construire la base filtrée (mêmes conditions que list_alert_events)
        q = select(Model)
        if alert_kind is not None:
            q = q.where(Model.alert_kind == alert_kind)
        if delivery_status is not None:
            q = q.where(Model.delivery_status == delivery_status)
        if audit_id is not None:
            q = q.where(Model.audit_id == audit_id)
        if feature_code is not None:
            q = q.where(Model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            q = q.where(Model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            q = q.where(Model.actor_type_snapshot == actor_type)
        if request_id is not None:
            q = q.where(Model.request_id == request_id)
        if date_from is not None:
            q = q.where(Model.created_at >= date_from)
        if date_to is not None:
            q = q.where(Model.created_at <= date_to)
        base = q.subquery()

        row = db.execute(
            select(
                func.count().label("total_count"),
                func.count(
                    case((base.c.delivery_status == "failed", 1))
                ).label("failed_count"),
                func.count(
                    case((base.c.delivery_status == "sent", 1))
                ).label("sent_count"),
                func.count(
                    case(((base.c.delivery_channel == "webhook") & (base.c.delivery_status == "failed"), 1))
                ).label("webhook_failed_count"),
                func.count(
                    case(((base.c.delivery_channel == "log") & (base.c.delivery_status == "sent"), 1))
                ).label("log_sent_count"),
            ).select_from(base)
        ).one()
        return AlertSummaryResult(
            total_count=row.total_count,
            failed_count=row.failed_count,
            sent_count=row.sent_count,
            retryable_count=row.failed_count,  # retryable ≡ failed
            webhook_failed_count=row.webhook_failed_count,
            log_sent_count=row.log_sent_count,
        )
```

### Endpoint `GET /mutation-audits/alerts/summary` — ordre critique

FastAPI fait du routage par ordre de déclaration. Si `GET /mutation-audits/alerts/{alert_event_id}` était jamais ajouté (detail), il capturerait "summary" comme `alert_event_id`. Pour future-proofing, déclarer `summary` en premier dans le fichier :

```python
@router.get("/mutation-audits/alerts/summary", ...)   # ← PREMIER
@router.get("/mutation-audits/alerts", ...)           # ← DEUXIÈME
# Endpoints 61.40 existants (déjà déclarés plus bas)
@router.get("/mutation-audits/alerts/{alert_event_id}/attempts", ...)
@router.post("/mutation-audits/alerts/{alert_event_id}/retry", ...)
```

Dans l'état actuel (61.40 n'a que `/{alert_event_id}/attempts` et `/{alert_event_id}/retry`), il n'y a pas de conflit fonctionnel. La contrainte d'ordre est préventive.

### Endpoint `GET /mutation-audits/alerts` — squelette

```python
@router.get(
    "/mutation-audits/alerts",
    response_model=AlertEventListApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_alert_events(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    alert_kind: str | None = Query(default=None),
    delivery_status: str | None = Query(default=None),
    audit_id: int | None = Query(default=None),
    feature_code: str | None = Query(default=None),
    plan_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    request_id_filter: str | None = Query(default=None, alias="request_id"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_query_service import (
        CanonicalEntitlementAlertQueryService,
    )
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (err := _enforce_limits(user=current_user, request_id=request_id, operation="list_alerts")) is not None:
        return err

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db,
        page=page,
        page_size=page_size,
        alert_kind=alert_kind,
        delivery_status=delivery_status,
        audit_id=audit_id,
        feature_code=feature_code,
        plan_code=plan_code,
        actor_type=actor_type,
        request_id=request_id_filter,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "data": {
            "items": [
                {
                    "id": row.event.id,
                    "audit_id": row.event.audit_id,
                    "dedupe_key": row.event.dedupe_key,
                    "alert_kind": row.event.alert_kind,
                    "delivery_status": row.event.delivery_status,
                    "delivery_channel": row.event.delivery_channel,
                    "delivery_error": row.event.delivery_error,
                    "created_at": row.event.created_at,
                    "delivered_at": row.event.delivered_at,
                    "feature_code_snapshot": row.event.feature_code_snapshot,
                    "plan_id_snapshot": row.event.plan_id_snapshot,
                    "plan_code_snapshot": row.event.plan_code_snapshot,
                    "risk_level_snapshot": row.event.risk_level_snapshot,
                    "effective_review_status_snapshot": row.event.effective_review_status_snapshot,
                    "actor_type_snapshot": row.event.actor_type_snapshot,
                    "actor_identifier_snapshot": row.event.actor_identifier_snapshot,
                    "age_seconds_snapshot": row.event.age_seconds_snapshot,
                    "sla_target_seconds_snapshot": row.event.sla_target_seconds_snapshot,
                    "due_at_snapshot": row.event.due_at_snapshot,
                    "request_id": row.event.request_id,
                    # Dérivés
                    "attempt_count": row.attempt_count,
                    "last_attempt_number": row.last_attempt_number,
                    "last_attempt_status": row.last_attempt_status,
                    "retryable": row.event.delivery_status == "failed",
                }
                for row in rows
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }
```

### Endpoint `GET /mutation-audits/alerts/summary` — squelette

```python
@router.get(
    "/mutation-audits/alerts/summary",
    response_model=AlertSummaryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_alert_events_summary(
    request: Request,
    alert_kind: str | None = Query(default=None),
    delivery_status: Literal["sent", "failed"] | None = Query(default=None),
    audit_id: int | None = Query(default=None),
    feature_code: str | None = Query(default=None),
    plan_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    request_id_filter: str | None = Query(default=None, alias="request_id"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_query_service import (
        CanonicalEntitlementAlertQueryService,
    )
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (err := _enforce_limits(user=current_user, request_id=request_id, operation="alert_events_summary")) is not None:
        return err

    summary = CanonicalEntitlementAlertQueryService.get_summary(
        db,
        alert_kind=alert_kind,
        delivery_status=delivery_status,
        audit_id=audit_id,
        feature_code=feature_code,
        plan_code=plan_code,
        actor_type=actor_type,
        request_id=request_id_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "data": {
            "total_count": summary.total_count,
            "failed_count": summary.failed_count,
            "sent_count": summary.sent_count,
            "retryable_count": summary.retryable_count,
            "webhook_failed_count": summary.webhook_failed_count,
            "log_sent_count": summary.log_sent_count,
        },
        "meta": {"request_id": request_id},
    }
```

### Tests unitaires — pattern avec Session mock

Suivre le pattern de `test_canonical_entitlement_mutation_audit_query_service.py` si présent, sinon de `test_canonical_entitlement_alert_retry_service.py`. Les tests unitaires du query service utilisent une vraie SQLite in-memory session (pattern cohérent avec 61.40) plutôt que des mocks complexes.

### Tests d'intégration — helpers à réutiliser de 61.40

```python
# Copier depuis test_ops_review_queue_alerts_retry_api.py :
def _cleanup_tables() -> None: ...
def _register_user_with_role_and_token(email: str, role: str) -> str: ...
def _seed_audit(db) -> CanonicalEntitlementMutationAuditModel: ...
def _seed_alert_event(db, *, audit_id: int, delivery_status: str = "failed") -> CanonicalEntitlementMutationAlertEventModel: ...
def _seed_attempt(db, *, alert_event_id: int, attempt_number: int, delivery_status: str) -> ...: ...
```

### `case()` SQLAlchemy — syntaxe correcte

La syntaxe `case` a changé entre SQLAlchemy 1.x et 2.x. Dans ce projet (SQLAlchemy 2.x), utiliser :

```python
from sqlalchemy import case
# SQLAlchemy 2.x : case((condition, valeur)) — tuple en premier arg
case((Model.delivery_status == "failed", 1))
# Pour condition multi-champs :
case(((Model.delivery_channel == "webhook") & (Model.delivery_status == "failed"), 1))
```

Ne pas utiliser l'ancienne syntaxe `case(value, whens=[...])`.

### Ne PAS créer

- Aucune migration Alembic
- Aucun nouveau modèle SQLAlchemy
- Aucune modification des services 61.39/61.40
- Aucun scheduleur ou background task

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/services/canonical_entitlement_alert_query_service.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier (+2 endpoints, +5 schémas Pydantic) |
| `backend/app/tests/unit/test_canonical_entitlement_alert_query_service.py` | Créer |
| `backend/app/tests/integration/test_ops_alert_events_list_api.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Modifier (section 61.41) |
| `backend/README.md` | Modifier (endpoints liste/summary alertes) |

### Références

- [Source: backend/app/services/canonical_entitlement_alert_retry_service.py] — pattern service (dataclasses, `_load_candidates`, `db.scalars()`)
- [Source: backend/app/services/canonical_entitlement_mutation_audit_query_service.py] — pattern query service (filtres, pagination, count subquery)
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py] — tous les champs du modèle
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_alert_delivery_attempt.py] — champs du modèle attempt
- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — `_ensure_ops_role()`, `_enforce_limits()`, `_error_response()`, `resolve_request_id()`, pattern réponse `{data, meta}`, schémas existants (dont `ResponseMeta`, `ErrorEnvelope`)
- [Source: backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py] — helpers de test à réutiliser

### Baseline tests attendue

- Tests existants avant 61.41 : tous les tests 61.37–61.40 passent
- **61.41 unitaires** : +9 (query service)
- **61.41 intégration** : +11 (list + summary API)

---

## Dev Agent Record

### Agent Model Used

gpt-5-codex

### Debug Log References

- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_canonical_entitlement_alert_query_service.py app/tests/integration/test_ops_alert_events_list_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_canonical_entitlement_alert_retry_service.py app/tests/integration/test_ops_review_queue_alerts_retry_api.py app/tests/integration/test_ops_review_queue_alerts_script.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q`
- `.\.venv\Scripts\Activate.ps1; cd backend; @'...TestClient(app)...'@ | python -`

### Completion Notes List

- Implémentation de `CanonicalEntitlementAlertQueryService` avec filtres SQL partagés, pagination triée `created_at DESC, id DESC`, dérivation `attempt_count/last_attempt_*`, et résumé agrégé en une requête.
- Ajout des endpoints ops `GET /v1/ops/entitlements/mutation-audits/alerts/summary` puis `GET /v1/ops/entitlements/mutation-audits/alerts`, avec contrôle de rôle, rate limiting, contrat `{data, meta}` et ordre de routes conforme à la story.
- Ajout des tests unitaires et d'intégration 61.41, plus un garde-fou sur la pagination hors plage conservant `total_count`.
- Vérification de non-régression des flows 61.39/61.40 et validation backend complète (`ruff check .`, `pytest -q`, bootstrap applicatif via `TestClient`).
- Première passe de code review: correction d'un écart AC sur le nombre de requêtes SQL dans `list_alert_events` et durcissement de la pagination vide.
- Deuxième passe de code review: aucune issue restante détectée sur les AC, contrats HTTP, ordre des routes, ou documentation.

### File List

- _bmad-output/implementation-artifacts/61-41-exposition-ops-alertes-canoniques.md
- backend/app/services/canonical_entitlement_alert_query_service.py
- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/tests/unit/test_canonical_entitlement_alert_query_service.py
- backend/app/tests/integration/test_ops_alert_events_list_api.py
- backend/docs/entitlements-canonical-platform.md
- backend/README.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-29: implémentation complète de la story 61.41, documentation incluse, double passe de code review et corrections appliquées, story passée à `done`.
