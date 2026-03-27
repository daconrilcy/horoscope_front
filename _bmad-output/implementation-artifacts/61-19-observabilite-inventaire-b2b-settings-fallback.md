# Story 61.19 : Observabilité et inventaire des comptes B2B encore en settings_fallback

Status: done

## Story

En tant qu'opérateur ou administrateur,
je veux consulter un endpoint interne d'audit qui liste l'état de résolution des entitlements canoniques pour chaque compte B2B actif,
afin de savoir quels comptes passent en `canonical` et lesquels restent en `settings_fallback`, d'identifier les cas bloquants pour la future décommission de `B2BUsageService`, et de détecter toute anomalie de configuration (binding manquant, `admin_user_id` absent, plan non backfillé).

## Contexte

Après 61.18, le contrôle d'accès B2B est hybride : `B2BApiEntitlementGate` donne la priorité au canonique si un binding `b2b_api_access` existe, et tombe en `settings_fallback` sinon. Avant de pouvoir décommissionner `B2BUsageService` et les settings `b2b_*`, il faut un inventaire fiable qui répond à :
- Combien de comptes B2B ont un plan canonique backfillé ?
- Parmi eux, combien ont un binding `b2b_api_access` actif (quota/unlimited/disabled) ?
- Combien restent en `settings_fallback` faute de binding ou de plan canonique ?
- Y a-t-il des `admin_user_id` manquants ou des cas `manual_review_required` ?

Cette story est **100% lecture pure** — aucune consommation, aucun effet de bord. Elle n'altère pas `B2BUsageService` ni aucun compteur.

## Acceptance Criteria

1. `GET /v1/ops/b2b/entitlements/audit` retourne la liste paginée des comptes B2B actifs avec leur état de résolution canonique. Accessible uniquement aux rôles `ops` et `admin` (HTTP 403 sinon).
2. Pour chaque compte, la réponse inclut les champs :
   - `account_id` (int)
   - `company_name` (str) — valeur de `EnterpriseAccountModel.company_name` ; ce champ est `NOT NULL` en base (`String(255)`, non nullable), donc toujours présent
   - `enterprise_plan_id` (int | null)
   - `enterprise_plan_code` (str | null)
   - `canonical_plan_id` (int | null)
   - `canonical_plan_code` (str | null)
   - `feature_code` = `"b2b_api_access"` (str)
   - `resolution_source` : `"canonical_quota"` | `"canonical_unlimited"` | `"canonical_disabled"` | `"settings_fallback"` (str)
   - `reason` : code enum du chemin de résolution — valeurs exactes : `"admin_user_id_missing"` | `"no_canonical_plan"` | `"no_binding"` | `"disabled_by_plan"` | `"unlimited_access"` | `"quota_binding_active"` | `"manual_review_required"` (str)
   - `binding_status` : `"quota"` | `"unlimited"` | `"disabled"` | `"missing"` | `null` (str | null) — règle : `"missing"` quand le plan canonique existe mais qu'aucun binding `b2b_api_access` n'est trouvé ; `null` quand l'évaluation du binding est impossible faute de plan canonique ou d'`admin_user_id`
   - `quota_limit` (int | null)
   - `remaining` (int | null)
   - `window_end` (str ISO8601 | null)
   - `admin_user_id_present` (bool)
   - `manual_review_required` (bool) — vrai si `included_monthly_units = 0` et pas de quota canonique
