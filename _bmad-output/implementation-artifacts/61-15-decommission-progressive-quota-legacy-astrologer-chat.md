# Story 61.15 : Décommission progressive du chemin legacy de quota sur `astrologer_chat`

Status: done

> **Révision v2 (2026-03-26)** : Correction de l'état réel du seed (trial=DISABLED, premium=2000/month), refonte du script de migration pour résoudre le quota canonique par user, ajout des AC et tests pour les cas basic/day et premium/month.

## Story

En tant que développeur de la plateforme,
je veux supprimer le chemin de fallback legacy (`reason="legacy_fallback"`) dans le flux d'entitlement d'`astrologer_chat`,
de sorte que la feature repose exclusivement sur le système canonique (`plan_feature_binding` + `feature_usage_counters`) et que le front puisse recevoir des `usage_states` fiables via l'endpoint 61.14.

## Contexte et motivation

`astrologer_chat` est la seule feature B2C encore hybride dans le système d'entitlements :

- Si un user a un binding canonique dans `plan_feature_binding` → chemin canonique (`QuotaUsageService`)
- Sinon → fallback legacy (`_legacy_fallback` dans `EntitlementService`) → `QuotaService.consume_quota_or_raise` sur `user_daily_quota_usages`

Ce fallback introduit plusieurs problèmes critiques détectés en code review :

1. **Deux tables de quota non synchronisées** : `user_daily_quota_usages` (legacy) et `feature_usage_counters` (canonique) coexistent. Un user migrant de l'un à l'autre perd son historique de consommation.
2. **`usage_states=[]` pour les users legacy** : `GET /v1/entitlements/me` (61.14) retourne une liste vide — le front ne peut pas afficher "Il vous reste N messages" pour ces users.
3. **Double appel `BillingService`** : `entitlement_service.py` + `quota_service.py` chacun appellent `get_subscription_status` indépendamment sur le même chemin.
4. **Comportement incohérent sur `trialing`** : `QuotaService._resolve_active_quota_from_subscription` exige `status == "active"` strictement — les users `trialing` avec fallback legacy reçoivent un 422 au lieu d'un 403.

Depuis 61.7/61.9/61.13, le seed canonique (`seed_product_entitlements.py`) couvre les plans `free`, `trial`, `basic`, `premium` avec des bindings explicites pour `astrologer_chat`. La décommission est maintenant sûre sous réserve de vérifier que tous les plans actifs en production ont leur binding.

## Acceptance Criteria

1. Après migration, `EntitlementService.get_feature_entitlement(db, user_id, "astrologer_chat")` ne retourne plus jamais `reason="legacy_fallback"` — uniquement des reasons canoniques (`canonical_binding`, `no_plan`, `billing_inactive`, `disabled_by_plan`, `canonical_no_binding`)
2. `ChatEntitlementGate.check_and_consume` ne contient plus de branche `if reason == "legacy_fallback"` ni de retour `path="legacy"`
3. `chat.py` (router) ne contient plus de `if entitlement_result.path == "legacy"` ni d'appel à `QuotaService.consume_quota_or_raise`
4. `EntitlementService._legacy_fallback` est supprimée ou rendue inaccessible (non appelée depuis `get_feature_entitlement` pour `astrologer_chat`)
5. Pour un user avec plan `basic` (binding canonique `astrologer_chat` QUOTA 5/day) : `GET /v1/entitlements/me` retourne `usage_states[0].remaining >= 0`, `usage_states[0].window_end` non null, `reason="canonical_binding"`
5b. Pour un user avec plan `premium` (binding canonique `astrologer_chat` QUOTA 2000/month) : `GET /v1/entitlements/me` retourne `usage_states[0].window_end` correspondant à la fin du mois calendaire UTC courant
6. Pour un user avec plan `free` ou `trial` (binding canonique `astrologer_chat` DISABLED) : `GET /v1/entitlements/me` retourne `final_access=False`, `reason="disabled_by_plan"`, `usage_states=[]`
7. `POST /v1/chat/messages` continue de fonctionner pour les users avec binding canonique actif — pas de régression
8. Un plan sans binding canonique `astrologer_chat` (edge case) retourne `reason="canonical_no_binding"`, `final_access=False` — pas de 500
9. Le script de migration `migrate_legacy_quota_to_canonical.py` est fourni pour convertir les lignes de `user_daily_quota_usages` (usage_count > 0) en entrées `feature_usage_counters`. Le script **résout le quota canonique courant de chaque user** via `PlanFeatureQuotaModel` avant de migrer :
   - Si le plan est `basic` (quota day/calendar) → migrer dans la fenêtre journalière correspondante
   - Si le plan est `premium` (quota month/calendar) → agréger les lignes daily legacy dans la fenêtre mensuelle courante (somme des `used_count` pour le mois calendaire UTC)
   - Si le binding est DISABLED (`free`, `trial`) → skip (pas de migration utile)
   - Si aucun binding canonique → skip + log WARNING anomalie
   - L'opération est idempotente (upsert par `ON CONFLICT DO UPDATE SET used_count = MAX(existing, new)`)
   - Support `--dry-run` et `--days N` (défaut : fenêtre active uniquement)
