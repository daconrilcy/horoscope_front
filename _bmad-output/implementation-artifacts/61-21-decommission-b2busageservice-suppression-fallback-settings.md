# Story 61.21 : Décommission de B2BUsageService et suppression du fallback settings sur b2b_api_access

Status: done

## Story

En tant qu'opérateur ou développeur backend,
je veux supprimer le chemin `settings_fallback` de `B2BApiEntitlementGate` et retirer l'appel à `B2BUsageService.consume_or_raise()` du flux runtime `/v1/b2b/astrology/weekly-by-sign`,
afin que tous les comptes B2B actifs in-scope soient résolus exclusivement en `canonical_quota`, `canonical_unlimited` ou `canonical_disabled`, et que le code legacy de fallback ne soit plus exécuté en production.

## Contexte

La story 61.20 a fourni les endpoints de réparation ops (`POST /repair/run`, `POST /repair/set-admin-user`, `POST /repair/classify-zero-units`) qui ont amené tous les comptes B2B actifs en résolution canonique. Le prérequis opérationnel — `GET /v1/ops/b2b/entitlements/audit?blocker_only=true` retourne vide ou uniquement des exceptions documentées — est satisfait.

La story 61.21 est l'étape de décommission : retirer définitivement le code de fallback du chemin critique runtime.

**Prérequis opérationnel (à vérifier avant déploiement) :**
```
GET /v1/ops/b2b/entitlements/audit?blocker_only=true → total_count=0
```

## Acceptance Criteria

### Décommission de la gate

1. `B2BApiEntitlementGate.check_and_consume()` ne retourne plus jamais `path="settings_fallback"`. Le Literal dans `B2BApiEntitlementResult` est mis à jour : `path: Literal["canonical_quota", "canonical_unlimited"]` (les deux seuls chemins de succès restants — `canonical_disabled` lève directement une exception).
2. Chaque situation qui retournait `settings_fallback` lève désormais une `B2BApiAccessDeniedError` explicite avec un code spécifique :
   - `admin_user_id is None` → code `b2b_account_not_configured` (log WARNING conservé, converti en erreur)
   - `canonical_plan is None` → code `b2b_no_canonical_plan`
   - `binding is None` → code `b2b_no_binding`
   - `binding.access_mode == QUOTA` mais aucun quota en DB → code `b2b_no_quota_defined`
   - `access_mode` inconnu / non géré → code `b2b_unknown_access_mode`
3. Chaque `B2BApiAccessDeniedError` levée en remplacement de `settings_fallback` fait l'objet d'un `logger.warning(...)` structuré dans la gate, **avant** le `raise`, avec au minimum `account_id` et `code`. Exemple : `logger.warning("b2b_gate_blocked account_id=%s code=%s", account_id, "b2b_no_canonical_plan")`. Ces logs constituent le signal d'exploitation principal pour détecter des comptes résiduels non configurés après déploiement.
4. Ces nouvelles erreurs sont toutes mappées à HTTP 403 dans `b2b_astrology.py` (même traitement que `b2b_api_access_denied`).
5. Le champ `source` du dataclass `B2BApiEntitlementResult` reste valide (valeur `"canonical"` inchangée).

### Décommission du fallback dans le router

