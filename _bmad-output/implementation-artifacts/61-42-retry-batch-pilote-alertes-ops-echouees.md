# Story 61.42 : Retry batch piloté des alertes ops échouées

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux pouvoir relancer en masse les alertes ops échouées depuis l'API interne, avec les mêmes filtres que la file des alertes (61.41),
afin de traiter rapidement un lot d'échecs de delivery sans passer par SQL ni par un script CLI manuel.

## Contexte

- **61.39** : alerting idempotent, persistance dans `canonical_entitlement_mutation_alert_events`
- **61.40** : table `canonical_entitlement_mutation_alert_delivery_attempts`, `CanonicalEntitlementAlertRetryService`, endpoints `GET .../alerts/{id}/attempts` et `POST .../alerts/{id}/retry`
- **61.41** : `GET /mutation-audits/alerts` (liste paginée+filtrée) et `GET /mutation-audits/alerts/summary` — l'opérateur voit maintenant les alertes `failed`
- **Gap** : il n'existe aucun endpoint pour relancer un lot d'alertes depuis l'API. L'opérateur doit soit relancer une par une via 61.40, soit sortir du produit pour utiliser le script CLI.

## Acceptance Criteria

### AC 1 — Endpoint `POST /v1/ops/entitlements/mutation-audits/alerts/retry-batch`

1. Endpoint `POST /mutation-audits/alerts/retry-batch` ajouté dans `ops_entitlement_mutation_audits.py`.
2. Rôle requis : `ops` ou `admin` (via `_ensure_ops_role()`).
3. Rate limit via `_enforce_limits()` avec l'opération `"batch_retry_alerts"` ; retourne 429 si dépassé.
4. Body JSON : `BatchRetryRequestBody` (voir AC 2).
5. Seules les alertes avec `delivery_status == "failed"` sont candidates — ce filtre est **toujours forcé**, indépendamment du body.
6. Le tri d'extraction des candidats est `id ASC` (FIFO) afin de traiter les alertes les plus anciennes en premier.
7. Réponse HTTP 200 avec body : `{ data: BatchRetryResultData, meta: { request_id } }`.
8. Endpoint **non read-only** : écrit des `canonical_entitlement_mutation_alert_delivery_attempts` et met à jour `delivery_status` sur les events. Le `db.commit()` est effectué dans le router **uniquement si** `dry_run=False`.

### AC 2 — Schéma `BatchRetryRequestBody`

9. Champs du body :
   ```python
   class BatchRetryRequestBody(BaseModel):
       limit: int = Field(default=..., ge=1, le=100)  # requis, 1 ≤ limit ≤ 100
       dry_run: bool = False
       alert_kind: str | None = None
       audit_id: int | None = None
       feature_code: str | None = None
       plan_code: str | None = None
       actor_type: str | None = None
       request_id_filter: str | None = Field(default=None, alias="request_id")
       date_from: datetime | None = None
       date_to: datetime | None = None
   ```
10. `limit` est **obligatoire** (pas de default) et borné : 1 ≤ limit ≤ 100. Valeur invalide → 422 natif FastAPI (Pydantic).
11. L'absence de `limit` dans le body → 422 natif FastAPI.
12. Les filtres optionnels permettent de cibler un sous-ensemble de `failed` : si tous sont `None`, l'endpoint traite jusqu'à `limit` alertes `failed` (ordre FIFO) sans erreur — la protection "trop large" est couverte par `limit` obligatoire.

### AC 3 — Service `CanonicalEntitlementAlertBatchRetryService`

13. `backend/app/services/canonical_entitlement_alert_batch_retry_service.py` créé.
14. Interface publique :
    ```python
    @dataclass
    class BatchRetryResult:
        candidate_count: int
        retried_count: int
        sent_count: int
        failed_count: int
        skipped_count: int
        dry_run: bool
        alert_event_ids: list[int]  # IDs des events traités (ou à traiter en dry_run)

    class CanonicalEntitlementAlertBatchRetryService:
        @staticmethod
        def batch_retry(
            db: Session,
            *,
            limit: int,
            dry_run: bool = False,
            request_id: str | None = None,
            alert_kind: str | None = None,
            audit_id: int | None = None,
            feature_code: str | None = None,
            plan_code: str | None = None,
            actor_type: str | None = None,
            request_id_filter: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
        ) -> BatchRetryResult: ...
    ```
