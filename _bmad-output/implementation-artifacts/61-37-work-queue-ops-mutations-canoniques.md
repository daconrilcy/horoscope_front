# Story 61.37 : Work queue ops des mutations canoniques à risque

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux consulter une file d'attente triée et filtrée des mutations canoniques à traiter,
afin de savoir immédiatement ce qui nécessite mon attention, ce qui est en cours, ce qui vieillit, et disposer d'un résumé chiffré du backlog ops.

## Contexte

61.36 a complété la chaîne de traçabilité (écriture canonique → audit trail → lecture ops → diff/scoring → revue courante → historique complet). Ce qui manquait : l'**opérabilité quotidienne** — un backlog structuré évitant aux opérateurs de bricoler des filtres manuels sur l'endpoint brut de 61.33.

**Architecture** : cette story est **100 % read-only** — aucune table créée, aucune migration. Toute la logique est construite à partir des tables existantes : `canonical_entitlement_mutation_audits` + `canonical_entitlement_mutation_audit_reviews` + `CanonicalEntitlementMutationDiffService`.

**Vue calculée applicativement** : contrairement à `GET /mutation-audits` (pagination SQL pure), la work queue ne peut pas paginer au niveau SQL car le tri métier dépend du `risk_level` (calculé par diff) et de l'`effective_review_status` (calculé à la volée). La séquence de traitement est donc impérative et dans cet ordre :
1. **Filtres SQL bruts** — `feature_code`, `actor_type`, `actor_identifier`, `date_from`, `date_to` passés à `list_mutation_audits()`.
2. **Chargement batch** — jusqu'à `_DIFF_FILTER_MAX` enregistrements ; retour 400 si dépassé.
3. **Calcul diff + review state** — pour chaque audit : `compute_diff()` + `_compute_review_state()`.
4. **Filtres applicatifs** — `risk_level`, `effective_review_status`, `incident_key` filtrés en mémoire.
5. **Tri métier** — par `_STATUS_PRIORITY[eff_status]` puis `occurred_at ASC`.
6. **Pagination mémoire** — slice `filtered[start:end]`.

**Flux ops complet** : détection (`risk_level`) → consultation (61.33) → qualification (61.35 POST) → historique (61.36 GET) → **work queue (61.37 GET)**.

**Deux endpoints dans cette story** :
- `GET /v1/ops/entitlements/mutation-audits/review-queue` — liste paginée, triée par priorité métier
- `GET /v1/ops/entitlements/mutation-audits/review-queue/summary` — compteurs agrégés pour le pilotage

## Acceptance Criteria

### AC 1 — Endpoint `GET /v1/ops/entitlements/mutation-audits/review-queue`

1. Route ajoutée dans `ops_entitlement_mutation_audits.py`.
2. Requiert authentification → **401** si token absent ou invalide (`require_authenticated_user`).
3. Requiert rôle `ops` ou `admin` → **403** sinon (`_ensure_ops_role`).
4. Soumis au rate limit ops → **429** si dépassé (`_enforce_limits`, opération `"review_queue"`).
5. Paramètres de filtrage optionnels (tous via `Query`):
   - `risk_level: Literal["high", "medium", "low"] | None = None`
   - `effective_review_status: ReviewStatusLiteral | None = None`
   - `feature_code: str | None = None`
   - `actor_type: str | None = None`
   - `actor_identifier: str | None = None`
   - `incident_key: str | None = None` (filtre post-chargement sur la revue)
   - `date_from: datetime | None = None`
   - `date_to: datetime | None = None`
6. Paramètres de pagination : `page: int = Query(default=1, ge=1)`, `page_size: int = Query(default=20, ge=1, le=100)`.
7. Retourne **HTTP 200** avec `ReviewQueueApiResponse` (voir AC 5).
8. Items triés par **priorité métier ASC**, puis `occurred_at ASC` (plus ancien en tête dans chaque groupe) :
   - `pending_review` → priorité 0
   - `investigating` → priorité 1
   - `acknowledged` → priorité 2
   - `expected` → priorité 3
   - `closed` → priorité 4
   - `None` (medium/low sans revue) → priorité 5