10. Les tests unitaires couvrent : plan sans binding → `canonical_no_binding`, plan `free`/`trial` DISABLED → `disabled_by_plan`, plan `basic` QUOTA 5/day → `canonical_binding` + `usage_states[0].window_end` non null, plan `premium` QUOTA 2000/month → `canonical_binding` + `usage_states[0].window_end` fin de mois UTC
11. Les tests d'intégration vérifient : `POST /v1/chat/messages` sans `QuotaService` appelé, `GET /v1/entitlements/me` avec `usage_states` peuplés pour un user `basic`, `GET /v1/entitlements/me` ne retourne jamais `reason="legacy_fallback"` pour aucun plan connu
12. Les tests existants de `test_entitlement_service.py`, `test_quota_usage_service.py`, `test_natal_chart_long_entitlement.py`, `test_entitlements_me.py` continuent de passer (non-régression)
13. `QuotaService` n'est plus importé dans `chat.py` (import supprimé)

## Tasks / Subtasks

- [x] **Vérifier la couverture seed avant de supprimer le fallback** (AC: 1, 8)
  - [x] Lire `backend/scripts/seed_product_entitlements.py` et confirmer que `free`, `trial`, `basic`, `premium` ont tous un binding explicite pour `astrologer_chat`
  - [x] Si un plan actif est absent du seed, l'ajouter avec `access_mode=DISABLED` comme garde-fou avant toute suppression

- [x] **Script de migration des données legacy** (AC: 9)
  - [x] Créer `backend/scripts/migrate_legacy_quota_to_canonical.py`
  - [x] Lire `user_daily_quota_usages` pour la fenêtre active (ou les N derniers jours via `--days N`) où `used_count > 0`
  - [x] Pour chaque user, résoudre le binding/quota canonique `astrologer_chat` via `EntitlementService.get_user_canonical_plan` + `PlanFeatureQuotaModel`
  - [x] **Branche `basic` (day/calendar)** : pour chaque ligne daily, insérer/mettre à jour `feature_usage_counters` avec `period_unit="day"`, `period_value=1`, `reset_mode="calendar"`, `window_start=début_du_jour_UTC`, `window_end=début_du_jour_suivant_UTC`
  - [x] **Branche `premium` (month/calendar)** : agréger toutes les lignes legacy du mois courant → insérer/mettre à jour une seule entrée `feature_usage_counters` avec `period_unit="month"`, `period_value=1`, `reset_mode="calendar"`, `window_start=début_du_mois_UTC`, `window_end=début_du_mois_suivant_UTC`, `used_count=somme(used_count)`
  - [x] **Branche DISABLED** (`free`, `trial`) : skip silencieux
  - [x] **Branche no-binding** : skip + `logger.warning("user %d: no canonical binding for astrologer_chat, skipping migration")`
  - [x] Upsert idempotent : si entrée existante → `used_count = max(existing, migrated)` (ne jamais diminuer)
  - [x] Logger le bilan : `N lignes legacy traitées, M entrées canoniques créées/mises à jour, K skips (disabled), L anomalies (no-binding)`

