# Story 61.33 : Exposition ops en lecture de l'audit trail canonique

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux consulter les lignes de `canonical_entitlement_mutation_audits` via une API interne paginée et filtrable,
afin d'investiguer les changements de bindings/quotas, d'identifier leur origine, et de corréler une régression à une mutation précise.

## Contexte

La story 61.32 a introduit un audit trail transactionnel fiable dans `canonical_entitlement_mutation_audits`.
Cette table est alimentée automatiquement par `CanonicalEntitlementMutationService.upsert_plan_feature_configuration`.

Aujourd'hui, les lignes existent en base mais aucun outil interne ne permet de les consulter sans passer directement par SQL.
Cette story rend l'audit trail **actionnable** via une API ops read-only, cohérente avec les autres endpoints ops du projet.

**Scope strict** : consultation uniquement. Pas de rollback, replay, revert, ni écriture en base.

## Acceptance Criteria

### AC 1 — Endpoint liste paginé et filtrable

1. `GET /v1/ops/entitlements/mutation-audits` retourne une liste paginée des audits, triée `occurred_at desc, id desc`.
2. Paramètres de filtre optionnels acceptés :
   - `plan_id` (int)
   - `plan_code` (str, match exact sur `plan_code_snapshot`)
   - `feature_code` (str)
   - `actor_type` (str)
   - `actor_identifier` (str, match exact)
   - `source_origin` (str)
   - `request_id` (str)
   - `date_from` (datetime ISO8601)
   - `date_to` (datetime ISO8601)
   - `include_payloads` (bool, default `false`)
2.b Les filtres temporels sont inclusifs :
   - `date_from` → `occurred_at >= date_from`
   - `date_to`   → `occurred_at <= date_to`
3. Pagination via `page` (≥ 1, défaut 1) et `page_size` (1–100, défaut 20).
4. La réponse a la forme :
   ```json
   {
     "data": {
       "items": [...],
       "total_count": int,
       "page": int,
       "page_size": int
     },
     "meta": { "request_id": "..." }
   }
   ```
   Chaque item contient : `id`, `occurred_at`, `operation`, `plan_id`, `plan_code_snapshot`, `feature_code`, `actor_type`, `actor_identifier`, `request_id`, `source_origin`.
5. Si `include_payloads=true`, ajoute `before_payload` et `after_payload` à chaque item.
   Si `include_payloads=false` (défaut), ces champs sont **omis** de la réponse JSON (pas présents à `null`).

### AC 2 — Endpoint détail par ID

6. `GET /v1/ops/entitlements/mutation-audits/{audit_id}` retourne l'audit complet incluant `before_payload` et `after_payload`.
7. Retourne 404 avec code `audit_not_found` si l'`audit_id` n'existe pas.

### AC 3 — Contrôle d'accès

8. Les deux endpoints retournent 403 (`insufficient_role`) si le rôle de l'appelant n'est pas `ops` ou `admin`.
9. Un utilisateur authentifié avec rôle `user` ou `b2b` reçoit 403.
10. Un appel non authentifié retourne 401.

### AC 4 — Rate limiting

11. Rate limits (clés uniformes entre AC et Dev Notes) :
    - `ops_entitlement_mutation_audits:global:{operation}` — 60 req/min
    - `ops_entitlement_mutation_audits:role:{role}:{operation}` — 30 req/min
    - `ops_entitlement_mutation_audits:user:{user_id}:{operation}` — 15 req/min

### AC 5 — Aucune écriture DB

12. Aucune écriture, flush, commit dans le service de query ni dans le router.
13. Le service `CanonicalEntitlementMutationAuditQueryService` est en lecture stricte.

### AC 6 — Service de query dédié

