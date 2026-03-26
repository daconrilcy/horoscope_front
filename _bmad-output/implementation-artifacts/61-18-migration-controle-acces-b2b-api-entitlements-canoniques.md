# Story 61.18 : Migration du contrôle d'accès B2B API vers les entitlements canoniques

Status: done

## Story

En tant que compte entreprise,
je veux que mon accès aux appels API B2B soit gouverné en priorité par le moteur d'entitlements canonique,
afin que les quotas `b2b_api_access` issus de `enterprise_billing_plans` soient réellement appliqués, que les refus soient cohérents, et que le fallback settings historique soit limité aux seuls cas non encore mappés.

## Contexte

Après 61.17, les flux B2C majeurs sont migrés et `QuotaService` a été supprimé.
Le chantier canonique reste incomplet côté B2B :
- 61.8 a introduit la feature canonique `b2b_api_access` dans `plan_catalog` (audience=b2b)
- Le backfill sait créer les plans B2B dans `plan_catalog` et leurs quotas `calls/month`
- Mais les flux B2B réels restent gouvernés par `B2BUsageService` et les settings `b2b_*`
- Colonnes/settings non encore migrées : `settings.b2b_daily_usage_limit`, `settings.b2b_monthly_usage_limit`, `settings.b2b_usage_limit_mode`

Cette story introduit la première migration métier B2B : priorité au canonique si un binding `b2b_api_access` existe, fallback contrôlé vers `B2BUsageService`/settings sinon. Aucune rupture client.

## Acceptance Criteria

1. Pour un compte B2B dont le plan courant a un binding canonique `b2b_api_access`, le contrôle d'accès B2B est gouverné par le **moteur canonique B2B** (`B2BApiEntitlementGate` + `QuotaUsageService`), sans passer par `EntitlementService.get_feature_entitlement()` (B2C-only).
2. Si le binding canonique B2B est `access_mode="quota"`, chaque appel API B2B accepté consomme exactement 1 unité `calls` dans `feature_usage_counters`.
3. Si le binding canonique B2B est `access_mode="unlimited"`, aucun compteur n'est consommé.
4. Si le binding canonique B2B est désactivé (`disabled_by_plan`), l'appel API est refusé HTTP 403 avec code `b2b_api_access_denied`, même si les settings `b2b_*` seraient permissifs — **le canonique gagne toujours**.
5. Si le quota canonique B2B est épuisé, l'appel API est refusé HTTP 429 avec code `b2b_api_quota_exceeded`.
6. Pour un plan B2B avec quota mensuel canonique (`calls / month / calendar`), `usage_states[0].window_end` correspond au début du mois suivant en UTC.
7. Si aucun binding canonique `b2b_api_access` n'existe pour le plan B2B courant, le flux existant `B2BUsageService`/settings continue sans régression.
8. Si `included_monthly_units = 0` correspond à un cas classé manual-review-required / non bindé, aucun comportement métier implicite n'est inventé ; le fallback settings reste utilisé.
9. La politique transactionnelle est : si le traitement aval (`B2BAstrologyService`) échoue **après** une consommation canonique réussie, la transaction est rollbackée et l'unité consommée est annulée. Le client reçoit une erreur 503/422 sans être débité.
10. Les réponses B2B protégées exposent des métadonnées de quota dans le **body JSON** uniquement, sous la clé `quota_info` :
    ```json
    { "quota_info": { "source": "canonical", "limit": 1000, "remaining": 742, "window_end": "2026-04-01T00:00:00Z" } }
    ```
    Pour `settings_fallback`, `quota_info.source = "settings_fallback"` et les champs `limit`/`remaining`/`window_end` sont absents (non disponibles sans appel supplémentaire à `B2BUsageService`).
