# Story 61.36 : Historisation append-only des transitions de revue ops

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux consulter le journal complet des transitions de statut de revue pour chaque audit canonique,
afin de retracer précisément qui a changé quoi, quand, et avec quel commentaire, et d'avoir un audit trail complet de l'activité ops.

## Contexte

61.35 a introduit `canonical_entitlement_mutation_audit_reviews` (projection mutable de l'état courant de revue). Aujourd'hui on sait qu'un audit est `closed` ou `investigating`, mais on ne peut **pas** reconstituer le journal : qui l'a fait passer de `pending_review` à `investigating`, quand, puis qui l'a fermé.

**Architecture** : la table `canonical_entitlement_mutation_audit_reviews` reste la **projection de l'état courant** (upsert). La nouvelle table `canonical_entitlement_mutation_audit_review_events` est **append-only** — elle ne remplace pas la projection, elle la complète.

Flux complet ops : détection (`risk_level`) → consultation (61.33) → qualification (61.35 POST) → **historique (61.36 GET)**.

**Règle no-op** : si `upsert_review()` est appelé avec exactement les mêmes valeurs (`review_status`, `review_comment`, `incident_key`) qu'en base, **ni la projection ni l'événement ne sont modifiés** — `reviewed_at` ne bouge pas, aucun flush supplémentaire n'est effectué. Le service retourne la projection existante telle quelle.

**Statut virtuel hors historique** : `pending_review` est un artefact de lecture calculé à la volée (61.35). Il n'est **jamais** écrit en base, ni comme `new_review_status` dans un événement, ni comme `previous_review_status` implicite. Si un audit high-risk sans revue persistée reçoit sa première revue explicite, le premier événement a `previous_review_status = null` — pas `"pending_review"`.

## Acceptance Criteria

### AC 1 — Table `canonical_entitlement_mutation_audit_review_events`

1. [x] Table créée via migration Alembic avec colonnes :
   - `id` (int, PK, autoincrement)
   - `audit_id` (int, FK → `canonical_entitlement_mutation_audits.id`, NOT NULL, index)
   - `previous_review_status` (str(32), nullable — null si premier événement)
   - `new_review_status` (str(32), NOT NULL)
   - `previous_review_comment` (Text, nullable)
   - `new_review_comment` (Text, nullable)
   - `previous_incident_key` (str(64), nullable)
   - `new_incident_key` (str(64), nullable)
   - `reviewed_by_user_id` (int, nullable)
   - `occurred_at` (DateTime timezone=True, NOT NULL, server_default=CURRENT_TIMESTAMP)
   - `request_id` (str(64), nullable — corrélation optionnelle)
2. [x] Index non-unique sur `audit_id` (requêtes d'historique par audit).
3. [x] Index non-unique sur `occurred_at` (tri chronologique).
4. [x] Pas de contrainte UNIQUE — append-only pur.
5. [x] `down_revision = "20260328_0057"` (dernière migration 61.35).

### AC 2 — Modèle SQLAlchemy

6. [x] `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py` créé.
7. [x] Classe `CanonicalEntitlementMutationAuditReviewEventModel(Base)` avec `__tablename__ = "canonical_entitlement_mutation_audit_review_events"`.
8. [x] FK déclarée vers `canonical_entitlement_mutation_audits.id`.
9. [x] Pattern `Mapped[...]` / `mapped_column(...)` conforme aux modèles 61.35.
10. [x] Modèle enregistré dans `backend/app/infra/db/models/__init__.py`.

### AC 3 — Modification de `CanonicalEntitlementMutationAuditReviewService.upsert_review()`

11. [x] Signature inchangée (pas de nouveau paramètre obligatoire). Paramètre optionnel `request_id: str | None = None` ajouté.
12. [x] L'état `previous_*` est capturé **avant** tout flush de la projection. Puis, **dans la même transaction** :
    - Si aucune revue n'existait avant → INSERT projection + INSERT événement avec `previous_review_status=null`, `previous_review_comment=null`, `previous_incident_key=null`. **`previous_review_status` vaut toujours `null` (jamais `"pending_review"`)**, même si l'audit a un `risk_level="high"`.
    - Si une revue existait → comparer `(review_status, review_comment, incident_key)` avant/après :
      - **Changement détecté** → UPDATE projection (`reviewed_at = now()`) + INSERT événement avec les valeurs `previous_*` (avant) et `new_*` (après).
      - **Aucun changement (no-op)** → **ni la projection ni l'événement ne sont modifiés**. `reviewed_at` reste inchangé. Le service retourne la projection existante sans aucun `db.flush()` supplémentaire.
13. [x] L'événement est ajouté via `db.add(event)` puis `db.flush()` — **pas de `db.commit()`** (le router contrôle la transaction, comme pour la projection).
14. [x] `pending_review` n'apparaît jamais dans les champs `new_review_status` ni `previous_review_status` d'un événement — c'est un état virtuel lecture seule.

### AC 4 — Endpoint `GET /v1/ops/entitlements/mutation-audits/{audit_id}/review-history`

15. [x] Endpoint ajouté dans `ops_entitlement_mutation_audits.py`.
16. [x] Requiert authentification → **401** si token absent ou invalide (géré par `require_authenticated_user`).
17. [x] Requiert rôle `ops` ou `admin` → **403** sinon (même pattern `_ensure_ops_role`).
18. [x] Soumis au rate limit ops → **429** si dépassé (même pattern `_enforce_limits`, opération `"review_history"`).
19. [x] Vérifie que `audit_id` existe dans `canonical_entitlement_mutation_audits` → **404** sinon.
20. [x] Retourne **HTTP 200** avec `ReviewHistoryApiResponse` :
    ```json
    {
      "data": {
        "items": [
          {
            "id": 1,
            "audit_id": 42,
            "new_review_status": "acknowledged",
            "new_review_comment": "checked",
            "reviewed_by_user_id": 7,
            "occurred_at": "2026-03-28T10:00:00Z"
          }
        ],
        "total_count": 1
      },
      "meta": { "request_id": "..." }
    }
    ```
    *(les champs `previous_*` null sont omis dans l'exemple car `response_model_exclude_none=True`)*
21. [x] Items triés par `occurred_at` ASC (ordre chronologique des transitions).
22. [x] `response_model_exclude_none=True` actif — les champs `previous_*` null sont **omis** de la réponse JSON (premier événement d'un audit sera donc sans champs `previous_*`).
23. [x] Aucune pagination (l'historique d'un audit restera raisonnable en volume).

### AC 5 — Schémas Pydantic

24. [x] `ReviewEventItem` : champs `id`, `audit_id`, `previous_review_status`, `new_review_status`, `previous_review_comment`, `new_review_comment`, `previous_incident_key`, `new_incident_key`, `reviewed_by_user_id`, `occurred_at`, `request_id` — tous optionnels sauf `id`, `audit_id`, `new_review_status`, `occurred_at`.
25. [x] `ReviewHistoryData` : `items: list[ReviewEventItem]`, `total_count: int`.
26. [x] `ReviewHistoryApiResponse` : `data: ReviewHistoryData`, `meta: ResponseMeta`.

### AC 5b — Séparation service / router (pattern existant à conserver)

27. [x] Le service `upsert_review()` lève `AuditNotFoundError` (exception métier, déjà en place en 61.35) — **jamais `HTTPException`**. Le router convertit cette exception en `_error_response(404)` dans le bloc `except AuditNotFoundError`.
28. [x] L'endpoint GET review-history vérifie l'existence de l'audit directement via `db.get()` dans le router et retourne `_error_response(404)` si absent — ce pattern est cohérent avec la séparation service/router : pas besoin de passer par le service pour une lecture simple.

### AC 6 — Tests unitaires

29. [x] `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` enrichi avec :
    - `test_upsert_creates_event_on_first_review` — premier appel crée un événement avec `previous_review_status=None` (jamais `"pending_review"`)
    - `test_upsert_creates_event_on_status_change` — update avec statut différent crée un événement avec les bonnes valeurs `previous_*`
    - `test_upsert_no_event_on_noop` — appel avec mêmes valeurs n'insère aucun événement **et ne modifie pas la projection** (`reviewed_at` inchangé, `db.flush` non rappelé)
    - `test_upsert_event_carries_request_id` — le `request_id` est propagé dans l'événement
    - `test_upsert_transactional_rollback` — si l'INSERT de l'événement échoue, la projection n'est pas committée (via rollback)

### AC 7 — Tests d'intégration

30. [x] `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` enrichi avec :
    - `test_get_review_history_empty_returns_200` — audit sans revue → `items=[]`, `total_count=0`
    - `test_get_review_history_after_one_review` — après un POST review → 1 événement, champs `previous_*` absents de la réponse JSON (omis via exclude_none)
    - `test_get_review_history_chain_of_transitions` — 3 POST successifs → 3 événements en ordre chronologique ASC, les `previous_*` enchaînés correctement
    - `test_get_review_history_noop_no_event_created` — POST avec mêmes valeurs → pas de nouvel événement, `total_count` inchangé
    - `test_get_review_history_nonexistent_audit_returns_404` — 404 avec `code="audit_not_found"`
    - `test_get_review_history_unauthenticated_returns_401` — 401 si pas de token
    - `test_get_review_history_requires_ops_role` — 403 si rôle `user`
    - `test_get_review_history_request_id_propagated` — `request_id` passé via header `X-Request-Id` se retrouve dans l'événement
31. [x] Les tests existants 61.35 (46 tests) restent verts.

### AC 8 — Non-régression sur le POST review

32. [x] L'appel `POST /v1/ops/entitlements/mutation-audits/{audit_id}/review` passe le `request_id` HTTP au service (via `resolve_request_id(request)`).
33. [x] Le router passe `request_id=request_id` au `upsert_review()`.
34. [x] Le comportement de réponse du POST (201, body `ReviewResponse`) est **inchangé** — pas de champ supplémentaire dans la réponse POST.

### AC 9 — Documentation

35. [x] `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.36 — Historisation append-only des transitions de revue"** décrivant :
    - La table `canonical_entitlement_mutation_audit_review_events` et son schéma.
    - La règle no-op complète : aucun changement sur la projection, aucun événement, `reviewed_at` inchangé.
    - Le fait que `pending_review` (état virtuel) n'est jamais persisté dans l'historique.
    - L'endpoint GET review-history et son contrat de réponse.
    - La propagation du `request_id` HTTP dans les événements.

### AC 10 — Périmètre strict

36. [x] `canonical_entitlement_mutation_service.py` — **non modifié**.
37. [x] `canonical_entitlement_mutation_audit_query_service.py` — **non modifié**.
38. [x] `canonical_entitlement_mutation_audit.py` (modèle audit) — **non modifié**.
39. [x] `canonical_entitlement_mutation_audit_review.py` (modèle projection) — **non modifié**.
40. [x] Seuls fichiers existants modifiés : `canonical_entitlement_mutation_audit_review_service.py`, `ops_entitlement_mutation_audits.py`, `__init__.py` (models), `test_ops_entitlement_mutation_audits_api.py`, `test_canonical_entitlement_mutation_audit_review_service.py`, `entitlements-canonical-platform.md`.

---

## Tasks / Subtasks

- [x] **Créer le modèle SQLAlchemy** (AC: 2)
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py`
  - [x] Définir `CanonicalEntitlementMutationAuditReviewEventModel(Base)` avec tous les champs, FK, et index
  - [x] Enregistrer dans `backend/app/infra/db/models/__init__.py`

- [x] **Créer la migration Alembic** (AC: 1)
  - [x] Créer `backend/migrations/versions/20260328_0058_create_canonical_entitlement_mutation_audit_review_events.py`
  - [x] `down_revision = "20260328_0057"`
  - [x] `upgrade()` : `op.create_table(...)` + index sur `audit_id` + index sur `occurred_at`
  - [x] `downgrade()` : `op.drop_index(...)` + `op.drop_table(...)`

- [x] **Modifier `CanonicalEntitlementMutationAuditReviewService.upsert_review()`** (AC: 3)
  - [x] Ajouter paramètre optionnel `request_id: str | None = None`
  - [x] Capturer l'état `previous_*` avant l'upsert (ou None si c'est une création)
  - [x] Détecter le no-op après upsert
  - [x] Insérer l'événement si changement réel, skip si no-op
  - [x] `db.add(event)` + `db.flush()` dans la même transaction

- [x] **Modifier le router — propagation `request_id` au service** (AC: 8)
  - [x] Dans `post_review`, passer `request_id=request_id` à `upsert_review()`

- [x] **Ajouter les schémas Pydantic** (AC: 5)
  - [x] `ReviewEventItem`, `ReviewHistoryData`, `ReviewHistoryApiResponse` dans le router

- [x] **Ajouter l'endpoint GET `/review-history`** (AC: 4)
  - [x] Route `GET /v1/ops/entitlements/mutation-audits/{audit_id}/review-history`
  - [x] Vérification rôle + rate limit
  - [x] Vérification existence `audit_id` (404 sinon)
  - [x] Requête SELECT … WHERE audit_id=… ORDER BY occurred_at ASC
  - [x] Retour 200 avec `ReviewHistoryApiResponse`

- [x] **Tests unitaires** (AC: 6)
  - [x] Enrichir `test_canonical_entitlement_mutation_audit_review_service.py` avec 5 nouveaux cas

- [x] **Tests d'intégration** (AC: 7)
  - [x] Enrichir `test_ops_entitlement_mutation_audits_api.py` avec 7 nouveaux cas

- [x] **Documentation** (AC: 9)
  - [x] `backend/docs/entitlements-canonical-platform.md` — section 61.36

- [x] **Validation finale**
  - [x] `ruff check` — zéro erreur
  - [x] `pytest unit` — tous verts (dont les 4 existants 61.35 + 5 nouveaux)
  - [x] `pytest integration` — tous verts (dont les 42 existants 61.35 + 7 nouveaux)

---

## Dev Notes

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py` | Créer |
| `backend/app/infra/db/models/__init__.py` | Modifier — enregistrer le nouveau modèle |
| `backend/migrations/versions/20260328_0058_create_canonical_entitlement_mutation_audit_review_events.py` | Créer |
| `backend/app/services/canonical_entitlement_mutation_audit_review_service.py` | Modifier |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier |
| `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` | Modifier |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Modifier |
| `backend/docs/entitlements-canonical-platform.md` | Modifier |

**NE PAS modifier** :
- `backend/app/services/canonical_entitlement_mutation_service.py`
- `backend/app/services/canonical_entitlement_mutation_audit_query_service.py`
- `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py`
- `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py`

---

### Pattern Session SQLAlchemy (CRITIQUE)

Le service utilise **`Session` synchrone** (pas `AsyncSession`). Vérifier dans le service existant :

```python
# backend/app/services/canonical_entitlement_mutation_audit_review_service.py
from sqlalchemy.orm import Session  # synchrone — PAS AsyncSession
```

Le router utilise `get_db_session` (synchrone) et `Session` :
```python
from app.infra.db.session import get_db_session
db: Session = Depends(get_db_session)
```

**Ne pas introduire d'`async def` dans le service** — le projet utilise des sessions synchrones dans ce router.

---

### Pattern Modèle SQLAlchemy (conforme à 61.35)

```python
# backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalEntitlementMutationAuditReviewEventModel(Base):
    __tablename__ = "canonical_entitlement_mutation_audit_review_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_audits.id"),
        nullable=False,
        index=True,
    )
    previous_review_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    previous_review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    new_incident_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reviewed_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, index=True
    )
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
```

---

### Pattern Migration Alembic

```python
# backend/migrations/versions/20260328_0058_create_canonical_entitlement_mutation_audit_review_events.py
"""create canonical_entitlement_mutation_audit_review_events

Revision ID: 20260328_0058
Revises: 20260328_0057
Create Date: 2026-03-28
"""

import sqlalchemy as sa
from alembic import op

revision = "20260328_0058"
down_revision = "20260328_0057"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_audit_review_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "audit_id",
            sa.Integer(),
            sa.ForeignKey("canonical_entitlement_mutation_audits.id"),
            nullable=False,
        ),
        sa.Column("previous_review_status", sa.String(32), nullable=True),
        sa.Column("new_review_status", sa.String(32), nullable=False),
        sa.Column("previous_review_comment", sa.Text(), nullable=True),
        sa.Column("new_review_comment", sa.Text(), nullable=True),
        sa.Column("previous_incident_key", sa.String(64), nullable=True),
        sa.Column("new_incident_key", sa.String(64), nullable=True),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cemaret_audit_id",
        "canonical_entitlement_mutation_audit_review_events",
        ["audit_id"],
    )
    op.create_index(
        "ix_cemaret_occurred_at",
        "canonical_entitlement_mutation_audit_review_events",
        ["occurred_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cemaret_occurred_at",
        table_name="canonical_entitlement_mutation_audit_review_events",
    )
    op.drop_index(
        "ix_cemaret_audit_id",
        table_name="canonical_entitlement_mutation_audit_review_events",
    )
    op.drop_table("canonical_entitlement_mutation_audit_review_events")
```

---

### Pattern Service modifié

```python
# Signature étendue — nouveau paramètre optionnel request_id
@staticmethod
def upsert_review(
    db: Session,
    *,
    audit_id: int,
    review_status: str,
    reviewed_by_user_id: int | None,
    review_comment: str | None,
    incident_key: str | None,
    request_id: str | None = None,  # NOUVEAU — optionnel pour compat 61.35
) -> CanonicalEntitlementMutationAuditReviewModel:
    audit = db.get(CanonicalEntitlementMutationAuditModel, audit_id)
    if audit is None:
        raise AuditNotFoundError(audit_id)

    # Capturer l'état AVANT l'upsert
    existing_review = CanonicalEntitlementMutationAuditReviewService._get_review_by_audit_id(db, audit_id)

    is_creation = existing_review is None
    previous_status = None if is_creation else existing_review.review_status
    previous_comment = None if is_creation else existing_review.review_comment
    previous_incident = None if is_creation else existing_review.incident_key

    # ... upsert de la projection (code existant 61.35 inchangé) ...

    # Détection no-op (uniquement sur update)
    # IMPORTANT : en cas de no-op, la projection n'est PAS modifiée (pas de flush sur reviewed_at).
    # Le service retourne la projection existante sans aucune écriture.
    if not is_creation:
        is_noop = (
            previous_status == review_status
            and previous_comment == review_comment
            and previous_incident == incident_key
        )
        if is_noop:
            return review  # ni flush, ni event, ni changement de reviewed_at

    # INSERT événement (reached only if creation OR real change)
    now = datetime.now(timezone.utc)
    event = CanonicalEntitlementMutationAuditReviewEventModel(
        audit_id=audit_id,
        previous_review_status=previous_status,
        new_review_status=review_status,
        previous_review_comment=previous_comment,
        new_review_comment=review_comment,
        previous_incident_key=previous_incident,
        new_incident_key=incident_key,
        reviewed_by_user_id=reviewed_by_user_id,
        occurred_at=now,
        request_id=request_id,
    )
    db.add(event)
    db.flush()
    return review
```

> **Important** : le `occurred_at` de l'événement doit être cohérent avec le `reviewed_at` de la projection. Utiliser la même variable `now` pour les deux.

---

### Pattern Endpoint GET review-history

```python
@router.get(
    "/mutation-audits/{audit_id}/review-history",
    response_model=ReviewHistoryApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_review_history(
    audit_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="review_history")
    if limit_error is not None:
        return limit_error

    # Vérification existence de l'audit
    from app.infra.db.models.canonical_entitlement_mutation_audit import CanonicalEntitlementMutationAuditModel
    audit = db.get(CanonicalEntitlementMutationAuditModel, audit_id)
    if audit is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="audit_not_found",
            message=f"Audit {audit_id} not found",
            details={"audit_id": audit_id},
        )

    result = db.execute(
        select(CanonicalEntitlementMutationAuditReviewEventModel)
        .where(CanonicalEntitlementMutationAuditReviewEventModel.audit_id == audit_id)
        .order_by(CanonicalEntitlementMutationAuditReviewEventModel.occurred_at.asc())
    )
    events = result.scalars().all()

    return {
        "data": {
            "items": [
                {
                    "id": e.id,
                    "audit_id": e.audit_id,
                    "previous_review_status": e.previous_review_status,
                    "new_review_status": e.new_review_status,
                    "previous_review_comment": e.previous_review_comment,
                    "new_review_comment": e.new_review_comment,
                    "previous_incident_key": e.previous_incident_key,
                    "new_incident_key": e.new_incident_key,
                    "reviewed_by_user_id": e.reviewed_by_user_id,
                    "occurred_at": e.occurred_at,
                    "request_id": e.request_id,
                }
                for e in events
            ],
            "total_count": len(events),
        },
        "meta": {"request_id": request_id},
    }
```

---

### Schémas Pydantic à ajouter dans le router

```python
class ReviewEventItem(BaseModel):
    id: int
    audit_id: int
    previous_review_status: ReviewStatusLiteral | None = None
    new_review_status: ReviewStatusLiteral
    previous_review_comment: str | None = None
    new_review_comment: str | None = None
    previous_incident_key: str | None = None
    new_incident_key: str | None = None
    reviewed_by_user_id: int | None = None
    occurred_at: datetime
    request_id: str | None = None


class ReviewHistoryData(BaseModel):
    items: list[ReviewEventItem]
    total_count: int


class ReviewHistoryApiResponse(BaseModel):
    data: ReviewHistoryData
    meta: ResponseMeta
```

---

### Propagation `request_id` dans le POST review (AC 8)

Dans l'endpoint `post_review` existant, passer le `request_id` HTTP au service :

```python
# AVANT (61.35) :
review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
    db,
    audit_id=audit_id,
    review_status=body.review_status,
    reviewed_by_user_id=current_user.id,
    review_comment=body.review_comment,
    incident_key=body.incident_key,
)

