# Story 61.44 : Historisation append-only des transitions de handling des alertes ops

Status: done

## Story

En tant qu'opérateur ou administrateur backend,
je veux consulter l'historique complet et ordonné des décisions de triage prises sur chaque alerte de delivery,
afin de tracer qui a supprimé ou résolu une alerte, quand, avec quel commentaire, et détecter toute réouverture ultérieure.

## Contexte

- **61.39** : alerting idempotent, persistance dans `canonical_entitlement_mutation_alert_events`
- **61.40** : `canonical_entitlement_mutation_alert_delivery_attempts`, retry unitaire par alerte
- **61.41** : `GET /mutation-audits/alerts` + `GET /mutation-audits/alerts/summary` — visibilité ops de la file
- **61.42** : `POST /mutation-audits/alerts/retry-batch` — retry en masse des alertes `failed`
- **61.43** : table mutable `canonical_entitlement_mutation_alert_event_handlings` (upsert), service `CanonicalEntitlementAlertHandlingService`, endpoint `POST /mutation-audits/alerts/{alert_event_id}/handle`
- **Gap** : 61.43 introduit une projection mutable de l'état courant du handling. Il n'existe aucun mécanisme pour répondre à "qui a supprimé cette alerte, quand, avec quel commentaire, puis qui l'a remise en `resolved` ensuite ?". La traçabilité complète du pilotage ops sur les alertes est absente.

**Pattern de référence : 61.35/61.36**
- 61.35 : table mutable `canonical_entitlement_mutation_audit_reviews` (review courante) → identique à 61.43
- 61.36 : table append-only `canonical_entitlement_mutation_audit_review_events` (historique des transitions) → **c'est ce pattern que 61.44 reproduit sur la couche alerting**

**Décision architecturale :**
- Table append-only `canonical_entitlement_mutation_alert_event_handling_events` — INSERT uniquement, jamais UPDATE/DELETE
- N lignes par `alert_event_id` (PAS de UNIQUE contrairement à la table mutable 61.43)
- Le service 61.43 (`CanonicalEntitlementAlertHandlingService.upsert_handling()`) est enrichi : il appelle `append_handling_event()` après chaque changement effectif
- **Règle no-op** : pas d'événement si `handling_status`, `ops_comment` ET `suppression_key` sont identiques à l'état précédent
- **Propagation `request_id`** : le router passe `request_id=resolve_request_id(request)` au service, qui le stocke dans chaque événement

**Différences clés avec le modèle `CanonicalEntitlementMutationAuditReviewEventModel` (61.36) :**
- Pas de champs `previous_*`/`new_*` — modèle plus simple, enregistre uniquement le nouvel état
- Champ timestamp nommé `handled_at` (pas `occurred_at`)
- `request_id` : `String(255)` (vs `String(64)` pour les reviews — IDs d'alertes peuvent être plus longs)
- L'endpoint GET history inclut une pagination `limit`/`offset` (le GET review-history n'en a pas)
- Résultats ordonnés `DESC` (vs `ASC` pour review-history)

---

## Acceptance Criteria

### AC 1 — Table `canonical_entitlement_mutation_alert_event_handling_events`

1. Migration Alembic créée : `backend/migrations/versions/20260329_0062_add_alert_event_handling_events_table.py`
   - `revision = "20260329_0062"`
   - `down_revision = "20260329_0061"` ← chaînage explicite avec la migration de la table mutable 61.43
2. Colonnes :
   - `id` (int, PK, autoincrement)
   - `alert_event_id` (int, FK → `canonical_entitlement_mutation_alert_events.id`, NOT NULL)
   - `handling_status` (String(32), NOT NULL) — `suppressed` ou `resolved`
   - `handled_by_user_id` (int, nullable)
   - `handled_at` (DateTime(timezone=True), NOT NULL, default=`utcnow`)
   - `ops_comment` (Text, nullable)
   - `suppression_key` (String(64), nullable)
   - `request_id` (String(255), nullable)
3. **PAS de UNIQUE** sur `alert_event_id` — c'est une table append-only (N lignes par alert_event_id).
4. Index non-unique sur `alert_event_id`.
5. Index non-unique sur `handled_at`.

### AC 2 — Modèle SQLAlchemy

