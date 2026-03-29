# Story 61.43 : Triage ops des alertes de delivery et suppression contrôlée du bruit

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux pouvoir qualifier chaque alerte de delivery avec un statut ops (`suppressed`, `resolved`), un commentaire et une clé de suppression,
afin de sortir durablement du backlog les alertes non-actionnables ou déjà traitées, et d'éviter qu'elles ne reviennent indéfiniment dans la file de retry.

## Contexte

- **61.39** : alerting idempotent, persistance dans `canonical_entitlement_mutation_alert_events`
- **61.40** : `canonical_entitlement_mutation_alert_delivery_attempts`, retry unitaire par alerte
- **61.41** : `GET /mutation-audits/alerts` + `GET /mutation-audits/alerts/summary` — visibilité ops de la file
- **61.42** : `POST /mutation-audits/alerts/retry-batch` — retry en masse des alertes `failed`
- **Gap** : les alertes `failed` connues, non-actionnables ou déjà traitées reviennent indéfiniment dans la file. Il n'existe aucun mécanisme pour les sortir durablement du backlog. Le batch retry 61.42 les traite toutes sans discrimination.

**Décision architecturale : table séparée** `canonical_entitlement_mutation_alert_event_handlings`
L'audit trail et les events restent immuables dans leur table. Le handling est une donnée mutable dans sa propre table. Une seule ligne par `alert_event_id` (upsert — dernier état = état courant). Ce pattern est identique à 61.35 (`canonical_entitlement_mutation_audit_reviews`).

**État virtuel `pending_retry`** : toute alerte `delivery_status="failed"` sans record de handling apparaît avec `handling_status="pending_retry"` dans les réponses API. Ce calcul est **application-level dans le router**, sans aucune écriture DB automatique.

**Impact sur le batch retry 61.42** : `_load_batch_candidates()` doit exclure les alertes dont le handling_status est `suppressed` ou `resolved`. Modification minimale de `CanonicalEntitlementAlertBatchRetryService._load_batch_candidates()`.

---

## Acceptance Criteria

### AC 1 — Table `canonical_entitlement_mutation_alert_event_handlings`

1. Table créée via migration Alembic dans `backend/migrations/versions/` avec colonnes :
   - `id` (int, PK, autoincrement)
   - `alert_event_id` (int, FK → `canonical_entitlement_mutation_alert_events.id`, NOT NULL, UNIQUE)
   - `handling_status` (str(32), NOT NULL) — valeurs : `suppressed`, `resolved`
   - `handled_by_user_id` (int, nullable)
   - `handled_at` (DateTime(timezone=True), NOT NULL, default=`utcnow`)
   - `ops_comment` (Text, nullable)
   - `suppression_key` (str(64), nullable) — raison/catégorie de suppression
2. Index UNIQUE sur `alert_event_id` (`uq_cemae_handling_alert_event_id`).
3. Index non-unique sur `handling_status`.

### AC 2 — Modèle SQLAlchemy

4. `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling.py` créé.
5. Classe `CanonicalEntitlementMutationAlertEventHandlingModel(Base)` avec `__tablename__ = "canonical_entitlement_mutation_alert_event_handlings"`.
6. FK déclarée vers `CanonicalEntitlementMutationAlertEventModel` via `ForeignKey("canonical_entitlement_mutation_alert_events.id")`.
7. `UniqueConstraint("alert_event_id", name="uq_cemae_handling_alert_event_id")` dans `__table_args__`.
8. Pattern identique à `canonical_entitlement_mutation_audit_review.py`.

### AC 3 — Service `CanonicalEntitlementAlertHandlingService`

9. `backend/app/services/canonical_entitlement_alert_handling_service.py` créé.
10. Interface publique :
    ```python
    class CanonicalEntitlementAlertHandlingService:
        @staticmethod
        def upsert_handling(
            db: Session,
            *,
            alert_event_id: int,
            handling_status: str,  # "suppressed" | "resolved"
            handled_by_user_id: int | None,
            ops_comment: str | None,
            suppression_key: str | None,
        ) -> CanonicalEntitlementMutationAlertEventHandlingModel: ...
    ```