14. La logique SQL est encapsulée dans `CanonicalEntitlementMutationAuditQueryService` dans un fichier dédié.
15. Le router ne contient aucune requête SQLAlchemy directe.
16. Les deux méthodes publiques du service sont :
    - `list_mutation_audits(db, *, page, page_size, plan_id=None, plan_code=None, feature_code=None, actor_type=None, actor_identifier=None, source_origin=None, request_id=None, date_from=None, date_to=None) -> tuple[list[CanonicalEntitlementMutationAuditModel], int]`
    - `get_mutation_audit_by_id(db, audit_id) -> CanonicalEntitlementMutationAuditModel | None`
    `include_payloads` est une décision de sérialisation du **router**, pas du service.

### AC 7 — Tests d'intégration

17. `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` est créé avec au minimum :
    - `test_list_returns_empty_when_no_audits` : liste vide → `items=[]`, `total_count=0`
    - `test_list_returns_audits_sorted_desc` : 3 audits créés → retournés par `occurred_at desc`
    - `test_list_filter_by_feature_code` : filtre exact sur `feature_code`
    - `test_list_filter_by_actor_type` : filtre exact sur `actor_type`
    - `test_list_filter_by_plan_code` : filtre exact sur `plan_code_snapshot`
    - `test_list_filter_by_request_id` : filtre exact sur `request_id`
    - `test_list_filter_by_date_range` : `date_from`/`date_to` inclusifs — seuls les audits dans la plage sont retournés
    - `test_list_pagination` : page 2 avec page_size=2 sur 3 audits
    - `test_list_include_payloads_false` : `before_payload`/`after_payload` **absents** (pas `null`) par défaut
    - `test_list_include_payloads_true` : payloads présents si `include_payloads=true`
    - `test_detail_returns_audit_with_payloads` : détail complet via `/{audit_id}`
    - `test_detail_returns_404_on_unknown_id` : id inexistant → 404
    - `test_detail_returns_403_for_non_ops_role` : rôle `user` → 403 sur le endpoint détail
    - `test_detail_returns_401_when_unauthenticated` : pas de token → 401 sur le endpoint détail
    - `test_list_returns_403_for_non_ops_role` : rôle `user` → 403
    - `test_list_returns_401_when_unauthenticated` : pas de token → 401

### AC 8 — Documentation

18. `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Story 61.33 — Exposition ops de l'audit trail (endpoint de consultation)"**.
19. La doc décrit les deux endpoints, les filtres disponibles, et le comportement de `include_payloads`.

### AC 9 — Non-régression

20. Aucun contrat API public modifié.
21. Pas de migration Alembic (la table est déjà créée en 61.32).
22. Les suites 61.31 et 61.32 restent vertes.

---

## Tasks / Subtasks

- [x] **Créer `CanonicalEntitlementMutationAuditQueryService`** (AC: 5, 6)
  - [x] Créer `backend/app/services/canonical_entitlement_mutation_audit_query_service.py`
  - [x] Implémenter `list_mutation_audits(db, *, page, page_size, plan_id, plan_code, feature_code, actor_type, actor_identifier, source_origin, request_id, date_from, date_to)` → `(list[...], int)` — pas de `include_payloads` ici
  - [x] Implémenter `get_mutation_audit_by_id(db, audit_id)` → `model | None`
  - [x] Tri stable : `occurred_at desc, id desc`

- [x] **Créer les schémas Pydantic** (AC: 1, 2, 4)
  - [x] `MutationAuditItem` — modèle unique avec `before_payload`/`after_payload` optionnels (`dict | None = None`)
  - [x] `MutationAuditListData` (items, total_count, page, page_size)
  - [x] Router déclare `response_model_exclude_none=True` pour que les payloads soient omis quand `include_payloads=false`

- [x] **Créer le router ops** (AC: 1, 2, 3, 4, 5)
  - [x] Créer `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
  - [x] `GET /v1/ops/entitlements/mutation-audits` avec filtres + pagination
  - [x] `GET /v1/ops/entitlements/mutation-audits/{audit_id}`
  - [x] `_ensure_ops_role`, `_enforce_limits`, `_error_response` (copier pattern des autres routers ops)