9. `response_model_exclude_none=True` actif : les champs optionnels nuls (`review`, `effective_review_status` quand `None`, `request_id` d'audit, etc.) sont **omis** de la réponse JSON.
10. Garde `_DIFF_FILTER_MAX = 10_000` : si le count SQL dépasse cette limite, retourne **400** avec `code="diff_filter_result_set_too_large"` (même pattern que `list_mutation_audits`).

### AC 2 — Champs dérivés dans chaque item de la queue

11. Chaque item inclut les champs dérivés suivants (calculés au moment de la réponse) :
    - `effective_review_status: ReviewStatusLiteral | None = None` — statut effectif = `review.status` si revue existante, `"pending_review"` si `risk_level="high"` sans revue, `None` pour les audits medium/low sans revue. **Omis de la réponse JSON quand `None`** (via `exclude_none=True`).
    - `age_seconds: int` — `int((now_utc - audit.occurred_at).total_seconds())`.
    - `age_hours: float` — `round(age_seconds / 3600, 2)`.
    - `is_pending: bool` — `effective_review_status == "pending_review"`.
    - `is_closed: bool` — `effective_review_status == "closed"`.
12. `effective_review_status` utilise **exactement** la logique de `_compute_review_state()` existante dans le router — pas de duplication. `review` (champ hérité de `MutationAuditItem`) vaut `None` pour medium/low sans revue et est **omis** de la réponse JSON.

### AC 3 — Endpoint `GET /v1/ops/entitlements/mutation-audits/review-queue/summary`

13. Route ajoutée dans `ops_entitlement_mutation_audits.py`.
14. Mêmes contrôles : **401**, **403**, **429** (opération `"review_queue_summary"`).
15. Accepte le **même ensemble complet de filtres** que `review-queue` (SQL et applicatifs : `risk_level`, `effective_review_status`, `feature_code`, `actor_type`, `actor_identifier`, `incident_key`, `date_from`, `date_to`) — **sauf** `page` et `page_size`. Applique la **même séquence de traitement** : filtres SQL → chargement batch → diff + review state → filtres applicatifs. Le résumé porte sur la totalité des items correspondant aux critères, sans pagination.
16. Applique le même garde `_DIFF_FILTER_MAX` → **400** si dépassé.
17. Retourne **HTTP 200** avec `ReviewQueueSummaryApiResponse` :
    ```json
    {
      "data": {
        "pending_review_count": 5,
        "investigating_count": 2,
        "acknowledged_count": 3,
        "closed_count": 10,
        "expected_count": 1,
        "no_review_count": 4,
        "high_unreviewed_count": 5,
        "total_count": 25
      },
      "meta": { "request_id": "..." }
    }
    ```
    - `high_unreviewed_count` = nombre d'audits avec `risk_level="high"` ET `effective_review_status="pending_review"`.
    - `no_review_count` = nombre d'audits avec `effective_review_status=None` (medium/low sans revue).
    - `total_count` = total tous statuts après filtrage.

### AC 4 — Ordre de déclaration des routes (CRITIQUE)

18. Les deux routes `/mutation-audits/review-queue` et `/mutation-audits/review-queue/summary` sont déclarées **avant** la route `/mutation-audits/{audit_id}` dans le fichier router. Bien que FastAPI ne matche pas "review-queue" contre `audit_id: int`, l'ordre explicite prévient tout ambiguïté future.

### AC 5 — Schémas Pydantic

19. `ReviewQueueItem` hérite de `MutationAuditItem` avec 5 champs supplémentaires :
    ```python
    class ReviewQueueItem(MutationAuditItem):
        effective_review_status: ReviewStatusLiteral | None = None
        age_seconds: int
        age_hours: float
        is_pending: bool
        is_closed: bool
    ```
20. `ReviewQueueListData` : `items: list[ReviewQueueItem]`, `total_count: int`, `page: int`, `page_size: int`.
21. `ReviewQueueApiResponse` : `data: ReviewQueueListData`, `meta: ResponseMeta`.
22. `ReviewQueueSummaryData` : `pending_review_count: int`, `investigating_count: int`, `acknowledged_count: int`, `closed_count: int`, `expected_count: int`, `no_review_count: int`, `high_unreviewed_count: int`, `total_count: int`.
23. `ReviewQueueSummaryApiResponse` : `data: ReviewQueueSummaryData`, `meta: ResponseMeta`.

### AC 6 — Séparation service / router

24. Toute la logique de la queue (filtrage diff, tri, dérivation des champs) est implémentée **dans le router**, directement — pas de nouveau service. Ce pattern est cohérent avec le chemin diff-filter existant de `list_mutation_audits`.
25. Un **helper privé de router** `_build_filtered_review_queue_rows(db, *, ...)` **doit** être extrait pour partager la séquence chargement → diff → filtrage entre les deux endpoints (`review-queue` et `review-queue/summary`). Cela évite de dupliquer ~40 lignes. Ce helper retourne `list[tuple[audit, diff, review_record, eff_status]]` et prend les mêmes paramètres que les deux endpoints (hors `page`, `page_size`). Il gère également la vérification `_DIFF_FILTER_MAX` en levant une exception interne ou en retournant un sentinel, au choix de l'implémenteur.
26. Les helpers existants sont réutilisés sans modification : `_to_item_with_diff`, `_compute_review_state`, `_load_reviews_by_audit_ids`, `_ensure_ops_role`, `_enforce_limits`, `_error_response`.
**`include_payloads` n'est PAS exposé** sur les endpoints `review-queue` et `review-queue/summary`. La queue reste légère ; les payloads complets restent accessibles via `GET /mutation-audits/{audit_id}` (61.33).
26. `CanonicalEntitlementMutationAuditQueryService.list_mutation_audits()` — **non modifié**, utilisé tel quel pour charger les audits candidats.
27. `CanonicalEntitlementMutationDiffService` — **non modifié**.

### AC 7 — Tests d'intégration

28. `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` enrichi avec :
    - `test_review_queue_empty_returns_200` — aucun audit → items=[], total_count=0
    - `test_review_queue_pending_review_from_high_risk_audit` — audit high-risk sans revue → apparaît avec `effective_review_status="pending_review"`, `is_pending=True`, `is_closed=False`
    - `test_review_queue_sort_priority_order` — pending_review < investigating < acknowledged : vérifier que les items sont triés dans cet ordre
    - `test_review_queue_age_fields_populated` — `age_seconds >= 0`, `age_hours >= 0`, cohérence entre les deux
    - `test_review_queue_filter_by_effective_review_status` — filtre sur `effective_review_status=investigating` ne retourne que les audits avec revue à ce statut
    - `test_review_queue_filter_by_feature_code` — filtre SQL standard
    - `test_review_queue_filter_by_incident_key` — filtre post-chargement sur `review.incident_key`
    - `test_review_queue_pagination` — page=2, page_size=1 sur 3 items : retourne le bon item
    - `test_review_queue_summary_counts` — 2 pending + 1 investigating → compteurs corrects, `high_unreviewed_count` = 2
    - `test_review_queue_unauthenticated_returns_401`
    - `test_review_queue_requires_ops_role_returns_403`
    - `test_review_queue_summary_unauthenticated_returns_401`
29. Les tests existants (54 tests = 46 de 61.35 + 8 de 61.36) restent **tous verts**.

### AC 8 — Documentation

30. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.37 — Work queue ops"** décrivant :
    - Les deux endpoints et leurs paramètres.
    - La logique de tri par priorité.
    - Les champs dérivés (`effective_review_status`, `age_seconds`, `age_hours`, `is_pending`, `is_closed`).
    - La règle de garde `_DIFF_FILTER_MAX` appliquée ici.

### AC 9 — Périmètre strict

31. `canonical_entitlement_mutation_audit_query_service.py` — **non modifié**.
32. `canonical_entitlement_mutation_audit_review_service.py` — **non modifié**.
33. Tous les modèles SQLAlchemy — **non modifiés**.
34. Pas de migration Alembic (aucune table créée).
35. Fichiers existants modifiés : uniquement `ops_entitlement_mutation_audits.py`, `test_ops_entitlement_mutation_audits_api.py`, `entitlements-canonical-platform.md`.

---

## Tasks / Subtasks

- [ ] **Ajouter les schémas Pydantic** (AC: 5)
  - [ ] `ReviewQueueItem(MutationAuditItem)` avec les 5 champs dérivés
  - [ ] `ReviewQueueListData`, `ReviewQueueApiResponse`
  - [ ] `ReviewQueueSummaryData`, `ReviewQueueSummaryApiResponse`

- [ ] **Helper `_build_filtered_review_queue_rows()` + `_to_queue_item()`** (AC: 2, 6)
  - [ ] Créer `_build_filtered_review_queue_rows(db, *, request_id, ...)` — retourne `list[tuple] | JSONResponse(400)`
  - [ ] Créer `_to_queue_item(audit, *, diff, review_record, eff_status, now_utc)` — **sans** `include_payloads` (toujours False)
  - [ ] `effective_review_status` via `_compute_review_state(diff.risk_level, review_record)` dans le helper — pas de duplication

- [ ] **Constante `_STATUS_PRIORITY`** (AC: 1)
  - [ ] Définir dans le router : `_STATUS_PRIORITY = {"pending_review": 0, "investigating": 1, "acknowledged": 2, "expected": 3, "closed": 4, None: 5}`

- [ ] **Endpoint GET `/mutation-audits/review-queue`** (AC: 1, 4)
  - [ ] Déclarer avant `/mutation-audits/{audit_id}` dans le fichier
  - [ ] Filtres SQL via `CanonicalEntitlementMutationAuditQueryService.list_mutation_audits()`
  - [ ] Garde `_DIFF_FILTER_MAX` sur le count SQL
  - [ ] Chargement batch des revues via `_load_reviews_by_audit_ids()`
  - [ ] Diff in-memory + filtre `risk_level` + filtre `effective_review_status` + filtre `incident_key`
  - [ ] Tri par `(_STATUS_PRIORITY[eff_status], occurred_at)` puis pagination
  - [ ] Retour 200 avec `ReviewQueueApiResponse`

- [ ] **Endpoint GET `/mutation-audits/review-queue/summary`** (AC: 3, 4)
  - [ ] Déclarer avant `/mutation-audits/{audit_id}` dans le fichier (et avant `/review-queue` pour éviter ambiguïté)
  - [ ] Mêmes filtres SQL + garde `_DIFF_FILTER_MAX`
  - [ ] Agrégation des compteurs par `effective_review_status` + `high_unreviewed_count`
  - [ ] Retour 200 avec `ReviewQueueSummaryApiResponse`

- [ ] **Tests d'intégration** (AC: 7)
  - [ ] Enrichir `test_ops_entitlement_mutation_audits_api.py` avec 12 nouveaux cas

- [ ] **Documentation** (AC: 8)
  - [ ] Section 61.37 dans `backend/docs/entitlements-canonical-platform.md`

- [ ] **Validation finale**
  - [ ] `ruff check` — zéro erreur
  - [ ] `pytest unit` — tous verts
  - [ ] `pytest integration` — tous verts (dont les 54 existants + 12 nouveaux)

---

## Dev Notes

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py` | Modifier |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Modifier (+12 tests) |
| `backend/docs/entitlements-canonical-platform.md` | Modifier |

**Aucun autre fichier à modifier.** Pas de migration Alembic, pas de nouveau modèle.

---

### CRITIQUE — Ordre de déclaration des routes dans le router

FastAPI matche les routes dans l'ordre de déclaration. Bien que `{audit_id}: int` ne matchera pas "review-queue" (string non-int), la bonne pratique impose de déclarer les routes spécifiques avant les routes paramétrées.

**Ordre actuel dans le fichier** :
1. `GET /mutation-audits` (list)
2. `GET /mutation-audits/{audit_id}` (detail)
3. `POST /mutation-audits/{audit_id}/review`
4. `GET /mutation-audits/{audit_id}/review-history`

**Ordre après 61.37** :
1. `GET /mutation-audits` (list)
2. `GET /mutation-audits/review-queue/summary` ← NOUVEAU — déclarer EN PREMIER parmi les deux nouvelles routes
3. `GET /mutation-audits/review-queue` ← NOUVEAU
4. `GET /mutation-audits/{audit_id}` (detail)
5. `POST /mutation-audits/{audit_id}/review`
6. `GET /mutation-audits/{audit_id}/review-history`

---

### Pattern Session SQLAlchemy (inchangé)

Service synchrone, Session synchrone — identique à 61.35/61.36 :
```python
from sqlalchemy.orm import Session  # synchrone — PAS AsyncSession
db: Session = Depends(get_db_session)
```

---

### Helper `_build_filtered_review_queue_rows()` + `_to_queue_item()` — implémentation type

Ce helper centralise la séquence partagée entre les deux endpoints. Il retourne soit les rows filtrées, soit une `JSONResponse` d'erreur (400 si `_DIFF_FILTER_MAX` dépassé) — l'appelant doit vérifier le type de retour.

```python
from datetime import datetime, timezone
from typing import Union

_STATUS_PRIORITY: dict[str | None, int] = {
    "pending_review": 0,
    "investigating": 1,
    "acknowledged": 2,
    "expected": 3,
    "closed": 4,
    None: 5,
}


def _build_filtered_review_queue_rows(
    db: Session,
    *,
    request_id: str,
    feature_code: str | None,
    actor_type: str | None,
    actor_identifier: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
    risk_level_filter: str | None,
    effective_review_status_filter: str | None,
    incident_key_filter: str | None,
) -> Union[list[tuple[Any, Any, Any, Any]], JSONResponse]:
    """Retourne list[(audit, diff, review_record, eff_status)] ou JSONResponse(400)."""
    sql_kwargs = dict(
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        date_from=date_from,
        date_to=date_to,
    )
    _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db, page=1, page_size=1, **sql_kwargs
    )
    if sql_count > _DIFF_FILTER_MAX:
        return _error_response(
            status_code=400, request_id=request_id,
            code="diff_filter_result_set_too_large",
            message=f"Too many results ({sql_count} > {_DIFF_FILTER_MAX}). Add filters to narrow.",
            details={"sql_count": sql_count, "max_allowed": _DIFF_FILTER_MAX},
        )
    all_items, _ = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db, page=1, page_size=_DIFF_FILTER_MAX, **sql_kwargs
    )
    reviews_by_id = _load_reviews_by_audit_ids(db, [a.id for a in all_items])
    rows: list[tuple[Any, Any, Any, Any]] = []
    for item in all_items:
        diff = CanonicalEntitlementMutationDiffService.compute_diff(
            item.before_payload or {}, item.after_payload or {}
        )
        if risk_level_filter and diff.risk_level != risk_level_filter:
            continue
        review_record = reviews_by_id.get(item.id)
        review_state = _compute_review_state(diff.risk_level, review_record)
        eff_status = review_state.status if review_state else None
        if effective_review_status_filter is not None and eff_status != effective_review_status_filter:
            continue
        if incident_key_filter is not None:
            if review_record is None or review_record.incident_key != incident_key_filter:
                continue
        rows.append((item, diff, review_record, eff_status))
    return rows