11. `upsert_handling` :
    - Vérifie que `alert_event_id` existe dans `canonical_entitlement_mutation_alert_events` → `HTTPException(404)` sinon.
    - Si aucun handling pour `alert_event_id` → INSERT.
    - Si un handling existe → UPDATE (tous les champs + `handled_at = utcnow()`).
    - `db.flush()` mais **PAS** `db.commit()` (le router contrôle la transaction).
12. Pas d'import circulaire : pas de dépendance vers le router.

### AC 4 — Endpoint `POST /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle`

13. Endpoint ajouté dans `ops_entitlement_mutation_audits.py`.
14. Rôle requis : `ops` ou `admin` (via `_ensure_ops_role()`).
15. Rate limit via `_enforce_limits()` avec l'opération `"handle_alert_event"`.
16. Body Pydantic `HandleAlertRequestBody` :
    ```python
    class HandleAlertRequestBody(BaseModel):
        handling_status: Literal["suppressed", "resolved"]  # obligatoire, 422 si invalide
        ops_comment: str | None = None
        suppression_key: str | None = None
    ```
17. `handled_by_user_id` extrait de `current_user.id` (dépendance auth injectée, **pas dans le body**).
18. Retourne **HTTP 201** avec `HandleAlertApiResponse` :
    ```python
    class HandleAlertResponseData(BaseModel):
        alert_event_id: int
        handling_status: str
        handled_by_user_id: int | None = None
        handled_at: datetime
        ops_comment: str | None = None
        suppression_key: str | None = None

    class HandleAlertApiResponse(BaseModel):
        data: HandleAlertResponseData
        meta: ResponseMeta
    ```
19. Si `alert_event_id` inexistant → **404**.
20. `response_model_exclude_none=True` actif sur l'endpoint.
21. `db.commit()` dans le router **après** appel du service si succès.

### AC 5 — Ordre des routes dans le router

22. Dans `ops_entitlement_mutation_audits.py`, l'endpoint 61.43 est déclaré dans cet ordre :
    1. `GET /mutation-audits/alerts/summary` (61.41)
    2. `GET /mutation-audits/alerts` (61.41)
    3. `POST /mutation-audits/alerts/retry-batch` (61.42)
    4. `POST /mutation-audits/alerts/{alert_event_id}/handle` ← **ajout 61.43**
    5. `GET /mutation-audits/alerts/{alert_event_id}/attempts` (61.40)
    6. `POST /mutation-audits/alerts/{alert_event_id}/retry` (61.40)
23. L'endpoint `POST /{alert_event_id}/handle` doit être déclaré **avant** `GET /{alert_event_id}/attempts` pour respecter le principe d'ordre croissant de spécificité des routes paramétriques.

### AC 6 — Enrichissement de `GET /mutation-audits/alerts` avec le statut de handling

24. `AlertEventItem` (Pydantic, dans le router) reçoit un nouveau champ :
    ```python
    handling: AlertHandlingState | None = None
    ```
    avec :
    ```python
    class AlertHandlingState(BaseModel):
        handling_status: str  # "pending_retry" (virtuel) | "suppressed" | "resolved"
        handled_by_user_id: int | None = None
        handled_at: datetime | None = None
        ops_comment: str | None = None
        suppression_key: str | None = None
    ```
25. Fonction helper `_load_handlings_by_event_ids(db, event_ids)` ajoutée dans le router (pattern identique à `_load_reviews_by_audit_ids`) :
    ```python
    def _load_handlings_by_event_ids(
        db: Session, event_ids: list[int]
    ) -> dict[int, CanonicalEntitlementMutationAlertEventHandlingModel]:
        if not event_ids:
            return {}
        result = db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
                CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id.in_(event_ids)
            )
        )
        return {r.alert_event_id: r for r in result.scalars().all()}
    ```
26. Fonction helper `_compute_alert_handling_state(delivery_status, handling_record)` :
    ```python
    def _compute_alert_handling_state(
        delivery_status: str,
        handling_record: CanonicalEntitlementMutationAlertEventHandlingModel | None,
    ) -> AlertHandlingState | None:
        if handling_record is not None:
            return AlertHandlingState(
                handling_status=handling_record.handling_status,
                handled_by_user_id=handling_record.handled_by_user_id,
                handled_at=handling_record.handled_at,
                ops_comment=handling_record.ops_comment,
                suppression_key=handling_record.suppression_key,
            )
        if delivery_status == "failed":
            return AlertHandlingState(handling_status="pending_retry")
        return None
    ```