15. `batch_retry` charge les candidats via `_load_batch_candidates()` (AC 4), puis exécute la boucle de retry (AC 5).
16. `skipped_count = candidate_count - retried_count` ; il vaut 0 dans l'implémentation normale (tous les candidats sont tentés).
17. `alert_event_ids` contient les IDs des events effectivement tentés (ou à tenter en dry_run) — au maximum `limit` éléments.
18. En `dry_run=True` : aucune écriture DB (ni `db.add()`, ni `db.flush()`). `retried_count = candidate_count`, `sent_count = 0`, `failed_count = 0`, `skipped_count = 0`.
19. Pas de `db.commit()` dans le service. Pas de `db.flush()` en dehors de la boucle de retry réel.

### AC 4 — `_load_batch_candidates()`

20. Méthode statique protégée dans `CanonicalEntitlementAlertBatchRetryService` :
    ```python
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
    ) -> list[CanonicalEntitlementMutationAlertEventModel]: ...
    ```
21. Requête de base : `SELECT ... FROM canonical_entitlement_mutation_alert_events WHERE delivery_status = 'failed'` + filtres optionnels + `ORDER BY id ASC LIMIT limit`.
22. Mapping des filtres sur les colonnes SQLAlchemy :
    - `alert_kind` → `Model.alert_kind`
    - `audit_id` → `Model.audit_id`
    - `feature_code` → `Model.feature_code_snapshot`
    - `plan_code` → `Model.plan_code_snapshot`
    - `actor_type` → `Model.actor_type_snapshot`
    - `request_id_filter` → `Model.request_id`
    - `date_from` → `Model.created_at >= date_from`
    - `date_to` → `Model.created_at <= date_to`

### AC 5 — Boucle de retry dans `batch_retry`

23. La boucle de retry dans `CanonicalEntitlementAlertBatchRetryService.batch_retry()` **réplique exactement** la logique de `CanonicalEntitlementAlertRetryService.retry_failed_alerts()` pour chaque candidat, à l'exception du chargement des candidats (AC 4).
24. Pour chaque event candidat :
    - Calcul de `attempt_number` via `CanonicalEntitlementAlertRetryService._next_attempt_number(db, alert_event_id=event.id)`
    - Delivery : si `settings.ops_review_queue_alert_webhook_url` → appel `CanonicalEntitlementAlertService._deliver_webhook()` ; sinon → log + status `"sent"`
    - Création de `CanonicalEntitlementMutationAlertDeliveryAttemptModel` avec le résultat
    - Mise à jour de `event.delivery_status`, `event.delivery_error`, `event.delivered_at`
25. Un seul `db.flush()` à la fin de la boucle (pas de flush par event) — identique au pattern de `retry_failed_alerts`.
26. `CanonicalEntitlementAlertRetryService` n'est **pas modifié** (ni son interface, ni sa logique). Seule `_next_attempt_number` est réutilisée en import direct.

### AC 6 — Schémas Pydantic dans le router

27. Les schémas suivants ajoutés dans `ops_entitlement_mutation_audits.py` :
    ```python
    class BatchRetryRequestBody(BaseModel):
        limit: int = Field(..., ge=1, le=100)
        dry_run: bool = False
        alert_kind: str | None = None
        audit_id: int | None = None
        feature_code: str | None = None
        plan_code: str | None = None
        actor_type: str | None = None
        request_id_filter: str | None = Field(default=None, alias="request_id")
        date_from: datetime | None = None
        date_to: datetime | None = None

        model_config = ConfigDict(populate_by_name=True)

    class BatchRetryResultData(BaseModel):
        candidate_count: int
        retried_count: int
        sent_count: int
        failed_count: int
        skipped_count: int
        dry_run: bool
        alert_event_ids: list[int]

    class BatchRetryApiResponse(BaseModel):
        data: BatchRetryResultData
        meta: ResponseMeta
    ```

### AC 7 — Ordre des routes dans le router

28. Dans `ops_entitlement_mutation_audits.py`, l'endpoint 61.42 est déclaré dans cet ordre par rapport aux endpoints alertes existants :
    1. `GET /mutation-audits/alerts/summary` (61.41)
    2. `GET /mutation-audits/alerts` (61.41)
    3. `POST /mutation-audits/alerts/retry-batch` ← **ajout 61.42**, avant les routes paramétriques
    4. `GET /mutation-audits/alerts/{alert_event_id}/attempts` (61.40)
    5. `POST /mutation-audits/alerts/{alert_event_id}/retry` (61.40)