- [x] **Supprimer les deux points d'invocation legacy dans `EntitlementService`** (AC: 1, 4)
  - [x] `entitlement_service.py:189-194` : supprimer le bloc `if feature_code == "astrologer_chat": return _legacy_fallback(...)` dans la branche "plan+feature existent, pas de binding" — remplacer par le retour générique `canonical_no_binding`
  - [x] `entitlement_service.py:207-211` : supprimer l'appel `_legacy_fallback` dans la branche "plan ou feature manquant" — remplacer par `feature_unknown` (comportement déjà existant pour non-`astrologer_chat`)
  - [x] Garder `_legacy_fallback` pour l'instant comme méthode privée deprecated (pour faciliter la revue diff) — ajouter un commentaire `# DEPRECATED: suppression en 61.16`
  - [x] S'assurer que `_legacy_fallback` n'est plus jamais appelée

- [x] **Nettoyer `ChatEntitlementGate`** (AC: 2)
  - [x] `chat_entitlement_gate.py:46-47` : supprimer le bloc `if entitlement.reason == "legacy_fallback": return ChatEntitlementResult(path="legacy")`
  - [x] Supprimer `path: str` de `ChatEntitlementResult` ou réduire les valeurs acceptées à `"canonical_quota" | "canonical_unlimited"` uniquement
  - [x] Mettre à jour `__init__` de `ChatEntitlementResult` si nécessaire

- [x] **Nettoyer le router `chat.py`** (AC: 3, 13)
  - [x] Supprimer le bloc `if entitlement_result.path == "legacy": QuotaService.consume_quota_or_raise(...)` (lignes 134-139)
  - [x] Supprimer `from app.services.quota_service import QuotaService, QuotaServiceError` (import)
  - [x] Supprimer le `except QuotaServiceError` handler (lignes 202-220) — il ne peut plus être déclenché par le chat
  - [x] Vérifier que `_build_quota_info` fonctionne correctement sans le chemin `legacy`

- [x] **Mettre à jour les tests unitaires** (AC: 10)
  - [x] `test_chat_entitlement_gate.py` : supprimer `test_legacy_fallback_returns_legacy_path` et `test_legacy_fallback_final_access_false_still_delegates` (ces tests documentaient le bug)
  - [x] Ajouter `test_canonical_no_binding_raises_access_denied` : `reason="canonical_no_binding"` → `ChatAccessDeniedError`
  - [x] `test_entitlement_service.py` : ajouter `test_no_binding_for_astrologer_chat_returns_canonical_no_binding` (plan et feature existent, pas de binding → `reason="canonical_no_binding"`)
  - [x] `test_entitlement_service.py` : ajouter `test_missing_plan_catalog_returns_feature_unknown` (plan absent du catalog → `reason="feature_unknown"`)
  - [x] `test_entitlement_service.py` : ajouter `test_basic_plan_astrologer_chat_quota_daily` (plan `basic`, quota 5/day → `canonical_binding`, `access_mode="quota"`, `usage_states[0].window_end` non null)
  - [x] `test_entitlement_service.py` : ajouter `test_premium_plan_astrologer_chat_quota_monthly` (plan `premium`, quota 2000/month → `canonical_binding`, `access_mode="quota"`, `usage_states[0].window_end` = fin du mois UTC)
  - [x] `test_entitlement_service.py` : ajouter `test_trial_plan_astrologer_chat_disabled` (plan `trial` → `disabled_by_plan`, `final_access=False`, `usage_states=[]`)