3. `resolution_source = "canonical_quota"` si le binding existe, `is_enabled=true`, `access_mode=QUOTA`, et un quota est défini avec `quota_limit > 0`.
4. `resolution_source = "canonical_unlimited"` si le binding existe, `is_enabled=true`, `access_mode=UNLIMITED`.
5. `resolution_source = "canonical_disabled"` si le binding existe mais `is_enabled=false` ou `access_mode=DISABLED` — **le canonique gagne même si settings permissifs** (cohérent avec AC4 de 61-18).
6. `resolution_source = "settings_fallback"` dans tous les autres cas : pas de plan canonique, pas de binding, `admin_user_id` manquant, ou `included_monthly_units=0` sans quota canonique.
7. Pour `resolution_source = "canonical_quota"`, `quota_limit`, `remaining` et `window_end` sont renseignés via `QuotaUsageService.get_usage()` (lecture pure, sans consommation).
8. Pour `resolution_source` ≠ `"canonical_quota"`, `quota_limit`, `remaining`, `window_end` sont `null`.
9. Le paramètre de query `page` (int, défaut=1) et `page_size` (int, défaut=20, max=100) permettent la pagination. La réponse inclut `total_count`, `page`, `page_size`. `total_count` représente le nombre total de comptes correspondant aux filtres actifs (`resolution_source` et/ou `blocker_only`), **avant** découpage en page — il ne reflète pas le nombre d'items retournés dans la page courante. Un `page_size > 100` ou `page < 1` est rejeté par FastAPI via `Query(ge=1)` / `Query(le=100)` (HTTP 422 automatique) — aucun `_error_response()` supplémentaire n'est nécessaire pour ce cas.
10. Le paramètre de query `resolution_source` (optionnel) filtre les résultats sur la valeur exacte. Les valeurs acceptées sont strictement : `canonical_quota`, `canonical_unlimited`, `canonical_disabled`, `settings_fallback`. Toute autre valeur provoque une réponse HTTP 422 via `_error_response()` avec code `invalid_resolution_source` — le filtre n'est pas ignoré silencieusement.
11. Le paramètre de query `blocker_only=true` (bool, défaut=false) filtre pour n'afficher que les cas bloquants pour la décommission : `settings_fallback` et `canonical_disabled`.
12. Le service est strictement en lecture : aucun `db.commit()`, aucun `db.flush()`, aucun `db.add(...)`, aucun appel à `QuotaUsageService.consume()`. Une transaction de lecture SQLAlchemy peut exister implicitement mais aucune mutation ne doit être effectuée ou poussée vers la base.
13. Si `admin_user_id` est `None` pour un compte, `admin_user_id_present=false`, `resolution_source="settings_fallback"`, `reason="admin_user_id_missing"`.
14. Les tests unitaires couvrent : `canonical_quota`, `canonical_unlimited`, `canonical_disabled` (is_enabled=false), binding manquant → `settings_fallback`, plan canonique absent → `settings_fallback`, `admin_user_id` manquant → `settings_fallback`, `manual_review_required=true`, pagination + filtre `resolution_source`, filtre `blocker_only`.
15. Les tests d'intégration couvrent : liste avec au moins 2 comptes de types différents, filtre `resolution_source=settings_fallback`, `blocker_only=true`, accès sans rôle `ops`/`admin` → 403.
16. Les tests existants `test_b2b_api_entitlement_gate.py`, `test_b2b_usage_service.py`, `test_entitlement_service.py`, `test_quota_usage_service.py` continuent de passer.

## Tasks / Subtasks

- [x] **Extraire `resolve_b2b_canonical_plan` dans un helper partagé** (AC: 1–6)
  - [x] Créer `backend/app/services/b2b_canonical_plan_resolver.py`
  - [x] Y déplacer la logique de `B2BApiEntitlementGate._resolve_b2b_canonical_plan()` en fonction publique `resolve_b2b_canonical_plan(db, account_id) -> PlanCatalogModel | None`
  - [x] Mettre à jour `b2b_api_entitlement_gate.py` pour importer et appeler `resolve_b2b_canonical_plan()` au lieu de `_resolve_b2b_canonical_plan()` (la méthode privée peut être supprimée ou devenir un alias)
  - [x] Ce helper n'a aucun effet de bord — lecture seule sur `enterprise_account_billing_plans` et `plan_catalog`

