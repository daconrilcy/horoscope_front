# Story 61.20 : Résorption des blockers B2B et préparation de la bascule 100% canonique

Status: done

## Story

En tant qu'opérateur ou administrateur,
je veux disposer d'un ensemble d'endpoints de réparation ops qui corrigent automatiquement ou guidés les cas `settings_fallback` identifiés par l'audit (61.19),
afin que tous les comptes B2B actifs in-scope passent en résolution canonique (`canonical_quota`, `canonical_unlimited` ou `canonical_disabled`) et que `GET /v1/ops/b2b/entitlements/audit` ne retourne plus `settings_fallback` sauf pour une liste d'exceptions explicitement documentées et acceptées.

## Contexte

La story 61.19 a fourni la visibilité : `GET /v1/ops/b2b/entitlements/audit` liste l'état de chaque compte B2B et identifie les cas bloquants pour la future décommission de `B2BUsageService`. La story 61.20 transforme cette visibilité en action.

Les cas `settings_fallback` identifiés dans l'audit sont de quatre natures :

| Reason | Cause | Réparation possible |
|--------|-------|---------------------|
| `admin_user_id_missing` | Le compte n'a pas d'`admin_user_id` lié | Manuelle : un ops affecte un user existant |
| `no_canonical_plan` | Aucune entrée `plan_catalog` pour ce plan enterprise | Automatique : backfill depuis `enterprise_billing_plans` |
| `no_binding` + `included_monthly_units > 0` | Plan canonique présent mais binding `b2b_api_access` absent | Automatique : création du binding + quota |
| `manual_review_required` / `no_binding` + `included_monthly_units = 0` | `included_monthly_units = 0` — sens ambigu (disabled ? unlimited ? quota ?) | Guidée : un ops choisit explicitement `disabled`, `unlimited` ou `quota` |

Les cas `canonical_disabled` sont intentionnels — le binding existe et désactive explicitement l'accès. **Ils ne sont pas un bug et ne doivent pas être modifiés par cette story.**

**Critère de sortie :** Après exécution des repairs, `GET /v1/ops/b2b/entitlements/audit?blocker_only=true` retourne une liste vide, **ou** retourne uniquement des comptes qui font partie d'une liste d'exceptions explicitement documentées (comptes inactifs hors périmètre, comptes en cours de provisioning, etc.).

## Acceptance Criteria

### Endpoint 1 : Backfill automatique des plans canoniques et des bindings