- [x] **Enregistrer le router** (AC: 1)
  - [x] Ajouter import dans `backend/app/main.py`
  - [x] Ajouter import + `__all__` dans `backend/app/api/v1/routers/__init__.py`
  - [x] Appeler `app.include_router(...)` dans `main.py`

- [x] **Créer les tests d'intégration** (AC: 7)
  - [x] `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
  - [x] Seed 3 audits de types différents en setup (feature_codes distincts, actor_types distincts, request_ids distincts, dates distinctes)
  - [x] Couvrir les 16 cas listés en AC 7

- [x] **Mettre à jour la documentation** (AC: 8)
  - [x] `backend/docs/entitlements-canonical-platform.md`

- [x] **Validation finale** (AC: 9)
  - [x] `ruff check` sur les fichiers créés/modifiés
  - [x] `pytest backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_mutation_audit.py`
  - [x] `pytest backend/app/tests/unit/test_canonical_entitlement_mutation_service.py`

---

## Dev Agent Record

### Agent Model Used
Gemini CLI

### Debug Log References
- Integration tests pass: 16/16
- Unit tests pass: 25/25
- Ruff check: Fixed long lines and unused imports.

### Completion Notes List
- Implemented `CanonicalEntitlementMutationAuditQueryService` for SQL logic.
- Implemented `ops_entitlement_mutation_audits` router with Pydantic schemas.
- Registered router in `main.py` and `api/v1/routers/__init__.py`.
- Added comprehensive integration tests covering all ACs.
- Updated architectural documentation.

### File List
- `backend/app/services/canonical_entitlement_mutation_audit_query_service.py`
- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/main.py`
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
- `backend/docs/entitlements-canonical-platform.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-28: Initial implementation of Story 61.33.

## Dev Notes

### Architecture

Ce pattern est **identique** à `b2b_entitlements_audit.py` (router + service query) et `ops_monitoring.py` (contrôle d'accès). Réutiliser exactement ces patterns — ne pas réinventer.

**Fichiers à créer / modifier :**

| Fichier | Action |
|---------|--------|
| `backend/app/services/canonical_entitlement_mutation_audit_query_service.py` | Créer |
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Créer |
| `backend/app/api/v1/routers/__init__.py` | Modifier — ajouter import + `__all__` |
| `backend/app/main.py` | Modifier — importer et include_router |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Créer |
| `backend/docs/entitlements-canonical-platform.md` | Mettre à jour |

### Modèle ORM existant (61.32)

```python
# backend/app/infra/db/models/canonical_entitlement_mutation_audit.py
class CanonicalEntitlementMutationAuditModel(Base):
    __tablename__ = "canonical_entitlement_mutation_audits"
    id: Mapped[int]
    occurred_at: Mapped[datetime]  # index
    operation: Mapped[str]
    plan_id: Mapped[int]           # index
    plan_code_snapshot: Mapped[str]
    feature_code: Mapped[str]      # index
    actor_type: Mapped[str]
    actor_identifier: Mapped[str]
    request_id: Mapped[str | None]
    source_origin: Mapped[str]
    before_payload: Mapped[dict]   # JSON
    after_payload: Mapped[dict]    # JSON
```

Pas de FK sur `plan_id` — table append-only.

### Patron exact du service de query

```python
# backend/app/services/canonical_entitlement_mutation_audit_query_service.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)