- [x] **Créer le service `B2BAuditService`** (AC: 2–13)
  - [x] Créer `backend/app/services/b2b_audit_service.py`
  - [x] Définir le dataclass `B2BAuditEntry` avec tous les champs de l'AC2
  - [x] Implémenter `B2BAuditService.list_b2b_entitlement_audit(db, *, page, page_size, resolution_source_filter, blocker_only) -> tuple[list[B2BAuditEntry], int]`
  - [x] Charger tous les comptes B2B actifs (`enterprise_accounts.status = 'active'`) paginés
  - [x] Pour chaque compte, résoudre la chaîne : `admin_user_id` → plan enterprise → plan canonique → binding → quota
  - [x] **Réutiliser** `resolve_b2b_canonical_plan()` depuis `b2b_canonical_plan_resolver.py` — ne pas dépendre des internals de la gate
  - [x] **Réutiliser** `QuotaUsageService.get_usage()` pour lire l'état du quota (lecture seule, sans consommation)
  - [x] Calculer `resolution_source` et `reason` selon les règles des AC3–AC6 ; utiliser les valeurs enum exactes définies dans l'AC2
  - [x] Calculer `manual_review_required = (included_monthly_units == 0 and (binding is None or quota_limit == 0))`
  - [x] Appliquer les filtres `resolution_source_filter` et `blocker_only` au niveau SQL ou Python

- [x] **Créer le router `b2b_entitlements_audit.py`** (AC: 1, 9–11)
  - [x] Créer `backend/app/api/v1/routers/b2b_entitlements_audit.py`
  - [x] Préfixe : `/v1/ops/b2b/entitlements`
  - [x] Tag : `ops-b2b-entitlements`
  - [x] Endpoint `GET /audit` avec params `page`, `page_size`, `resolution_source` (optional), `blocker_only` (bool, défaut false)
  - [x] Valider `resolution_source` en entrée : si fourni et hors des 4 valeurs autorisées, retourner `_error_response(status_code=422, code="invalid_resolution_source", ...)` — ne pas laisser FastAPI produire une response non structurée
  - [x] **Réutiliser** le pattern `_ensure_ops_role()` de `ops_monitoring.py` (rôles `ops` et `admin`)
  - [x] **Réutiliser** le pattern `_enforce_limits()` avec rate limiting cohérent (ex. 60 req/min global)
  - [x] **Réutiliser** le pattern `_error_response()` pour les erreurs structurées
  - [x] Définir `B2BAuditListApiResponse` (Pydantic) avec `data: B2BAuditListData` + `meta: ResponseMeta`
  - [x] Définir `B2BAuditListData` avec `items`, `total_count`, `page`, `page_size`

- [x] **Enregistrer le router dans `main.py`** (AC: 1)
  - [x] Importer `b2b_entitlements_audit_router` depuis le nouveau fichier
  - [x] Ajouter `app.include_router(b2b_entitlements_audit_router)` dans la liste des routers

- [x] **Tests unitaires** (AC: 14)
  - [x] Créer `backend/app/tests/unit/test_b2b_audit_service.py`
  - [x] Mocker `resolve_b2b_canonical_plan()` (depuis `b2b_canonical_plan_resolver`) et `QuotaUsageService.get_usage()`
  - [x] Test : compte avec plan canonique + binding quota + quota disponible → `canonical_quota`, `remaining` renseigné
  - [x] Test : compte avec binding `unlimited` → `canonical_unlimited`, `remaining=null`
  - [x] Test : compte avec binding `is_enabled=false` → `canonical_disabled`, `remaining=null`
  - [x] Test : compte sans binding → `settings_fallback`, `reason="no_binding"`
  - [x] Test : compte sans plan canonique → `settings_fallback`, `reason="no_canonical_plan"`
  - [x] Test : compte avec `admin_user_id=None` → `settings_fallback`, `reason="admin_user_id_missing"`, `admin_user_id_present=false`
  - [x] Test : `manual_review_required=true` quand `included_monthly_units=0` sans quota canonique
  - [x] Test : filtre `resolution_source="settings_fallback"` exclut les comptes canoniques
  - [x] Test : filtre `blocker_only=true` inclut `settings_fallback` et `canonical_disabled`, exclut `canonical_quota` et `canonical_unlimited`
  - [x] Test : `binding_status=null` quand `admin_user_id` manquant ou plan canonique absent ; `binding_status="missing"` quand plan présent sans binding
  - [x] Test : pagination → page 2 renvoie les bons items