1. `POST /v1/ops/b2b/entitlements/repair/run` lance le repair automatique. Accessible uniquement aux rôles `ops` et `admin` (HTTP 403 sinon).
2. Le repair automatique couvre, pour chaque compte B2B actif, les deux cas suivants **dans un seul passage** (un compte `no_canonical_plan` avec `included_monthly_units > 0` déclenche d'abord la création du plan canonique, puis immédiatement la création du binding et du quota dans le même appel, sans nécessiter une seconde exécution) :
   - **Cas `no_canonical_plan`** : si `enterprise_billing_plans` existe pour ce compte et qu'aucune entrée `plan_catalog` avec `source_type=migrated_from_enterprise_plan` et `source_id=enterprise_billing_plans.id` n'existe, créer l'entrée manquante (`audience=b2b`, `is_active=true`, `plan_code=<enterprise_plan.code>`, `plan_name=<enterprise_plan.display_name>`, `source_type="migrated_from_enterprise_plan"`, `source_id=enterprise_plan.id`). Après création, si `included_monthly_units > 0`, enchaîner immédiatement sur la création du binding et du quota dans le même run.
   - **Cas `no_binding` avec `included_monthly_units > 0`** : si le plan canonique existe mais qu'aucun `PlanFeatureBindingModel` `b2b_api_access` n'est lié, créer le binding avec `access_mode=QUOTA`, `is_enabled=True`, `source_origin="migrated_from_enterprise_plan"` + le quota correspondant (`quota_key="calls"`, `period_unit="month"`, `period_value=1`, `reset_mode="calendar"`, `quota_limit=included_monthly_units`, `source_origin="migrated_from_enterprise_plan"`).
3. Le repair automatique ne touche PAS aux cas `admin_user_id_missing`, `manual_review_required`, ni aux bindings existants (même `is_enabled=false`).
4. Paramètre optionnel `dry_run=true` (bool, défaut=false) : lorsqu'il est activé, le service calcule et retourne le plan d'action sans aucune mutation DB (`db.commit()` ou `db.add()` interdits). La réponse `dry_run=true` est identique en structure à la réponse normale.
5. La réponse inclut un rapport structuré :
   - `accounts_scanned` (int) — total des comptes actifs examinés
   - `plans_created` (int) — entrées `plan_catalog` créées
   - `bindings_created` (int) — entrées `plan_feature_bindings` créées
   - `quotas_created` (int) — entrées `plan_feature_quotas` créées
   - `skipped_already_canonical` (int) — comptes déjà en résolution canonique, non modifiés
   - `remaining_blockers` (list) — comptes toujours en `settings_fallback` après le repair, avec leur `account_id`, `company_name`, `reason` et une recommandation d'action (`set_admin_user` ou `classify_zero_units`)
   - `dry_run` (bool) — reflète le paramètre d'entrée
6. Le repair est idempotent : re-exécuter `POST /v1/ops/b2b/entitlements/repair/run` sur un état déjà réparé ne crée pas de doublons et retourne `plans_created=0`, `bindings_created=0`, `quotas_created=0`.
7. Le repair respecte les contraintes de schéma existantes : `UniqueConstraint("plan_id", "feature_id")` sur `plan_feature_bindings`, `UniqueConstraint("plan_code")` sur `plan_catalog`, `CheckConstraint("quota_limit > 0")` sur `plan_feature_quotas` — toute violation est capturée et incluse dans `remaining_blockers` avec `reason="schema_constraint_violation"`.

### Endpoint 2 : Affectation de l'`admin_user_id`

8. `POST /v1/ops/b2b/entitlements/repair/set-admin-user` affecte un `admin_user_id` à un compte qui en est dépourvu. Rôles `ops` et `admin` requis (HTTP 403 sinon).
9. Payload JSON : `{ "account_id": int, "user_id": int }`.
10. Vérifications avant mutation :
    - Le compte existe et est actif (`status="active"`) → sinon HTTP 422, code `account_not_found_or_inactive`.
    - Le compte n'a pas encore d'`admin_user_id` → sinon HTTP 422, code `admin_user_already_set` (protection contre l'écrasement accidentel).
    - L'utilisateur cible existe dans `users` → sinon HTTP 422, code `user_not_found`.
    - L'`admin_user_id` cible n'est pas déjà utilisé par un autre compte (`unique=True` en DB) → sinon HTTP 422, code `user_already_admin_of_another_account`.
11. Après mutation réussie, la réponse HTTP 200 inclut `{ "account_id": int, "user_id": int, "status": "ok" }`.

### Endpoint 3 : Classification des plans `included_monthly_units = 0`

12. `POST /v1/ops/b2b/entitlements/repair/classify-zero-units` permet à un ops de décider explicitement de l'`access_mode` d'un binding `b2b_api_access` pour un plan canonique dont `included_monthly_units = 0`. Rôles `ops` et `admin` requis (HTTP 403 sinon).
13. Payload JSON : `{ "canonical_plan_id": int, "access_mode": "disabled" | "unlimited" | "quota", "quota_limit": int | null }`.
14. Règles de validation (dans cet ordre) :
    - Le `canonical_plan_id` doit correspondre à un plan `audience=b2b`, `is_active=true` → sinon HTTP 422, code `canonical_plan_not_found`.
    - Le plan canonique ciblé doit avoir une source `EnterpriseBillingPlanModel` dont `included_monthly_units = 0` : résoudre via `source_type=migrated_from_enterprise_plan` + `source_id` → charger `EnterpriseBillingPlanModel.included_monthly_units` → si `≠ 0`, HTTP 422, code `canonical_plan_not_zero_units_eligible` (protection contre l'utilisation de cet endpoint sur des plans déjà à sémantique claire).
    - Si `access_mode = "quota"`, `quota_limit` doit être fourni et `> 0` → sinon HTTP 422, code `quota_limit_required_for_quota_mode`.
    - Si `access_mode ≠ "quota"`, `quota_limit` doit être `null` ou absent → sinon HTTP 422, code `quota_limit_forbidden_for_non_quota_mode`.
15. Comportement :
    - Si aucun binding `b2b_api_access` n'existe pour ce plan : créer le binding avec l'`access_mode` choisi (`source_origin="manual"`) + le quota si applicable (`source_origin="manual"`). Retourner `"status": "created"`.
    - Si un binding `b2b_api_access` existe déjà avec `access_mode` différent : mettre à jour `access_mode`, `is_enabled` et le quota — supprimer les `PlanFeatureQuotaModel` obsolètes si `access_mode ≠ "quota"`, créer/mettre à jour le `PlanFeatureQuotaModel` si `access_mode = "quota"`. Le `source_origin` du binding et du quota mis à jour devient `"manual"`. Retourner `"status": "updated"`.
    - Si un binding `b2b_api_access` existe déjà avec le même `access_mode` ET le même `quota_limit` : retourner HTTP 200 avec `"status": "already_configured"` (idempotent, aucune mutation).
16. Réponse HTTP 200 : `{ "canonical_plan_id": int, "access_mode": str, "quota_limit": int | null, "status": "created" | "updated" | "already_configured" }`.

### Invariants globaux

17. Aucun des trois endpoints ne modifie `B2BUsageService`, les settings `b2b_*`, ni `B2BApiEntitlementGate`.
18. Aucun des trois endpoints ne supprime de plans (`plan_catalog`), de bindings (`plan_feature_bindings`), ni de comptes (`enterprise_accounts`). L'endpoint `classify-zero-units` est la seule exception autorisée : il peut supprimer des lignes `PlanFeatureQuotaModel` devenues obsolètes lorsqu'un binding existant est reclassifié de `QUOTA` vers `DISABLED` ou `UNLIMITED`. Cette suppression de quotas est explicitement autorisée car elle corrige une incohérence de configuration, pas une donnée métier.
19. Après un appel réussi à `POST /repair/run` (hors dry_run) suivi d'appels `POST /repair/set-admin-user` et `POST /repair/classify-zero-units` pour tous les `remaining_blockers`, un appel à `GET /v1/ops/b2b/entitlements/audit?blocker_only=true` doit retourner `total_count=0` (ou uniquement les exceptions documentées).
20. Chaque endpoint de repair utilise `db.commit()` au bon endroit (contrairement à 61.19 qui était lecture seule). Les commits ne doivent pas être oubliés — c'est la différence architecturale clé avec le service d'audit.
21. Les tests unitaires couvrent : dry_run sans mutation, backfill plan manquant, backfill binding+quota (included_monthly_units > 0), skip si plan/binding déjà présent, contrainte unicité capturée dans remaining_blockers, set-admin-user valide, set-admin-user compte inconnu → 422, set-admin-user user déjà admin → 422, classify-zero-units disabled, classify-zero-units unlimited, classify-zero-units quota avec quota_limit, classify-zero-units quota_limit absent → 422, idempotence (already_configured).
22. Les tests d'intégration couvrent : repair/run sur 3 comptes (1 no_canonical_plan, 1 no_binding avec units > 0, 1 manual_review_required) → rapport correct ; dry_run=true → aucune donnée créée en DB ; set-admin-user end-to-end ; classify-zero-units end-to-end ; accès sans rôle ops/admin → 403 ; appel à GET /audit?blocker_only=true après repair → total_count = 1 (le cas zero_units non classifié) puis total_count = 0 après classify-zero-units.
23. Les tests de non-régression `test_b2b_api_entitlement_gate.py`, `test_b2b_usage_service.py`, `test_b2b_audit_service.py`, `test_b2b_entitlements_audit.py` continuent de passer.

## Tasks / Subtasks

- [x] **Créer `B2BEntitlementRepairService`** (AC: 1–7, 17–20)
  - [x] Service implémenté avec rapport structuré, dry-run, backfill plan/binding/quota, validations métier et commits adaptés.
  - [x] Le run batch précharge les comptes/plans/features et réutilise désormais les créations en mémoire pendant le même passage pour éviter les faux doublons quand plusieurs comptes partagent un plan enterprise.
  - [x] Les violations de contraintes restent capturées comme `schema_constraint_violation`.

- [x] **Implémenter la logique set-admin-user et classify-zero-units dans le service** (AC: 8–16)
  - [x] `set_admin_user()` valide le compte, l’utilisateur cible et l’unicité de l’admin avant commit.
  - [x] `classify_zero_units()` gère création, mise à jour, suppression de quotas obsolètes et idempotence.

- [x] **Créer le router `b2b_entitlement_repair.py`** (AC: 1, 4, 5, 8–9, 12–13, 17)
  - [x] Endpoints `/run`, `/set-admin-user` et `/classify-zero-units` exposés sous `/v1/ops/b2b/entitlements/repair`.
  - [x] Contrôles de rôle, rate limiting et réponses d’erreur structurées en place.

- [x] **Enregistrer le router dans `main.py`** (AC: 1)

- [x] **Tests unitaires** (AC: 21)
  - [x] Couverture service de repair et audit enrichie, y compris le cas multi-comptes sur plan partagé introduit pendant la revue.
  - [x] Les validations et comportements idempotents principaux sont couverts.

- [x] **Tests d'intégration** (AC: 22)
  - [x] Parcours end-to-end `repair/run`, `set-admin-user`, `classify-zero-units` et `audit?blocker_only=true` couverts.
  - [x] La revue a ajouté la vérification que `canonical_disabled` n’est plus compté comme blocker dans `blocker_only=true`.

- [x] **Non-régression** (AC: 23)
  - [x] Les suites B2B ciblées continuent de passer après correction.

## Dev Notes

### Architecture de la story

Cette story est **la suite directe** de 61.19. Elle réutilise toute l'infrastructure mise en place :
- `resolve_b2b_canonical_plan()` depuis `b2b_canonical_plan_resolver.py`
- `B2BAuditService` (peut être appelé pour recalculer l'état final dans les tests d'intégration)
- Pattern router `b2b_entitlements_audit.py` à reproduire fidèlement

### Différence clé avec 61.19 : les commits

En 61.19, zéro `db.commit()`. En 61.20, les endpoints de repair **doivent commiter**. Le pattern recommandé :
- Un seul `db.commit()` à la fin de `run_auto_repair()` si `dry_run=False`
- Un `db.commit()` par mutation dans `set_admin_user()` et `classify_zero_units()`
- En cas d'exception avant le commit, SQLAlchemy annule automatiquement la transaction (pas besoin de `db.rollback()` explicite avec `get_db_session` en dépendance FastAPI)

### Pourquoi ne pas réutiliser directement B2BAuditService dans run_auto_repair

`B2BAuditService.list_b2b_entitlement_audit()` est optimisé pour la pagination et les filtres. Pour le repair, on a besoin d'itérer sur **tous** les comptes (pas seulement une page) et d'avoir accès direct aux objets DB (pas des dataclasses sérialisées). Implémenter la logique inline dans `B2BEntitlementRepairService` en réutilisant les helpers de bas niveau :
- `_prefetch_canonical_plans()` de `B2BAuditService` (méthode statique, réutilisable directement)
- `resolve_b2b_canonical_plan()` si le préchargement est insuffisant

### Gestion de l'exception de service pour les validations

Définir `RepairValidationError(Exception)` dans `b2b_entitlement_repair_service.py` avec `code: str` et `message: str`. Le router attrape cette exception et retourne `_error_response(status_code=422, ...)`. Ce pattern évite de polluer le service avec la logique HTTP.

```python
class RepairValidationError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)
```

### Logique de backfill `_backfill_canonical_plan`

Réutilise exactement la logique de 61.8. La méthode vérifie d'abord l'existence :

```python
existing = db.scalar(
    select(PlanCatalogModel).where(
        PlanCatalogModel.source_type == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        PlanCatalogModel.source_id == enterprise_plan.id,
        PlanCatalogModel.audience == Audience.B2B,
    )
)
if existing:
    return False  # déjà présent, skip

if not dry_run:
    new_plan = PlanCatalogModel(
        plan_code=enterprise_plan.code,
        plan_name=enterprise_plan.display_name,
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=enterprise_plan.id,
        is_active=enterprise_plan.is_active,
    )
    db.add(new_plan)
    db.flush()  # pour obtenir new_plan.id avant le commit final
return True
```

**Important :** utiliser `db.flush()` (pas `db.commit()`) pendant le repair pour obtenir les IDs avant de créer les bindings dépendants, puis un seul `db.commit()` à la fin.

### Provenance (source_type / source_origin) — règle de traçabilité

| Opération | Objet créé/modifié | source_type / source_origin |
|-----------|-------------------|----------------------------|
| `run_auto_repair` — création plan | `plan_catalog` | `source_type = "migrated_from_enterprise_plan"` |
| `run_auto_repair` — création binding | `plan_feature_bindings` | `source_origin = "migrated_from_enterprise_plan"` |
| `run_auto_repair` — création quota | `plan_feature_quotas` | `source_origin = "migrated_from_enterprise_plan"` |
| `classify_zero_units` — création ou mise à jour binding | `plan_feature_bindings` | `source_origin = "manual"` (décision ops explicite) |
| `classify_zero_units` — création ou mise à jour quota | `plan_feature_quotas` | `source_origin = "manual"` (décision ops explicite) |

Cette distinction permet de distinguer après coup les éléments backfillés automatiquement (depuis la DB legacy) des décisions prises manuellement par un ops.

### Logique de `classify_zero_units` — garde contre les plans non-éligibles

Avant toute modification, vérifier que le plan canonique ciblé provient bien d'un `EnterpriseBillingPlanModel` avec `included_monthly_units = 0` :

```python
# Résoudre le plan enterprise source
enterprise_plan = db.scalar(
    select(EnterpriseBillingPlanModel)
    .where(EnterpriseBillingPlanModel.id == canonical_plan.source_id)
) if canonical_plan.source_type == SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value else None

if enterprise_plan is None or enterprise_plan.included_monthly_units != 0:
    raise RepairValidationError(
        code="canonical_plan_not_zero_units_eligible",
        message="This canonical plan is not eligible for classify-zero-units (included_monthly_units != 0 or source not enterprise plan)",
    )
```

### Logique de `classify_zero_units` — mise à jour binding existant

Si un binding `b2b_api_access` existe déjà, l'endpoint doit permettre de le reclassifier (ex. passage de `DISABLED` vers `QUOTA` après correction du plan). La logique de mise à jour :

```python
# Supprimer les quotas existants si on passe en non-QUOTA (seule suppression autorisée par AC 18)
if binding.access_mode == AccessMode.QUOTA and access_mode != "quota":
    for quota in db.scalars(select(PlanFeatureQuotaModel)
                             .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)):
        db.delete(quota)

# Mettre à jour le binding avec source_origin="manual"
binding.access_mode = AccessMode(access_mode)
binding.is_enabled = (access_mode != "disabled")
binding.source_origin = SourceOrigin.MANUAL

# Créer le quota si QUOTA (source_origin="manual")
if access_mode == "quota":
    existing_quota = db.scalar(
        select(PlanFeatureQuotaModel)
        .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
        .limit(1)
    )
    if existing_quota:
        existing_quota.quota_limit = quota_limit
        existing_quota.source_origin = SourceOrigin.MANUAL
    else:
        db.add(PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="calls",
            quota_limit=quota_limit,
            period_unit=PeriodUnit.MONTH,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
            source_origin=SourceOrigin.MANUAL,
        ))
```

### Contrainte `admin_user_id` nullable vs NOT NULL

Le modèle `EnterpriseAccountModel` définit `admin_user_id: Mapped[int]` (NOT NULL en ORM), mais le code de la gate et de l'audit défend contre `None`. Cette défensive programming couvre des données legacy antérieures à la contrainte NOT NULL. La mutation `set_admin_user` doit donc fonctionner même si le champ est théoriquement NOT NULL — en pratique, si un compte a `admin_user_id=None`, c'est qu'il est en base avec NULL.

### Modèle `UserModel` pour la validation

Importer depuis `app.infra.db.models.user` (à vérifier — chercher la classe `UserModel` dans `backend/app/infra/db/models/`).

### Pattern Pydantic des requêtes

```python
class RepairRunResponse(BaseModel):
    data: RepairRunData
    meta: ResponseMeta

class RepairRunData(BaseModel):
    accounts_scanned: int
    plans_created: int
    bindings_created: int
    quotas_created: int
    skipped_already_canonical: int
    remaining_blockers: list[RepairBlockerPayload]
    dry_run: bool

class RepairBlockerPayload(BaseModel):
    account_id: int
    company_name: str
    reason: str
    recommended_action: str
```

### Rate limiting pour les endpoints de repair

Ces endpoints sont mutatifs — appliquer des limites plus restrictives que l'audit :
- Global : 10 req/min
- Par rôle : 5 req/min
- Par user : 3 req/min

Utiliser le même pattern `check_rate_limit()` que `b2b_entitlements_audit.py` avec des clés distinctes (ex. `"b2b_repair:global:run"`).

### Hors périmètre (ne pas toucher)

- Supprimer ou modifier `B2BUsageService` — ce sera une story ultérieure (61.21 ou 61.22)
- Supprimer les settings `b2b_*`
- Créer une migration Alembic
- Modifier `B2BApiEntitlementGate`
- Modifier `b2b_astrology.py`
- Modifier les plans canoniques existants déjà en `canonical_quota` / `canonical_unlimited`

### Commandes de validation

```bash
# Activer le venv
.\.venv\Scripts\Activate.ps1

# Lint
cd backend && ruff check app/services/b2b_entitlement_repair_service.py app/api/v1/routers/b2b_entitlement_repair.py

# Tests unitaires
cd backend && pytest -q app/tests/unit/test_b2b_entitlement_repair_service.py -v

# Tests d'intégration
cd backend && pytest -q app/tests/integration/test_b2b_entitlement_repair.py -v

# Non-régression
cd backend && pytest -q \
  app/tests/unit/test_b2b_api_entitlement_gate.py \
  app/tests/unit/test_b2b_usage_service.py \
  app/tests/unit/test_b2b_audit_service.py \
  app/tests/integration/test_b2b_entitlements_audit.py \
  app/tests/integration/test_b2b_astrology_api.py \
  app/tests/integration/test_b2b_api_entitlements.py \
  -v
```

### Project Structure Notes

Nouveaux fichiers à créer :
- `backend/app/services/b2b_entitlement_repair_service.py` — service de repair
- `backend/app/api/v1/routers/b2b_entitlement_repair.py` — router ops
- `backend/app/tests/unit/test_b2b_entitlement_repair_service.py`
- `backend/app/tests/integration/test_b2b_entitlement_repair.py`

Fichier modifié :
- `backend/app/main.py` — enregistrer `b2b_entitlement_repair_router`

### References

- [Source: backend/app/services/b2b_audit_service.py] — `B2BAuditService` et ses méthodes `_prefetch_*` réutilisables
- [Source: backend/app/services/b2b_canonical_plan_resolver.py] — `resolve_b2b_canonical_plan()` helper partagé
- [Source: backend/app/api/v1/routers/b2b_entitlements_audit.py] — pattern router ops à reproduire (helpers `_ensure_ops_role`, `_enforce_limits`, `_error_response`)
- [Source: backend/app/infra/db/models/product_entitlements.py] — `PlanCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, `FeatureCatalogModel`, `AccessMode`, `Audience`, `SourceOrigin`, `PeriodUnit`, `ResetMode`
- [Source: backend/app/infra/db/models/enterprise_account.py] — `EnterpriseAccountModel.admin_user_id`
- [Source: backend/app/infra/db/models/enterprise_billing.py] — `EnterpriseBillingPlanModel.included_monthly_units`, `EnterpriseAccountBillingPlanModel`
- [Source: backend/app/api/dependencies/auth.py] — `AuthenticatedUser`, `require_authenticated_user`
- [Source: backend/app/main.py] — liste des routers enregistrés
- [Source: backend/app/infra/db/models/] — chercher `UserModel` pour la validation `user_not_found`
- [Source: backend/app/tests/integration/test_b2b_entitlements_audit.py] — pattern setup B2B à réutiliser pour les tests d'intégration

### File List

- `backend/app/infra/db/models/enterprise_account.py` : Rendu `admin_user_id` nullable pour supporter les blockers legacy.
- `backend/app/services/b2b_entitlement_repair_service.py` : Logique de backfill automatique et manuelle, avec réutilisation en mémoire des créations pendant le même batch.
- `backend/app/services/b2b_audit_service.py` : Ajustement du filtre `blocker_only=true` pour exclure `canonical_disabled`.
- `backend/app/api/v1/routers/b2b_entitlement_repair.py` : Router ops avec rate limiting et validation.
- `backend/app/main.py` : Enregistrement du nouveau router.
- `backend/app/tests/unit/test_b2b_entitlement_repair_service.py` : Tests unitaires du service, y compris le cas de plan enterprise partagé.
- `backend/app/tests/unit/test_b2b_audit_service.py` : Test unitaire du filtre `blocker_only=true` mis à jour.
- `backend/app/tests/integration/test_b2b_entitlement_repair.py` : Tests d'intégration end-to-end.
- `backend/app/tests/integration/test_b2b_entitlements_audit.py` : Test d’intégration vérifiant que `canonical_disabled` n’est pas compté comme blocker.

## Dev Agent Record

### Agent Model Used

gemini-2-0-flash-001

### Debug Log References

- [Debug: run_auto_repair IntegrityError fixes] — Ajout de savepoints (`begin_nested`) pour éviter le rollback complet du batch.
- [Debug: Integration tests IntegrityError] — Ajout de `monthly_fixed_cents=0` dans les setups de plans de test.

### Completion Notes List

- Story 61.20 implémentée avec succès.
- Tous les tests (unit, integration, non-régression) sont au vert.
- Le modèle `EnterpriseAccountModel` a été modifié pour autoriser NULL sur `admin_user_id` (blocker legacy).
- Les validations métier de `classify_zero_units` ont été centralisées dans le service.
- Le rate limiting a été appliqué conformément aux AC (10/5/3).
- Code review post-implémentation effectuée et entièrement résorbée sans action ouverte.
- Correction appliquée sur `run_auto_repair()` pour réutiliser les backfills déjà réalisés pendant le même batch et éviter les faux `schema_constraint_violation` sur plans enterprise partagés.
- Correction appliquée sur l’audit `blocker_only=true` pour exclure `canonical_disabled`, conforme au contrat 61.20.
