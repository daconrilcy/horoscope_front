# Story 61.66 : Quotas d'usage canoniques — suppression des valeurs hardcodées et cohérence d'upgrade intra-période

Status: done

## Story

En tant que système billing SaaS,
je veux que les limites de quota par plan soient **pilotées uniquement par la base de données** (catalogue canonique `PlanFeatureQuotaModel`), sans aucune valeur codée en dur ni dans le backend ni dans le frontend,
afin que les quotas puissent être modifiés simplement dans le catalogue sans toucher au code, et que les chiffres affichés correspondent à l'enforcement réel.

---

## Contexte

### Incohérence triple découverte après analyse du code

Trois sources de vérité sur les quotas `astrologer_chat` donnent des valeurs contradictoires :

| Source | basic | premium |
|--------|-------|---------|
| `seed_product_entitlements.py` (catalogue canonique) | **5/jour** | **2000/mois** |
| `_PLAN_DEFAULTS` dans `billing_service.py` | **50** | **1000** |
| `SubscriptionSettings.tsx` (hardcodé) | "50 msg/jour" | "1000 msg/jour" |

L'enforcement réel est celui du **catalogue canonique** (`PlanFeatureQuotaModel`), utilisé par `EffectiveEntitlementResolverService`. Les deux autres sources sont ignorées à l'exécution.

### Conséquence sur le comportement upgrade

Le plan `basic` utilise `period_unit=DAY` et le plan `premium` utilise `period_unit=MONTH` pour `astrologer_chat`. Ces quotas ont des `period_unit` différents → la clé composite de `FeatureUsageCounterModel` diffère entre plans → un upgrade basic→premium crée **un nouveau compteur mensuel**, sans tenir compte des messages déjà consommés aujourd'hui sous basic.

Cela n'est **pas une perte pour l'utilisateur** (il passe de 5/jour à 2000/mois), mais c'est incohérent avec la règle R6 du draft "pas de reset de consommation sur upgrade". Plus problématique : si les deux plans utilisaient le même `period_unit`, le compteur serait partagé et la règle serait naturellement respectée.

### Objectif de la story

1. **Choisir des quotas alignés** entre basic et premium pour que l'upgrade soit sémantiquement correct (même `period_unit`, même `quota_key`, seule la limite change)
2. **Supprimer les valeurs codées en dur** dans `_PLAN_DEFAULTS` et `SubscriptionSettings` — lire depuis le catalogue ou l'API entitlements
3. **Exposer les données d'usage temps réel** dans `GET /billing/subscription` (périmètre déjà ouvert par 61-65)
4. **Vérifier par test** le comportement correct de l'upgrade

---

## Décision technique préalable

### Quotas cibles — valeurs figées pour cette story

Le dev agent applique les quotas suivants dans le catalogue :

| Plan | Feature | quota_key | quota_limit | period_unit | reset_mode |
|------|---------|-----------|-------------|-------------|------------|
| basic | astrologer_chat | messages | **50** | **month** | calendar |
| basic | thematic_consultation | consultations | 4 | week | calendar |
| premium | astrologer_chat | messages | **1000** | **month** | calendar |
| premium | thematic_consultation | consultations | 2 | day | calendar |

**Raison de l'alignement sur `month`** : basic et premium partagent le même `quota_key="messages"` et `period_unit=month` → même clé composite `FeatureUsageCounterModel` → l'upgrade ne crée pas de nouveau compteur, il lit la limite supérieure sur le compteur mensuel existant.