6. Fichier créé : `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling_event.py`
7. Classe `CanonicalEntitlementMutationAlertEventHandlingEventModel(Base)` avec `__tablename__ = "canonical_entitlement_mutation_alert_event_handling_events"`.
8. FK déclarée vers `canonical_entitlement_mutation_alert_events.id`.
9. Pas de `__table_args__` avec UniqueConstraint (contrairement au modèle 61.43).
10. Fonction `_utc_now()` locale pour le `default` de `handled_at`.
11. Pattern SQLAlchemy 2.x avec `Mapped[T]` et `mapped_column()`.
12. Le modèle est enregistré dans `backend/app/infra/db/models/__init__.py` (import ajouté pour que `Base.metadata` le découvre au boot et dans les tests).

### AC 3 — Enrichissement de `CanonicalEntitlementAlertHandlingService`

12. Nouveau paramètre `request_id: str | None = None` ajouté à `upsert_handling()` — valeur par défaut `None` pour compatibilité ascendante.
13. Nouvelle méthode statique `append_handling_event(db, *, alert_event_id, handling_status, handled_by_user_id, ops_comment, suppression_key, request_id)` :
    - Crée et ajoute un `CanonicalEntitlementMutationAlertEventHandlingEventModel`
    - Appelle `db.flush()` mais **PAS** `db.commit()`
14. Logique de `upsert_handling()` mise à jour :
    - Lire l'état précédent avant INSERT/UPDATE (capturer `previous_status`, `previous_comment`, `previous_suppression_key`)
    - **Cas création** : appeler `append_handling_event()` systématiquement
    - **Cas mise à jour** : appeler `append_handling_event()` **uniquement si** au moins un champ parmi `handling_status`, `ops_comment`, `suppression_key` a changé vs état précédent
    - **Règle no-op** : si les trois champs sont identiques → retourner le record existant sans flush supplémentaire ni événement
15. Imports à ajouter dans le service :
    ```python
    from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling_event import (
        CanonicalEntitlementMutationAlertEventHandlingEventModel,
    )
    ```
16. Pas de `db.commit()` dans le service (invariant existant conservé).
17. Pas d'import circulaire vers le router.

### AC 4 — Propagation du `request_id` dans le router

18. Dans `handle_alert_event()` (router `ops_entitlement_mutation_audits.py`), l'appel à `upsert_handling()` est mis à jour :
    ```python
    handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
        db,
        alert_event_id=alert_event_id,
        handling_status=body.handling_status,
        handled_by_user_id=current_user.id,
        ops_comment=body.ops_comment,
        suppression_key=body.suppression_key,
        request_id=request_id,  # ← ajout
    )
    ```
19. L'interface HTTP de `POST /handle` reste **identique** (body, status code 201, réponse).

### AC 5 — Endpoint `GET /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handling-history`

20. Ajouté dans `ops_entitlement_mutation_audits.py`.
21. Rôle requis : `ops` ou `admin` (via `_ensure_ops_role()`).
22. Rate limit via `_enforce_limits()` avec l'opération `"get_alert_handling_history"`.
23. Paramètres Query :
    - `limit: int = Query(default=50, ge=1, le=200)`
    - `offset: int = Query(default=0, ge=0)`
24. Si `alert_event_id` inexistant → retourner `_error_response(status_code=404, code="alert_event_not_found", ...)`.
25. Nouveaux schémas Pydantic :
    ```python
    class AlertHandlingHistoryItem(BaseModel):
        id: int
        alert_event_id: int
        handling_status: str
        handled_by_user_id: int | None = None
        handled_at: datetime
        ops_comment: str | None = None
        suppression_key: str | None = None
        request_id: str | None = None

    class AlertHandlingHistoryData(BaseModel):
        items: list[AlertHandlingHistoryItem]
        total_count: int
        limit: int
        offset: int

    class AlertHandlingHistoryApiResponse(BaseModel):
        data: AlertHandlingHistoryData
        meta: ResponseMeta
    ```
    `total_count` = nombre total de lignes pour cet `alert_event_id` (avant application de limit/offset), calculé via `SELECT COUNT(*)` ou `len()` sur la liste complète selon la volumétrie attendue (faible → `len()` sur `.all()` acceptable).