6. Dans `b2b_astrology.py`, la branche `if gate_result.path == "settings_fallback"` est supprimée ainsi que l'appel à `B2BUsageService.consume_or_raise()`.
7. L'import `from app.services.b2b_usage_service import B2BUsageService, B2BUsageServiceError` est supprimé du router `b2b_astrology.py`.
8. Le bloc `except (B2BUsageServiceError, B2BApiAccessDeniedError, B2BApiQuotaExceededError)` est simplifié pour ne plus mentionner `B2BUsageServiceError` (qui n'est plus levée dans ce contexte).
9. La variable `quota_info` dans le handler `get_weekly_by_sign` est unifiée sur `"source": "canonical"` pour **tous** les chemins canoniques. La distinction quota vs unlimited est portée par la présence ou l'absence des champs `limit`, `remaining`, et `window_end` (présents pour `canonical_quota`, absents pour `canonical_unlimited`). Le cas `"source": "settings_fallback"` est supprimé. Contrat après décommission :
   - `canonical_quota` → `{"source": "canonical", "limit": N, "remaining": N, "window_end": datetime}`
   - `canonical_unlimited` → `{"source": "canonical"}` (sans `limit`/`remaining`)

### Conservation de B2BUsageService

10. Le fichier `backend/app/services/b2b_usage_service.py` est conservé sans suppression. La classe `B2BUsageService` est marquée deprecated via un commentaire de classe et un avertissement docstring : `"Deprecated: ce service n'est plus appelé dans le flux runtime principal depuis la story 61.21. Il reste actif pour les endpoints /v1/b2b/usage/* jusqu'à leur décommission future."`.
11. `B2BUsageService` continue d'être utilisé par `GET /v1/b2b/usage/summary` (endpoint séparé, hors périmètre de cette story).
12. Les settings `b2b_daily_usage_limit`, `b2b_monthly_usage_limit`, `b2b_usage_limit_mode` dans `app/core/config.py` sont conservés sans modification (ils sont encore lus par `B2BUsageService`).

### Mise à jour des tests unitaires de la gate

13. Dans `test_b2b_api_entitlement_gate.py`, les tests `test_check_and_consume_fallback_no_canonical` et `test_check_and_consume_fallback_no_binding` sont mis à jour : ils doivent désormais asserter `pytest.raises(B2BApiAccessDeniedError)` avec les codes respectifs `b2b_no_canonical_plan` et `b2b_no_binding`.
14. Le test `test_check_and_consume_admin_user_missing_logs_warning` est mis à jour : asserter `pytest.raises(B2BApiAccessDeniedError)` avec code `b2b_account_not_configured`, et vérifier que le log WARNING est toujours émis (`"b2b_gate_blocked"` ou `"admin_user_id_missing"` dans `caplog.text`).
15. Aucun nouveau test ne doit asserter `result.path == "settings_fallback"`.

### Mise à jour des tests d'intégration b2b_astrology

16. Dans `test_b2b_astrology_api.py`, les tests qui créent un compte sans plan canonique (`_create_enterprise_api_key`) et s'attendent à HTTP 200 via le fallback doivent être adaptés :
    - **Option A** (recommandée) : Créer un helper `_create_enterprise_api_key_with_canonical_plan()` qui, en plus du compte, crée un `PlanCatalogModel` B2B + `FeatureCatalogModel` + `PlanFeatureBindingModel(access_mode=UNLIMITED, source_origin="manual")` liés à un `EnterpriseBillingPlanModel` fictif (voir patron complet dans Dev Notes). Remplacer `_create_enterprise_api_key()` par ce helper dans les tests : `test_b2b_astrology_returns_weekly_by_sign_with_valid_api_key`, `test_b2b_astrology_returns_429_when_rate_limited`, `test_b2b_astrology_keeps_auth_error_when_audit_is_unavailable`.
    - **Option B** : Mocker `B2BApiEntitlementGate.check_and_consume()` pour retourner directement `B2BApiEntitlementResult(path="canonical_unlimited")` dans les tests qui ne testent pas la gate elle-même.
    - **`test_b2b_usage_summary_returns_metrics_for_credential` n'est PAS modifié** (voir invariant 18) — il prouve que `B2BUsageService` reste fonctionnel indépendamment du nouveau monde canonique.
17. Le test `test_b2b_astrology_returns_429_when_b2b_quota_exceeded` doit tester la limite canonique (via `B2BApiQuotaExceededError` levée par la gate) plutôt que via `B2BUsageService`. Utiliser un helper dédié qui crée un binding QUOTA avec `quota_limit=1` + `source_origin="manual"`. Faire 2 appels HTTP : le premier retourne 200 (consomme 1/1), le second retourne 429 avec code `b2b_api_quota_exceeded`. **Ne plus passer par `monkeypatch.setattr(settings, "b2b_*")`** — ces settings n'impactent plus ce code path.

### Invariants

18. `test_b2b_usage_summary_returns_metrics_for_credential` n'est **pas modifié** : ce test prouve que `B2BUsageService` et l'endpoint `/v1/b2b/usage/summary` restent fonctionnels. Son compte sans plan canonique va maintenant retourner 403 sur `weekly-by-sign` — ce n'est plus son périmètre. Le test lui-même teste un endpoint différent et reste valide sans modification (il appelle uniquement `/v1/b2b/usage/summary`).
19. `B2BUsageService` n'est pas supprimé, ni ses tests unitaires (`test_b2b_usage_service.py`) ni ses tests d'intégration (`test_b2b_usage_api.py`).
20. Aucune migration Alembic, aucune suppression de données en base, aucune modification du modèle de données.
21. Aucune modification de `b2b_canonical_plan_resolver.py`, `b2b_audit_service.py`, `b2b_entitlement_repair_service.py`, `b2b_entitlements_audit.py`, `b2b_entitlement_repair.py`.
22. Les tests `test_b2b_usage_service.py`, `test_b2b_usage_api.py`, `test_b2b_entitlements_audit.py`, `test_b2b_entitlement_repair.py`, `test_b2b_billing_api.py` continuent de passer sans modification.

### Tests de non-régression

23. Tous les tests suivants passent après implémentation :
    - `test_b2b_api_entitlement_gate.py` (modifié)
    - `test_b2b_astrology_api.py` (modifié)
    - `test_b2b_usage_service.py` (non modifié)
    - `test_b2b_usage_api.py` (non modifié)
    - `test_b2b_audit_service.py` (non modifié)
    - `test_b2b_entitlements_audit.py` (non modifié)
    - `test_b2b_entitlement_repair.py` (non modifié)
    - `test_b2b_entitlement_repair_service.py` (non modifié)
    - `test_b2b_api_entitlements.py` (non modifié)
    - `test_b2b_billing_api.py` (non modifié)

## Tasks / Subtasks

- [x] **Modifier `B2BApiEntitlementGate`** (AC: 1–5)
  - [x] Mettre à jour le Literal de `B2BApiEntitlementResult.path` : `Literal["canonical_quota", "canonical_unlimited"]`
  - [x] Remplacer le `return B2BApiEntitlementResult(path="settings_fallback")` sur `admin_user_id is None` par `logger.warning("b2b_gate_blocked account_id=%s code=%s", account_id, "b2b_account_not_configured")` + `raise B2BApiAccessDeniedError(code="b2b_account_not_configured", details={"reason": "admin_user_id_missing"})`
  - [x] Remplacer le `return B2BApiEntitlementResult(path="settings_fallback")` sur `canonical_plan is None` par `logger.warning(...)` + `raise B2BApiAccessDeniedError(code="b2b_no_canonical_plan", details={"account_id": account_id})`
  - [x] Remplacer le `return B2BApiEntitlementResult(path="settings_fallback")` sur `binding is None` par `logger.warning(...)` + `raise B2BApiAccessDeniedError(code="b2b_no_binding", details={"account_id": account_id})`
  - [x] Remplacer le `return B2BApiEntitlementResult(path="settings_fallback")` sur `QUOTA sans quotas` par `logger.warning(...)` + `raise B2BApiAccessDeniedError(code="b2b_no_quota_defined", details={"account_id": account_id})`
  - [x] Remplacer le dernier `return B2BApiEntitlementResult(path="settings_fallback")` (fin de méthode) par `logger.warning(...)` + `raise B2BApiAccessDeniedError(code="b2b_unknown_access_mode", details={"access_mode": str(binding.access_mode)})`

- [x] **Modifier `b2b_astrology.py`** (AC: 6–9)
  - [x] Supprimer l'import `from app.services.b2b_usage_service import B2BUsageService, B2BUsageServiceError`
  - [x] Supprimer la branche `if gate_result.path == "settings_fallback": B2BUsageService.consume_or_raise(...)`
  - [x] Retirer `B2BUsageServiceError` du bloc `except (B2BUsageServiceError, B2BApiAccessDeniedError, B2BApiQuotaExceededError)` — le simplifier en `except (B2BApiAccessDeniedError, B2BApiQuotaExceededError)`
  - [x] Unifier `quota_info` sur `"source": "canonical"` : `canonical_quota` → `{"source": "canonical", "limit": ..., "remaining": ..., "window_end": ...}` ; `canonical_unlimited` → `{"source": "canonical"}` (sans les champs optionnels)
  - [x] Vérifier que tous les nouveaux codes d'erreur de la gate sont mappés à HTTP 403 (via le `isinstance(error, B2BApiAccessDeniedError)` existant)

- [x] **Marquer `B2BUsageService` deprecated** (AC: 10–12)
  - [x] Ajouter un commentaire de classe + docstring deprecation dans `b2b_usage_service.py`
  - [x] Ne rien toucher d'autre dans ce fichier

- [x] **Mettre à jour `test_b2b_api_entitlement_gate.py`** (AC: 13–15)
  - [x] `test_check_and_consume_fallback_no_canonical` → `pytest.raises(B2BApiAccessDeniedError)` avec `exc.value.code == "b2b_no_canonical_plan"`
  - [x] `test_check_and_consume_fallback_no_binding` → `pytest.raises(B2BApiAccessDeniedError)` avec `exc.value.code == "b2b_no_binding"`
  - [x] `test_check_and_consume_admin_user_missing_logs_warning` → `pytest.raises(B2BApiAccessDeniedError)` avec `exc.value.code == "b2b_account_not_configured"` + `assert "b2b_gate_blocked" in caplog.text` (ou `"admin_user_id_missing"` selon le message choisi)

- [x] **Mettre à jour `test_b2b_astrology_api.py`** (AC: 16–17)
  - [x] Créer `_create_enterprise_api_key_with_canonical_plan(email)` : crée user + account + `EnterpriseBillingPlanModel(included_monthly_units=0)` + `EnterpriseAccountBillingPlanModel` + `PlanCatalogModel(audience=B2B, source_type=migrated_from_enterprise_plan, is_active=True)` + `FeatureCatalogModel(feature_code="b2b_api_access")` + `PlanFeatureBindingModel(access_mode=UNLIMITED, is_enabled=True, source_origin="manual")` (voir patron complet dans Dev Notes)
  - [x] Remplacer `_create_enterprise_api_key(...)` par `_create_enterprise_api_key_with_canonical_plan(...)` dans : `test_b2b_astrology_returns_weekly_by_sign_with_valid_api_key`, `test_b2b_astrology_returns_429_when_rate_limited`, `test_b2b_astrology_keeps_auth_error_when_audit_is_unavailable` (3 tests seulement — **pas** `test_b2b_usage_summary_returns_metrics_for_credential`)
  - [x] Mettre à jour `test_b2b_astrology_returns_429_when_b2b_quota_exceeded` : binding QUOTA `quota_limit=1` + `source_origin="manual"`, 2 appels HTTP pour déclencher le 429. Supprimer les `monkeypatch.setattr(settings, "b2b_*")`.

- [x] **Vérification non-régression** (AC: 21)
  - [x] Lancer : `pytest -q app/tests/unit/test_b2b_api_entitlement_gate.py app/tests/integration/test_b2b_astrology_api.py -v`
  - [x] Lancer : `pytest -q app/tests/unit/test_b2b_usage_service.py app/tests/integration/test_b2b_usage_api.py app/tests/unit/test_b2b_audit_service.py app/tests/integration/test_b2b_entitlements_audit.py app/tests/integration/test_b2b_entitlement_repair.py app/tests/unit/test_b2b_entitlement_repair_service.py app/tests/integration/test_b2b_api_entitlements.py app/tests/integration/test_b2b_billing_api.py -v`

## Dev Notes

### Principe directeur : erreur explicite plutôt que dégradation silencieuse

Avant 61.21, un compte sans plan canonique tombait silencieusement en `settings_fallback` puis était compté via `B2BUsageService`. Après 61.21, la gate **refuse explicitement** avec un code d'erreur métier clair (HTTP 403). C'est un changement de comportement intentionnel — les comptes non configurés doivent être repérés et corrigés, pas silencieusement acceptés.

### État exact du code avant modification

**`b2b_api_entitlement_gate.py` lignes à modifier (4 occurrences de `settings_fallback`) :**
- Ligne 70 : `return B2BApiEntitlementResult(path="settings_fallback")` après `admin_user_id is None`
- Ligne 77 : `return B2BApiEntitlementResult(path="settings_fallback")` après `canonical_plan is None`
- Ligne 90 : `return B2BApiEntitlementResult(path="settings_fallback")` après `binding is None`
- Ligne 113 : `return B2BApiEntitlementResult(path="settings_fallback")` après `not quotas_models`
- Ligne 147 : `return B2BApiEntitlementResult(path="settings_fallback")` en fin de méthode

**`b2b_astrology.py` lignes à supprimer :**
- Ligne 31 : `from app.services.b2b_usage_service import B2BUsageService, B2BUsageServiceError`
- Lignes 149–157 : bloc `if gate_result.path == "settings_fallback": B2BUsageService.consume_or_raise(...); quota_info = {"source": "settings_fallback"}`
- Ligne 202–208 : `B2BUsageServiceError` dans le bloc except

### Pattern du helper de test pour l'Option A

Le binding utilise `source_origin="manual"` car il représente un plan classifié manuellement via `classify-zero-units` (trajectoire réelle du système décrite dans 61.20). Vérifier la valeur exacte de l'enum `SourceOrigin.MANUAL` dans `product_entitlements.py` — si absent, utiliser la valeur string `"manual"` directement.

```python
def _create_enterprise_api_key_with_canonical_plan(email: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="enterprise_admin")
        account = EnterpriseAccountModel(admin_user_id=auth.user.id, company_name="Acme Media", status="active")
        db.add(account)
        db.flush()

        # Plan enterprise fictif (included_monthly_units=0, classifié manuellement en UNLIMITED)
        ent_plan = EnterpriseBillingPlanModel(code=f"plan-{auth.user.id}", display_name="Test Plan",
                                              monthly_fixed_cents=1000, included_monthly_units=0)
        db.add(ent_plan)
        db.flush()
        db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=account.id, plan_id=ent_plan.id))

        # Plan canonique (migré depuis enterprise plan)
        plan = PlanCatalogModel(plan_code=f"b2b-{auth.user.id}", plan_name="B2B Test", audience=Audience.B2B,
                                source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
                                source_id=ent_plan.id, is_active=True)
        db.add(plan)
        db.flush()

        # Feature catalog (get_or_create — peut exister dans d'autres tests du même run)
        feature = db.scalar(select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "b2b_api_access"))
        if not feature:
            feature = FeatureCatalogModel(feature_code="b2b_api_access", feature_name="B2B API", is_metered=True)
            db.add(feature)
            db.flush()

        # Binding classifié manuellement (source_origin="manual" = trajectoire classify-zero-units)
        binding = PlanFeatureBindingModel(plan_id=plan.id, feature_id=feature.id,
                                          access_mode=AccessMode.UNLIMITED, is_enabled=True,
                                          source_origin="manual")
        db.add(binding)

        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key
```

**Imports à ajouter dans `test_b2b_astrology_api.py` :**
```python
from sqlalchemy import select
from app.infra.db.models.enterprise_billing import EnterpriseAccountBillingPlanModel, EnterpriseBillingPlanModel
from app.infra.db.models.product_entitlements import (
    AccessMode, Audience, FeatureCatalogModel, PlanCatalogModel, PlanFeatureBindingModel, SourceOrigin,
)
```

### Pattern pour tester la limite canonique (test_b2b_astrology_returns_429_when_b2b_quota_exceeded)

Créer un helper local avec binding QUOTA + `source_origin="manual"` + quota à 1 unité. Deux appels HTTP suffisent : le premier consomme la seule unité disponible (HTTP 200), le second déclenche `B2BApiQuotaExceededError` (HTTP 429). Pas besoin de `FeatureUsageCounterModel` pré-alimenté.

```python
# binding QUOTA classifié manuellement, quota_limit=1
binding = PlanFeatureBindingModel(plan_id=plan.id, feature_id=feature.id,
                                  access_mode=AccessMode.QUOTA, is_enabled=True,
                                  source_origin="manual")
db.add(binding)
db.flush()
quota = PlanFeatureQuotaModel(plan_feature_binding_id=binding.id, quota_key="calls", quota_limit=1,
                               period_unit=PeriodUnit.MONTH, period_value=1, reset_mode=ResetMode.CALENDAR,
                               source_origin="manual")
db.add(quota)
```

Code d'erreur asserté inchangé : `b2b_api_quota_exceeded`. Les `monkeypatch.setattr(settings, "b2b_*")` sont supprimés.

### Pourquoi conserver B2BUsageService

Le service alimente encore `GET /v1/b2b/usage/summary` (router `b2b_usage_api.py`) et a ses propres tests. Sa suppression est une story future (61.22+). Pour l'instant, la décommission ne concerne que le flux `check_and_consume` dans la gate et le router astrology.

### Contrat unifié quota_info dans la réponse astrology

`quota_info.source` vaut toujours `"canonical"` après décommission. La distinction quota vs unlimited est portée par la présence/absence des champs optionnels `limit`, `remaining`, `window_end` — déjà déclarés `| None` dans le modèle Pydantic `QuotaInfoPayload`.

```python
# canonical_quota (après décommission)
quota_info = {"source": "canonical", "limit": state.quota_limit, "remaining": state.remaining, "window_end": state.window_end}

# canonical_unlimited (après décommission)
quota_info = {"source": "canonical"}
```

Rupture de contrat mineure : `"source": "settings_fallback"` n'est plus émis. Acceptable car c'était un état transitoire documenté.

### Commandes de validation

```bash
.\.venv\Scripts\Activate.ps1

# Lint
cd backend && ruff check app/services/b2b_api_entitlement_gate.py app/api/v1/routers/b2b_astrology.py

# Tests modifiés
cd backend && pytest -q \
  app/tests/unit/test_b2b_api_entitlement_gate.py \
  app/tests/integration/test_b2b_astrology_api.py \
  -v

# Non-régression complète
cd backend && pytest -q \
  app/tests/unit/test_b2b_usage_service.py \
  app/tests/integration/test_b2b_usage_api.py \
  app/tests/unit/test_b2b_audit_service.py \
  app/tests/integration/test_b2b_entitlements_audit.py \
  app/tests/integration/test_b2b_entitlement_repair.py \
  app/tests/unit/test_b2b_entitlement_repair_service.py \
  app/tests/integration/test_b2b_api_entitlements.py \
  app/tests/integration/test_b2b_billing_api.py \
  -v
```

### Project Structure Notes

**Fichiers modifiés :**
- `backend/app/services/b2b_api_entitlement_gate.py` — suppression de tous les retours `settings_fallback`, remplacement par erreurs explicites
- `backend/app/api/v1/routers/b2b_astrology.py` — suppression de la branche `settings_fallback` et de l'import `B2BUsageService`
- `backend/app/services/b2b_usage_service.py` — ajout deprecation docstring uniquement
- `backend/app/tests/unit/test_b2b_api_entitlement_gate.py` — mise à jour des 3 tests fallback
- `backend/app/tests/integration/test_b2b_astrology_api.py` — ajout helper canonical + mise à jour 4-5 tests

**Fichiers NON modifiés :**
- `backend/app/services/b2b_canonical_plan_resolver.py`
- `backend/app/services/b2b_audit_service.py`
- `backend/app/services/b2b_entitlement_repair_service.py`
- `backend/app/api/v1/routers/b2b_entitlements_audit.py`
- `backend/app/api/v1/routers/b2b_entitlement_repair.py`
- `backend/app/core/config.py`
- `backend/app/main.py`

### References

- [Source: backend/app/services/b2b_api_entitlement_gate.py] — code actuel à modifier (5 occurrences de `settings_fallback`)
- [Source: backend/app/api/v1/routers/b2b_astrology.py] — lignes 31, 149-157, 202-208 à supprimer
- [Source: backend/app/services/b2b_usage_service.py] — conserver, annoter deprecated uniquement
- [Source: backend/app/tests/unit/test_b2b_api_entitlement_gate.py] — 3 tests à mettre à jour (lignes 202-234)
- [Source: backend/app/tests/integration/test_b2b_astrology_api.py] — helper + tests à mettre à jour
- [Source: backend/app/infra/db/models/product_entitlements.py] — `AccessMode`, `Audience`, `PlanCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, `FeatureCatalogModel`, `SourceOrigin`, `PeriodUnit`, `ResetMode`
- [Source: backend/app/infra/db/models/enterprise_billing.py] — `EnterpriseBillingPlanModel`, `EnterpriseAccountBillingPlanModel`
- [Source: backend/app/tests/unit/test_b2b_api_entitlement_gate.py#seed_b2b_data] — pattern de seed réutilisable pour le helper de test

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
