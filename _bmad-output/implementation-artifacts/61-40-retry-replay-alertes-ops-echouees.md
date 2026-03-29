# Story 61.40 : Retry/replay contrôlé des alertes ops échouées

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux pouvoir relancer proprement les alertes ops en échec sans recréer de doublons métier,
afin de récupérer les incidents de delivery webhook introduits par 61.39 tout en conservant une traçabilité complète des tentatives.

## Contexte

61.39 a introduit l'alerting idempotent sur la review queue SLA, avec persistance append-only dans `canonical_entitlement_mutation_alert_events`.

Le comportement actuel est volontairement conservateur :
- une alerte est dédupliquée par `dedupe_key`
- un event `failed` reste enregistré mais bloqué
- aucun retry automatique n'est déclenché
- un rerun identique ne renvoie pas l'alerte

Il manque l'outil ops pour traiter les `failed` sans bricoler en base.

**Décision d'architecture** :
- on ne modifie pas la sémantique métier de `dedupe_key`
- on ajoute une notion de **tentative de delivery** séparée de l'event d'alerte
- l'event d'alerte reste la vérité métier "une alerte a été émise pour cet état"
- les retries créent des lignes append-only de tentative, pas de nouveaux alert events métier

## Acceptance Criteria

### AC 1 — Table append-only `canonical_entitlement_mutation_alert_delivery_attempts`