29. L'endpoint `POST /mutation-audits/alerts/retry-batch` doit être déclaré **avant** `POST /mutation-audits/alerts/{alert_event_id}/retry` pour éviter que FastAPI ne capture `"retry-batch"` comme `alert_event_id` (bien que la collision soit improbable car `retry-batch` n'est pas un int, il vaut mieux respecter ce principe de précaution).

### AC 8 — Tests unitaires

30. `backend/app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py` créé avec :
    - `test_batch_retry_dry_run_returns_candidate_count_without_writes`
    - `test_batch_retry_dry_run_no_db_add`
    - `test_batch_retry_real_retries_all_failed_candidates`
    - `test_batch_retry_respects_limit`
    - `test_batch_retry_filter_by_alert_kind`
    - `test_batch_retry_filter_by_feature_code`
    - `test_batch_retry_filter_by_audit_id`
    - `test_batch_retry_returns_correct_alert_event_ids`
    - `test_batch_retry_skipped_count_is_zero_when_all_retried`
    - `test_batch_retry_empty_when_no_failed`

### AC 9 — Tests d'intégration

31. `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` créé avec :
    - `test_post_retry_batch_dry_run_no_persistence`
    - `test_post_retry_batch_real_retries_multiple_failed`
    - `test_post_retry_batch_with_filter_by_feature_code`
    - `test_post_retry_batch_with_filter_by_alert_kind`
    - `test_post_retry_batch_respects_limit`
    - `test_post_retry_batch_requires_ops_role`
    - `test_post_retry_batch_returns_429_when_rate_limited`
    - `test_post_retry_batch_returns_422_when_limit_missing`
    - `test_post_retry_batch_returns_422_when_limit_exceeds_100`
    - `test_post_retry_batch_empty_when_no_failed`
    - `test_post_retry_batch_does_not_affect_sent_events`
32. Les tests 61.40 et 61.41 restent verts (non-régression).

### AC 10 — Non-régression

33. Aucun contrat HTTP des endpoints 61.37–61.41 modifié.
34. Aucune migration Alembic créée.
35. `CanonicalEntitlementAlertService` inchangé.
36. `CanonicalEntitlementAlertRetryService` inchangé (seule `_next_attempt_number` est importée).
37. Modèles SQLAlchemy existants non modifiés.

### AC 11 — Documentation

38. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.42 — Retry batch piloté des alertes ops"** : endpoint, schéma body/réponse, règle `limit` obligatoire, ordre des routes.
39. `backend/README.md` mis à jour avec mention de l'endpoint de retry batch.

---

## Tasks / Subtasks

- [x] **Créer `CanonicalEntitlementAlertBatchRetryService`** (AC: 3, 4, 5)
  - [x] `backend/app/services/canonical_entitlement_alert_batch_retry_service.py`
  - [x] Définir `BatchRetryResult` dataclass
  - [x] Implémenter `_load_batch_candidates()` (filtre delivery_status=failed + filtres optionnels + limit)
  - [x] Implémenter `batch_retry()` (dry_run + boucle retry + flush unique)

- [x] **Ajouter les schémas Pydantic** (AC: 6)
  - [x] `BatchRetryRequestBody` avec `limit` requis, `model_config = ConfigDict(populate_by_name=True)` pour alias `request_id`
  - [x] `BatchRetryResultData`, `BatchRetryApiResponse`
  - [x] Ajout dans `ops_entitlement_mutation_audits.py`

- [x] **Ajouter l'endpoint** (AC: 1, 7)
  - [x] `POST /mutation-audits/alerts/retry-batch` dans `ops_entitlement_mutation_audits.py`
  - [x] Vérifier l'ordre de déclaration : après GET summary/liste, avant `/{alert_event_id}/attempts`

- [x] **Tests unitaires** (AC: 8)
  - [x] `backend/app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py` (10 tests)

- [x] **Tests d'intégration** (AC: 9)
  - [x] `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` (11 tests)
  - [x] Vérifier non-régression 61.40 et 61.41