11. Si `EnterpriseAccountModel.admin_user_id` est nul ou introuvable pour le `account_id` fourni, la gate retourne `path="settings_fallback"` et logue un warning structuré — pas de 500, pas d'interruption du service.
12. Les tests unitaires couvrent : canonique quota, canonique unlimited, canonique disabled, quota épuisé, fallback si pas de binding, fallback si pas de plan canonique, fallback si `admin_user_id` nul, fenêtre mensuelle UTC, aucune double consommation.
13. Les tests d'intégration couvrent : quota canonique actif, quota épuisé, sans binding → fallback settings, binding disabled avec settings permissifs → 403 (canonique gagne), aucune double consommation.
14. Les tests existants `test_b2b_usage_service.py`, `test_entitlement_service.py`, `test_quota_usage_service.py` continuent de passer.

## Tasks / Subtasks

- [x] **Audit du point d'entrée B2B** (AC: 1, 7, 9)
  - [x] Confirmer que `backend/app/api/v1/routers/b2b_astrology.py` `get_weekly_by_sign()` est le seul point d'appel direct à `B2BUsageService.consume_or_raise()` (actuellement ligne 126)
  - [x] Vérifier si d'autres routers B2B (`b2b_editorial.py`, `b2b_billing.py`) appellent aussi `B2BUsageService.consume_or_raise()` — les inclure dans le périmètre si oui

- [x] **Créer `B2BApiEntitlementGate`** (AC: 1-11)
  - [x] Créer `backend/app/services/b2b_api_entitlement_gate.py`
  - [x] Définir `FEATURE_CODE = "b2b_api_access"`
  - [x] Définir `B2BApiAccessDeniedError(code, message, details)`
  - [x] Définir `B2BApiQuotaExceededError(code, message, details)`
  - [x] Définir dataclass `B2BApiEntitlementResult` avec :
    - `path: Literal["canonical_quota", "canonical_unlimited", "settings_fallback"]`
    - `usage_states: list[UsageState]`
    - `source: str`
  - [x] Implémenter `check_and_consume(db, *, account_id: int) -> B2BApiEntitlementResult` :
    1. Charger l'`EnterpriseAccountModel` → `admin_user_id` ; si nul/absent → log warning + retourner `path="settings_fallback"` (AC: 11)
    2. Résoudre le plan canonique B2B via `_resolve_b2b_canonical_plan(db, account_id)`
    3. Si pas de plan canonique → retourner `path="settings_fallback"` immédiatement
    4. Lire le binding `b2b_api_access` depuis `plan_feature_bindings`
    5. Si pas de binding → retourner `path="settings_fallback"` immédiatement
    6. Si `access_mode=DISABLED` → lever `B2BApiAccessDeniedError(code="b2b_api_access_denied")` (AC: 4 — le canonique gagne même si settings permissifs)
    7. Si `access_mode=UNLIMITED` → retourner `path="canonical_unlimited"`, `usage_states=[]`
    8. Si `access_mode=QUOTA` → charger les quotas, appeler `QuotaUsageService.consume(db, user_id=admin_user_id, ...)`, si `QuotaExhaustedError` → lever `B2BApiQuotaExceededError(code="b2b_api_quota_exceeded")`, sinon retourner `path="canonical_quota"`, `usage_states=[état après consommation]`

- [x] **Implémenter `_resolve_b2b_canonical_plan`** (AC: 1, 8)
  - [x] Requête : `enterprise_account_billing_plans WHERE enterprise_account_id = account_id ORDER BY id DESC LIMIT 1` → `enterprise_billing_plans.id` → `plan_catalog WHERE source_type='migrated_from_enterprise_plan' AND source_id=enterprise_billing_plans.id AND audience='b2b' AND is_active=true`
  - [x] Règle de sélection du plan courant : la ligne `enterprise_account_billing_plans` la plus récente (`ORDER BY id DESC LIMIT 1`) — `EnterpriseAccountBillingPlanModel` a une contrainte d'unicité sur `enterprise_account_id` (voir modèle), donc une seule ligne par compte ; le `LIMIT 1` est défensif
  - [x] Si aucun plan canonique trouvé → retourner `None` (déclenche le fallback settings)
  - [x] Ne jamais appeler `BillingService.get_subscription_status()` — c'est du B2C Stripe