- [x] **Tests d'intégration** (AC: 15)
  - [x] Créer `backend/app/tests/integration/test_b2b_entitlements_audit.py`
  - [x] Setup : créer 2 comptes B2B — 1 avec plan canonique + binding quota, 1 sans binding
  - [x] Test : `GET /v1/ops/b2b/entitlements/audit` avec user `role=ops` → 200, liste les 2 comptes
  - [x] Test : filtre `resolution_source=settings_fallback` → retourne seulement le compte sans binding
  - [x] Test : `blocker_only=true` → retourne le compte sans binding
  - [x] Test : `GET /v1/ops/b2b/entitlements/audit` avec user `role=user` → 403
  - [x] Test : `resolution_source=valeur_inconnue` → 422, code `invalid_resolution_source`
  - [x] Test : aucun `FeatureUsageCounterModel` créé pendant l'appel (effet de bord interdit)

- [x] **Non-régression** (AC: 16)
  - [x] Vérifier que `test_b2b_api_entitlement_gate.py`, `test_b2b_usage_service.py`, `test_entitlement_service.py`, `test_quota_usage_service.py`, `test_b2b_astrology_api.py` passent toujours

## Dev Notes

### Endpoint cible

```
GET /v1/ops/b2b/entitlements/audit
  ?page=1
  &page_size=20
  &resolution_source=settings_fallback  (optionnel)
  &blocker_only=false                   (optionnel)
```

**Auth** : JWT `require_authenticated_user` + `user.role in ["ops", "admin"]` (pattern identique à `ops_monitoring.py`)

### Nouveau helper partagé : `b2b_canonical_plan_resolver.py`

La logique de résolution du plan canonique B2B est extraite dans un helper public pour éviter tout couplage avec les internals d'une gate métier.

```python
# backend/app/services/b2b_canonical_plan_resolver.py
from sqlalchemy.orm import Session
from app.infra.db.models.product_entitlements import PlanCatalogModel

def resolve_b2b_canonical_plan(db: Session, account_id: int) -> PlanCatalogModel | None:
    # Même logique qu'avant : enterprise_account_billing_plans → plan_catalog
    ...
```

**Utilisateurs de ce helper :**
- `b2b_api_entitlement_gate.py` — remplace l'appel à `_resolve_b2b_canonical_plan()` (méthode privée désormais supprimée ou alias)
- `b2b_audit_service.py` — importe directement `resolve_b2b_canonical_plan`

Ne jamais importer depuis `b2b_api_entitlement_gate` dans le service d'audit.

### Réutilisation : lecture quota sans consommation

```python
# Lecture état quota (SANS consommation)
state = QuotaUsageService.get_usage(
    db,
    user_id=admin_user_id,
    feature_code="b2b_api_access",
    quota=quota_def,
)
```

### Chaîne de résolution dans `B2BAuditService`