27. `_alert_event_to_item(row)` reçoit un paramètre supplémentaire `handling_record` et inclut `"handling"` dans le dict retourné.
28. Dans `list_alert_events`, après la récupération des rows, charger les handlings :
    ```python
    event_ids = [row.event.id for row in rows]
    handlings = _load_handlings_by_event_ids(db, event_ids)
    items = [
        _alert_event_to_item(row, handling_record=handlings.get(row.event.id))
        for row in rows
    ]
    ```
29. Champ `"retryable"` mis à jour dans `_alert_event_to_item()` :
    ```python
    handling_state = _compute_alert_handling_state(event.delivery_status, handling_record)
    "retryable": (
        handling_state is not None
        and handling_state.handling_status == "pending_retry"
    ),
    ```

### AC 7 — Filtre `handling_status` sur `GET /mutation-audits/alerts`

30. `list_alert_events` accepte un nouveau paramètre Query optionnel `handling_status` :
    ```python
    handling_status: Literal["pending_retry", "suppressed", "resolved"] | None = Query(default=None)
    ```
    Valeur invalide → 422 automatique FastAPI.
31. Le filtre est appliqué dans `CanonicalEntitlementAlertQueryService.list_alert_events()` et `_build_filtered_query()` via la signature étendue :
    ```python
    @staticmethod
    def _build_filtered_query(
        *,
        ...existing params...,
        handling_status: str | None = None,
    ):
        model = CanonicalEntitlementMutationAlertEventModel
        handling_model = CanonicalEntitlementMutationAlertEventHandlingModel
        query = select(model)
        # ...filtres existants...
        if handling_status == "suppressed" or handling_status == "resolved":
            handled_subq = select(handling_model.alert_event_id).where(
                handling_model.handling_status == handling_status
            )
            query = query.where(model.id.in_(handled_subq))
        elif handling_status == "pending_retry":
            any_handled_subq = select(handling_model.alert_event_id)
            query = query.where(
                model.delivery_status == "failed",
                model.id.notin_(any_handled_subq),
            )
        return query
    ```
32. `CanonicalEntitlementAlertQueryService.list_alert_events()` et `get_summary()` reçoivent un paramètre `handling_status: str | None = None` et le transmettent à `_build_filtered_query()`.
33. Le `_build_filtered_query()` utilise des subqueries `IN`/`NOT IN` (pas de JOIN) pour ne pas perturber le pattern `column_names = [column.name for column in model.__table__.columns]` utilisé dans `list_alert_events`.

### AC 8 — Enrichissement du summary avec les compteurs de handling

34. `AlertSummaryData` reçoit deux nouveaux champs :
    ```python
    suppressed_count: int
    resolved_count: int
    ```
35. `CanonicalEntitlementAlertQueryService.get_summary()` calcule ces compteurs via un LEFT JOIN de la table handling sur le subquery de base :
    ```python
    handling_model = CanonicalEntitlementMutationAlertEventHandlingModel
    handling_subq = select(
        handling_model.alert_event_id,
        handling_model.handling_status.label("handling_status"),
    ).subquery("h")

    joined = (
        select(base, handling_subq.c.handling_status.label("hs"))
        .outerjoin(handling_subq, base.c.id == handling_subq.c.alert_event_id)
        .subquery()
    )
    row = db.execute(
        select(
            func.count().label("total_count"),
            func.count(case((joined.c.delivery_status == "failed", 1))).label("failed_count"),
            func.count(case((joined.c.delivery_status == "sent", 1))).label("sent_count"),
            func.count(case((joined.c.hs == "suppressed", 1))).label("suppressed_count"),
            func.count(case((joined.c.hs == "resolved", 1))).label("resolved_count"),
            ...
        ).select_from(joined)
    ).one()
    ```
36. `AlertSummaryResult` (dataclass) reçoit `suppressed_count: int` et `resolved_count: int`.
37. Le router retransmet ces champs dans `AlertSummaryData`.

### AC 9 — Modification du batch retry 61.42 pour exclure suppressed/resolved