# APRÈS (61.36) — ajouter request_id :
review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
    db,
    audit_id=audit_id,
    review_status=body.review_status,
    reviewed_by_user_id=current_user.id,
    review_comment=body.review_comment,
    incident_key=body.incident_key,
    request_id=request_id,  # AJOUT
)
```

---

### Règle no-op — sémantique complète

En cas de no-op (`review_status`, `review_comment`, `incident_key` identiques à la projection courante) :
- **La projection n'est PAS mise à jour** — `reviewed_at` reste la valeur précédente.
- **Aucun événement n'est inséré**.
- **Aucun `db.flush()` supplémentaire** n'est appelé après le retour anticipé.
- Le service retourne l'objet projection existant tel quel.

La détection compare les 3 champs **tels quels** (pas de normalisation) :
- `None` == `None` → égal
- `""` != `None` → différent (pas no-op)

En pratique, le body Pydantic déclare `str | None = None` donc les valeurs vides du client arrivent comme `None` — pas de cas `""` à gérer.

**`pending_review` jamais dans l'historique** : le premier événement d'un audit high-risk sans revue préalable aura toujours `previous_review_status = null`. Ne pas confondre le statut virtuel de lecture avec un état persisté.

---

### Tests unitaires — pattern mock 61.35

Les tests unitaires existants utilisent `MagicMock` pour simuler la `Session`. Reproduire ce pattern :

```python
# test_upsert_creates_event_on_first_review
def test_upsert_creates_event_on_first_review():
    db = MagicMock()
    audit = MagicMock()
    db.get.return_value = audit  # audit existe

    # Pas de revue existante
    db.execute.return_value.scalar_one_or_none.return_value = None

    result = CanonicalEntitlementMutationAuditReviewService.upsert_review(
        db,
        audit_id=1,
        review_status="acknowledged",
        reviewed_by_user_id=7,
        review_comment="ok",
        incident_key=None,
        request_id="req-abc",
    )

    # db.add() appelé 2 fois : 1x projection + 1x événement
    assert db.add.call_count == 2
    event_arg = db.add.call_args_list[1][0][0]
    assert isinstance(event_arg, CanonicalEntitlementMutationAuditReviewEventModel)
    assert event_arg.previous_review_status is None
    assert event_arg.new_review_status == "acknowledged"
    assert event_arg.request_id == "req-abc"