**Ces valeurs sont définitives pour cette story.** Si un ajustement produit est nécessaire ultérieurement, il se fera uniquement via `seed_product_entitlements.py` ou `CanonicalEntitlementMutationService` — aucun changement de code applicatif requis (c'est précisément le but de cette story).

---

## Acceptance Criteria

### AC1 — Source de vérité unique : `PlanFeatureQuotaModel` en base

`PlanFeatureQuotaModel` (table `plan_feature_quotas`) est la **seule** source de vérité pour les limites et périodes de quota, peuplée par `seed_product_entitlements.py`.

- Aucune constante `_CHAT_QUOTA_BY_PLAN` ni `daily_message_limit` ne doit être consommée pour produire les chiffres exposés à l'utilisateur.
- Modifier un quota = modifier le seed + re-exécuter, ou muter via `CanonicalEntitlementMutationService`. Aucun changement de code applicatif requis.

### AC2 — Upgrade basic → premium : pas de reset de compteur

Quand un utilisateur passe de `basic` à `premium` pendant un mois calendaire :
- Le compteur mensuel `(user, astrologer_chat, messages, month, 1, calendar, window_start)` est partagé entre les deux plans (même clé composite)
- L'upgrade augmente la `quota_limit` consultée (50 → 1000) sans créer un nouveau compteur
- `remaining = max(0, 1000 - consumed)` — le consommé du mois est conservé

Ce comportement découle naturellement de l'alignement des `period_unit` en AC1. Pas de logique spéciale requise — uniquement que les deux plans partagent le même `period_unit` et `quota_key`.

### AC3 — Downgrade premium → basic : pas de réduction immédiate du quota actuel

Pendant la période où le plan effectif est encore `premium` (61-65 garantit `entitlement_plan=premium` jusqu'à l'échéance), le quota restant n'est pas réduit. Aucune modification côté quota pour ce cas — c'est un test de non-régression de 61-65.

### AC4 — Rotation de quotas : fenêtre calendaire, pas de reset explicite

La remise à zéro du quota mensuel résulte **uniquement** du calcul de fenêtre calendaire par `QuotaWindowResolver`, pas d'un déclencheur applicatif sur `invoice.paid` :

- Le 1er du mois suivant, `QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt)` retourne une nouvelle `window_start` → aucun compteur existant ne correspond → `QuotaUsageService` crée un nouveau compteur vierge à la première consommation
- `invoice.paid` est un signal billing Stripe (renouvellement d'abonnement) mais **n'est pas** le déclencheur technique de la rotation des compteurs de quota
- Aucune logique de reset explicite ne doit être ajoutée dans le handler `invoice.paid`
- Ce comportement est documenté par un test unitaire de `QuotaWindowResolver` couvrant le passage de mois

### AC5 — Usage temps réel exposé dans `GET /billing/subscription`

L'endpoint `GET /v1/billing/subscription` enrichi en 61-65 inclut, pour la feature principale (`astrologer_chat`) :
```json
{
  "current_quota": {
    "feature_code": "astrologer_chat",
    "quota_limit": 1000,
    "consumed": 420,
    "remaining": 580,
    "period_unit": "month",
    "period_value": 1,
    "reset_mode": "calendar",
    "window_start": "2026-03-01T00:00:00Z",
    "window_end": "2026-04-01T00:00:00Z"
  }
}
```

Règles sur la nullité :
- `current_quota` est **non-null** dès que le plan a un binding quota actif pour `astrologer_chat`, même si l'utilisateur n'a pas encore consommé (`consumed=0`, `remaining=quota_limit`)
- `current_quota` est **null** uniquement si le plan n'a pas de binding quota pour cette feature (ex : plan `free`, plan sans entitlement configuré)
- Cette distinction permet au frontend de différencier "plan sans quota" de "quota existant, non encore consommé"

### AC6 — Frontend : limites dynamiques depuis `subscription.current_quota`

`SubscriptionSettings.tsx` n'affiche plus les limites codées en dur ("50 msg/jour", "1000 msg/jour"). La **seule source** pour l'affichage des limites est `subscription.current_quota` (champ de `GET /billing/subscription`, ajouté en AC5) :

- `quota_limit` → valeur numérique de la limite
- `period_unit` → période formatée dynamiquement ("mois", "jour", etc.)
- Fallback si `current_quota` est null ou si la requête échoue : afficher "— msg"

`GET /entitlements/me` n'est **pas** utilisé pour l'affichage des limites dans les cards de plan — son rôle reste la gestion des gates produit (quota_remaining pour le CTA "quota épuisé").

### AC7 — Aucune constante de quota dans le code applicatif ou les tests métier

Ni `_CHAT_QUOTA_BY_PLAN`, ni `daily_message_limit`, ni aucune autre constante applicative ne sert à produire les limites affichées à l'utilisateur ou les `QuotaDefinition` utilisées pour lire les compteurs.

- `_PLAN_DEFAULTS.daily_message_limit` dans `BillingPlanData` peut subsister dans le DTO pour la compatibilité de sérialisation legacy, mais :
  - aucun test métier (unitaire ou d'intégration) ne doit s'appuyer sur sa valeur pour vérifier un quota
  - si un test utilise actuellement cette valeur comme référence de limite, il doit être mis à jour pour lire la limite depuis le catalogue DB
- Toute valeur de quota exposée à l'utilisateur doit remonter depuis `PlanFeatureQuotaModel`.

### AC8 — Tests

- Test unitaire : upgrade basic→premium intra-mois → le compteur mensuel `messages/month` est partagé, remaining = quota_premium - consumed
- Test unitaire : `QuotaWindowResolver.compute_window` pour passage de mois (rotation automatique)
- Test d'intégration : `GET /billing/subscription` retourne `current_quota` non-null pour un utilisateur actif ayant consommé des messages
- Test de non-régression : downgrade programmé (plan effectif = premium) → quota limit reste à la valeur premium jusqu'à l'échéance

---

## Tasks / Subtasks

- [x] **T1 — Aligner le catalogue canonique** (AC: 1, 2)
  - [x] Mettre à jour `seed_product_entitlements.py` : basic `astrologer_chat` → 50/month, premium `astrologer_chat` → 1000/month (même `quota_key="messages"`, même `period_unit=MONTH`)
  - [x] Mettre à jour le seed pour `thematic_consultation` si nécessaire pour cohérence
  - [x] Vérifier que `CanonicalEntitlementMutationService.upsert_plan_feature_configuration` remplace correctement les quotas existants (pas de doublon)
  - [x] Documenter la décision dans les notes de completion

- [x] **T2 — Exposer `current_quota` dans `SubscriptionStatusData` via lecture DB** (AC: 5)
  - [x] Ajouter `current_quota: CurrentQuotaData | None = None` dans `SubscriptionStatusData` (Pydantic, défaut None)
  - [x] Créer `CurrentQuotaData(BaseModel)` avec `feature_code`, `quota_limit`, `consumed`, `remaining`, `period_unit`, `period_value`, `reset_mode`, `window_start`, `window_end`
  - [x] Créer `BillingService._resolve_current_quota(db, *, user_id, plan_code) -> CurrentQuotaData | None`
    - Charger `PlanCatalogModel` pour `plan_code` (audience=B2C)
    - Charger `PlanFeatureBindingModel` actif pour `(plan, feature=astrologer_chat)`, access_mode=QUOTA
    - Charger le quota de la feature billing principale : `PlanFeatureQuotaModel` ordonné par `quota_key` de façon déterministe (ex: `ORDER BY quota_key ASC LIMIT 1`) — **jamais de `.limit(1)` sans order** sur une table à plusieurs quotas potentiels
    - Construire `QuotaDefinition` depuis ces données DB
    - Appeler `QuotaUsageService.get_usage(...)` — si aucun compteur n'existe, retourner `consumed=0, remaining=quota_limit`
    - Retourner `CurrentQuotaData` avec les valeurs DB + usage réel
  - [x] Si pas de binding actif ou plan inconnu : retourner `None` (mais jamais `None` simplement parce que consumed=0)
  - [x] Appeler `_resolve_current_quota` dans `_to_stripe_subscription_data` — non bloquant (exception catchée → `current_quota=None`)
  - [x] **Jamais de dict de constantes hardcodées** : toutes les valeurs de quota viennent de `PlanFeatureQuotaModel`

- [x] **T3 — Frontend : limites dynamiques depuis `subscription.current_quota`** (AC: 6, 7)
  - [x] Dans `SubscriptionSettings.tsx`, lire `quota_limit` et `period_unit` depuis `useBillingSubscription().data.current_quota` — **pas** depuis `useMyEntitlements()`
  - [x] Pour chaque plan affiché, associer la limite au plan courant (`current_quota`) — **limitation assumée de cette story** : les plans non actifs (pas encore souscrits par l'utilisateur) affichent "— msg" ; l'exposition d'un catalogue complet de quotas par plan (pour les cards non actives) est hors scope et sera traitée séparément si le produit l'exige
  - [x] Formater dynamiquement la limite en i18n : `${quota_limit} msg / ${t.periodUnit[period_unit]}` via `settings.ts`
  - [x] Ajouter clés i18n dans la section `subscription` de `settings.ts` : `quotaPerDay`, `quotaPerMonth`, `quotaPerWeek`
  - [x] Fallback si `current_quota` est null ou requête en erreur : afficher "— msg"
  - [x] Ne pas modifier la logique de checkout/portal — uniquement l'affichage

- [x] **T4 — Supprimer la consommation de `daily_message_limit` pour l'affichage** (AC: 7)
  - [x] Vérifier dans le frontend que `daily_message_limit` n'est plus affiché directement après T3
  - [x] Le champ peut rester dans `BillingPlanData` pour compatibilité (ne pas le supprimer du DTO)

- [x] **T5 — Tests** (AC: 2, 4, 8)
  - [x] Unit test `QuotaWindowResolver` : passage de mois (window_start change le 1er du mois)
  - [x] Unit test comportement upgrade : `quota_key="messages"` + `period_unit=month` → même compteur avant et après upgrade
  - [x] Integration test `GET /billing/subscription` → `current_quota` présent et exact
  - [x] Test de non-régression downgrade : plan effectif premium → quota limit = 1000 (pas 50)

---

## Dev Notes

### Architecture : comment fonctionne le compteur partagé (AC2)

`FeatureUsageCounterModel` est identifié par `(user_id, feature_code, quota_key, period_unit, period_value, reset_mode, window_start)`.

Si basic et premium définissent tous deux `astrologer_chat` avec `quota_key="messages"`, `period_unit=MONTH`, `period_value=1`, `reset_mode=CALENDAR` → même 7-uplet, même ligne en base. Après upgrade, `EffectiveEntitlementResolverService` lit le plan premium → `quota_limit=1000`. Le `used_count` dans le compteur est inchangé. `remaining = 1000 - used_count`. Pas de logique spéciale : c'est structurellement correct.

### T2 — `_resolve_current_quota` : lecture 100% depuis la DB

**Principe** : aucune constante dans `billing_service.py`. La `QuotaDefinition` est construite à partir de `PlanFeatureQuotaModel`.

```python
# Dans billing_service.py

class CurrentQuotaData(BaseModel):
    feature_code: str
    quota_limit: int
    consumed: int
    remaining: int
    period_unit: str
    period_value: int
    reset_mode: str
    window_start: datetime
    window_end: datetime | None = None

_BILLING_QUOTA_FEATURE = "astrologer_chat"  # feature principale exposée dans le résumé billing

@staticmethod
def _resolve_current_quota(
    db: Session, *, user_id: int, plan_code: str
) -> "CurrentQuotaData | None":
    """
    Résout le quota courant de la feature principale (astrologer_chat)
    depuis le catalogue DB + le compteur utilisateur.
    Retourne None si le plan n'a pas de binding actif ou si le quota est introuvable.
    """
    from app.infra.db.models.product_entitlements import (
        Audience, FeatureCatalogModel, PlanCatalogModel,
        PlanFeatureBindingModel, PlanFeatureQuotaModel, AccessMode,
    )
    from app.services.entitlement_types import QuotaDefinition
    from app.services.quota_usage_service import QuotaUsageService
    from sqlalchemy import select

    # 1. Plan canonique
    plan = db.scalar(
        select(PlanCatalogModel).where(
            PlanCatalogModel.plan_code == plan_code,
            PlanCatalogModel.audience == Audience.B2C,
            PlanCatalogModel.is_active.is_(True),
        ).limit(1)
    )
    if plan is None:
        return None

    # 2. Feature
    feature = db.scalar(
        select(FeatureCatalogModel).where(
            FeatureCatalogModel.feature_code == BillingService._BILLING_QUOTA_FEATURE
        ).limit(1)
    )
    if feature is None:
        return None

    # 3. Binding plan ↔ feature
    binding = db.scalar(
        select(PlanFeatureBindingModel).where(
            PlanFeatureBindingModel.plan_id == plan.id,
            PlanFeatureBindingModel.feature_id == feature.id,
            PlanFeatureBindingModel.is_enabled.is_(True),
            PlanFeatureBindingModel.access_mode == AccessMode.QUOTA,
        ).limit(1)
    )
    if binding is None:
        return None

    # 4. Quota principal du binding — ordre déterministe pour éviter un résultat aléatoire
    # si plusieurs quotas coexistent sur le même binding à l'avenir
    from sqlalchemy import asc
    quota_row = db.scalar(
        select(PlanFeatureQuotaModel)
        .where(PlanFeatureQuotaModel.plan_feature_binding_id == binding.id)
        .order_by(asc(PlanFeatureQuotaModel.quota_key))
        .limit(1)
    )
    if quota_row is None:
        return None

    q_def = QuotaDefinition(
        quota_key=quota_row.quota_key,
        quota_limit=quota_row.quota_limit,
        period_unit=quota_row.period_unit.value,
        period_value=quota_row.period_value,
        reset_mode=quota_row.reset_mode.value,
    )

    # 5. Compteur courant (get_usage retourne used=0 si absent)
    usage = QuotaUsageService.get_usage(
        db,
        user_id=user_id,
        feature_code=BillingService._BILLING_QUOTA_FEATURE,
        quota=q_def,
    )

    return CurrentQuotaData(
        feature_code=BillingService._BILLING_QUOTA_FEATURE,
        quota_limit=usage.quota_limit,
        consumed=usage.used,
        remaining=usage.remaining,
        period_unit=usage.period_unit,
        period_value=usage.period_value,
        reset_mode=usage.reset_mode,
        window_start=usage.window_start,
        window_end=usage.window_end,
    )
```

**Dans `_to_stripe_subscription_data`** :
```python
current_quota = None
if is_active and app_plan_code:
    try:
        current_quota = BillingService._resolve_current_quota(
            db, user_id=profile.user_id, plan_code=app_plan_code
        )
    except Exception:
        logger.warning("Failed to resolve current_quota for user=%s", profile.user_id)

return SubscriptionStatusData(..., current_quota=current_quota)
```

**Conséquence** : modifier un quota = UPDATE sur `plan_feature_quotas` via seed ou `CanonicalEntitlementMutationService`. Zéro changement de code applicatif.

### T3 — Source unique pour l'affichage des limites : `subscription.current_quota`

Le frontend utilise **uniquement** `subscription.current_quota` (champ de `GET /billing/subscription`). Pas de second appel à `GET /entitlements/me` pour l'affichage des limites.

```typescript
const quota = subscription?.current_quota

// Affichage de la limite du plan courant
const limitDisplay = quota
  ? `${quota.quota_limit} ${t.subscription.quotaUnit}/${t.subscription.periodUnit[quota.period_unit]}`
  : "—"
```

`GET /entitlements/me` continue d'être consommé par les gates produit (bouton "quota épuisé", accès aux features) — son rôle est orthogonal à l'affichage des limites dans les cards de plan.

### Fichiers clés

| Fichier | Modification |
|---------|-------------|
| `backend/scripts/seed_product_entitlements.py` | Aligner quotas basic/premium chat sur month/50 et month/1000 |
| `backend/app/services/billing_service.py` | Ajouter `CurrentQuotaData`, `_resolve_current_quota`, `current_quota` dans `SubscriptionStatusData` |
| `backend/app/services/quota_usage_service.py` | Aucune modification |
| `frontend/src/pages/settings/SubscriptionSettings.tsx` | Remplacer valeurs hardcodées |
| `frontend/src/i18n/settings.ts` | Ajouter clés i18n quota |
| `backend/app/tests/unit/test_quota_window_resolver.py` | Nouveau ou enrichir |
| `backend/app/tests/integration/test_billing_api.py` | current_quota dans response |

### Non-régression critique : ne pas casser `GET /entitlements/me`

`GET /entitlements/me` retourne déjà `quota_limit` et `usage_states` pour `astrologer_chat`. Cette story ne modifie pas ce endpoint. Elle ne modifie pas `EffectiveEntitlementResolverService`. Elle ne modifie pas `QuotaUsageService`. Seul `billing_service.py` est enrichi (nouveau champ dans le DTO) et le seed est mis à jour.

### Rotation automatique à l'échéance (AC4) : comment ça fonctionne

`QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt)` retourne toujours `window_start = 1er du mois courant`. Quand `invoice.paid` arrive (début nouvelle période Stripe), il n'est PAS nécessaire d'appeler quoi que ce soit sur les compteurs. La prochaine requête quota le 1er du mois aura `window_start = 2026-04-01`, donc trouvera un compteur vierge (used_count=0) ou en créera un. La rotation est **totalement transparente** — c'est l'un des points forts de l'architecture actuelle.

**Attention** : cela suppose que la période Stripe commence autour du 1er du mois calendaire. Si un utilisateur s'abonne le 15 du mois, sa période Stripe va du 15 au 15, mais son quota `messages/month` se remet le 1er (calendaire). C'est une légère désynchronisation, acceptable pour cette story. L'alignement parfait sur la période Stripe nécessiterait de changer `reset_mode` en `billing_period` — **hors scope**, à traiter dans une story future si le produit l'exige.

### Previous Story Intelligence (61-65)

- Les champs `current_period_start`, `current_period_end`, `scheduled_plan_code`, `cancel_at_period_end` ont été ajoutés à `StripeBillingProfileModel` en 61-65
- `SubscriptionStatusData` a déjà `cancel_at_period_end`, `current_period_end`, `scheduled_plan`, `change_effective_at`
- Cette story ajoute `current_quota` dans `SubscriptionStatusData` — champ optionnel, pas de breaking change

### Git Intelligence (commits récents)

- `e4cedbe fix(billing): add missing integration tests (Story 61-64)`
- `ca3b75c feat(billing): explicit Stripe Customer Portal configuration (Story 61-64)`
- Story 61-65 est marquée `done` — ses nouveaux champs sont disponibles

### References

- [Source: `backend/scripts/seed_product_entitlements.py`] — quotas actuels basic=5/day, premium=2000/month → à corriger
- [Source: `backend/app/services/billing_service.py`] — `_PLAN_DEFAULTS`, `SubscriptionStatusData`, `_to_stripe_subscription_data`
- [Source: `backend/app/services/quota_usage_service.py`] — `QuotaUsageService.get_usage`
- [Source: `backend/app/services/quota_window_resolver.py`] — `QuotaWindowResolver.compute_window`
- [Source: `backend/app/infra/db/models/product_entitlements.py`] — `FeatureUsageCounterModel`
- [Source: `frontend/src/pages/settings/SubscriptionSettings.tsx`] — limites hardcodées lignes 38-54
- [Source: `frontend/src/i18n/settings.ts`] — section subscription, clés existantes
- [Source: `_bmad-output/implementation-artifacts/61-65-coherence-plan-effectif-upgrade-immediat-downgrade-cancel-echeance.md`] — contexte plan effectif

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Story créée le 2026-03-31 après analyse complète du seed catalog et de l'architecture quota.
- Incohérence triple découverte : `_PLAN_DEFAULTS` (50/jour, 1000/jour) ≠ seed catalog (5/jour basic, 2000/mois premium) ≠ frontend hardcodé (50 msg/jour, 1000 msg/jour).
- L'enforcement réel est toujours le catalogue canonique — les valeurs affichées sont fausses.
- L'alignement sur `period_unit=MONTH` pour basic et premium résout naturellement la règle R6 (pas de reset sur upgrade) sans logique spéciale.
- `current_quota` ajouté dans `SubscriptionStatusData` pour exposer l'usage temps réel sans requête frontend supplémentaire.
- La rotation à l'échéance Stripe est gratuite grâce à `QuotaWindowResolver` — pas de code supplémentaire nécessaire.
- [Ajustement 2026-03-31] `_resolve_current_quota` lit 100% depuis `PlanFeatureQuotaModel` en base — aucune constante hardcodée dans le code applicatif, conformément à l'exigence produit "quotas pilotés par la DB".
- [Review 2026-03-31] Valeurs cibles figées dans la story (plus de "à valider") — si changement produit : via seed/mutation service uniquement.
- [Review 2026-03-31] AC4 clarifié : rotation = fenêtre calendaire `QuotaWindowResolver`, pas `invoice.paid` (signal billing ≠ déclencheur technique).
- [Review 2026-03-31] AC5 + T2 : `current_quota` retourné même si `consumed=0` — `null` uniquement si pas de binding quota actif.
- [Review 2026-03-31] T2 pseudo-code : `ORDER BY quota_key ASC LIMIT 1` sur `PlanFeatureQuotaModel` pour déterminisme.
- [Review 2026-03-31] AC6 + T3 : source frontend unique = `subscription.current_quota` — `GET /entitlements/me` exclu de l'affichage des limites.
- [Review 2026-03-31] AC7 : `_PLAN_DEFAULTS.daily_message_limit` neutralisé dans les tests métier — aucun test ne s'appuie sur cette valeur comme référence de limite.

### File List

- `_bmad-output/implementation-artifacts/61-66-coherence-quotas-usage-affichage-limites-plans.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/billing_service.py`
- `backend/scripts/seed_product_entitlements.py`
- `frontend/src/i18n/settings.ts`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `backend/app/tests/unit/test_quota_window_resolver.py`
- `backend/app/tests/unit/test_quota_usage_service.py`
- `backend/app/tests/integration/test_billing_api.py`
- `backend/app/tests/integration/test_billing_api_61_66.py`