- [x] **Mettre à jour les tests d'intégration** (AC: 11)
  - [x] `test_chat_entitlement.py` : supprimer `test_send_message_legacy_fallback_still_works`
  - [x] Ajouter `test_send_message_quota_service_never_called` : vérifier que `QuotaService.consume_quota_or_raise` n'est jamais appelé dans le router chat, même en mockant le gate comme canonique
  - [x] `test_entitlements_me.py` : ajouter `test_basic_user_chat_usage_states_populated` — user `basic` avec consommation existante → `usage_states[0].remaining reflète la vraie consommation (pas null), window_end non null
  - [x] `test_entitlements_me.py` : ajouter `test_no_legacy_fallback_reason_in_response` — pour tous les plans connus (`free`, `trial`, `basic`, `premium`), vérifier qu'aucun feature ne retourne `reason="legacy_fallback"` dans la réponse de `GET /v1/entitlements/me`

- [x] **Non-régression** (AC: 12)
  - [x] `pytest backend/app/tests/unit/test_entitlement_service.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_chat_entitlement_gate.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_quota_usage_service.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_natal_chart_long_entitlement.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_entitlements_me.py` — tous verts

---

## Dev Notes

### Architecture Guardrails

- **Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Pas de nouvelle table** — `feature_usage_counters` existe depuis 61-9 ; `user_daily_quota_usages` reste en place (non supprimée en 61.15 — dépréciation en 61.16)
- **Idempotence obligatoire** pour le script de migration — il peut être exécuté en staging puis en prod sans risque de doublon
- **Pas de downtime** — la suppression du fallback est safe une fois le seed canonique vérifié et le script de migration joué

### Les deux points d'invocation legacy dans `entitlement_service.py`

```python
# POINT A (ligne 189-194) — plan + feature existent, MAIS pas de binding
# Actuellement :
if feature_code == "astrologer_chat":
    fallback = EntitlementService._legacy_fallback(subscription, feature_code)
    ...
    return fallback

# APRÈS 61.15 — même traitement que les autres features :
return FeatureEntitlement(
    plan_code=plan_code,
    billing_status=billing_status,
    is_enabled_by_plan=False,
    access_mode="unknown",
    variant_code=None,
    quotas=[],
    final_access=False,
    reason="billing_inactive" if not is_billing_active else "canonical_no_binding",
)
```

```python
# POINT B (ligne 207-211) — plan ou feature absents du catalog
# Actuellement :
fallback = EntitlementService._legacy_fallback(subscription, feature_code)
...
return fallback

# APRÈS 61.15 — même traitement que les autres features :
return FeatureEntitlement(
    plan_code=plan_code,
    billing_status=billing_status,
    is_enabled_by_plan=False,
    access_mode="unknown",
    variant_code=None,
    quotas=[],
    final_access=False,
    reason="billing_inactive" if not is_billing_active else "feature_unknown",
)
```

### Nettoyage `ChatEntitlementGate` — diff cible

```python
# AVANT (chat_entitlement_gate.py:46-47)
if entitlement.reason == "legacy_fallback":
    return ChatEntitlementResult(path="legacy", usage_states=[])

# APRÈS — supprimer ces 2 lignes entièrement
# Le flux tombe directement sur le check final_access
```

```python
# AVANT (ChatEntitlementResult)
@dataclass
class ChatEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited" | "legacy"
    usage_states: list[UsageState] = field(default_factory=list)

# APRÈS
@dataclass
class ChatEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited"
    usage_states: list[UsageState] = field(default_factory=list)
```

### Nettoyage `chat.py` — diff cible

```python
# AVANT (lignes 134-139)
entitlement_result = ChatEntitlementGate.check_and_consume(db, user_id=current_user.id)
if entitlement_result.path == "legacy":
    QuotaService.consume_quota_or_raise(
        db,
        user_id=current_user.id,
        request_id=request_id,
    )

# APRÈS
entitlement_result = ChatEntitlementGate.check_and_consume(db, user_id=current_user.id)
# (pas de branche legacy — consume est géré dans le gate canonique)
```

```python
# AVANT — import à supprimer
from app.services.quota_service import QuotaService, QuotaServiceError