def _to_queue_item(
    audit: Any,
    *,
    diff: Any,
    review_record: CanonicalEntitlementMutationAuditReviewModel | None,
    eff_status: str | None,
    now_utc: datetime,
) -> dict[str, Any]:
    # include_payloads=False : la queue est légère, payloads via GET /mutation-audits/{id}
    base = _to_item_with_diff(audit, diff=diff, include_payloads=False, review_record=review_record)
    occurred_at = audit.occurred_at
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
    age_seconds = int((now_utc - occurred_at).total_seconds())
    return {
        **base,
        "effective_review_status": eff_status,
        "age_seconds": age_seconds,
        "age_hours": round(age_seconds / 3600, 2),
        "is_pending": eff_status == "pending_review",
        "is_closed": eff_status == "closed",
    }
```

> **Note** : `audit.occurred_at` est stocké avec timezone (DateTime(timezone=True)) — utiliser `audit.occurred_at` directement. La normalisation `replace(tzinfo=timezone.utc)` est un garde-fou pour les rows legacy éventuels.

---

### Pattern endpoints — squelettes avec helper partagé

```python
# ── review-queue ─────────────────────────────────────────────────────────────
@router.get(
    "/mutation-audits/review-queue",
    response_model=ReviewQueueApiResponse,
    response_model_exclude_none=True,
    responses={400: {"model": ErrorEnvelope}, 401: {"model": ErrorEnvelope},
                403: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def get_review_queue(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    risk_level_filter: Literal["high", "medium", "low"] | None = Query(default=None, alias="risk_level"),
    effective_review_status_filter: ReviewStatusLiteral | None = Query(default=None, alias="effective_review_status"),
    feature_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    actor_identifier: str | None = Query(default=None),
    incident_key_filter: str | None = Query(default=None, alias="incident_key"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (err := _enforce_limits(user=current_user, request_id=request_id, operation="review_queue")) is not None:
        return err

    rows = _build_filtered_review_queue_rows(
        db, request_id=request_id,
        feature_code=feature_code, actor_type=actor_type, actor_identifier=actor_identifier,
        date_from=date_from, date_to=date_to,
        risk_level_filter=risk_level_filter,
        effective_review_status_filter=effective_review_status_filter,
        incident_key_filter=incident_key_filter,
    )
    if isinstance(rows, JSONResponse):
        return rows  # 400 _DIFF_FILTER_MAX dépassé

    rows.sort(key=lambda x: (_STATUS_PRIORITY.get(x[3], 5), x[0].occurred_at))
    now_utc = datetime.now(timezone.utc)
    total_count = len(rows)
    start = (page - 1) * page_size
    return {
        "data": {
            "items": [
                _to_queue_item(item, diff=diff, review_record=review_record, eff_status=eff_status, now_utc=now_utc)
                for item, diff, review_record, eff_status in rows[start : start + page_size]
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }


# ── review-queue/summary ──────────────────────────────────────────────────────
@router.get(
    "/mutation-audits/review-queue/summary",
    response_model=ReviewQueueSummaryApiResponse,
    response_model_exclude_none=True,
    responses={400: {"model": ErrorEnvelope}, 401: {"model": ErrorEnvelope},
                403: {"model": ErrorEnvelope}, 429: {"model": ErrorEnvelope}},
)
def get_review_queue_summary(
    request: Request,
    risk_level_filter: Literal["high", "medium", "low"] | None = Query(default=None, alias="risk_level"),
    effective_review_status_filter: ReviewStatusLiteral | None = Query(default=None, alias="effective_review_status"),
    feature_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    actor_identifier: str | None = Query(default=None),
    incident_key_filter: str | None = Query(default=None, alias="incident_key"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (err := _enforce_limits(user=current_user, request_id=request_id, operation="review_queue_summary")) is not None:
        return err

    rows = _build_filtered_review_queue_rows(
        db, request_id=request_id,
        feature_code=feature_code, actor_type=actor_type, actor_identifier=actor_identifier,
        date_from=date_from, date_to=date_to,
        risk_level_filter=risk_level_filter,
        effective_review_status_filter=effective_review_status_filter,
        incident_key_filter=incident_key_filter,
    )
    if isinstance(rows, JSONResponse):
        return rows  # 400 _DIFF_FILTER_MAX dépassé

    counts: dict[str, int] = {}
    high_unreviewed = 0
    for _, diff, _, eff_status in rows:
        key = eff_status if eff_status is not None else "none"
        counts[key] = counts.get(key, 0) + 1
        if diff.risk_level == "high" and eff_status == "pending_review":
            high_unreviewed += 1
    return {
        "data": {
            "pending_review_count": counts.get("pending_review", 0),
            "investigating_count": counts.get("investigating", 0),
            "acknowledged_count": counts.get("acknowledged", 0),
            "closed_count": counts.get("closed", 0),
            "expected_count": counts.get("expected", 0),
            "no_review_count": counts.get("none", 0),
            "high_unreviewed_count": high_unreviewed,
            "total_count": len(rows),
        },
        "meta": {"request_id": request_id},
    }
```

---

### Schémas Pydantic — implémentation type

```python
class ReviewQueueItem(MutationAuditItem):
    effective_review_status: ReviewStatusLiteral | None = None
    age_seconds: int
    age_hours: float
    is_pending: bool
    is_closed: bool


class ReviewQueueListData(BaseModel):
    items: list[ReviewQueueItem]
    total_count: int
    page: int
    page_size: int


class ReviewQueueApiResponse(BaseModel):
    data: ReviewQueueListData
    meta: ResponseMeta


class ReviewQueueSummaryData(BaseModel):
    pending_review_count: int
    investigating_count: int
    acknowledged_count: int
    closed_count: int
    expected_count: int
    no_review_count: int
    high_unreviewed_count: int
    total_count: int


class ReviewQueueSummaryApiResponse(BaseModel):
    data: ReviewQueueSummaryData
    meta: ResponseMeta
```

---

### Pattern Tests d'intégration — exemples

```python
# test_review_queue_pending_review_from_high_risk_audit
def test_review_queue_pending_review_from_high_risk_audit() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        # before_payload={} → binding_created → risk_level dépend de access_mode
        # Pour forcer high: access_mode="quota" dans after_payload
        _seed_audit(
            db,
            before_payload={},
            after_payload={"is_enabled": True, "access_mode": "quota", "quotas": []},
        )
        db.commit()

    resp = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_count"] == 1
    item = data["items"][0]
    assert item["effective_review_status"] == "pending_review"
    assert item["is_pending"] is True
    assert item["is_closed"] is False
    assert item["age_seconds"] >= 0
    assert item["age_hours"] >= 0


# test_review_queue_sort_priority_order
def test_review_queue_sort_priority_order() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        high_payload = {"is_enabled": True, "access_mode": "quota", "quotas": []}
        a1 = _seed_audit(db, before_payload={}, after_payload=high_payload, feature_code="f1")
        a2 = _seed_audit(db, before_payload={}, after_payload=high_payload, feature_code="f2")
        a3 = _seed_audit(db, before_payload={}, after_payload=high_payload, feature_code="f3")
        db.flush()
        # a2 → investigating, a3 → acknowledged, a1 reste pending
        db.add(CanonicalEntitlementMutationAuditReviewModel(
            audit_id=a2.id, review_status="investigating",
            reviewed_by_user_id=None, reviewed_at=datetime.now(timezone.utc),
        ))
        db.add(CanonicalEntitlementMutationAuditReviewModel(
            audit_id=a3.id, review_status="acknowledged",
            reviewed_by_user_id=None, reviewed_at=datetime.now(timezone.utc),
        ))
        db.commit()

    resp = client.get(
        "/v1/ops/entitlements/mutation-audits/review-queue",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    statuses = [i["effective_review_status"] for i in items]
    assert statuses == ["pending_review", "investigating", "acknowledged"]
```

---

### Imports additionnels à ajouter dans le router

```python
from collections import Counter  # pour le summary
# datetime.timezone déjà importé via from datetime import datetime, timezone
# Les autres imports (CanonicalEntitlementMutationDiffService, etc.) sont déjà présents
```

---

### Baseline tests actuelle (avant 61.37)

- 61.35 : 46 tests intégration
- 61.36 : +8 tests → **54 tests** au total
- 61.37 : +12 tests → **66 tests** attendus après

---

### Project Structure Notes

```
backend/
  app/
    api/v1/routers/
      ops_entitlement_mutation_audits.py  ← MODIFIER
        Ajouter (dans l'ordre) :
          1. Constante _STATUS_PRIORITY
          2. Schémas ReviewQueueItem, ReviewQueueListData, ReviewQueueApiResponse
          3. Schémas ReviewQueueSummaryData, ReviewQueueSummaryApiResponse
          4. Helper _to_queue_item()
          5. Route GET /mutation-audits/review-queue/summary  ← AVANT {audit_id}
          6. Route GET /mutation-audits/review-queue          ← AVANT {audit_id}
    tests/integration/
      test_ops_entitlement_mutation_audits_api.py  ← MODIFIER (+12 tests)
  docs/
    entitlements-canonical-platform.md  ← MODIFIER
```

**NE PAS modifier** :
- `canonical_entitlement_mutation_audit_query_service.py`
- `canonical_entitlement_mutation_audit_review_service.py`
- `canonical_entitlement_mutation_diff_service.py`
- Tout modèle SQLAlchemy sous `infra/db/models/`
- Pas de migration Alembic

---

### Références

- [Source: backend/app/api/v1/routers/ops_entitlement_mutation_audits.py] — router à étendre, helpers `_to_item_with_diff`, `_compute_review_state`, `_load_reviews_by_audit_ids`, `_ensure_ops_role`, `_enforce_limits`, `_error_response`, `_DIFF_FILTER_MAX`
- [Source: backend/app/services/canonical_entitlement_mutation_audit_query_service.py] — `list_mutation_audits()` à utiliser tel quel
- [Source: backend/app/services/canonical_entitlement_mutation_diff_service.py] — `compute_diff()` → `MutationDiffResult.risk_level`
- [Source: backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py] — patterns `_cleanup_tables`, `_seed_audit`, `_register_user_with_role_and_token`
- [Source: backend/docs/entitlements-canonical-platform.md] — documentation à compléter (section 61.37)

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Added `ReviewQueueItem`, `ReviewQueueListData`, `ReviewQueueApiResponse`, `ReviewQueueSummaryData`, `ReviewQueueSummaryApiResponse` Pydantic schemas.
- Implemented `_STATUS_PRIORITY` constant for work queue sorting.
- Implemented `_build_filtered_review_queue_rows` helper to centralize filtering and limitation logic for queue and summary.
- Implemented `_to_queue_item` helper for calculating derived fields (`age_seconds`, `age_hours`, `is_pending`, `is_closed`).
- Added `GET /v1/ops/entitlements/mutation-audits/review-queue/summary` endpoint.
- Added `GET /v1/ops/entitlements/mutation-audits/review-queue` endpoint.
- Updated `entitlements-canonical-platform.md` documentation.
- Added 12 integration tests in `test_ops_entitlement_mutation_audits_api.py`.
- Verified all 63 tests pass.

### File List

- `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
- `backend/docs/entitlements-canonical-platform.md`

### Change Log

- 2026-03-28 : Story 61.37 créée.