`binding_status` suit une règle stricte : `null` si l'évaluation n'a pas atteint le binding (pas de plan canonique ou pas d'`admin_user_id`), `"missing"` si le plan canonique existe mais qu'aucun binding n'est trouvé, sinon `"quota"` / `"unlimited"` / `"disabled"`.

Pour chaque compte B2B actif :

```
1. account.admin_user_id is None
   → settings_fallback, reason="admin_user_id_missing"
   binding_status=null  (évaluation impossible)

2. resolve_b2b_canonical_plan(db, account.id) is None
   → settings_fallback, reason="no_canonical_plan"
   binding_status=null  (évaluation impossible)

3. binding = SELECT PlanFeatureBindingModel
              JOIN FeatureCatalogModel ON feature_code = 'b2b_api_access'
              WHERE plan_id = canonical_plan.id
   binding is None:
   → settings_fallback, reason="no_binding"
   binding_status="missing"  (plan présent, binding absent)

4. not binding.is_enabled or binding.access_mode == AccessMode.DISABLED:
   → canonical_disabled, reason="disabled_by_plan"
   binding_status="disabled"

5. binding.access_mode == AccessMode.UNLIMITED:
   → canonical_unlimited, reason="unlimited_access"
   binding_status="unlimited"

6. binding.access_mode == AccessMode.QUOTA:
   quotas = SELECT PlanFeatureQuotaModel WHERE plan_feature_binding_id = binding.id
   quotas is empty or quota_limit == 0:
     → settings_fallback, reason="manual_review_required"
     binding_status="quota"  (binding présent mais quota non configuré)
     manual_review_required = True
   quotas present:
     state = QuotaUsageService.get_usage(...)
     → canonical_quota, remaining/window_end renseignés
     binding_status="quota"
```

### `manual_review_required`

Corrélé à `EnterpriseBillingPlanModel.included_monthly_units == 0` et absence de quota canonique valide. Indique que le plan a été créé sans quota précis — cas de revue manuelle avant décommission.

Requête complémentaire utile :
```python
enterprise_plan = db.scalar(
    select(EnterpriseBillingPlanModel)
    .where(EnterpriseBillingPlanModel.id == account_plan.plan_id)
)
manual_review_required = (
    enterprise_plan is not None
    and enterprise_plan.included_monthly_units == 0
    and (binding is None or not quota_models)  # parenthèses obligatoires — or lié à and
)
```

### Pattern router à reproduire

Fichier de référence : `backend/app/api/v1/routers/ops_monitoring.py`

Structure à reproduire :
```python
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id

router = APIRouter(prefix="/v1/ops/b2b/entitlements", tags=["ops-b2b-entitlements"])

def _ensure_ops_role(user, request_id) -> JSONResponse | None: ...
def _enforce_limits(*, user, request_id, operation) -> JSONResponse | None: ...
def _error_response(...) -> JSONResponse: ...

@router.get("/audit", response_model=B2BAuditListApiResponse, ...)
def get_b2b_entitlements_audit(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    resolution_source: str | None = Query(default=None),
    blocker_only: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any: ...
```

### Validation du filtre `resolution_source`

`resolution_source` est reçu comme `str | None` — FastAPI ne connaît pas les valeurs autorisées. Valider manuellement dans le handler avant tout autre traitement :

```python
VALID_RESOLUTION_SOURCES = {"canonical_quota", "canonical_unlimited", "canonical_disabled", "settings_fallback"}

if resolution_source is not None and resolution_source not in VALID_RESOLUTION_SOURCES:
    return _error_response(
        status_code=422,
        request_id=request_id,
        code="invalid_resolution_source",
        message="Invalid resolution_source filter value",
        details={"allowed": sorted(VALID_RESOLUTION_SOURCES), "received": resolution_source},
    )
```

Ce contrôle se place après `_ensure_ops_role()` et `_enforce_limits()`, avant l'appel au service.

### Contrat de réponse

```json
{
  "data": {
    "items": [
      {
        "account_id": 42,
        "company_name": "Acme Corp",
        "enterprise_plan_id": 7,
        "enterprise_plan_code": "acme_plan_v2",
        "canonical_plan_id": 3,
        "canonical_plan_code": "b2b_acme_plan_v2",
        "feature_code": "b2b_api_access",
        "resolution_source": "canonical_quota",
        "reason": "quota_binding_active",
        "binding_status": "quota",
        "quota_limit": 1000,
        "remaining": 742,
        "window_end": "2026-04-01T00:00:00Z",
        "admin_user_id_present": true,
        "manual_review_required": false
      },
      {
        "account_id": 99,
        "company_name": "Beta SAS",
        "enterprise_plan_id": 12,
        "enterprise_plan_code": "beta_plan_v1",
        "canonical_plan_id": null,
        "canonical_plan_code": null,
        "feature_code": "b2b_api_access",
        "resolution_source": "settings_fallback",
        "reason": "no_canonical_plan",
        "binding_status": null,
        "quota_limit": null,
        "remaining": null,
        "window_end": null,
        "admin_user_id_present": true,
        "manual_review_required": true
      }
    ],
    "total_count": 2,
    "page": 1,
    "page_size": 20
  },
  "meta": { "request_id": "req_abc123" }
}
```

### Performance et volumétrie

En production, la liste des comptes B2B actifs est supposée faible (< 500 comptes). La pagination (défaut 20) et les filtres évitent tout problème de charge. Ne pas faire de requêtes N+1 : pré-charger les `EnterpriseAccountBillingPlanModel` et `EnterpriseBillingPlanModel` en une seule requête (JOIN ou `in_()`) si le volume est > 50 comptes.

### Interdictions strictes

- **NE PAS** appeler `QuotaUsageService.consume()` — lecture seule uniquement
- **NE PAS** appeler `BillingService.get_subscription_status()` — B2C Stripe uniquement
- **NE PAS** appeler `EntitlementService.get_feature_entitlement()` — B2C uniquement
- **NE PAS** appeler `B2BApiEntitlementGate.check_and_consume()` — consomme des unités
- **NE PAS** ouvrir de `db.commit()` dans ce service

### Hors périmètre (ne pas toucher)

- Supprimer ou modifier `B2BUsageService`
- Supprimer les settings `b2b_*`
- Créer une migration Alembic
- Modifier `B2BApiEntitlementGate`
- Modifier `b2b_astrology.py`

### Commandes de validation

```bash
# Activer le venv
.\.venv\Scripts\Activate.ps1

# Lint
cd backend && ruff check app/services/b2b_canonical_plan_resolver.py app/services/b2b_audit_service.py app/api/v1/routers/b2b_entitlements_audit.py app/services/b2b_api_entitlement_gate.py

# Tests unitaires
cd backend && pytest -q app/tests/unit/test_b2b_audit_service.py -v

# Tests d'intégration
cd backend && pytest -q app/tests/integration/test_b2b_entitlements_audit.py -v

# Non-régression
cd backend && pytest -q app/tests/unit/test_b2b_api_entitlement_gate.py app/tests/unit/test_b2b_usage_service.py app/tests/unit/test_entitlement_service.py app/tests/unit/test_quota_usage_service.py app/tests/integration/test_b2b_astrology_api.py app/tests/integration/test_b2b_api_entitlements.py -v
```

### Project Structure Notes

Nouveaux fichiers à créer :
- `backend/app/services/b2b_canonical_plan_resolver.py` (helper partagé — même répertoire que `b2b_api_entitlement_gate.py`)
- `backend/app/services/b2b_audit_service.py` (même répertoire que `b2b_api_entitlement_gate.py`)
- `backend/app/api/v1/routers/b2b_entitlements_audit.py` (même répertoire que `ops_monitoring.py`)
- `backend/app/tests/unit/test_b2b_audit_service.py`
- `backend/app/tests/integration/test_b2b_entitlements_audit.py`

Fichiers modifiés :
- `backend/app/services/b2b_api_entitlement_gate.py` — remplacer l'appel à `_resolve_b2b_canonical_plan()` par `resolve_b2b_canonical_plan()` importé depuis `b2b_canonical_plan_resolver`
- `backend/app/main.py` — ajouter l'import et `app.include_router(b2b_entitlements_audit_router)`

### References

- [Source: backend/app/services/b2b_canonical_plan_resolver.py] — `resolve_b2b_canonical_plan()` helper partagé (à créer dans cette story)
- [Source: backend/app/services/b2b_api_entitlement_gate.py] — gate existante (61-18), à mettre à jour pour utiliser le resolver partagé
- [Source: backend/app/services/quota_usage_service.py] — `get_usage()` lecture seule
- [Source: backend/app/api/v1/routers/ops_monitoring.py] — pattern router ops à reproduire
- [Source: backend/app/infra/db/models/enterprise_account.py] — `EnterpriseAccountModel.admin_user_id`, `status`
- [Source: backend/app/infra/db/models/enterprise_billing.py] — `EnterpriseBillingPlanModel.included_monthly_units`, `EnterpriseAccountBillingPlanModel`
- [Source: backend/app/infra/db/models/product_entitlements.py] — `PlanCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, `AccessMode`, `Audience`
- [Source: backend/app/services/entitlement_types.py] — `QuotaDefinition`, `UsageState`
- [Source: backend/app/api/dependencies/auth.py] — `AuthenticatedUser`, `require_authenticated_user`
- [Source: backend/app/tests/integration/test_b2b_api_entitlements.py] — pattern setup B2B à réutiliser (créé en 61-18)
- [Source: backend/app/main.py] — liste des routers enregistrés

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