class CanonicalEntitlementMutationAuditQueryService:
    @staticmethod
    def list_mutation_audits(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        plan_id: int | None = None,
        plan_code: str | None = None,
        feature_code: str | None = None,
        actor_type: str | None = None,
        actor_identifier: str | None = None,
        source_origin: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[CanonicalEntitlementMutationAuditModel], int]:
        q = select(CanonicalEntitlementMutationAuditModel)
        if plan_id is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.plan_id == plan_id)
        if plan_code is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.plan_code_snapshot == plan_code)
        if feature_code is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.feature_code == feature_code)
        if actor_type is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.actor_type == actor_type)
        if actor_identifier is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.actor_identifier == actor_identifier)
        if source_origin is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.source_origin == source_origin)
        if request_id is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.request_id == request_id)
        if date_from is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.occurred_at >= date_from)
        if date_to is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.occurred_at <= date_to)

        count_q = select(func.count()).select_from(q.subquery())
        total_count = db.scalar(count_q) or 0

        q = (
            q.order_by(
                CanonicalEntitlementMutationAuditModel.occurred_at.desc(),
                CanonicalEntitlementMutationAuditModel.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(db.scalars(q).all())
        return items, total_count

    @staticmethod
    def get_mutation_audit_by_id(
        db: Session, audit_id: int
    ) -> CanonicalEntitlementMutationAuditModel | None:
        return db.get(CanonicalEntitlementMutationAuditModel, audit_id)
```

### Patron exact du router

**CRITIQUE** : Copier exactement le patron de `b2b_entitlements_audit.py` pour `_error_response`, `_ensure_ops_role`, `_enforce_limits`. Ne pas réinventer.

```python
# backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
router = APIRouter(prefix="/v1/ops/entitlements", tags=["ops-entitlement-audits"])

# Rate limits — clés identiques aux AC :
# key: f"ops_entitlement_mutation_audits:global:{operation}", limit=60, window_seconds=60
# key: f"ops_entitlement_mutation_audits:role:{user.role}:{operation}", limit=30, window_seconds=60
# key: f"ops_entitlement_mutation_audits:user:{user.id}:{operation}", limit=15, window_seconds=60
```

**Schémas Pydantic — modèle unique avec payloads optionnels** :

Utiliser un seul modèle `MutationAuditItem` avec `before_payload`/`after_payload` optionnels et `response_model_exclude_none=True` sur les deux endpoints de liste et de détail. Cela évite les surprises de sérialisation liées aux unions Pydantic et garantit que les champs sont **absents** (pas `null`) quand `include_payloads=false`.

```python
class MutationAuditItem(BaseModel):
    id: int
    occurred_at: datetime
    operation: str
    plan_id: int
    plan_code_snapshot: str
    feature_code: str
    actor_type: str
    actor_identifier: str
    request_id: str | None
    source_origin: str
    before_payload: dict | None = None  # omis si None grâce à exclude_none
    after_payload: dict | None = None   # omis si None grâce à exclude_none

class MutationAuditListData(BaseModel):
    items: list[MutationAuditItem]
    total_count: int
    page: int
    page_size: int

class MutationAuditListApiResponse(BaseModel):
    data: MutationAuditListData
    meta: ResponseMeta

class MutationAuditDetailApiResponse(BaseModel):
    data: MutationAuditItem
    meta: ResponseMeta
```

Dans le router, construire le dict de l'item ainsi :
```python
def _to_item(audit, *, include_payloads: bool) -> dict:
    d = {
        "id": audit.id,
        "occurred_at": audit.occurred_at,
        ...
    }
    if include_payloads:
        d["before_payload"] = audit.before_payload
        d["after_payload"] = audit.after_payload
    return d
```

Déclarer `response_model_exclude_none=True` sur les deux `@router.get(...)` :
```python
@router.get("/mutation-audits", response_model=MutationAuditListApiResponse,
            response_model_exclude_none=True, ...)
@router.get("/mutation-audits/{audit_id}", response_model=MutationAuditDetailApiResponse,
            response_model_exclude_none=True, ...)
```

**Endpoints** :

```python
@router.get("/mutation-audits", response_model=MutationAuditListApiResponse, ...)
def list_mutation_audits(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    plan_id: int | None = Query(default=None),
    plan_code: str | None = Query(default=None),
    feature_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    actor_identifier: str | None = Query(default=None),
    source_origin: str | None = Query(default=None),
    request_id_filter: str | None = Query(default=None, alias="request_id"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    include_payloads: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    ...

@router.get("/mutation-audits/{audit_id}", response_model=MutationAuditDetailApiResponse, ...)
def get_mutation_audit(
    audit_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    ...
    # 404 si not found :
    # return _error_response(status_code=404, ..., code="audit_not_found", ...)
```

**ATTENTION** : le paramètre `request_id` de Query entre en conflit potentiel avec `request: Request`. Utiliser `alias="request_id"` avec le nom de variable `request_id_filter`.

### Enregistrement dans main.py

Pattern exact des autres routers ops (lignes 40–47 de main.py) :

```python
from app.api.v1.routers.ops_entitlement_mutation_audits import router as ops_entitlement_mutation_audits_router
# ...
app.include_router(ops_entitlement_mutation_audits_router)
```

Également dans `backend/app/api/v1/routers/__init__.py` :
```python
from app.api.v1.routers.ops_entitlement_mutation_audits import router as ops_entitlement_mutation_audits_router
# Dans __all__ :
"ops_entitlement_mutation_audits_router",
```

### Pattern des tests d'intégration

Même pattern que `test_ops_monitoring_api.py` — TestClient(app) with vraie DB SQLite via `SessionLocal`.

```python
from fastapi.testclient import TestClient
from app.infra.db.session import SessionLocal, engine
from app.infra.db.base import Base
from app.main import app
from app.services.auth_service import AuthService
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)

client = TestClient(app)

def _seed_audit(db, *, feature_code="astrologer_chat", actor_type="script",
                actor_identifier="test.py", plan_id=1, plan_code="basic-entry",
                source_origin="manual", before_payload=None, after_payload=None):
    audit = CanonicalEntitlementMutationAuditModel(
        operation="upsert_plan_feature_configuration",
        plan_id=plan_id,
        plan_code_snapshot=plan_code,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        source_origin=source_origin,
        before_payload=before_payload or {},
        after_payload=after_payload or {"is_enabled": True},
    )
    db.add(audit)
    db.flush()
    return audit
```

Pour les tests de filtre, créer 3 audits avec des `feature_code` / `actor_type` différents et vérifier l'isolation.

### Précédent : b2b_entitlements_audit.py (référence directe)

La story actuelle suit exactement le même pattern que ce fichier existant. Le `B2BAuditService` dans `backend/app/services/b2b_audit_service.py` est le modèle de `CanonicalEntitlementMutationAuditQueryService`.

### Aucune migration Alembic

La table `canonical_entitlement_mutation_audits` existe déjà (migration `20260328_0056`). Ne PAS créer de nouvelle migration.

### Project Structure Notes

- Routers ops : `backend/app/api/v1/routers/ops_*.py` — préfixe `/v1/ops/`
- Services query : `backend/app/services/*_query_service.py` ou `*_service.py`
- Tests intégration : `backend/app/tests/integration/test_*_api.py`
- Tests unitaires : `backend/app/tests/unit/test_*.py`

### Références

- [Source: backend/app/api/v1/routers/b2b_entitlements_audit.py] — pattern router ops paginé le plus proche
- [Source: backend/app/api/v1/routers/ops_monitoring.py] — pattern `_ensure_ops_role` + `_enforce_limits`
- [Source: backend/app/infra/db/models/canonical_entitlement_mutation_audit.py] — modèle ORM à requêter
- [Source: backend/app/services/canonical_entitlement_mutation_service.py] — `CanonicalMutationContext` pour contexte
- [Source: backend/app/main.py:40-47] — pattern d'enregistrement des routers ops
- [Source: backend/app/api/v1/routers/__init__.py] — registre des routers à mettre à jour
- [Source: backend/app/tests/integration/test_ops_monitoring_api.py] — pattern de test intégration

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log