```

---

### Rollback transactionnel — pattern test

```python
# test_upsert_transactional_rollback
def test_upsert_transactional_rollback():
    """Si db.flush() sur l'event lève une exception, la session peut rollback."""
    db = MagicMock()
    db.get.return_value = MagicMock()  # audit existe
    db.execute.return_value.scalar_one_or_none.return_value = None

    # Simuler un flush qui échoue sur le 2ème appel (après l'insertion de l'événement)
    flush_call_count = {"n": 0}
    def flush_side_effect():
        flush_call_count["n"] += 1
        if flush_call_count["n"] == 2:
            raise Exception("DB error on event insert")
    db.flush.side_effect = flush_side_effect

    with pytest.raises(Exception, match="DB error"):
        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db, audit_id=1, review_status="closed",
            reviewed_by_user_id=1, review_comment=None, incident_key=None,
        )
```

---

### Project Structure Notes

```
backend/
  migrations/versions/
    20260328_0058_create_canonical_entitlement_mutation_audit_review_events.py  ← CRÉER
  app/
    infra/db/models/
      canonical_entitlement_mutation_audit_review_event.py  ← CRÉER
      __init__.py  ← MODIFIER (enregistrement)
    services/
      canonical_entitlement_mutation_audit_review_service.py  ← MODIFIER
    api/v1/routers/
      ops_entitlement_mutation_audits.py  ← MODIFIER
    tests/
      unit/
        test_canonical_entitlement_mutation_audit_review_service.py  ← MODIFIER (+5 tests)
      integration/
        test_ops_entitlement_mutation_audits_api.py  ← MODIFIER (+7 tests)
  docs/
    entitlements-canonical-platform.md  ← MODIFIER