- [x] **Intégrer la gate dans `b2b_astrology.py`** (AC: 2-10)
  - [x] Importer `B2BApiEntitlementGate`, `B2BApiAccessDeniedError`, `B2BApiQuotaExceededError`
  - [x] Dans `get_weekly_by_sign()`, remplacer l'appel direct à `B2BUsageService.consume_or_raise()` par :
    ```python
    gate_result = B2BApiEntitlementGate.check_and_consume(db, account_id=client.account_id)
    if gate_result.path == "settings_fallback":
        B2BUsageService.consume_or_raise(db, account_id=..., credential_id=..., request_id=..., units=1)
    # else: pas de B2BUsageService — le canonique a déjà consommé
    ```
  - [x] Gérer `B2BApiAccessDeniedError` → HTTP 403 + code `b2b_api_access_denied` (avant tout traitement aval)
  - [x] Gérer `B2BApiQuotaExceededError` → HTTP 429 + code `b2b_api_quota_exceeded` (avant tout traitement aval)
  - [x] Si traitement aval (`B2BAstrologyService`) lève une exception après consommation canonique → `db.rollback()` (annule la consommation, AC: 9)
  - [x] Enrichir la réponse avec `quota_info` dans le body JSON (AC: 10) — `WeeklyBySignApiResponse` à étendre avec `quota_info: QuotaInfoPayload | None`
  - [x] Ne pas appeler `B2BUsageService` si `gate_result.path != "settings_fallback"`

- [x] **Tests unitaires** (AC: 12)
  - [x] Créer `backend/app/tests/unit/test_b2b_api_entitlement_gate.py`
  - [x] Test : binding canonique `quota` + quota disponible → `path="canonical_quota"`, 1 unité consommée
  - [x] Test : binding canonique `unlimited` → `path="canonical_unlimited"`, aucune consommation
  - [x] Test : binding canonique `disabled` → lève `B2BApiAccessDeniedError`
  - [x] Test : binding canonique `quota` épuisé → lève `B2BApiQuotaExceededError`
  - [x] Test : pas de binding → `path="settings_fallback"`, aucune consommation canonique
  - [x] Test : pas de plan canonique → `path="settings_fallback"`
  - [x] Test : `admin_user_id` nul → `path="settings_fallback"` + warning loggé (AC: 11)
  - [x] Test : fenêtre mensuelle UTC → `usage_states[0].window_end` = début du mois suivant
  - [x] Test : aucune double consommation (canonical + settings) sur un même appel

- [x] **Tests d'intégration** (AC: 13)
  - [x] Créer `backend/app/tests/integration/test_b2b_api_entitlements.py`
  - [x] Setup : créer compte B2B + plan canonique seedé avec binding `b2b_api_access` quota (1000 calls/month)
  - [x] Test : appel réussi → HTTP 200, `response["quota_info"]["source"] == "canonical"`
  - [x] Test : quota épuisé → HTTP 429, code `b2b_api_quota_exceeded`
  - [x] Test : compte sans plan canonique → HTTP 200 via fallback settings, `quota_info["source"] == "settings_fallback"`
  - [x] Test : binding `disabled` + settings permissifs → HTTP 403, code `b2b_api_access_denied` (canonique gagne, AC: 4)
  - [x] Test : `window_end` aligné sur début du mois UTC suivant
  - [x] Test : deux appels consécutifs → `remaining` décrémenté de 2

- [x] **Documentation** (AC: 10, 14)
  - [x] Mettre à jour `backend/docs/entitlements-canonical-platform.md`
  - [x] Ajouter section "B2B canonical priority + settings fallback"
  - [x] Documenter la règle de priorité : canonique gagne toujours si binding existe (y compris `disabled`)
  - [x] Documenter la dette technique `admin_user_id` comme compromis transitoire
  - [x] Documenter que `B2BUsageService` n'est pas décommissionné dans cette story
  - [x] Documenter les cas `manual-review-required` (`included_monthly_units = 0`)

## Dev Notes

### Point d'entrée exact à modifier