# AVANT — handler à supprimer (lignes 202-220)
except QuotaServiceError as error:
    db.rollback()
    if error.code == "quota_exceeded":
        status_code = 429
    elif error.code == "no_active_subscription":
        status_code = 403
    else:
        status_code = 422
    return JSONResponse(...)
```

### Script de migration — squelette de référence

Le script ne hardcode PAS la forme du quota. Il résout le quota canonique courant de chaque user, puis migre selon sa fenêtre réelle.

```python
# backend/scripts/migrate_legacy_quota_to_canonical.py
"""
Migration one-shot : user_daily_quota_usages → feature_usage_counters pour astrologer_chat.

Le script résout le quota canonique courant de chaque user :
- basic (day/calendar) → migration 1:1 par fenêtre journalière
- premium (month/calendar) → agrégation des lignes daily dans la fenêtre mensuelle courante
- free / trial (DISABLED) → skip silencieux
- aucun binding canonique → skip + log WARNING

Usage:
    python backend/scripts/migrate_legacy_quota_to_canonical.py
    python backend/scripts/migrate_legacy_quota_to_canonical.py --dry-run
    python backend/scripts/migrate_legacy_quota_to_canonical.py --days 30
"""
import argparse
import logging
from datetime import UTC, date, datetime, timedelta
from collections import defaultdict

from sqlalchemy import select
from app.infra.db.session import SessionLocal
from app.infra.db.models.billing import UserDailyQuotaUsageModel
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel, FeatureUsageCounterModel,
    PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel,
)
from app.services.billing_service import BillingService
from app.services.quota_window_resolver import QuotaWindowResolver

logger = logging.getLogger(__name__)
FEATURE_CODE = "astrologer_chat"
QUOTA_KEY = "messages"


def _resolve_canonical_quota(db, user_id: int):
    """Retourne PlanFeatureQuotaModel ou None si pas de binding actif."""
    subscription = BillingService.get_subscription_status(db, user_id=user_id)
    if not subscription.plan:
        return None
    plan = db.scalar(
        select(PlanCatalogModel)
        .where(PlanCatalogModel.plan_code == subscription.plan.code).limit(1)
    )
    feature = db.scalar(
        select(FeatureCatalogModel)
        .where(FeatureCatalogModel.feature_code == FEATURE_CODE).limit(1)
    )
    if not plan or not feature:
        return None
    binding = db.scalar(
        select(PlanFeatureBindingModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            PlanFeatureBindingModel.feature_id == feature.id,
        ).limit(1)
    )
    if not binding or not binding.is_enabled or binding.access_mode.value == "disabled":
        return None  # DISABLED (free, trial) → skip
    return db.scalar(
        select(PlanFeatureQuotaModel)
        .where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id,
            PlanFeatureQuotaModel.quota_key == QUOTA_KEY,
        ).limit(1)
    )


def _upsert_counter(db, *, user_id, window_start, window_end,
                    period_unit, period_value, reset_mode, used_count, dry_run):
    existing = db.scalar(
        select(FeatureUsageCounterModel).where(
            FeatureUsageCounterModel.user_id == user_id,
            FeatureUsageCounterModel.feature_code == FEATURE_CODE,
            FeatureUsageCounterModel.quota_key == QUOTA_KEY,
            FeatureUsageCounterModel.period_unit == period_unit,
            FeatureUsageCounterModel.period_value == period_value,
            FeatureUsageCounterModel.reset_mode == reset_mode,
            FeatureUsageCounterModel.window_start == window_start,
        )
    )
    if dry_run:
        return
    if existing:
        existing.used_count = max(existing.used_count, used_count)
    else:
        db.add(FeatureUsageCounterModel(
            user_id=user_id, feature_code=FEATURE_CODE, quota_key=QUOTA_KEY,
            period_unit=period_unit, period_value=period_value, reset_mode=reset_mode,
            window_start=window_start, window_end=window_end, used_count=used_count,
        ))