- [x] **Documentation** (AC: 11)
  - [x] Section 61.42 dans `backend/docs/entitlements-canonical-platform.md`
  - [x] `backend/README.md`

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest unit`
  - [x] `pytest integration`

---

## Dev Notes

### Architecture : pourquoi un nouveau service dédié

Ne pas modifier `CanonicalEntitlementAlertRetryService` pour ajouter les filtres batch : cela étendrait son interface de manière orthogonale à sa responsabilité actuelle (retry ciblé par ID + retry CLI sans filtre métier). Le nouveau `CanonicalEntitlementAlertBatchRetryService` est responsable uniquement du cas d'usage "batch piloté par filtres depuis l'API".

La seule dépendance vers le service existant est l'import de `CanonicalEntitlementAlertRetryService._next_attempt_number()` pour le calcul du prochain numéro de tentative. Cela évite de dupliquer la logique de comptage.

### Implémentation `batch_retry` — squelette exact

```python
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.services.canonical_entitlement_alert_retry_service import (
    CanonicalEntitlementAlertRetryService,
)
from app.services.canonical_entitlement_alert_service import CanonicalEntitlementAlertService

logger = logging.getLogger(__name__)


@dataclass
class BatchRetryResult:
    candidate_count: int
    retried_count: int
    sent_count: int
    failed_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int] = field(default_factory=list)


class CanonicalEntitlementAlertBatchRetryService:
    @staticmethod
    def batch_retry(
        db: Session,
        *,
        limit: int,
        dry_run: bool = False,
        request_id: str | None = None,
        alert_kind: str | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> BatchRetryResult:
        effective_now = datetime.now(timezone.utc)
        candidates = CanonicalEntitlementAlertBatchRetryService._load_batch_candidates(
            db,
            limit=limit,
            alert_kind=alert_kind,
            audit_id=audit_id,
            feature_code=feature_code,
            plan_code=plan_code,
            actor_type=actor_type,
            request_id_filter=request_id_filter,
            date_from=date_from,
            date_to=date_to,
        )

        candidate_count = len(candidates)
        alert_event_ids = [e.id for e in candidates]

        if dry_run:
            return BatchRetryResult(
                candidate_count=candidate_count,
                retried_count=candidate_count,
                sent_count=0,
                failed_count=0,
                skipped_count=0,
                dry_run=True,
                alert_event_ids=alert_event_ids,
            )

        retried_count = 0
        sent_count = 0
        failed_count = 0

        for event in candidates:
            attempt_number = CanonicalEntitlementAlertRetryService._next_attempt_number(
                db, alert_event_id=event.id
            )
            delivery_channel = "log"
            delivery_status = "sent"
            delivery_error = None
            delivered_at = effective_now

            if settings.ops_review_queue_alert_webhook_url:
                delivery_channel = "webhook"
                success, error_message = CanonicalEntitlementAlertService._deliver_webhook(
                    settings.ops_review_queue_alert_webhook_url,
                    event.payload,
                )
                if success:
                    sent_count += 1
                else:
                    delivery_status = "failed"
                    delivery_error = error_message
                    delivered_at = None
                    failed_count += 1
            else:
                logger.info("ops_alert_batch_retry_log_delivery payload=%s", event.payload)
                sent_count += 1

            db.add(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel(
                    alert_event_id=event.id,
                    attempt_number=attempt_number,
                    delivery_channel=delivery_channel,
                    delivery_status=delivery_status,
                    delivery_error=delivery_error,
                    request_id=request_id,
                    payload=event.payload,
                    delivered_at=delivered_at,
                )
            )

            event.delivery_status = delivery_status
            event.delivery_error = delivery_error
            event.delivered_at = delivered_at
            retried_count += 1

        db.flush()
        return BatchRetryResult(
            candidate_count=candidate_count,
            retried_count=retried_count,
            sent_count=sent_count,
            failed_count=failed_count,
            skipped_count=candidate_count - retried_count,
            dry_run=False,
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
        Model = CanonicalEntitlementMutationAlertEventModel
        q = select(Model).where(Model.delivery_status == "failed")
        if alert_kind is not None:
            q = q.where(Model.alert_kind == alert_kind)
        if audit_id is not None:
            q = q.where(Model.audit_id == audit_id)
        if feature_code is not None:
            q = q.where(Model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            q = q.where(Model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            q = q.where(Model.actor_type_snapshot == actor_type)
        if request_id_filter is not None:
            q = q.where(Model.request_id == request_id_filter)
        if date_from is not None:
            q = q.where(Model.created_at >= date_from)
        if date_to is not None:
            q = q.where(Model.created_at <= date_to)
        q = q.order_by(Model.id.asc()).limit(limit)
        return list(db.scalars(q).all())
```

### Endpoint `POST /mutation-audits/alerts/retry-batch` — squelette

```python
@router.post(
    "/mutation-audits/alerts/retry-batch",
    response_model=BatchRetryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"description": "Validation error (limit manquant ou hors bornes)"},
        429: {"model": ErrorEnvelope},
    },
)
def batch_retry_alerts(
    body: BatchRetryRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_batch_retry_service import (
        CanonicalEntitlementAlertBatchRetryService,
    )

    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user, request_id=request_id, operation="batch_retry_alerts"
        )
    ) is not None:
        return err

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db,
        limit=body.limit,
        dry_run=body.dry_run,
        request_id=request_id,
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
            "retried_count": result.retried_count,
            "sent_count": result.sent_count,
            "failed_count": result.failed_count,
            "skipped_count": result.skipped_count,
            "dry_run": result.dry_run,
            "alert_event_ids": result.alert_event_ids,
        },
        "meta": {"request_id": request_id},
    }