**Fichier** : [backend/app/api/v1/routers/b2b_astrology.py](backend/app/api/v1/routers/b2b_astrology.py#L126)

Le seul appel à déplacer est à la ligne 126 dans `get_weekly_by_sign()` :
```python
B2BUsageService.consume_or_raise(
    db,
    account_id=client.account_id,
    credential_id=client.credential_id,
    request_id=request_id,
    units=1,
)
```
L'exception `B2BUsageServiceError` est catchée aux lignes 156-165 — adapter le catch pour les nouvelles erreurs canoniques.

### Contrainte architecturale critique : `feature_usage_counters.user_id`

`FeatureUsageCounterModel` ([backend/app/infra/db/models/product_entitlements.py](backend/app/infra/db/models/product_entitlements.py#L217)) a `user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))`.

Les clients B2B ne sont **pas** des utilisateurs directs — ils s'authentifient via `enterprise_accounts.id` / `credential_id`. La clé de pont est `EnterpriseAccountModel.admin_user_id` ([backend/app/infra/db/models/enterprise_account.py](backend/app/infra/db/models/enterprise_account.py#L22)).

**Règle** : utiliser `admin_user_id` (récupéré via `SELECT admin_user_id FROM enterprise_accounts WHERE id = account_id`) comme `user_id` lors des appels à `QuotaUsageService.get_usage()` et `QuotaUsageService.consume()`. Si `admin_user_id` est `None` (cas théoriquement impossible avec la contrainte DB mais à défendre), retourner `settings_fallback` + `logger.warning(...)`.

> **Dette technique** : les compteurs B2B seront techniquement rangés dans `feature_usage_counters` sous la clé `user_id = admin_user_id`. Ce n'est pas un identifiant métier B2B natif — c'est un compromis transitoire pour éviter une migration Alembic dans cette story. Une future story devra soit ajouter une colonne `enterprise_account_id` nullable dans `feature_usage_counters`, soit créer une table `enterprise_feature_usage_counters` dédiée. Ne pas traiter ce mapping comme un design final.

### Résolution du plan canonique B2B

Chaîne de résolution (pas de `BillingService.get_subscription_status()` — c'est du B2C) :

```
account_id
  → enterprise_account_billing_plans.enterprise_account_id = account_id
  → enterprise_billing_plans.id (via .plan_id)
  → plan_catalog WHERE source_type='migrated_from_enterprise_plan'
                   AND source_id = enterprise_billing_plans.id
                   AND audience = 'b2b'
```

Modèles impliqués :
- `EnterpriseAccountBillingPlanModel` ([backend/app/infra/db/models/enterprise_billing.py](backend/app/infra/db/models/enterprise_billing.py#L37))
- `EnterpriseBillingPlanModel` ([backend/app/infra/db/models/enterprise_billing.py](backend/app/infra/db/models/enterprise_billing.py#L15))
- `PlanCatalogModel` ([backend/app/infra/db/models/product_entitlements.py](backend/app/infra/db/models/product_entitlements.py#L60)) — `audience = Audience.B2B`

### `EntitlementService` existant — NE PAS utiliser directement

`EntitlementService.get_feature_entitlement(db, user_id, feature_code)` ([backend/app/services/entitlement_service.py](backend/app/services/entitlement_service.py#L55)) appelle `BillingService.get_subscription_status(db, user_id=user_id)` qui lit les abonnements B2C Stripe. Ce chemin est **incompatible** avec le contexte B2B.

La gate doit implémenter sa propre résolution de plan (`_resolve_b2b_canonical_plan`) puis réutiliser uniquement `QuotaUsageService` et les requêtes sur `plan_feature_bindings` / `plan_feature_quotas`.

### Services et types réutilisables

| Import | Usage dans la gate |
|--------|-------------------|
| `QuotaUsageService.get_usage()` | lire l'état avant consommation (optionnel) |
| `QuotaUsageService.consume()` | consommer 1 unité, peut lever `QuotaExhaustedError` |
| `QuotaExhaustedError` | capturer → lever `B2BApiQuotaExceededError` |
| `QuotaDefinition` | construire à partir des `PlanFeatureQuotaModel` |
| `UsageState` | retourner dans `B2BApiEntitlementResult.usage_states` |
| `AccessMode` (enum) | comparer `binding.access_mode` |
| `PlanFeatureBindingModel`, `PlanFeatureQuotaModel` | requêtes SQL sur le plan |

### Politique transactionnelle (AC: 9)

La consommation canonique s'effectue **dans la même transaction SQLAlchemy** que le traitement aval. Si `B2BAstrologyService` ou toute étape ultérieure lève une exception, le `db.rollback()` du handler annule également la consommation. Aucun mécanisme de compensation n'est nécessaire — c'est le comportement standard de SQLAlchemy avec `db.commit()` en fin de succès uniquement.

**Séquence dans `get_weekly_by_sign()` :**
1. `gate_result = B2BApiEntitlementGate.check_and_consume(db, ...)` — consomme dans la transaction courante
2. Si erreur gate → `db.rollback()` + réponse d'erreur (403/429) — aucune unité débitée
3. Traitement aval (`B2BAstrologyService`, etc.)
4. Si erreur aval → `db.rollback()` + réponse d'erreur — **consommation annulée**
5. Si succès → `db.commit()` — consommation effective

### Règle de sélection du plan B2B courant

`EnterpriseAccountBillingPlanModel` a une contrainte d'unicité sur `enterprise_account_id` (voir [backend/app/infra/db/models/enterprise_billing.py](backend/app/infra/db/models/enterprise_billing.py#L37) `UniqueConstraint("enterprise_account_id")`). Il n'y a donc qu'une seule ligne par compte.

Requête recommandée :
```python
account_plan = db.scalar(
    select(EnterpriseAccountBillingPlanModel)
    .where(EnterpriseAccountBillingPlanModel.enterprise_account_id == account_id)
    .limit(1)
)
```
Si `account_plan` est `None` → pas de plan B2B assigné → retourner `settings_fallback`.

Puis résoudre le `plan_catalog` :
```python
canonical_plan = db.scalar(
    select(PlanCatalogModel)
    .where(
        PlanCatalogModel.source_type == "migrated_from_enterprise_plan",
        PlanCatalogModel.source_id == account_plan.plan_id,
        PlanCatalogModel.audience == Audience.B2B,
        PlanCatalogModel.is_active == True,
    )
    .limit(1)
)
```
Si `canonical_plan` est `None` → plan enterprise non encore backfillé en canonique → retourner `settings_fallback`.

### Contrat de réponse `quota_info` (AC: 10)

**Body JSON uniquement** — pas de headers. Étendre `WeeklyBySignApiResponse` avec un champ optionnel `quota_info`.

Pour path `canonical_quota` :
```json
{
  "data": { "..." : "..." },
  "meta": { "request_id": "..." },
  "quota_info": { "source": "canonical", "limit": 1000, "remaining": 742, "window_end": "2026-04-01T00:00:00Z" }
}
```
Pour path `canonical_unlimited` :
```json
{ "quota_info": { "source": "canonical_unlimited" } }
```
Pour path `settings_fallback` :
```json
{ "quota_info": { "source": "settings_fallback" } }
```
`limit`, `remaining`, `window_end` sont absents en `settings_fallback` (non disponibles sans appel supplémentaire à `B2BUsageService.get_usage_summary()`).

### Règle de non-double-consommation

**Invariant à respecter** : si `gate_result.path != "settings_fallback"`, le code **ne doit pas** appeler `B2BUsageService.consume_or_raise()`. Un `if/else` strict est obligatoire, jamais un `if gate_result.path == "settings_fallback": B2BUsageService.consume_or_raise(...)`  sans else.

### Structure de test recommandée

**Setup test d'intégration** — seeder le plan canonique B2B :
```python
def _seed_canonical_b2b_plan(db: Session, *, account_id: int, quota_limit: int = 1000) -> None:
    # 1. Récupérer l'enterprise_billing_plan lié au compte
    # 2. Créer ou trouver plan_catalog entry avec audience=b2b, source_type='migrated_from_enterprise_plan'
    # 3. Créer feature_catalog entry pour 'b2b_api_access'
    # 4. Créer plan_feature_bindings avec access_mode=quota
    # 5. Créer plan_feature_quotas avec period_unit='month', period_value=1, reset_mode='calendar', quota_limit=quota_limit
    ...
```

Pour le test de quota épuisé, utiliser directement `QuotaUsageService.consume()` en boucle ou insérer un `FeatureUsageCounterModel` avec `used_count = quota_limit` avant l'appel API.

### Structures existantes à ne pas réinventer

- Pattern d'erreur `_error_response()` dans `b2b_astrology.py` (ligne 52) — le réutiliser
- Pattern test B2B : `_cleanup_tables()`, `_create_enterprise_api_key()` dans `test_b2b_astrology_api.py` — s'en inspirer
- Pattern gate B2C : `backend/app/services/` `*_entitlement_gate.py` (stories 61.11–61.13) — même structure `check_and_consume` avec levée d'erreur métier

### Règle style CSS (non applicable ici — backend only)

Cette story est 100% backend. Aucune modification frontend requise.

### Hors périmètre (ne pas toucher)

- Supprimer `B2BUsageService`
- Supprimer les settings `b2b_*`
- Créer une migration Alembic
- Refondre les endpoints B2B hors point de contrôle d'accès/quota
- Migrer les usages historiques B2B en masse

### Commandes de validation

```bash
# Activer le venv
.\.venv\Scripts\Activate.ps1

# Lint
cd backend && ruff check app/services/b2b_api_entitlement_gate.py

# Tests unitaires
cd backend && pytest -q app/tests/unit/test_b2b_api_entitlement_gate.py -v

# Tests d'intégration
cd backend && pytest -q app/tests/integration/test_b2b_api_entitlements.py -v

# Non-régression existante
cd backend && pytest -q app/tests/unit/test_b2b_usage_service.py app/tests/unit/test_entitlement_service.py app/tests/unit/test_quota_usage_service.py app/tests/integration/test_b2b_astrology_api.py -v
```

### Project Structure Notes

- Nouveau fichier à créer : `backend/app/services/b2b_api_entitlement_gate.py` (même répertoire que `entitlement_service.py`, `quota_usage_service.py`)
- Nouveau fichier test unitaire : `backend/app/tests/unit/test_b2b_api_entitlement_gate.py`
- Nouveau fichier test intégration : `backend/app/tests/integration/test_b2b_api_entitlements.py`
- Fichier modifié : `backend/app/api/v1/routers/b2b_astrology.py`
- Fichier modifié : `backend/docs/entitlements-canonical-platform.md`

### References

- [Source: backend/app/api/v1/routers/b2b_astrology.py#L126] — point d'entrée actuel `B2BUsageService.consume_or_raise()`
- [Source: backend/app/services/b2b_usage_service.py] — service fallback à conserver
- [Source: backend/app/services/entitlement_service.py#L55] — `get_feature_entitlement()` B2C uniquement, non réutilisable directement
- [Source: backend/app/services/quota_usage_service.py] — `consume()` / `get_usage()` à réutiliser
- [Source: backend/app/services/entitlement_types.py] — `QuotaDefinition`, `UsageState`, `FeatureEntitlement`
- [Source: backend/app/infra/db/models/product_entitlements.py#L217] — `FeatureUsageCounterModel.user_id` FK to `users.id`
- [Source: backend/app/infra/db/models/enterprise_account.py#L22] — `EnterpriseAccountModel.admin_user_id` (pont vers `users.id`)
- [Source: backend/app/infra/db/models/enterprise_billing.py#L37] — `EnterpriseAccountBillingPlanModel` (résolution plan courant)
- [Source: backend/app/api/dependencies/b2b_auth.py] — `AuthenticatedEnterpriseClient(account_id, credential_id, key_prefix)`
- [Source: backend/app/tests/integration/test_b2b_astrology_api.py] — structure de test B2B à réutiliser

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- backend/app/services/b2b_api_entitlement_gate.py (NOUVEAU)
- backend/app/api/v1/routers/b2b_astrology.py
- backend/app/tests/unit/test_b2b_api_entitlement_gate.py (NOUVEAU)
- backend/app/tests/integration/test_b2b_api_entitlements.py (NOUVEAU)
- backend/docs/entitlements-canonical-platform.md