def migrate(days: int = 1, dry_run: bool = False) -> dict:
    today = datetime.now(UTC).date()
    cutoff = today - timedelta(days=days - 1)
    ref_dt = datetime.now(UTC)
    stats = {"processed": 0, "created_or_updated": 0, "skipped_disabled": 0, "anomalies": 0}

    with SessionLocal() as db:
        # Charger toutes les lignes legacy concernées, regroupées par user
        rows = db.scalars(
            select(UserDailyQuotaUsageModel)
            .where(UserDailyQuotaUsageModel.quota_date >= cutoff)
            .where(UserDailyQuotaUsageModel.used_count > 0)
            .order_by(UserDailyQuotaUsageModel.user_id, UserDailyQuotaUsageModel.quota_date)
        ).all()

        if not rows:
            logger.info("No legacy quota usage found since %s.", cutoff)
            return stats

        by_user = defaultdict(list)
        for row in rows:
            by_user[row.user_id].append(row)

        for user_id, user_rows in by_user.items():
            quota_model = _resolve_canonical_quota(db, user_id)

            if quota_model is None:
                # Distinguer DISABLED (binding existe mais disabled) de no-binding
                # Simplification : logger comme skip_disabled si le plan existe, anomalie sinon
                logger.warning("user %d: no active canonical quota for %s — skipping", user_id, FEATURE_CODE)
                stats["skipped_disabled"] += len(user_rows)
                continue

            period_unit = quota_model.period_unit.value
            period_value = quota_model.period_value
            reset_mode = quota_model.reset_mode.value

            if period_unit == "day":
                # Migration 1:1 par fenêtre journalière
                for row in user_rows:
                    window_start = datetime.combine(row.quota_date, datetime.min.time(), tzinfo=UTC)
                    window_end = window_start + timedelta(days=1)
                    _upsert_counter(
                        db, user_id=user_id,
                        window_start=window_start, window_end=window_end,
                        period_unit=period_unit, period_value=period_value,
                        reset_mode=reset_mode, used_count=row.used_count, dry_run=dry_run,
                    )
                    stats["created_or_updated"] += 1
            elif period_unit == "month":
                # Agréger les lignes daily dans la fenêtre mensuelle courante
                window = QuotaWindowResolver.compute_window(
                    period_unit, period_value, reset_mode, ref_dt
                )
                total_used = sum(r.used_count for r in user_rows)
                _upsert_counter(
                    db, user_id=user_id,
                    window_start=window.window_start, window_end=window.window_end,
                    period_unit=period_unit, period_value=period_value,
                    reset_mode=reset_mode, used_count=total_used, dry_run=dry_run,
                )
                stats["created_or_updated"] += 1
            else:
                logger.warning(
                    "user %d: unsupported period_unit '%s' for %s — skipping",
                    user_id, period_unit, FEATURE_CODE
                )
                stats["anomalies"] += 1
                continue

            stats["processed"] += len(user_rows)

        if not dry_run:
            db.commit()

    logger.info(
        "Migration %s: %d lignes traitées, %d entrées canoniques upsertées, "
        "%d skips (disabled/no-binding), %d anomalies",
        "(DRY RUN) " if dry_run else "",
        stats["processed"], stats["created_or_updated"],
        stats["skipped_disabled"], stats["anomalies"],
    )
    return stats