26. Résultats ordonnés par `handled_at DESC, id DESC`.
27. `response_model_exclude_none=True` actif sur l'endpoint.
28. Retourne HTTP 200.
29. Le modèle `CanonicalEntitlementMutationAlertEventHandlingEventModel` est importé en local dans la fonction (pattern utilisé dans le router pour les modèles d'events : voir `get_review_history` lignes 1549-1551).

### AC 6 — Ordre des routes dans le router

30. Dans `ops_entitlement_mutation_audits.py`, l'endpoint 61.44 est déclaré dans cet ordre :
    1. `GET /mutation-audits/alerts/summary` (61.41)
    2. `GET /mutation-audits/alerts` (61.41)
    3. `POST /mutation-audits/alerts/retry-batch` (61.42)
    4. `POST /mutation-audits/alerts/{alert_event_id}/handle` (61.43)
    5. `GET /mutation-audits/alerts/{alert_event_id}/handling-history` ← **ajout 61.44**
    6. `GET /mutation-audits/alerts/{alert_event_id}/attempts` (61.40)
    7. `POST /mutation-audits/alerts/{alert_event_id}/retry` (61.40)

### AC 7 — Tests unitaires

31. Fichier créé : `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py`
32. Tests à implémenter :
    - `test_append_handling_event_inserts_record` — vérifie l'INSERT dans la table d'events
    - `test_upsert_handling_creates_event_on_insert` — première création → event créé
    - `test_upsert_handling_creates_event_on_status_change` — UPDATE avec nouveau statut → event créé
    - `test_upsert_handling_no_event_when_no_change` — règle no-op : même corps re-POSTé → pas d'event
    - `test_upsert_handling_creates_event_when_ops_comment_changes` — seul ops_comment change → event créé
    - `test_upsert_handling_creates_event_when_suppression_key_changes` — seul suppression_key change → event créé
    - `test_upsert_handling_stores_request_id_in_event` — request_id propagé dans l'event
    - `test_upsert_handling_flushes_event_without_commit` — flush mais pas commit

### AC 8 — Tests d'intégration

33. Fichier créé : `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py`
34. Tests à implémenter :
    - `test_get_handling_history_empty_when_no_handlings` — 200, liste vide
    - `test_get_handling_history_returns_single_event_after_first_handle` — après POST /handle, 1 event
    - `test_get_handling_history_returns_multiple_events_on_status_change` — 2 POST différents → 2 events
    - `test_get_handling_history_no_duplicate_on_identical_re_post` — même corps × 2 → toujours 1 event (no-op)
    - `test_get_handling_history_stores_request_id` — request_id du POST /handle dans l'event
    - `test_get_handling_history_ordered_by_handled_at_desc` — dernier event en premier
    - `test_get_handling_history_pagination` — limit=1, offset=1 retourne le bon event
    - `test_get_handling_history_returns_404_when_alert_event_not_found`
    - `test_get_handling_history_requires_ops_role`
    - `test_get_handling_history_unauthenticated_returns_401`
    - `test_get_handling_history_returns_429_when_rate_limited`
    - `test_handle_alert_still_returns_201_after_61_44_changes` — non-régression POST /handle
    - `test_batch_retry_still_excludes_suppressed_after_61_44_changes` — non-régression batch retry

### AC 9 — Non-régression

35. Interface HTTP de `POST /mutation-audits/alerts/{alert_event_id}/handle` **inchangée** (body, status code, réponse).
36. `upsert_handling()` : nouveau paramètre `request_id` avec valeur par défaut `None` — compatibilité ascendante.
37. Tests 61.40, 61.41, 61.42, 61.43 restent verts.
38. Aucune modification des endpoints existants (sauf ajout de `request_id=request_id` dans l'appel interne au service).
39. Aucune modification de `CanonicalEntitlementAlertQueryService`, `CanonicalEntitlementAlertBatchRetryService`, ni de la table `canonical_entitlement_mutation_alert_event_handlings`.

### AC 10 — Documentation

40. `backend/docs/entitlements-canonical-platform.md` mis à jour avec section **"Story 61.44 — Historisation des transitions de handling"** : table append-only, règle no-op, endpoint GET handling-history, propagation request_id.
41. `backend/README.md` mis à jour avec mention de l'endpoint de consultation de l'historique de handling.

---

## Tasks / Subtasks

- [x] AC 1+2 — Migration Alembic + Modèle SQLAlchemy
  - [x] Créer `backend/migrations/versions/20260329_0062_add_alert_event_handling_events_table.py`
  - [x] Colonnes : id, alert_event_id (FK, index non-unique), handling_status (str32), handled_by_user_id (nullable), handled_at (timestamptz, index), ops_comment (Text), suppression_key (str64), request_id (str255)
  - [x] Créer `backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling_event.py`
  - [x] Classe `CanonicalEntitlementMutationAlertEventHandlingEventModel(Base)`, pattern SQLAlchemy 2.x `Mapped[T]`
  - [x] Enregistrer le modèle dans `backend/app/infra/db/models/__init__.py`

- [x] AC 3+4 — Enrichissement du service + propagation request_id dans le router
  - [x] Modifier `backend/app/services/canonical_entitlement_alert_handling_service.py`
  - [x] Ajouter méthode statique `append_handling_event()`
  - [x] Ajouter paramètre `request_id: str | None = None` à `upsert_handling()`
  - [x] Implémenter logique no-op (capturer état précédent, comparer 3 champs sémantiques)
  - [x] Appeler `append_handling_event()` si création ou changement effectif
  - [x] Modifier `ops_entitlement_mutation_audits.py` : passer `request_id=request_id` dans l'appel à `upsert_handling()`

- [x] AC 5+6 — Endpoint GET handling-history
  - [x] Ajouter schémas `AlertHandlingHistoryItem`, `AlertHandlingHistoryData` et `AlertHandlingHistoryApiResponse` dans le router
  - [x] Ajouter endpoint `GET /mutation-audits/alerts/{alert_event_id}/handling-history` avec pagination limit/offset
  - [x] Respecter l'ordre des routes (AC 6)
  - [x] Import local du modèle `CanonicalEntitlementMutationAlertEventHandlingEventModel`

- [x] AC 7 — Tests unitaires
  - [x] Créer `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py` (8 tests)

- [x] AC 8 — Tests d'intégration
  - [x] Créer `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py` (12 tests)
  - [x] Réutiliser les helpers `_cleanup_tables`, `_seed_audit`, `_seed_alert_event` depuis `test_ops_review_queue_alerts_retry_api.py`

- [x] AC 10 — Documentation
  - [x] Mettre à jour `backend/docs/entitlements-canonical-platform.md`
  - [x] Mettre à jour `backend/README.md`

---

## Dev Notes

### État exact du code au départ de 61.44

**`backend/app/services/canonical_entitlement_alert_handling_service.py`** (tel qu'implémenté en 61.43) :
```python
class CanonicalEntitlementAlertHandlingService:
    @staticmethod
    def upsert_handling(
        db: Session,
        *,
        alert_event_id: int,
        handling_status: str,
        handled_by_user_id: int | None,
        ops_comment: str | None,
        suppression_key: str | None,
        # PAS DE request_id — à ajouter en 61.44
    ) -> CanonicalEntitlementMutationAlertEventHandlingModel:
        alert_event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
        if alert_event is None:
            raise HTTPException(status_code=404, detail="alert event not found")

        handling = db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingModel).where(...)
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if handling is None:
            handling = CanonicalEntitlementMutationAlertEventHandlingModel(...)
            db.add(handling)
        else:
            handling.handling_status = handling_status
            # ... mise à jour de tous les champs
        db.flush()
        return handling
```
**À noter** : pas de `begin_nested()`, pas de vérification no-op, pas d'événement d'historique.

**`backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`** — appel existant (ligne 1220) :
```python
handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
    db,
    alert_event_id=alert_event_id,
    handling_status=body.handling_status,
    handled_by_user_id=current_user.id,
    ops_comment=body.ops_comment,
    suppression_key=body.suppression_key,
    # request_id=request_id  ← À AJOUTER
)
```

### Pattern de référence : `CanonicalEntitlementMutationAuditReviewService`

Le service de review (61.35/61.36) implémente la logique complète no-op + event. Points critiques à reproduire :

```python
# Capture de l'état précédent
is_creation = review is None
previous_status = None if is_creation else review.review_status
previous_comment = None if is_creation else review.review_comment
previous_incident = None if is_creation else review.incident_key

# Règle no-op
is_noop = (
    not is_creation
    and previous_status == review_status
    and previous_comment == review_comment
    and previous_incident == incident_key
)
if is_noop:
    return review  # Retour immédiat, pas de flush, pas d'event

# INSERT event après le upsert
event = CanonicalEntitlementMutationAuditReviewEventModel(
    audit_id=audit_id,
    previous_review_status=previous_status,
    new_review_status=review_status,
    ...
    request_id=request_id,
)
db.add(event)
db.flush()
return review
```

**Pour 61.44** : le modèle d'event est plus simple (pas de `previous_*`/`new_*`), il enregistre directement le nouvel état :
```python
event = CanonicalEntitlementMutationAlertEventHandlingEventModel(
    alert_event_id=alert_event_id,
    handling_status=handling_status,
    handled_by_user_id=handled_by_user_id,
    handled_at=now,
    ops_comment=ops_comment,
    suppression_key=suppression_key,
    request_id=request_id,
)
```

### Pattern GET history — endpoint de référence (61.36, ligne 1516)

```python
@router.get(
    "/mutation-audits/{audit_id}/review-history",
    response_model=ReviewHistoryApiResponse,
    response_model_exclude_none=True,
    ...
)
def get_review_history(audit_id: int, request: Request, ...) -> Any:
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None: return err
    if (err := _enforce_limits(..., operation="review_history")) is not None: return err

    # Import local du modèle
    from app.infra.db.models.canonical_entitlement_mutation_audit_review_event import (
        CanonicalEntitlementMutationAuditReviewEventModel,
    )

    audit = db.get(CanonicalEntitlementMutationAuditModel, audit_id)
    if audit is None:
        return _error_response(status_code=404, ...)

    result = db.execute(
        select(CanonicalEntitlementMutationAuditReviewEventModel)
        .where(CanonicalEntitlementMutationAuditReviewEventModel.audit_id == audit_id)
        .order_by(...asc(), ...asc())
    )
    events = result.scalars().all()
    return {"data": {"items": [...], "total_count": len(events)}, "meta": {...}}
```

**Différences 61.44 vs 61.36** :
1. Ordre : `DESC` (not `ASC`)
2. Pagination : `limit`/`offset` Query params (pas dans 61.36)
3. Schéma réponse : `data: {items, total_count, limit, offset}` (homogène avec 61.33/61.37/61.41)
4. Modèle : `CanonicalEntitlementMutationAlertEventHandlingEventModel`, FK = `alert_event_id`

### Convention de nommage

| Élément | Nom |
|---|---|
| Table | `canonical_entitlement_mutation_alert_event_handling_events` |
| Modèle SQLAlchemy | `CanonicalEntitlementMutationAlertEventHandlingEventModel` |
| Fichier modèle | `canonical_entitlement_mutation_alert_event_handling_event.py` |
| Méthode service | `append_handling_event()` |
| Schéma Pydantic item | `AlertHandlingHistoryItem` |
| Schéma réponse | `AlertHandlingHistoryApiResponse` |
| Opération rate limit | `"get_alert_handling_history"` |
| Fichier migration | `20260329_0062_add_alert_event_handling_events_table.py` |

### Structure des fichiers

```
# NOUVEAUX
backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling_event.py
backend/migrations/versions/20260329_0062_add_alert_event_handling_events_table.py
backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py
backend/app/tests/integration/test_ops_alert_event_handling_history_api.py

# MODIFIÉS
backend/app/infra/db/models/__init__.py
  → +import CanonicalEntitlementMutationAlertEventHandlingEventModel

backend/app/services/canonical_entitlement_alert_handling_service.py
  → upsert_handling() : +request_id param, +capture état précédent, +règle no-op, +appel append_handling_event(), now unique partagé
  → +append_handling_event() méthode statique

backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
  → handle_alert_event() : passer request_id=request_id à upsert_handling()
  → +AlertHandlingHistoryItem, AlertHandlingHistoryData, AlertHandlingHistoryApiResponse (schémas, avant ErrorPayload)
  → +GET /{alert_event_id}/handling-history endpoint (entre /handle et /attempts)

backend/docs/entitlements-canonical-platform.md
backend/README.md
```

### Tests — réutilisation des helpers existants

Tests d'intégration doivent importer depuis `test_ops_review_queue_alerts_retry_api.py` :
```python
from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
    _cleanup_tables,
    _register_user_with_role_and_token,
    _seed_alert_event,
    _seed_audit,
)
```
Pattern identique à `test_ops_alert_event_handle_api.py` (61.43).

**La fonction `_cleanup_tables()` doit être étendue pour purger aussi `canonical_entitlement_mutation_alert_event_handling_events`** (nouvelle table 61.44). Sans cette purge, les tests de comptage d'events (`total_count`, no-op) se parasitent entre eux. Ajouter dans `_cleanup_tables()` (dans `test_ops_review_queue_alerts_retry_api.py` ou en local) :
```python
db.execute(text("DELETE FROM canonical_entitlement_mutation_alert_event_handling_events"))
```
à insérer **avant** le DELETE de `canonical_entitlement_mutation_alert_event_handlings`.

### Tests unitaires — pattern existant à étendre

Fichier de référence : `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py`
- Utilise `Base.metadata.drop_all(bind=engine)` + `Base.metadata.create_all(bind=engine)` en setup
- Session directe via `SessionLocal`
- Les nouveaux tests en 61.44 doivent appeler `_setup()` pour recréer toutes les tables (y compris la nouvelle table d'events)

### Point d'attention : `begin_nested()` non utilisé dans le service 61.43

Le service de review (61.35) utilise `begin_nested()` pour gérer les race conditions sur l'INSERT :
```python
try:
    with db.begin_nested():
        db.add(review)
        db.flush()
except IntegrityError:
    review = self._get_review_by_audit_id(db, audit_id)
    ...
```
Le service de handling (61.43) ne l'utilise **pas**. En 61.44, il n'est pas requis d'ajouter `begin_nested()` — la table d'events n'a pas de contrainte UNIQUE, donc pas de risque d'IntegrityError. Le service de handling existant peut rester sans `begin_nested()`.

### Règle no-op — comportement exact attendu

```
POST /handle {handling_status: "suppressed", ops_comment: "spam"}   → INSERT handling + INSERT event
POST /handle {handling_status: "suppressed", ops_comment: "spam"}   → no-op: retour immédiat (pas de UPDATE, pas d'event)
POST /handle {handling_status: "suppressed", ops_comment: "autre"}  → UPDATE handling + INSERT event
POST /handle {handling_status: "resolved", ops_comment: "autre"}    → UPDATE handling + INSERT event
```

En cas de no-op, **ni la ligne mutable (table `handlings`) ni la table d'historique** ne sont modifiées. `handled_at` reste inchangé dans les deux tables. Comportement identique au service de review.

### `now` unique pour projection mutable et event append-only

Sur création ou update effectif, le service calcule **un seul** `now = datetime.now(timezone.utc)` et l'utilise à la fois pour :
- `handling.handled_at = now` (ligne mutable, table `handlings`)
- `event.handled_at = now` (event append-only, table `handling_events`)

Cela garantit que les deux timestamps sont identiques à la microseconde près, simplifie les assertions de tests et la lecture ops ("l'event correspond exactement à l'état courant au moment T").

### Références

- [Source: modèle review event] `backend/app/infra/db/models/canonical_entitlement_mutation_audit_review_event.py`
- [Source: service review avec no-op + append_review_event] `backend/app/services/canonical_entitlement_mutation_audit_review_service.py`
- [Source: service handling à enrichir] `backend/app/services/canonical_entitlement_alert_handling_service.py`
- [Source: router — endpoint handle (ligne 1186) + review-history (ligne 1516)] `backend/app/api/v1/routers/ops_entitlement_mutation_audits.py`
- [Source: tests intégration 61.43] `backend/app/tests/integration/test_ops_alert_event_handle_api.py`
- [Source: tests unitaires 61.43] `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implémentation de la table append-only `canonical_entitlement_mutation_alert_event_handling_events` avec migration Alembic `20260329_0062` et enregistrement du modèle SQLAlchemy dans `Base.metadata`.
- Enrichissement de `CanonicalEntitlementAlertHandlingService` avec propagation `request_id`, règle no-op, historisation append-only et conservation de l'invariant "pas de commit dans le service".
- Ajout de l'endpoint `GET /mutation-audits/alerts/{alert_event_id}/handling-history` avec pagination `limit`/`offset`, ordre `handled_at DESC, id DESC`, contrôle d'accès ops/admin et réponse `response_model_exclude_none=True`.
- Ajout des tests unitaires et d'intégration couvrant création d'events, changements réels, no-op, propagation `request_id`, pagination, ordre, sécurité et non-régressions batch retry / handle.
- Validation locale exécutée dans le venv: `ruff check .` puis `pytest -q` sur tout le backend, résultat `2525 passed, 3 skipped`.
- Double passe de revue `bmad-code-review` effectuée sur le périmètre 61.44: aucune issue code HIGH/MEDIUM restante; un seul écart de traçabilité story (`File List`) a été corrigé entre les deux passes.

### File List

- _bmad-output/implementation-artifacts/61-44-historisation-append-only-transitions-handling-alertes-ops.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/canonical_entitlement_mutation_alert_event_handling_event.py
- backend/app/services/canonical_entitlement_alert_handling_service.py
- backend/app/tests/integration/test_ops_alert_event_handling_history_api.py
- backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py
- backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py
- backend/docs/entitlements-canonical-platform.md
- backend/migrations/versions/20260329_0062_add_alert_event_handling_events_table.py
- backend/README.md

### Change Log

- 2026-03-29: Implémentation complète de la story 61.44, ajout de l'historique append-only de handling, couverture de tests associée et mise à jour de la documentation.