1. Migration Alembic `20260329_0060_create_canonical_entitlement_mutation_alert_delivery_attempts.py` créée.
2. Colonnes :
   - `id` (PK, autoincrement)
   - `alert_event_id` (FK → `canonical_entitlement_mutation_alert_events.id`, NOT NULL, index)
   - `attempt_number` (int, NOT NULL)
   - `delivery_channel` (str(32), NOT NULL) — `webhook` ou `log`
   - `delivery_status` (str(32), NOT NULL) — `sent` ou `failed` (`dry_run` non persisté : aucun attempt n'est écrit en mode dry-run)
   - `delivery_error` (Text, nullable)
   - `request_id` (str(64), nullable)
   - `payload` (JSON, NOT NULL)
   - `created_at` (datetime timezone=True, NOT NULL, server_default=now(), index)
   - `delivered_at` (datetime timezone=True, nullable)
3. Contrainte d'unicité sur `(alert_event_id, attempt_number)`.
4. `down_revision = "20260329_0059"`.

### AC 2 — Alert event inchangée comme vérité métier

5. `canonical_entitlement_mutation_alert_events` n'est pas recréée et garde sa sémantique actuelle.
6. `dedupe_key` continue d'empêcher la recréation d'un nouvel alert event métier pour le même état `(audit_id, effective_review_status, sla_status)`.
7. Le retry d'une alerte échouée ne crée **pas** un nouveau `canonical_entitlement_mutation_alert_event`.
8. Le retry met à jour les champs `delivery_status`, `delivery_error`, `delivered_at` de l'event parent.

### AC 3 — Modèle SQLAlchemy `CanonicalEntitlementMutationAlertDeliveryAttemptModel`

9. `backend/app/infra/db/models/canonical_entitlement_mutation_alert_delivery_attempt.py` créé.
10. Mapping SQLAlchemy moderne `Mapped[...] / mapped_column(...)`, pattern identique à `canonical_entitlement_mutation_alert_event.py`.
11. Enregistré dans `backend/app/infra/db/models/__init__.py` — AVANT `canonical_entitlement_mutation_alert_event` (ordre alphabétique : `alert_delivery_attempt` < `alert_event`).

### AC 4 — Service `CanonicalEntitlementAlertRetryService`

12. `backend/app/services/canonical_entitlement_alert_retry_service.py` créé.
13. Interface : `retry_failed_alerts(db, *, now_utc=None, dry_run=False, request_id=None, limit=None, alert_event_id=None) -> AlertRetryRunResult`
14. `AlertRetryRunResult` dataclass : `candidate_count`, `retried_count`, `sent_count`, `failed_count`, `dry_run`.
15. Candidats par défaut : `canonical_entitlement_mutation_alert_events.delivery_status == "failed"`.
16. Si `alert_event_id` fourni : retry ciblé sur cet event uniquement ; lever `AlertEventNotFoundError` (hérite de `ValueError`) si l'ID n'existe pas.
16b. Si l'event existe mais que `delivery_status != "failed"`, lever `AlertEventNotRetryableError` (hérite de `ValueError`) — un event déjà `sent` ne doit pas être rejoué.
17. Chaque retry :
    - calcule `attempt_number = max(existing attempt_number for this alert_event_id) + 1`, ou `1` s'il n'existe aucune tentative
    - réutilise le `payload` stocké dans l'event parent
    - persiste une ligne `CanonicalEntitlementMutationAlertDeliveryAttemptModel` append-only
    - met à jour l'event parent : `delivery_status`, `delivery_error`, `delivered_at`
18. Pas de `db.commit()` dans le service.

### AC 5 — Règle dry-run

19. `dry_run=True` : aucun webhook réel, aucune ligne de tentative persistée, aucun event parent modifié.
20. `AlertRetryRunResult` en dry-run :
    - `candidate_count` = nombre de candidats trouvés
    - `retried_count` = nombre de candidats qui auraient été retentés
    - `sent_count = 0`
    - `failed_count = 0`
    - `dry_run = True`

### AC 6 — Delivery webhook et fallback log cohérents avec 61.39

21. Le retry réutilise exactement le même mécanisme de delivery que `CanonicalEntitlementAlertService._deliver_webhook()` et le fallback log.
22. En fallback log (`ops_review_queue_alert_webhook_url` non configuré) : tentative considérée `sent`.
23. En échec HTTP : tentative persistée `failed`, event parent mis à jour `delivery_status="failed"`.

### AC 7 — Endpoint ops de consultation des tentatives

24. `GET /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/attempts` ajouté dans `ops_entitlement_mutation_audits.py`.
25. Rôle requis : `ops` ou `admin` (via `_ensure_ops_role()`).
26. Retourne la liste chronologique ASC des tentatives de delivery pour un alert event.
27. 404 (`alert_event_not_found`) si `alert_event_id` inconnu.
27b. Endpoint soumis au rate limit ops habituel via `_enforce_limits()` ; retourne 429 si dépassé.
28. Endpoint strictement read-only, aucune écriture DB.
28b. Les tentatives sont triées par `attempt_number ASC`, puis `id ASC` en garde-fou.
29. Schéma réponse : `{ data: { items: [...], total_count: int }, meta: { request_id } }`.

### AC 8 — Endpoint ops de retry ciblé

30. `POST /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry` ajouté dans `ops_entitlement_mutation_audits.py`.
31. Rôle requis : `ops` ou `admin`.
32. Body : `{ dry_run: bool = false }` — schéma Pydantic `AlertRetryRequestBody`.
33. Le router passe `request_id = resolve_request_id(request)` au service.
34. Retourne 200 avec `{ data: { alert_event_id, attempted, delivery_status, attempt_number, request_id }, meta: { request_id } }`.
35. 404 si `alert_event_id` inconnu.
35b. Endpoint soumis au rate limit ops habituel via `_enforce_limits()` ; retourne 429 si dépassé.
35c. Si `alert_event_id` existe mais n'est pas `failed`, retourne 409 avec `code="alert_event_not_retryable"`.
36. `db.commit()` dans le router après appel du service (si non dry-run et sans erreur).

### AC 9 — Script CLI batch de retry

37. `backend/scripts/retry_ops_review_queue_alerts.py` créé.
38. Arguments : `--dry-run`, `--limit`, `--alert-event-id` (int, optionnel).
39. Même pattern que `run_ops_review_queue_alerts.py` : `_ensure_backend_root_on_path()`, `SessionLocal`, commit/rollback.
40. Codes de sortie : `0` succès/dry-run, `1` si `failed_count > 0`, `2` erreur inattendue.
41. Sortie : `[OK] retried=X sent=Y failed=Z candidates=N`.

### AC 10 — Tests unitaires

42. `backend/app/tests/unit/test_canonical_entitlement_alert_retry_service.py` créé avec :
    - `test_retry_failed_alert_creates_attempt`
    - `test_retry_failed_alert_updates_parent_status_on_success`
    - `test_retry_failed_alert_keeps_failed_on_delivery_failure`
    - `test_retry_dry_run_persists_nothing`
    - `test_retry_targeted_unknown_alert_raises_not_found`
    - `test_retry_targeted_non_failed_alert_raises_not_retryable`
    - `test_retry_attempt_number_increments`
    - `test_retry_ignores_non_failed_events_in_batch_mode`

### AC 11 — Tests d'intégration

43. `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py` créé avec :
    - `test_get_attempts_empty_for_alert_without_attempts`
    - `test_get_attempts_returns_attempt_history`
    - `test_post_retry_creates_new_attempt`
    - `test_post_retry_dry_run_creates_no_attempt`
    - `test_post_retry_requires_ops_role`
    - `test_post_retry_returns_404_for_unknown_alert`
    - `test_post_retry_returns_409_for_non_failed_alert`
44. Les tests 61.39 restent verts.

### AC 12 — Documentation

45. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.40 — Retry/replay des alertes échouées"** : table des tentatives, endpoints, script CLI, règle `dedupe_key` inchangée.
46. `backend/README.md` mis à jour avec exemple cron pour le retry batch.

### AC 13 — Non-régression

47. Aucun contrat des endpoints 61.37–61.39 n'est modifié.
48. Une seule migration Alembic créée.
49. Aucun scheduler interne FastAPI.
50. `CanonicalEntitlementReviewQueueService` et `CanonicalEntitlementAlertService` restent non modifiés.

---

## Tasks / Subtasks

- [x] **Créer le modèle ORM** (AC: 3)
  - [x] `backend/app/infra/db/models/canonical_entitlement_mutation_alert_delivery_attempt.py`
  - [x] Ajouter import dans `__init__.py` en position alphabétique (avant `alert_event`)

- [x] **Créer la migration Alembic** (AC: 1)
  - [x] `backend/migrations/versions/20260329_0060_create_canonical_entitlement_mutation_alert_delivery_attempts.py`
  - [x] `down_revision = "20260329_0059"`
  - [x] `upgrade()` : create table + unique index `(alert_event_id, attempt_number)` + index `alert_event_id` + index `created_at`
  - [x] `downgrade()` : drop indexes + drop table

- [x] **Créer `CanonicalEntitlementAlertRetryService`** (AC: 4, 5, 6)
  - [x] `backend/app/services/canonical_entitlement_alert_retry_service.py`
  - [x] Définir `AlertRetryRunResult`, `AlertEventNotFoundError` et `AlertEventNotRetryableError`
  - [x] Implémenter chargement candidats (batch ou ciblé)
  - [x] Implémenter calcul `attempt_number`
  - [x] Implémenter persistance tentative + update event parent
  - [x] Réutiliser `_deliver_webhook` de `CanonicalEntitlementAlertService`
  - [x] Implémenter `dry_run=True`

- [x] **Ajouter les endpoints** (AC: 7, 8)
  - [x] Schémas Pydantic `AlertAttemptItem`, `AlertAttemptsListData`, `AlertAttemptsApiResponse`
  - [x] Schéma `AlertRetryRequestBody`, `AlertRetryResponseData`, `AlertRetryApiResponse`
  - [x] `GET /mutation-audits/alerts/{alert_event_id}/attempts` (+ rate limit 429)
  - [x] `POST /mutation-audits/alerts/{alert_event_id}/retry` (+ rate limit 429 + 409 not_retryable)

- [x] **Créer le script CLI** (AC: 9)
  - [x] `backend/scripts/retry_ops_review_queue_alerts.py`
  - [x] `--dry-run`, `--limit`, `--alert-event-id`

- [x] **Tests unitaires** (AC: 10)
  - [x] `test_canonical_entitlement_alert_retry_service.py` (7 tests)

- [x] **Tests d'intégration** (AC: 11)
  - [x] `test_ops_review_queue_alerts_retry_api.py` (6 tests)
  - [x] Vérifier non-régression 61.39

- [x] **Documentation** (AC: 12)
  - [x] Section 61.40 dans `backend/docs/entitlements-canonical-platform.md`
  - [x] Runbook / README

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest unit`
  - [x] `pytest integration`
  - [x] `alembic upgrade head` / `alembic downgrade -1` / `alembic upgrade head`

---

## Dev Notes

### Principe architectural clé

Séparer **l'identité métier de l'alerte** (event) de **ses tentatives de delivery** (attempts) :

- `canonical_entitlement_mutation_alert_events` = "il faut/il a fallu alerter pour cet état" — **vérité métier**
- `canonical_entitlement_mutation_alert_delivery_attempts` = "combien de fois on a essayé de livrer cette alerte" — **journal technique**

La `dedupe_key` ne change pas de sémantique. Elle empêche toujours la création d'un doublon métier. Les retries ne contournent pas cette règle ; ils opèrent sur un event déjà créé.

---

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/infra/db/models/canonical_entitlement_mutation_alert_delivery_attempt.py` | Créer |
| `backend/app/infra/db/models/__init__.py` | Modifier (import alphabétique avant `alert_event`) |
| `backend/migrations/versions/20260329_0060_create_canonical_entitlement_mutation_alert_delivery_attempts.py` | Créer |
| `backend/app/services/canonical_entitlement_alert_retry_service.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier — 2 nouveaux endpoints uniquement |
| `backend/scripts/retry_ops_review_queue_alerts.py` | Créer |
| `backend/app/tests/unit/test_canonical_entitlement_alert_retry_service.py` | Créer |
| `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Modifier (section 61.40) |
| `backend/README.md` | Modifier (exemple cron retry) |

### Ne pas modifier

- `canonical_entitlement_alert_service.py` (sauf extraction éventuelle de `_deliver_webhook` en helper partagé si jugé nécessaire)
- `canonical_entitlement_review_queue_service.py`
- Modèles SQLAlchemy existants (audit, review, alert_event)
- Contrats HTTP 61.37–61.39

---

### Modèle SQLAlchemy — pattern exact à suivre

Se baser sur le pattern de `canonical_entitlement_mutation_alert_event.py` :

```python
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def _utc_now() -> datetime:
    from datetime import timezone
    return datetime.now(timezone.utc)


class CanonicalEntitlementMutationAlertDeliveryAttemptModel(Base):
    __tablename__ = "canonical_entitlement_mutation_alert_delivery_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_events.id"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, index=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

La contrainte `UniqueConstraint("alert_event_id", "attempt_number")` est définie dans `__table_args__` :

```python
from sqlalchemy import UniqueConstraint

class CanonicalEntitlementMutationAlertDeliveryAttemptModel(Base):
    __tablename__ = "canonical_entitlement_mutation_alert_delivery_attempts"
    __table_args__ = (
        UniqueConstraint("alert_event_id", "attempt_number", name="uq_alert_delivery_attempt"),
    )
    # ... colonnes ...
```

---

### Enregistrement dans `__init__.py`

`alert_delivery_attempt` < `alert_event` alphabétiquement → insérer **avant** la ligne existante `canonical_entitlement_mutation_alert_event` :

```python
# Ajouter AVANT la ligne existante:
from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
```

Ajouter également `"CanonicalEntitlementMutationAlertDeliveryAttemptModel"` dans `__all__`, avant `"CanonicalEntitlementMutationAlertEventModel"`.

---

### Migration Alembic — numérotation

```
20260329_0059 — canonical_entitlement_mutation_alert_events  ← down_revision de 0060
20260329_0060 — canonical_entitlement_mutation_alert_delivery_attempts  ← NOUVELLE
```

```python
revision = "20260329_0060"
down_revision = "20260329_0059"
branch_labels = None
depends_on = None
```

Pattern `upgrade()` basé sur la migration 0059 :

```python
def upgrade():
    op.create_table(
        'canonical_entitlement_mutation_alert_delivery_attempts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('alert_event_id', sa.Integer(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('delivery_channel', sa.String(length=32), nullable=False),
        sa.Column('delivery_status', sa.String(length=32), nullable=False),
        sa.Column('delivery_error', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(length=64), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['alert_event_id'],
                                ['canonical_entitlement_mutation_alert_events.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alert_event_id', 'attempt_number',
                            name='uq_alert_delivery_attempt'),
    )
    op.create_index(
        op.f('ix_canonical_entitlement_mutation_alert_delivery_attempts_alert_event_id'),
        'canonical_entitlement_mutation_alert_delivery_attempts', ['alert_event_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_canonical_entitlement_mutation_alert_delivery_attempts_created_at'),
        'canonical_entitlement_mutation_alert_delivery_attempts', ['created_at'],
        unique=False
    )
```

---

### Service de retry — squelette

Réutiliser `_deliver_webhook` de `CanonicalEntitlementAlertService`. Options :
- copier/coller la méthode statique (simple, pas de dépendance croisée)
- extraire dans un module helper `backend/app/services/_alert_delivery.py` (préférable si les deux services doivent évoluer ensemble — laisser au dev le choix)

```python
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.services.canonical_entitlement_alert_service import CanonicalEntitlementAlertService

logger = logging.getLogger(__name__)


class AlertEventNotFoundError(ValueError):
    pass


class AlertEventNotRetryableError(ValueError):
    pass


@dataclass
class AlertRetryRunResult:
    candidate_count: int
    retried_count: int
    sent_count: int
    failed_count: int
    dry_run: bool


class CanonicalEntitlementAlertRetryService:
    @staticmethod
    def retry_failed_alerts(
        db: Session,
        *,
        now_utc: datetime | None = None,
        dry_run: bool = False,
        request_id: str | None = None,
        limit: int | None = None,
        alert_event_id: int | None = None,
    ) -> AlertRetryRunResult:
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        # Charger les candidats
        query = select(CanonicalEntitlementMutationAlertEventModel).where(
            CanonicalEntitlementMutationAlertEventModel.delivery_status == "failed"
        )
        if alert_event_id is not None:
            query = select(CanonicalEntitlementMutationAlertEventModel).where(
                CanonicalEntitlementMutationAlertEventModel.id == alert_event_id
            )
            result = db.execute(query).scalar_one_or_none()
            if result is None:
                raise AlertEventNotFoundError(f"Alert event {alert_event_id} not found")
            if result.delivery_status != "failed":
                raise AlertEventNotRetryableError(
                    f"Alert event {alert_event_id} is not retryable (status={result.delivery_status!r})"
                )
            candidates = [result]
        else:
            candidates = list(db.execute(query).scalars().all())

        if limit is not None:
            candidates = candidates[:limit]

        candidate_count = len(candidates)
        retried_count = 0
        sent_count = 0
        failed_count = 0

        for event in candidates:
            # Calculer attempt_number
            max_attempt = db.execute(
                select(func.max(CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number))
                .where(CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id == event.id)
            ).scalar()
            attempt_number = (max_attempt or 0) + 1

            if dry_run:
                retried_count += 1
                continue

            # Delivery
            payload = event.payload
            delivery_channel = "log"
            delivery_status = "sent"
            delivery_error = None
            delivered_at = None

            if settings.ops_review_queue_alert_webhook_url:
                delivery_channel = "webhook"
                success, error_msg = CanonicalEntitlementAlertService._deliver_webhook(
                    settings.ops_review_queue_alert_webhook_url, payload
                )
                if success:
                    delivery_status = "sent"
                    delivered_at = datetime.now(timezone.utc)
                    sent_count += 1
                else:
                    delivery_status = "failed"
                    delivery_error = error_msg
                    failed_count += 1
            else:
                logger.info("ops_alert_retry_log_delivery payload=%s", payload)
                delivered_at = datetime.now(timezone.utc)
                sent_count += 1

            # Persister la tentative
            attempt = CanonicalEntitlementMutationAlertDeliveryAttemptModel(
                alert_event_id=event.id,
                attempt_number=attempt_number,
                delivery_channel=delivery_channel,
                delivery_status=delivery_status,
                delivery_error=delivery_error,
                request_id=request_id,
                payload=payload,
                delivered_at=delivered_at,
            )
            db.add(attempt)

            # Mettre à jour l'event parent
            event.delivery_status = delivery_status
            event.delivery_error = delivery_error
            event.delivered_at = delivered_at

            db.flush()
            retried_count += 1

        return AlertRetryRunResult(
            candidate_count=candidate_count,
            retried_count=retried_count,
            sent_count=sent_count,
            failed_count=failed_count,
            dry_run=dry_run,
        )
```

---

### Endpoints — schémas Pydantic à ajouter dans le router

```python
class AlertAttemptItem(BaseModel):
    id: int
    alert_event_id: int
    attempt_number: int
    delivery_channel: str
    delivery_status: str
    delivery_error: str | None = None
    request_id: str | None = None
    created_at: datetime
    delivered_at: datetime | None = None


class AlertAttemptsListData(BaseModel):
    items: list[AlertAttemptItem]
    total_count: int


class AlertAttemptsApiResponse(BaseModel):
    data: AlertAttemptsListData
    meta: ResponseMeta


class AlertRetryRequestBody(BaseModel):
    dry_run: bool = False


class AlertRetryResponseData(BaseModel):
    alert_event_id: int
    attempted: bool
    delivery_status: str | None = None
    attempt_number: int | None = None
    request_id: str | None = None


class AlertRetryApiResponse(BaseModel):
    data: AlertRetryResponseData
    meta: ResponseMeta
```

---

### Endpoints — GET attempts

```python
@router.get(
    "/mutation-audits/alerts/{alert_event_id}/attempts",
    response_model=AlertAttemptsApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_alert_attempts(
    alert_event_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="get_alert_attempts")
    if limit_error is not None:
        return limit_error

    # Vérifier que l'event existe
    event = db.execute(
        select(CanonicalEntitlementMutationAlertEventModel).where(
            CanonicalEntitlementMutationAlertEventModel.id == alert_event_id
        )
    ).scalar_one_or_none()
    if event is None:
        return _error_response(
            status_code=404, request_id=request_id,
            code="alert_event_not_found",
            message=f"Alert event {alert_event_id} not found",
            details={"alert_event_id": alert_event_id},
        )

    attempts = db.execute(
        select(CanonicalEntitlementMutationAlertDeliveryAttemptModel)
        .where(CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id == alert_event_id)
        .order_by(
            CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number.asc(),
            CanonicalEntitlementMutationAlertDeliveryAttemptModel.id.asc(),
        )
    ).scalars().all()

    items = [
        AlertAttemptItem(
            id=a.id,
            alert_event_id=a.alert_event_id,
            attempt_number=a.attempt_number,
            delivery_channel=a.delivery_channel,
            delivery_status=a.delivery_status,
            delivery_error=a.delivery_error,
            request_id=a.request_id,
            created_at=a.created_at,
            delivered_at=a.delivered_at,
        )
        for a in attempts
    ]

    return AlertAttemptsApiResponse(
        data=AlertAttemptsListData(items=items, total_count=len(items)),
        meta=ResponseMeta(request_id=request_id),
    )
```

---

### Endpoints — POST retry

```python
@router.post(
    "/mutation-audits/alerts/{alert_event_id}/retry",
    response_model=AlertRetryApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def retry_alert(
    alert_event_id: int,
    body: AlertRetryRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_retry_service import (
        AlertEventNotFoundError,
        AlertEventNotRetryableError,
        CanonicalEntitlementAlertRetryService,
    )

    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="retry_alert")
    if limit_error is not None:
        return limit_error

    try:
        result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db,
            dry_run=body.dry_run,
            request_id=request_id,
            alert_event_id=alert_event_id,
        )
    except AlertEventNotFoundError:
        return _error_response(
            status_code=404, request_id=request_id,
            code="alert_event_not_found",
            message=f"Alert event {alert_event_id} not found",
            details={"alert_event_id": alert_event_id},
        )
    except AlertEventNotRetryableError:
        return _error_response(
            status_code=409, request_id=request_id,
            code="alert_event_not_retryable",
            message=f"Alert event {alert_event_id} is not in failed state",
            details={"alert_event_id": alert_event_id},
        )

    if not body.dry_run:
        db.commit()

    # Récupérer le statut final de l'event
    event = db.execute(
        select(CanonicalEntitlementMutationAlertEventModel).where(
            CanonicalEntitlementMutationAlertEventModel.id == alert_event_id
        )
    ).scalar_one_or_none()

    return AlertRetryApiResponse(
        data=AlertRetryResponseData(
            alert_event_id=alert_event_id,
            attempted=result.retried_count > 0,
            delivery_status=event.delivery_status if event else None,
            attempt_number=(
                db.execute(
                    select(func.max(CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number))
                    .where(CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id == alert_event_id)
                ).scalar()
            ) if not body.dry_run else None,
            request_id=request_id,
        ),
        meta=ResponseMeta(request_id=request_id),
    )
```

> **Note dev** : Ajouter les imports nécessaires en haut du router :
> `from sqlalchemy import func` (déjà peut-être importé),
> `from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import CanonicalEntitlementMutationAlertDeliveryAttemptModel`

---

### Script CLI — pattern exact

Se baser sur `run_ops_review_queue_alerts.py` (story 61.39) :

```python
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_backend_root_on_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


def _positive_int(raw_value: str) -> int:
    parsed = int(raw_value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("--limit must be greater than 0")
    return parsed


def main() -> int:
    _ensure_backend_root_on_path()

    parser = argparse.ArgumentParser(
        description="Retry failed SLA alert deliveries for canonical entitlement mutations."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=_positive_int)
    parser.add_argument("--alert-event-id", type=int, dest="alert_event_id")
    args = parser.parse_args()

    from app.infra.db.session import SessionLocal
    from app.services.canonical_entitlement_alert_retry_service import (
        AlertEventNotFoundError,
        CanonicalEntitlementAlertRetryService,
    )

    try:
        with SessionLocal() as db:
            result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
                db,
                dry_run=args.dry_run,
                limit=args.limit,
                alert_event_id=args.alert_event_id,
            )

            if not args.dry_run:
                db.commit()

            status = "OK" if result.failed_count == 0 else "PARTIAL"
            print(
                f"[{status}] retried={result.retried_count} "
                f"sent={result.sent_count} "
                f"failed={result.failed_count} "
                f"candidates={result.candidate_count}"
            )

            return 1 if result.failed_count > 0 else 0

    except AlertEventNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 2
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        print(f"[CRITICAL] Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

---

### Tests — patterns à réutiliser

Depuis `test_ops_entitlement_mutation_audits_api.py` et `test_ops_review_queue_alerts_script.py` (61.39) :
- `_seed_audit(db, before_payload, after_payload, occurred_at=None)` — créer un audit
- `_cleanup_tables(db)` — nettoyer entre tests (ajouter `canonical_entitlement_mutation_alert_delivery_attempts` à la liste de tables à purger)
- `_register_user_with_role_and_token(client, role="ops_admin")` — auth ops

Pour créer un alert event `failed` en seed de test, insérer directement en base :

```python
def _seed_failed_alert_event(db, audit_id: int) -> int:
    """Crée un alert event failed pour les tests de retry."""
    from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
        CanonicalEntitlementMutationAlertEventModel,
    )
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:review:pending_review:sla:overdue",
        alert_kind="sla_overdue",
        risk_level_snapshot="high",
        feature_code_snapshot="test_feature",
        plan_id_snapshot=1,
        plan_code_snapshot="premium",
        actor_type_snapshot="user",
        actor_identifier_snapshot="user@test.com",
        age_seconds_snapshot=99999,
        delivery_channel="webhook",
        delivery_status="failed",
        delivery_error="Connection refused",
        payload={"alert_kind": "sla_overdue", "audit_id": audit_id},
    )
    db.add(event)
    db.flush()
    return event.id
```

Pour les tests d'intégration webhook, mocker avec `unittest.mock.patch` :

```python
with patch(
    "app.services.canonical_entitlement_alert_retry_service."
    "CanonicalEntitlementAlertService._deliver_webhook",
    return_value=(True, None),
):
    # ...
```

---

### Baseline tests (avant 61.40)

- 61.38 : **75 tests**
- 61.39 unitaires : +8 (alert service) + N (queue service)
- 61.39 intégration : +4
- **61.40 unitaires** : +7 (retry service) → nouveau fichier
- **61.40 intégration** : +6 → nouveau fichier

---

### Project Structure Notes

```
backend/
  app/
    api/v1/routers/
      ops_entitlement_mutation_audits.py  ← MODIFIER (+2 endpoints, +5 schémas Pydantic)
    services/
      canonical_entitlement_alert_retry_service.py  ← CRÉER
    infra/db/models/
      canonical_entitlement_mutation_alert_delivery_attempt.py  ← CRÉER
      __init__.py  ← MODIFIER (import avant alert_event)
    tests/
      unit/
        test_canonical_entitlement_alert_retry_service.py  ← CRÉER
      integration/
        test_ops_review_queue_alerts_retry_api.py  ← CRÉER
  migrations/versions/
    20260329_0060_create_canonical_entitlement_mutation_alert_delivery_attempts.py  ← CRÉER
  scripts/
    retry_ops_review_queue_alerts.py  ← CRÉER
  docs/
    entitlements-canonical-platform.md  ← MODIFIER (section 61.40)
  README.md  ← MODIFIER (exemple cron retry)
```

---

### Références

- [Source: backend/app/services/canonical_entitlement_alert_service.py] — `CanonicalEntitlementAlertService._deliver_webhook()`, `AlertRunResult`, pattern delivery webhook/log
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_alert_event.py] — pattern modèle SQLAlchemy exact à reproduire
- [Source: backend/app/infra/db/models/__init__.py] — ordre alphabétique, pattern `__all__`
- [Source: backend/migrations/versions/20260329_0059_create_canonical_entitlement_mutation_alert_events.py] — pattern migration Alembic exact
- [Source: backend/scripts/run_ops_review_queue_alerts.py] — pattern script CLI exact
- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — `_ensure_ops_role()`, `_enforce_limits()`, `_error_response()`, `resolve_request_id()`, patterns réponse `{data, meta}`
- [Story 61.39](61-39-alerting-ops-idempotent-sla.md) — source de `CanonicalEntitlementAlertService`, migration 0059, script CLI, tests d'intégration seed helpers

---

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- 2026-03-29 12:00 Europe/Paris — `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit/test_canonical_entitlement_alert_retry_service.py -q`
- 2026-03-29 12:05 Europe/Paris — `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit/test_canonical_entitlement_alert_retry_service.py app/tests/integration/test_ops_review_queue_alerts_retry_api.py -q`
- 2026-03-29 12:10 Europe/Paris — `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
- 2026-03-29 12:12 Europe/Paris — `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit/test_canonical_entitlement_alert_service.py app/tests/unit/test_canonical_entitlement_alert_retry_service.py app/tests/integration/test_ops_review_queue_alerts_script.py app/tests/integration/test_ops_review_queue_alerts_retry_api.py app/tests/integration/test_ops_entitlement_mutation_audits_api.py -q`
- 2026-03-29 12:15 Europe/Paris — `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit -q`
- 2026-03-29 12:18 Europe/Paris — `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/integration -q`
- 2026-03-29 12:22 Europe/Paris — `DATABASE_URL=sqlite:///.../horoscope_story_61_40_alembic_20260329.sqlite alembic upgrade head / downgrade -1 / upgrade head`

### Completion Notes List

- Implémentation du journal append-only `canonical_entitlement_mutation_alert_delivery_attempts` avec migration 0060, modèle ORM et enregistrement global SQLAlchemy.
- Ajout du service `CanonicalEntitlementAlertRetryService` pour retry batch ou ciblé, sans recréation d'alert event métier et sans `db.commit()` interne.
- Ajout des endpoints ops de consultation des tentatives et de retry ciblé avec rôles, rate limiting, 404/409 dédiés et réponses `{data, meta}`.
- Ajout du script CLI `retry_ops_review_queue_alerts.py` pour rejouer les alertes échouées en batch ou par identifiant.
- Documentation 61.40 ajoutée dans `backend/docs/entitlements-canonical-platform.md` et runbook README enrichi.
- Validation complète exécutée dans le venv Python: lint backend, suites unitaires et d'intégration complètes, non-régression 61.39 et aller-retour Alembic sur base SQLite dédiée.
- Double passe `bmad-code-review` exécutée ; la seconde revue n'a relevé aucun écart résiduel sur le cahier des charges 61.40.

### File List

- _bmad-output/implementation-artifacts/61-40-retry-replay-alertes-ops-echouees.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/canonical_entitlement_mutation_alert_delivery_attempt.py
- backend/app/services/canonical_entitlement_alert_retry_service.py
- backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py
- backend/app/tests/unit/test_canonical_entitlement_alert_retry_service.py
- backend/docs/entitlements-canonical-platform.md
- backend/migrations/versions/20260329_0059_create_canonical_entitlement_mutation_alert_events.py
- backend/migrations/versions/20260329_0060_create_canonical_entitlement_mutation_alert_delivery_attempts.py
- backend/README.md
- backend/scripts/retry_ops_review_queue_alerts.py

### Change Log

- 2026-03-29 : Story 61.40 créée — retry/replay contrôlé des alertes ops échouées, basé sur la table append-only de tentatives séparée de l'event métier.
- 2026-03-29 : Corrections review : 409 + `AlertEventNotRetryableError` pour retry ciblé sur event non `failed` ; rate limit 429 sur les deux endpoints ; `delivery_status` attempts réduit à `sent`/`failed` ; `AlertRetryRunResult` dry-run précisé ; tri attempts `attempt_number ASC, id ASC` ; 2 tests supplémentaires.
- 2026-03-29 : Implémentation complète 61.40 — migration 0060, modèle ORM des tentatives, service de retry, endpoints ops, script CLI, documentation et validations backend complètes.
- 2026-03-29 : Corrections revue BMAD n°1 — contrat `attempt_number` conservé en dry-run côté API, messages CLI clarifiés pour les erreurs métier connues, traçabilité story/git réalignée.
- 2026-03-29 : Revue BMAD n°2 propre — aucun écart supplémentaire, story 61.40 passée en `done`.