```

### Données canoniques par plan (seed `seed_product_entitlements.py` — état vérifié)

| Plan | `astrologer_chat` access_mode | quota_key | limit | fenêtre |
|------|-------------------------------|-----------|-------|---------|
| free | **DISABLED** | — | — | — |
| trial | **DISABLED** | — | — | — |
| basic | QUOTA | messages | **5** | **day/calendar** |
| premium | QUOTA | messages | **2000** | **month/calendar** |

### Politique de migration en cas de changement de plan récent

Le script s'appuie sur le **binding canonique courant au moment de son exécution**. Il ne tente pas de reconstituer rétroactivement un historique multi-plan ambigu (ex : user passé de `basic` à `premium` en cours de période).

Conséquence concrète : si un user était sur `basic` (5/day) hier et est passé sur `premium` (2000/month) aujourd'hui, le script lira un quota canonique `month/calendar` et agrégera les lignes legacy dans la fenêtre mensuelle — y compris des lignes produites sous le plan `basic`. C'est le comportement le plus sûr disponible sans audit d'historique de plan.

Les cas jugés ambigus (ex : quota_model résolu but `period_unit` non supporté, ou user_id présent dans `user_daily_quota_usages` mais absent de `billing`) sont journalisés via `logger.warning` et **exclus de la migration automatique**. Ils sont comptabilisés dans le stat `anomalies` du bilan final. Aucune exception ne doit interrompre la migration des autres users.

Cette politique est explicitement hors périmètre de 61.15 : la reconstitution d'un historique multi-plan nécessiterait un audit de la table `user_subscriptions` (historique de changements) qui n'existe pas encore dans ce schéma.

### Données canoniques par plan (seed `seed_product_entitlements.py` — état vérifié)

Points critiques pour la migration :
- `free` et `trial` sont DISABLED → **aucune migration** utile pour ces users
- `basic` et `premium` ont des fenêtres **différentes** (day vs month) → le script doit brancher selon le quota canonique courant
- Un user `basic` peut avoir plusieurs lignes legacy journalières → migration 1:1 par fenêtre journalière
- Un user `premium` peut avoir plusieurs lignes legacy journalières sur le mois → agrégation en une seule fenêtre mensuelle
- Tous les plans connus sont couverts. Le fallback legacy ne peut être déclenché que par des plans hors seed (edge case production)

### Ordre d'exécution recommandé en production

1. Déployer le seed mis à jour (si ajout de plan)
2. Jouer `migrate_legacy_quota_to_canonical.py --dry-run` → valider les comptes
3. Jouer `migrate_legacy_quota_to_canonical.py` (sans dry-run)
4. Déployer le code 61.15
5. Monitorer les logs pour `reason="canonical_no_binding"` sur `astrologer_chat` (devrait être zéro)

### Éviter les régressions critiques

- **Ne pas supprimer `user_daily_quota_usages`** en 61.15 — laisser en place pour rollback éventuel ; dépréciation prévue en 61.16
- **Ne pas modifier `QuotaUsageService`** — il reste utilisé pour natal_chart_long et thematic_consultation
- **Ne pas modifier les autres gates** (`ThematicConsultationEntitlementGate`, `NatalChartLongEntitlementGate`)
- **`quota_service.py`** n'est plus importé depuis `chat.py` après 61.15, mais le fichier reste — d'autres usages possibles (admin, monitoring)

### Localisation des fichiers

```
backend/app/services/entitlement_service.py          ← MODIFIÉ (suppression 2 invocations legacy)
backend/app/services/chat_entitlement_gate.py        ← MODIFIÉ (suppression branche legacy)
backend/app/api/v1/routers/chat.py                   ← MODIFIÉ (suppression QuotaService + handler)
backend/scripts/migrate_legacy_quota_to_canonical.py ← NOUVEAU
backend/app/tests/unit/test_chat_entitlement_gate.py ← MODIFIÉ (suppression 2 tests legacy)
backend/app/tests/unit/test_entitlement_service.py   ← MODIFIÉ (ajout 2 tests canonical_no_binding)
backend/app/tests/integration/test_chat_entitlement.py ← MODIFIÉ (suppression test legacy, ajout test no QuotaService)
```

### Références

- `EntitlementService._legacy_fallback` : `backend/app/services/entitlement_service.py:213-260`
- `ChatEntitlementGate.check_and_consume` : `backend/app/services/chat_entitlement_gate.py:40-104`
- Branche legacy dans le router : `backend/app/api/v1/routers/chat.py:134-139`
- `QuotaService` (legacy) : `backend/app/services/quota_service.py`
- `QuotaUsageService` (canonique) : `backend/app/services/quota_usage_service.py`
- Pattern test existant : `backend/app/tests/unit/test_chat_entitlement_gate.py`
- Seed canonique : `backend/scripts/seed_product_entitlements.py`

### Contexte stories précédentes

- **61-9 (done)** : `EntitlementService.get_feature_entitlement` — le fallback legacy a été conservé intentionnellement le temps que le seed soit complet
- **61-11 (done)** : `ChatEntitlementGate` introduit le chemin hybride legacy/canonique
- **61-13 (done)** : `NatalChartLongEntitlementGate` — 100% canonique, pas de legacy, modèle à suivre
- **61-14 (done)** : `GET /v1/entitlements/me` — expose les `usage_states` ; retourne `[]` pour les users legacy, ce qui bloque l'UX front (motivation directe de 61.15)

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Code review BMAD exécutée sur l'implémentation finale de 61-15.
- Correction du script de migration pour distinguer `disabled` vs `no canonical binding`.
- Correction de la portée de migration `premium/month` pour n'agréger que la fenêtre mensuelle canonique active.
- Ajout de tests unitaires du script de migration et extension de couverture `free` sur `GET /v1/entitlements/me`.

### File List

- `backend/app/services/entitlement_service.py`
- `backend/app/services/chat_entitlement_gate.py`
- `backend/app/api/v1/routers/chat.py`
- `backend/scripts/migrate_legacy_quota_to_canonical.py`
- `backend/app/tests/unit/test_chat_entitlement_gate.py`
- `backend/app/tests/unit/test_entitlement_service.py`
- `backend/app/tests/unit/test_migrate_legacy_quota_to_canonical.py`
- `backend/app/tests/integration/test_chat_entitlement.py`
- `backend/app/tests/integration/test_entitlements_me.py`

## Senior Developer Review (AI)

### Findings

1. `HIGH` `backend/scripts/migrate_legacy_quota_to_canonical.py`
   - Le script classait indistinctement les cas `disabled` et `no binding` en `skipped_disabled`, ce qui violait l'AC 9 demandant un `WARNING` + comptage en anomalie pour l'absence de binding canonique.
   - Corrigé en introduisant une résolution explicite des statuts canoniques (`quota`, `disabled`, `no_binding`, `missing_catalog`).
2. `HIGH` `backend/scripts/migrate_legacy_quota_to_canonical.py`
   - Le chemin `premium/month` pouvait agréger des lignes legacy hors fenêtre mensuelle canonique, notamment avec `--days` couvrant un changement de mois.
   - Corrigé en filtrant strictement les lignes sur la fenêtre canonique active avant agrégation.
3. `MEDIUM` `backend/scripts/migrate_legacy_quota_to_canonical.py`
   - Le mode par défaut ne modélisait pas la "fenêtre active uniquement" de l'AC 9 pour les quotas mensuels.
   - Corrigé en faisant du comportement par défaut une migration par fenêtre canonique active, avec `--days` comme override explicite.
4. `MEDIUM` `backend/app/tests/integration/test_entitlements_me.py`
   - La couverture annoncée des plans connus ne testait pas `free`, alors que la story et le seed le considèrent comme plan canonique supporté.
   - Corrigé avec un cas d'intégration dédié et extension de l'audit anti-`legacy_fallback`.

### Validation

- `ruff check .`
- `pytest -q app/tests/unit/test_migrate_legacy_quota_to_canonical.py app/tests/unit/test_entitlement_service.py app/tests/unit/test_chat_entitlement_gate.py app/tests/unit/test_quota_usage_service.py app/tests/integration/test_chat_entitlement.py app/tests/integration/test_entitlements_me.py app/tests/integration/test_natal_chart_long_entitlement.py`

### Outcome

- Tous les findings `HIGH` et `MEDIUM` ont été corrigés.
- Le statut reste `done`.

## Change Log

- 2026-03-26: code review BMAD 61-15, correction du script de migration canonique, ajout des tests de migration et extension de couverture `free`.