38. `CanonicalEntitlementAlertBatchRetryService._load_batch_candidates()` modifié :
    - Ajout d'un filtre NOT IN sur les alertes ayant un handling record avec `handling_status IN ('suppressed', 'resolved')`.
    - Implémentation :
      ```python
      from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
          CanonicalEntitlementMutationAlertEventHandlingModel,
      )
      handling_model = CanonicalEntitlementMutationAlertEventHandlingModel
      excluded_subq = select(handling_model.alert_event_id).where(
          handling_model.handling_status.in_(["suppressed", "resolved"])
      )
      query = query.where(model.id.notin_(excluded_subq))
      ```
    - Ce filtre est ajouté **après** le filtre `delivery_status == "failed"` existant et **avant** `ORDER BY id ASC LIMIT limit`.
39. Les candidats `failed` avec handling `pending_retry` (c'est-à-dire sans record de handling) **restent candidats** : comportement inchangé par rapport à 61.42.
40. **Aucune autre modification** de `CanonicalEntitlementAlertBatchRetryService` (ni `batch_retry`, ni son interface publique).
41. **Aucune modification** de l'endpoint `POST /retry-batch` (ni son schéma, ni sa signature).

### AC 10 — Tests unitaires

42. `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py` créé avec :
    - `test_upsert_handling_creates_new_record_when_none_exists`
    - `test_upsert_handling_updates_existing_record`
    - `test_upsert_handling_raises_404_when_alert_event_not_found`
    - `test_upsert_handling_does_not_commit`
    - `test_upsert_handling_flushes_session`
    - `test_upsert_handling_suppressed_sets_correct_status`
    - `test_upsert_handling_resolved_sets_correct_status`
    - `test_upsert_handling_stores_ops_comment_and_suppression_key`

### AC 11 — Tests d'intégration

43. `backend/app/tests/integration/test_ops_alert_event_handle_api.py` créé avec :
    - `test_post_handle_creates_suppressed_handling`
    - `test_post_handle_creates_resolved_handling`
    - `test_post_handle_updates_existing_handling`
    - `test_post_handle_stores_ops_comment_and_suppression_key`
    - `test_post_handle_returns_404_when_alert_event_not_found`
    - `test_post_handle_requires_ops_role`
    - `test_post_handle_returns_422_for_invalid_status`
    - `test_post_handle_returns_429_when_rate_limited`
    - `test_list_alert_events_includes_handling_state`
    - `test_list_alert_events_filter_by_handling_status_suppressed`
    - `test_list_alert_events_filter_by_handling_status_resolved`
    - `test_list_alert_events_filter_by_handling_status_pending_retry`
    - `test_list_alert_events_pending_retry_virtual_for_failed_without_handling`
    - `test_summary_includes_suppressed_and_resolved_counts`
    - `test_batch_retry_excludes_suppressed_alerts`
    - `test_batch_retry_excludes_resolved_alerts`
    - `test_batch_retry_includes_pending_retry_alerts`
    - `test_retryable_false_when_suppressed`
    - `test_retryable_false_when_resolved`
    - `test_retryable_true_when_pending_retry`

### AC 12 — Non-régression

44. Aucun contrat HTTP des endpoints 61.37–61.42 modifié (sauf ajout de champs dans les réponses existantes).
45. `AlertEventItem.handling` est optionnel (`None` par défaut) — ajout non-breaking pour les consommateurs existants.
46. `AlertSummaryData.suppressed_count` et `resolved_count` sont de nouveaux champs — ajout non-breaking.
47. `CanonicalEntitlementAlertBatchRetryService` : l'interface publique `batch_retry()` est **inchangée**. Seul `_load_batch_candidates()` (méthode protégée) est modifié.
48. `CanonicalEntitlementAlertQueryService.list_alert_events()` et `get_summary()` : nouveaux paramètres avec valeurs par défaut `None` — compatibilité ascendante.
49. `_alert_event_to_item()` : le paramètre supplémentaire `handling_record` a une valeur par défaut `None` — compatibilité ascendante si appelé ailleurs.
50. Aucune modification de `CanonicalEntitlementAlertService`, `CanonicalEntitlementAlertRetryService`.
51. Tests 61.40, 61.41, 61.42 restent verts.

### AC 13 — Documentation

52. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.43 — Triage ops des alertes de delivery"** : table, états, endpoint handle, enrichissement GET alerts, filtre handling_status, impact sur retry-batch.
53. `backend/README.md` mis à jour avec mention de l'endpoint de handling des alertes.

---

## Tasks / Subtasks

- [x] AC 1 — Migration Alembic
  - [x] Créer `backend/migrations/versions/{rev_id}_add_alert_event_handlings_table.py` avec table `canonical_entitlement_mutation_alert_event_handlings`
  - [x] Colonnes : id, alert_event_id (FK + UNIQUE), handling_status (str32), handled_by_user_id (int nullable), handled_at (timestamptz), ops_comment (Text nullable), suppression_key (str64 nullable)
  - [x] Index non-unique sur `handling_status`

- [x] AC 2 — Modèle SQLAlchemy
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling.py`
  - [x] Classe `CanonicalEntitlementMutationAlertEventHandlingModel(Base)` avec `UniqueConstraint`
  - [x] Pattern identique à `canonical_entitlement_mutation_audit_review.py`

- [x] AC 3 — Service `CanonicalEntitlementAlertHandlingService`
  - [x] Créer `backend/app/services/canonical_entitlement_alert_handling_service.py`
  - [x] Méthode `upsert_handling()` : vérification existence alert_event_id → 404, INSERT ou UPDATE, flush sans commit

- [x] AC 4+5 — Endpoint handle dans le router
  - [x] Ajouter `HandleAlertRequestBody`, `HandleAlertResponseData`, `HandleAlertApiResponse` dans `ops_entitlement_mutation_audits.py`
  - [x] Ajouter `POST /mutation-audits/alerts/{alert_event_id}/handle` (201, ops/admin, rate limit `handle_alert_event`)
  - [x] Respecter l'ordre des routes (AC 5)
  - [x] `db.commit()` dans le router après succès

- [x] AC 6 — Enrichissement de `_alert_event_to_item()` et `AlertEventItem`
  - [x] Ajouter `AlertHandlingState` dans les schémas du router
  - [x] Ajouter `handling: AlertHandlingState | None = None` à `AlertEventItem`
  - [x] Créer `_load_handlings_by_event_ids()` et `_compute_alert_handling_state()`
  - [x] Modifier `_alert_event_to_item()` pour accepter `handling_record` et calculer `handling` + nouveau `retryable`
  - [x] Modifier `list_alert_events` pour charger et passer les handlings

- [x] AC 7 — Filtre `handling_status` sur list
  - [x] Étendre `CanonicalEntitlementAlertQueryService._build_filtered_query()` avec `handling_status` (subqueries IN/NOT IN)
  - [x] Étendre `list_alert_events()` et `get_summary()` du service avec `handling_status`
  - [x] Ajouter le paramètre `handling_status` Query dans l'endpoint `list_alert_events` du router

- [x] AC 8 — Enrichissement du summary
  - [x] Modifier `AlertSummaryResult` (dataclass) avec `suppressed_count` et `resolved_count`
  - [x] Modifier `get_summary()` pour calculer via LEFT JOIN (subquery)
  - [x] Modifier `AlertSummaryData` Pydantic avec les deux nouveaux champs
  - [x] Mettre à jour le handler `get_alert_events_summary` dans le router

- [x] AC 9 — Modification du batch retry
  - [x] Modifier `CanonicalEntitlementAlertBatchRetryService._load_batch_candidates()` : ajouter `NOT IN (excluded_subq)` pour exclure suppressed/resolved

- [x] AC 10 — Tests unitaires
  - [x] Créer `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py` (8 tests, AC 10)

- [x] AC 11 — Tests d'intégration
  - [x] Créer `backend/app/tests/integration/test_ops_alert_event_handle_api.py` (21 tests, AC 11)

- [x] AC 13 — Documentation
  - [x] Mettre à jour `backend/docs/entitlements-canonical-platform.md`
  - [x] Mettre à jour `backend/README.md`

---

## Dev Notes

### Patterns critiques à respecter

**Modèle de référence : 61.35** (canonical_entitlement_mutation_audit_review)
- Cette story suit exactement le même pattern que 61.35, mais sur les `alert_events` au lieu des `audits`.
- Fichier modèle à copier : `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py`
- Service à copier : `backend/app/services/canonical_entitlement_mutation_audit_review_service.py`
- Fonctions helpers router à copier : `_load_reviews_by_audit_ids()`, `_compute_review_state()`

**Table cible** : `canonical_entitlement_mutation_alert_event_handlings` (PAS dans `alert_events`, table séparée).

**État virtuel `pending_retry`** : jamais écrit en DB. Calculé application-level.
- Règle : `delivery_status == "failed"` ET aucun record de handling → `handling_status = "pending_retry"`
- Règle : `delivery_status == "failed"` ET record de handling → utiliser le statut du record
- Règle : `delivery_status == "sent"` ET aucun record → `handling: None`

**`retryable` mise à jour** (ligne `"retryable": event.delivery_status == "failed"` dans `_alert_event_to_item()`) :
- Ancienne logique : `event.delivery_status == "failed"`
- Nouvelle logique : `effective_handling_status == "pending_retry"` (i.e. failed SANS handling suppressed/resolved)
- Cela change le comportement : une alerte `failed` + `suppressed` n'est plus `retryable: true`.

**Subqueries IN/NOT IN** dans `_build_filtered_query()` :
- NE PAS utiliser de JOIN car `list_alert_events` reconstruit les instances model via `column_names = [column.name for column in model.__table__.columns]`. Un JOIN ajouterait des colonnes parasites.
- Utiliser `model.id.in_(subq)` et `model.id.notin_(subq)` uniquement.

**LEFT JOIN dans `get_summary()`** :
- Le summary ne reconstruit pas d'instances model, donc un JOIN est safe ici.
- Utiliser `select(base, handling_subq.c.handling_status).outerjoin(handling_subq, ...)` pour calculer les compteurs en une seule requête.

### Structure des fichiers

```
# NOUVEAU
backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling.py
backend/app/services/canonical_entitlement_alert_handling_service.py
backend/migrations/versions/{rev}_add_alert_event_handlings_table.py
backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py
backend/app/tests/integration/test_ops_alert_event_handle_api.py

# MODIFIÉ
backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
  → +AlertHandlingState, HandleAlertRequestBody, HandleAlertResponseData, HandleAlertApiResponse (schémas)
  → +handling: AlertHandlingState | None dans AlertEventItem
  → +suppressed_count, resolved_count dans AlertSummaryData
  → +_load_handlings_by_event_ids(), _compute_alert_handling_state() (helpers)
  → _alert_event_to_item() modifié (handling_record param, handling field, retryable update)
  → list_alert_events() : +handling_status Query param + appel handlings
  → get_alert_events_summary() : +handling_status Query param
  → +POST /{alert_event_id}/handle endpoint

backend/app/services/canonical_entitlement_alert_query_service.py
  → AlertSummaryResult : +suppressed_count, resolved_count
  → _build_filtered_query() : +handling_status param, subquery IN/NOT IN
  → list_alert_events() : +handling_status param
  → get_summary() : +handling_status param, JOIN pour suppressed/resolved counts

backend/app/services/canonical_entitlement_alert_batch_retry_service.py
  → _load_batch_candidates() : +NOT IN excluded_subq (suppressed/resolved)

backend/docs/entitlements-canonical-platform.md
backend/README.md
```

### Imports SQLAlchemy dans `canonical_entitlement_alert_query_service.py`

Ajouter l'import du nouveau modèle :
```python
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
```

### Imports dans `ops_entitlement_mutation_audits.py`

Ajouter l'import du nouveau modèle (en import local dans les fonctions ou global) :
```python
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
from app.services.canonical_entitlement_alert_handling_service import (
    CanonicalEntitlementAlertHandlingService,
)
```

### Convention de nommage

| Élément | Nom |
|---|---|
| Table | `canonical_entitlement_mutation_alert_event_handlings` |
| Modèle | `CanonicalEntitlementMutationAlertEventHandlingModel` |
| Fichier modèle | `canonical_entitlement_mutation_alert_event_handling.py` |
| Service | `CanonicalEntitlementAlertHandlingService` |
| Fichier service | `canonical_entitlement_alert_handling_service.py` |
| FK colonne | `alert_event_id` |
| Unique constraint | `uq_cemae_handling_alert_event_id` |
| Schéma Pydantic état | `AlertHandlingState` |
| Schéma body | `HandleAlertRequestBody` |
| Schéma réponse data | `HandleAlertResponseData` |
| Schéma réponse enveloppe | `HandleAlertApiResponse` |

### Points d'attention pour les tests d'intégration

- Les tests doivent vérifier que `POST /retry-batch` **n'inclut pas** les alertes `suppressed`/`resolved` dans ses candidats (AC 11 : `test_batch_retry_excludes_suppressed_alerts`, `test_batch_retry_excludes_resolved_alerts`).
- Les tests doivent vérifier que `retryable: false` pour les alertes `suppressed`/`resolved` (AC 11 : `test_retryable_false_when_suppressed`, `test_retryable_false_when_resolved`).
- Pour le filtre `handling_status=pending_retry`, vérifier qu'une alerte `sent` (même sans handling) n'apparaît pas.
- L'endpoint `POST /handle` retourne **201** (pas 200) — vérifier dans les tests.

### Notes depuis les stories précédentes (61.42)

- `_ensure_ops_role()` et `_enforce_limits()` sont dans le router `ops_entitlement_mutation_audits.py`, lignes 359 et 371.
- `ResponseMeta` est importé depuis le router.
- `resolve_request_id()` est la fonction standard pour extraire le request_id.
- Toujours déclarer `db.commit()` dans le **router**, jamais dans le **service**.
- Le service fait `db.flush()` pour que le record soit lisible dans la même transaction.
- Pour le 404 dans le service : lever `HTTPException(status_code=404, detail="alert event not found")`.

### Technos et dépendances

- SQLAlchemy 2.x (style `select(model)`, `db.scalars()`, `db.execute()`)
- FastAPI + Pydantic v2 (`from pydantic import BaseModel, Field, ConfigDict, Literal`)
- Alembic pour la migration (dossier `backend/migrations/versions/`)
- Tests : pytest + conftest existant (voir tests 61.40/61.41 pour le pattern)

### Références

- [Source: story 61.35 — pattern table séparée mutable] `_bmad-output/implementation-artifacts/61-35-workflow-ops-revue-mutations-canoniques.md`
- [Source: story 61.42 — pattern batch retry, `_load_batch_candidates()`] `_bmad-output/implementation-artifacts/61-42-retry-batch-pilote-alertes-ops-echouees.md`
- [Source: model review] `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review.py`
- [Source: query service] `backend/app/services/canonical_entitlement_alert_query_service.py`
- [Source: batch retry service] `backend/app/services/canonical_entitlement_alert_batch_retry_service.py`
- [Source: router helpers `_load_reviews_by_audit_ids`, `_compute_review_state`] `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py#L401`
- [Source: AlertEventItem + `_alert_event_to_item()`] `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py#L269`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implémentation complète de la table mutable `canonical_entitlement_mutation_alert_event_handlings`, du modèle SQLAlchemy et du service d’upsert sans `commit`.
- Ajout du endpoint `POST /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle` avec rôle ops/admin, rate limit, 404 métier et réponse `201`.
- Enrichissement des endpoints `GET /alerts` et `GET /alerts/summary` avec l’état de handling, le filtre `handling_status`, les compteurs `suppressed_count`/`resolved_count` et la logique virtuelle `pending_retry`.
- Mise à jour du batch retry pour exclure les alertes `suppressed` et `resolved` sans modifier l’interface publique existante.
- Ajout des tests unitaires et d’intégration de la story, puis validation complète: `ruff check .`, `pytest -q` (`2504 passed, 3 skipped`) et chargement applicatif `from app.main import app`.
- Première passe de code review: correction du calcul `retryable_count` pour compter strictement les alertes `failed` sans handling, et alignement des assertions de non-régression.
- Seconde passe de code review: aucun finding bloquant restant sur le périmètre applicatif de la story.

### File List

- _bmad-output/implementation-artifacts/61-43-triage-ops-alertes-delivery-suppression-bruit.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling.py
- backend/app/services/canonical_entitlement_alert_batch_retry_service.py
- backend/app/services/canonical_entitlement_alert_handling_service.py
- backend/app/services/canonical_entitlement_alert_query_service.py
- backend/app/tests/integration/test_ops_alert_event_handle_api.py
- backend/app/tests/integration/test_ops_alert_events_list_api.py
- backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py
- backend/docs/entitlements-canonical-platform.md
- backend/migrations/versions/20260329_0061_add_alert_event_handlings_table.py
- backend/README.md

## Change Log

- 2026-03-29: Implémentation complète de la story 61.43, revue corrective en deux passes, validations backend complètes, story passée à `done`.