```

### Schéma `BatchRetryRequestBody` — alias `request_id`

Le champ `request_id_filter` utilise un alias `request_id` (cohérent avec le paramètre query `request_id_filter` de 61.41) pour éviter de shadow la variable FastAPI `request_id` dans le router. `model_config = ConfigDict(populate_by_name=True)` est obligatoire pour que Pydantic accepte les deux noms.

```python
from pydantic import BaseModel, ConfigDict, Field

class BatchRetryRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., ge=1, le=100)
    dry_run: bool = False
    alert_kind: str | None = None
    audit_id: int | None = None
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    request_id_filter: str | None = Field(default=None, alias="request_id")
    date_from: datetime | None = None
    date_to: datetime | None = None
```

### Ordre critique des routes dans le router (AC 7)

```python
@router.get("/mutation-audits/alerts/summary", ...)   # 61.41 — PREMIER
@router.get("/mutation-audits/alerts", ...)           # 61.41 — DEUXIÈME
@router.post("/mutation-audits/alerts/retry-batch", ...) # 61.42 — TROISIÈME (avant paramétriques)
@router.get("/mutation-audits/alerts/{alert_event_id}/attempts", ...)  # 61.40
@router.post("/mutation-audits/alerts/{alert_event_id}/retry", ...)    # 61.40
```

### Tests unitaires — pattern avec SQLite in-memory

Suivre le pattern de `test_canonical_entitlement_alert_query_service.py` (session SQLite in-memory, seeds manuels). Les tests unitaires du batch retry service **ne mockent pas** la DB.

Pour tester dry_run sans écriture :
```python
def test_batch_retry_dry_run_no_db_add(db_session):
    # seed 3 failed events
    ...
    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(db_session, limit=10, dry_run=True)
    assert result.candidate_count == 3
    assert result.retried_count == 3
    assert result.dry_run is True
    # Aucun attempt créé
    assert db_session.execute(select(func.count()).select_from(AttemptModel)).scalar() == 0
```

Pour tester que les events `sent` ne sont pas candidats :
```python
def test_batch_retry_empty_when_no_failed(db_session):
    # seed 2 sent events
    ...
    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(db_session, limit=10, dry_run=False)
    assert result.candidate_count == 0
    assert result.alert_event_ids == []
```

### Tests d'intégration — helpers à réutiliser de 61.40

```python
# Copier depuis test_ops_review_queue_alerts_retry_api.py :
def _cleanup_tables() -> None: ...
def _register_user_with_role_and_token(email: str, role: str) -> str: ...
def _seed_audit(db) -> CanonicalEntitlementMutationAuditModel: ...
def _seed_alert_event(db, *, audit_id: int, delivery_status: str = "failed") -> ...: ...
```

Exemple de test intégration :
```python
def test_post_retry_batch_dry_run_no_persistence():
    _cleanup_tables()
    token = _register_user_with_role_and_token("ops@test.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db)
        _seed_alert_event(db, audit_id=audit.id, delivery_status="failed")
        _seed_alert_event(db, audit_id=audit.id, delivery_status="failed")
        db.commit()

    resp = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 10, "dry_run": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["candidate_count"] == 2
    assert data["dry_run"] is True
    # Aucune tentative persistée
    with SessionLocal() as db:
        count = db.execute(select(func.count()).select_from(AttemptModel)).scalar()
        assert count == 0

def test_post_retry_batch_returns_422_when_limit_missing():
    token = _register_user_with_role_and_token("ops2@test.com", "ops")
    resp = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"dry_run": False},  # limit absent
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422