```

---

### Références

- [Source: backend/app/services/canonical_entitlement_mutation_audit_review_service.py] — service à étendre (synchrone, `Session`)
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py] — modèle projection à ne pas modifier, pattern `Mapped[...]` à reproduire
- [Source: backend/migrations/versions/20260328_0057_create_canonical_entitlement_mutation_audit_reviews.py] — migration 61.35 (`down_revision` cible)
- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — router à étendre (helpers `_ensure_ops_role`, `_enforce_limits`, `_error_response`, `resolve_request_id`)
- [Source: backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py] — patterns tests d'intégration (`_cleanup_tables`, `_seed_audit`, `_register_user_with_role_and_token`)
- [Source: backend/docs/entitlements-canonical-platform.md] — documentation à compléter

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- AC 1 à 10 implémentés et validés par tests.
- Règle no-op stricte respectée (pas de changement de `reviewed_at`).
- `pending_review` correctement traité comme statut virtuel (jamais persisté).
- Propagation du `request_id` opérationnelle sur POST et GET history.
- Couverture de tests augmentée sur les courses de création et le contrat de schéma de l'historique.
- Correctif revue AI : no-op restauré après course sur la première création de revue, et contrat `ReviewEventItem` resserré pour exclure `pending_review`.

### File List

- `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py` (créé)
- `backend/app/infra/db/models/__init__.py` (modifié)
- `backend/migrations/versions/20260328_0058_create_canonical_entitlement_mutation_audit_review_events.py` (créé)
- `backend/app/services/canonical_entitlement_mutation_audit_review_service.py` (modifié)
- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` (modifié)
- `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` (modifié)
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` (modifié)
- `backend/docs/entitlements-canonical-platform.md` (modifié)

### Change Log

- 2026-03-28 : Story 61.36 créée.
- 2026-03-28 : Durcissement pre-dev — 4 points : (1) no-op = projection inchangée + reviewed_at stable + aucun flush ; (2) pending_review virtuel jamais dans les events (previous_review_status toujours null au premier event) ; (3) 401/403/429 explicites dans AC 4 ; (4) pattern AuditNotFoundError confirmé existant, GET review-history utilise _error_response(404) directement dans le router.
- 2026-03-28 : Implémentation complète story 61.36.
- 2026-03-28 : Code review et correctifs (WritableReviewStatusLiteral, test rollback via mocks).
- 2026-03-28 : Revue senior AI post-implémentation — correction du no-op en cas de course sur la première création, tri stable de l'historique, verrouillage du schéma `ReviewEventItem` contre `pending_review`, tests et documentation mis à jour.

## Senior Developer Review (AI)

### Findings

1. [High] `backend/app/services/canonical_entitlement_mutation_audit_review_service.py` : en cas de course sur la première création, le chemin `IntegrityError` mettait à jour la projection et insérait un événement même si la revue concurrente avait déjà exactement les mêmes valeurs métier. Cela violait la règle no-op de l'AC 3 en modifiant `reviewed_at` et en ajoutant un événement parasite.
2. [Medium] `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` : `ReviewEventItem` annonçait encore `pending_review` comme valeur possible pour `previous_review_status` et `new_review_status`, alors que l'AC 3.14 interdit explicitement ce statut dans l'historique. Le contrat OpenAPI exposait donc une valeur impossible.

### Fixes Applied

1. Le service recharge désormais l'état concurrent persistant après `IntegrityError`, recalcule le no-op sur les valeurs réellement en base, puis saute toute écriture si la demande est déjà satisfaite.
2. Le schéma `ReviewEventItem` utilise désormais un type de statut persisté excluant `pending_review`, et le tri de l'historique est stabilisé par `occurred_at ASC, id ASC`.
3. Tests ajoutés : course concurrente no-op sans événement parasite, et validation de schéma rejetant `pending_review` pour un event.