def test_post_retry_batch_returns_422_when_limit_exceeds_100():
    token = _register_user_with_role_and_token("ops3@test.com", "ops")
    resp = client.post(
        "/v1/ops/entitlements/mutation-audits/alerts/retry-batch",
        json={"limit": 101},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
```

### `ConfigDict` et `Field` — imports nécessaires

Le router utilise déjà `from pydantic import BaseModel`. Ajouter `ConfigDict, Field` à l'import existant :
```python
from pydantic import BaseModel, ConfigDict, Field
```

### Ne PAS créer

- Aucune migration Alembic
- Aucun nouveau modèle SQLAlchemy
- Aucune modification de `CanonicalEntitlementAlertService`
- Aucune modification de `CanonicalEntitlementAlertRetryService` (ni son interface, ni sa logique)
- Aucun scheduler ou background task
- Aucun endpoint detail `GET /mutation-audits/alerts/{id}`

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/services/canonical_entitlement_alert_batch_retry_service.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier (+1 endpoint, +3 schémas Pydantic, +imports `ConfigDict, Field`) |
| `backend/app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py` | Créer |
| `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Modifier (section 61.42) |
| `backend/README.md` | Modifier (endpoint retry batch) |

### Références

- [Source: backend/app/services/canonical_entitlement_alert_retry_service.py] — pattern de retry, `_next_attempt_number`, `_load_candidates`, `AlertRetryRunResult`
- [Source: backend/app/services/canonical_entitlement_alert_service.py] — `_deliver_webhook()` (à réutiliser)
- [Source: backend/app/services/canonical_entitlement_alert_query_service.py] — pattern de filtres SQLAlchemy avec les mêmes colonnes
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py] — tous les champs du modèle
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_alert_delivery_attempt.py] — champs du modèle attempt
- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — `_ensure_ops_role()`, `_enforce_limits()`, `_error_response()`, `resolve_request_id()`, schémas existants (`ResponseMeta`, `ErrorEnvelope`), pattern `db.commit()` dans le router
- [Source: backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py] — helpers `_cleanup_tables`, `_register_user_with_role_and_token`, `_seed_audit`, `_seed_alert_event`

### Baseline tests attendue

- Tests existants avant 61.42 : tous les tests 61.37–61.41 passent
- **61.42 unitaires** : +10 (batch retry service)
- **61.42 intégration** : +11 (batch retry API)

---

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py app/tests/integration/test_ops_alert_events_batch_retry_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/services/canonical_entitlement_alert_batch_retry_service.py app/api/v1/routers/ops_entitlement_mutation_audits.py app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py app/tests/integration/test_ops_alert_events_batch_retry_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py app/tests/unit/test_canonical_entitlement_alert_retry_service.py app/tests/integration/test_ops_alert_events_batch_retry_api.py app/tests/integration/test_ops_alert_events_list_api.py app/tests/integration/test_ops_review_queue_alerts_retry_api.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q`

### Completion Notes List

- Implémentation du service `CanonicalEntitlementAlertBatchRetryService` avec sélection FIFO `id ASC`, filtres SQLAlchemy alignés sur 61.41, dry-run sans écriture et flush unique en retry réel.
- Ajout de l'endpoint `POST /v1/ops/entitlements/mutation-audits/alerts/retry-batch` avec schémas Pydantic dédiés, contrôle de rôle ops/admin, rate limiting `batch_retry_alerts` et commit uniquement hors dry-run.
- Ajout de 10 tests unitaires 61.42 et de 11 tests d'intégration 61.42, plus validation de non-régression des stories 61.40 et 61.41.
- Mise à jour de `backend/docs/entitlements-canonical-platform.md` et `backend/README.md` pour documenter le body, la réponse, la règle `limit` obligatoire et l'ordre critique des routes.
- Revue adversariale effectuée deux fois ; correction appliquée sur l'ordre des routes dans le router et ajout de tests de garde sur le filtre body `request_id`.

### File List

- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/services/canonical_entitlement_alert_batch_retry_service.py
- backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py
- backend/app/tests/unit/test_canonical_entitlement_alert_batch_retry_service.py
- backend/docs/entitlements-canonical-platform.md
- backend/README.md
- _bmad-output/implementation-artifacts/61-42-retry-batch-pilote-alertes-ops-echouees.md

### Change Log

- 2026-03-29: implémentation complète de la story 61.42, ajout des tests, documentation et validations backend.
- 2026-03-29: correction post-review de l'ordre des routes alertes et ajout de tests de couverture sur l'alias body `request_id`.
