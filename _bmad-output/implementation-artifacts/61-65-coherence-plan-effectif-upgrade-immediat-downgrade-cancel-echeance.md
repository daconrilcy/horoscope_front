# Story 61.65 : Cohérence plan effectif — upgrade immédiat, downgrade/cancel à échéance

Status: done

## Story

En tant que système backend billing SaaS,
je veux aligner strictement les droits applicatifs et le plan affiché sur le **moment d'effet réel du changement de subscription dans Stripe**,
afin que l'application n'accorde jamais trop tôt ni ne retire trop tôt des droits — upgrade immédiat facturé au prorata, downgrade et cancel effectifs à la prochaine échéance.

---

## Contexte

La story 61-64 a durci la configuration du Stripe Customer Portal (`proration_behavior=always_invoice`, `schedule_at_period_end.conditions=[{type:"decreasing_item_amount"}]`). Désormais Stripe applique le bon comportement côté facturation, mais **le backend local ne distingue pas encore plan effectif et plan programmé**. Résultat :

- **Upgrade `basic → premium`** : Stripe facture immédiatement et change la price_id de la subscription. La logique `derive_entitlement_plan` lit `items[0].price.id` et accorde immédiatement `premium`. ✓ **correct comportement** mais non testé explicitement.
- **Downgrade `premium → basic`** : Stripe crée une **subscription schedule** (portail configuré avec `schedule_at_period_end`). La price_id courante reste `premium` → `derive_entitlement_plan` retourne "premium". ✓ Mais aucun champ local ne porte `scheduled_plan_code=basic` → l'API et le frontend n'exposent pas le changement prévu.
- **Cancel via portail** : Stripe pose `cancel_at_period_end=true`. Le champ existe dans `StripeBillingProfileModel` mais n'est pas exposé dans `SubscriptionStatusData` → le frontend affiche `cancelSoon` statique, sans date ni état réel.
- **Fin de période** : Quand la subscription est effectivement annulée (`customer.subscription.deleted`), la logique bascule correctement en `free`. ✓ Mais la rotation de `scheduled_plan_code` n'est pas nettoyée.

**Ce qui manque** :
1. Champs DB : `current_period_start`, `scheduled_plan_code`, `scheduled_change_effective_at`, `pending_cancellation_effective_at`
2. Détection du downgrade programmé (subscription schedule) dans le webhook
3. Extension du DTO `SubscriptionStatusData` avec les champs plan futur / annulation
4. Frontend : afficher le plan programmé, activer l'annulation, afficher "Résiliation prévue le…"

---

## Acceptance Criteria

### AC1 — Upgrade immédiat : plan effectif mis à jour instantanément

Quand `customer.subscription.updated` arrive avec une price_id premium effective (status `active`, items[0].price.id = premium), le profil local reflète `entitlement_plan=premium` et `scheduled_plan_code=null` immédiatement.

### AC2 — Downgrade programmé : plan effectif conservé, plan prévu tracé

Quand une subscription schedule Stripe programme une bascule vers `basic` à `current_period_end` :
- `entitlement_plan` reste `premium`
- `scheduled_plan_code = "basic"`
- `scheduled_change_effective_at = current_period_end`
- l'API retourne ces champs distincts

### AC3 — Cancel programmé : droits maintenus, annulation exposée

Quand `cancel_at_period_end=true` dans Stripe :
- `entitlement_plan` reste inchangé jusqu'à `current_period_end`
- `pending_cancellation_effective_at` = `current_period_end`
- l'API retourne `cancel_at_period_end=true` et `current_period_end`

### AC4 — Fin effective : bascule correcte + nettoyage complet

Quand `customer.subscription.deleted` arrive :
- `entitlement_plan = "free"`
- `scheduled_plan_code = null`
- `scheduled_change_effective_at = null`
- `pending_cancellation_effective_at = null`
- `cancel_at_period_end = false`
- `current_period_start` et `current_period_end` conservés tels quels (valeur historique, pas de mise à null) — sauf si la story 61-66 décide autrement

L'état résultant ne doit jamais laisser `cancel_at_period_end=true` avec `entitlement_plan="free"`, ce qui produirait un marqueur incohérent.

### AC5 — Contrat API enrichi et règle d'accès

`GET /v1/billing/subscription` retourne :
```json
{
  "status": "active",
  "subscription_status": "active",
  "plan": { "code": "premium", ... },
  "scheduled_plan": { "code": "basic", ... },
  "change_effective_at": "2026-04-30T22:00:00Z",
  "cancel_at_period_end": false,
  "current_period_end": "2026-04-30T22:00:00Z"
}
```
Tous les champs additionnels sont nullable/optionnels pour ne pas casser les clients existants.

**Règle invariante** : `scheduled_plan` est **informatif uniquement**. Il n'ouvre ni ne ferme aucun droit runtime. Tous les gates produit (quota, features) continuent de lire `plan.code` (= `entitlement_plan`), jamais `scheduled_plan`. Cette règle doit être respectée dans tout le code qui consomme ce DTO.

### AC6 — Frontend : annulation activée et états affichés

- La carte "Gratuit" dans `SubscriptionSettings` peut être sélectionnée quand l'utilisateur a un abonnement actif, déclenchant le flow portal cancel.
- Si `cancel_at_period_end=true` : afficher "Résiliation prévue le [date]" au lieu du texte `cancelSoon` statique.
- Si `scheduled_plan` existe : afficher "Passage à [plan] le [date]".

### AC7 — Webhook idempotent et non-régressif

Les traitements `customer.subscription.updated`, `invoice.paid` et `customer.subscription.deleted` restent idempotents. Pas de double rotation de plan.

`subscription_schedule.updated` est **optionnel** : s'il est branché, il doit être idempotent ; s'il ne l'est pas, la détection du downgrade programmé passe uniquement par l'inspection du champ `subscription.schedule` dans `customer.subscription.updated`. Son absence n'est pas un bloquant pour valider la story.

### AC8 — Tests couvrant les 4 parcours

Tests unitaires et d'intégration couvrent : souscription directe, upgrade immédiat, downgrade différé, cancel différé.

---

## Tasks / Subtasks

- [x] **T1 — Migration DB : nouveaux champs** (AC: 2, 3, 4)
  - [x] Ajouter dans `StripeBillingProfileModel` : `current_period_start`, `scheduled_plan_code`, `scheduled_change_effective_at`, `pending_cancellation_effective_at`
  - [x] Créer la migration Alembic correspondante
  - [x] Vérifier la rétro-compatibilité (champs nullable)

- [x] **T2 — Détection du downgrade programmé dans le webhook** (AC: 2)
  - [x] Dans `update_from_event_payload`, si `subscription.schedule` est non-null, appeler `stripe.SubscriptionSchedule.retrieve(schedule_id)` pour lire `phases[1]` et en extraire la price_id du prochain plan
  - [x] Mapper cette price_id sur `scheduled_plan_code` via `STRIPE_PRICE_ENTITLEMENT_MAP`
  - [x] Mettre `scheduled_change_effective_at = current_period_end`
  - [x] Si `subscription.schedule` est null : vider `scheduled_plan_code` et `scheduled_change_effective_at`
  - [x] (Optionnel) Ajouter `subscription_schedule.updated` dans la liste des événements traités par `StripeWebhookService.handle_event` — non bloquant pour la story ; voir AC7

- [x] **T3 — Enrichissement `update_from_event_payload`** (AC: 1, 2, 3, 4)
  - [x] Mettre à jour `current_period_start` depuis `data_obj.get("current_period_start")`
  - [x] Mettre à jour `pending_cancellation_effective_at` : si `cancel_at_period_end=True` → `current_period_end`, sinon `None`
  - [x] Sur `customer.subscription.deleted` : forcer `scheduled_plan_code=None`, `scheduled_change_effective_at=None`, `pending_cancellation_effective_at=None`

- [x] **T4 — Extension DTO `SubscriptionStatusData`** (AC: 5)
  - [x] Ajouter dans `billing_service.py` :
    ```python
    scheduled_plan: BillingPlanData | None = None
    change_effective_at: datetime | None = None
    cancel_at_period_end: bool = False
    current_period_end: datetime | None = None
    ```
  - [x] Alimenter ces champs dans `_to_stripe_subscription_data`

- [x] **T5 — Frontend : activer le cancel et afficher les états** (AC: 6)
  - [x] Dans `SubscriptionSettings`, permettre la sélection du plan "Gratuit" si `stripeSubscriptionStatus === "active"`, en appelant le flow cancel portal
  - [x] Ajouter les clés i18n dans `settings.ts` : `cancelScheduled`, `planChangeScheduled`, `planFree`
  - [x] Afficher le message "Résiliation prévue le [date]" si `subscription.cancel_at_period_end === true`
  - [x] Afficher "Passage à [plan] le [date]" si `subscription.scheduled_plan` est non-null
  - [x] Supprimer ou conditionner le texte `cancelSoon` statique

- [x] **T6 — Tests** (AC: 7, 8)
  - [x] Unit tests `derive_entitlement_plan` : upgrade, downgrade (schedule détecté), cancel, deleted
  - [x] Unit tests `update_from_event_payload` : vérifier la population de `scheduled_plan_code`, `pending_cancellation_effective_at`
  - [x] Integration tests webhook : `customer.subscription.updated` pour les 3 cas (upgrade, downgrade programmé, cancel programmé)
  - [x] Integration test `customer.subscription.deleted` (vérifie état final complet : free + cancel_at_period_end=false + scheduled_plan_code=null)
  - [x] Test `GET /billing/subscription` pour les champs enrichis
  - [x] (Optionnel) Integration test `subscription_schedule.updated` si l'événement est branché


---

## Dev Notes

### Architecture — principe à ne pas violer

> Le plan effectif (`entitlement_plan`) gouverne les droits **maintenant**. Il ne doit jamais avancer vers un plan futur avant que Stripe ne le rende effectif. `scheduled_plan_code` est informatif uniquement — il n'affecte aucun droit runtime.

La logique est toujours : **webhook Stripe → profil local → droits produit**. Aucune mutation directe de droits au clic utilisateur.

### Fichiers clés

| Fichier | Rôle |
|---------|------|
| `backend/app/infra/db/models/stripe_billing.py` | Ajouter les 4 nouveaux champs |
| `backend/alembic/versions/*.py` | Migration Alembic |
| `backend/app/services/stripe_billing_profile_service.py` | `update_from_event_payload` + `derive_entitlement_plan` |
| `backend/app/services/stripe_webhook_service.py` | Ajouter `subscription_schedule.updated` dans le dispatch |
| `backend/app/services/billing_service.py` | `SubscriptionStatusData` + `_to_stripe_subscription_data` |
| `backend/app/api/v1/routers/billing.py` | Aucun changement de route nécessaire |
| `frontend/src/pages/settings/SubscriptionSettings.tsx` | Affichage états programmés + cancel |
| `frontend/src/i18n/settings.ts` | Clés i18n manquantes |

### T2 — Détection du downgrade via subscription schedule

Quand la portal config utilise `schedule_at_period_end.conditions=[{type:"decreasing_item_amount"}]`, un downgrade via le portail crée une `SubscriptionSchedule` Stripe avec 2 phases :
- Phase 0 (actuelle) : fin = `current_period_end`, items = [premium price_id]
- Phase 1 (prochaine) : début = `current_period_end`, items = [basic price_id]

Dans `customer.subscription.updated`, l'objet subscription contiendra `subscription.schedule = "sub_sched_xxx"`.

```python
# Dans update_from_event_payload, section "if object_type == 'subscription':"
schedule_id = data_obj.get("schedule")
if schedule_id:
    # Appel Stripe pour lire les phases — non-bloquant
    try:
        client = get_stripe_client()
        if client:
            schedule = client.subscription_schedules.retrieve(schedule_id)
            phases = schedule.get("phases", [])
            # Chercher la prochaine phase dont start_date >= now (période courante)
            # Ne pas supposer que l'index 1 est toujours correct (peut y avoir des phases passées)
            now_ts = datetime.now(timezone.utc).timestamp()
            next_phase = next(
                (p for p in phases if p.get("start_date", 0) > now_ts),
                None,
            )
            if next_phase:
                next_price_items = next_phase.get("items", [])
                if next_price_items:
                    next_price_id = next_price_items[0].get("price")
                    profile.scheduled_plan_code = STRIPE_PRICE_ENTITLEMENT_MAP.get(next_price_id)
                    profile.scheduled_change_effective_at = datetime.fromtimestamp(
                        next_phase["start_date"], tz=timezone.utc
                    )
            else:
                # Aucune phase future trouvée : schedule sans effet programmé
                profile.scheduled_plan_code = None
                profile.scheduled_change_effective_at = None
    except Exception:
        logger.warning("Failed to retrieve subscription schedule %s", schedule_id)
        # Non-bloquant : on laisse les champs tels quels si le fetch échoue
else:
    profile.scheduled_plan_code = None
    profile.scheduled_change_effective_at = None
```

**Important** : Si `get_stripe_client()` retourne None (tests), skipper silencieusement et ne pas populer `scheduled_plan_code`. Dans les tests, mocker le client et simuler les données de schedule.

### T3 — `pending_cancellation_effective_at`

```python
# Dans update_from_event_payload
if profile.cancel_at_period_end and profile.current_period_end:
    profile.pending_cancellation_effective_at = profile.current_period_end
elif not profile.cancel_at_period_end:
    profile.pending_cancellation_effective_at = None
```

### T4 — `_to_stripe_subscription_data` enrichi

```python
@staticmethod
def _to_stripe_subscription_data(db, *, profile) -> SubscriptionStatusData:
    # ... existant ...
    scheduled_plan_data = None
    if profile.scheduled_plan_code:
        plan_model = BillingService._get_plan_by_code(db, profile.scheduled_plan_code)
        scheduled_plan_data = (
            BillingService._to_plan_data(plan_model)
            if plan_model else
            BillingService._get_default_plan_data_by_code(profile.scheduled_plan_code)
        )

    return SubscriptionStatusData(
        status=exposed_status,
        subscription_status=profile.subscription_status,
        plan=plan_data,
        scheduled_plan=scheduled_plan_data,
        change_effective_at=profile.scheduled_change_effective_at,
        cancel_at_period_end=profile.cancel_at_period_end,
        current_period_end=profile.current_period_end,
        failure_reason=None,
        updated_at=profile.updated_at,
    )
```

### T5 — Frontend : logique cancel

Actuellement, `handleValidate` interdit `selectedPlanCode === null`. Il faut lever cette restriction pour les utilisateurs avec subscription active, et brancher le flow cancel :

```typescript
// si sélection du plan gratuit + subscription active → portal cancel
if (displaySelected === null && stripeSubscriptionStatus === "active") {
  // appeler portalCancelSession au lieu de bloquer
}
```

Le bouton "Valider" doit être actif quand le plan Gratuit est sélectionné et l'abonnement est actif.

### T5 — Clés i18n à ajouter dans `settings.ts`

```typescript
// Dans subscription.*
planFree: "Gratuit",  // existe déjà en dur dans SubscriptionSettings - à centraliser
cancelScheduled: "Résiliation prévue le {{date}}",
planChangeScheduled: "Passage à {{plan}} le {{date}}",
cancelConfirmTitle: "Résilier l'abonnement",
cancelConfirmDesc: "Votre accès restera actif jusqu'au {{date}}.",
```

### Pas de migration des crédits/usage dans cette story

Cette story se concentre sur la **réconciliation du plan effectif et du plan prévu**. Le modèle de crédits mensuel (`monthly_credit_limit`, `consumed_credits`) décrit dans le draft est **hors scope** de cette story — il sera traité dans une story 61-66 dédiée si nécessaire. Cette story implémente uniquement les champs de billing profile et les droits d'accès.

### Migration Alembic

Créer une migration dans `backend/alembic/versions/` :
```python
# Nouveaux champs nullable
op.add_column("stripe_billing_profiles", sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True))
op.add_column("stripe_billing_profiles", sa.Column("scheduled_plan_code", sa.String(32), nullable=True))
op.add_column("stripe_billing_profiles", sa.Column("scheduled_change_effective_at", sa.DateTime(timezone=True), nullable=True))
op.add_column("stripe_billing_profiles", sa.Column("pending_cancellation_effective_at", sa.DateTime(timezone=True), nullable=True))
```

### Idempotence webhook `subscription_schedule.updated`

L'événement `subscription_schedule.updated` peut contenir l'objet schedule complet. Son traitement peut soit :
- Appeler `update_from_event_payload` avec l'ID customer/subscription résolu depuis le schedule
- Soit utiliser une méthode dédiée `_update_scheduled_plan_from_schedule_event`

Dans tous les cas, l'idempotence est garantie par le `StripeWebhookIdempotencyService` existant (event_id). Pas besoin de logique supplémentaire.

### Compatibilité frontend existante

`SubscriptionStatusData` hérite de Pydantic avec des valeurs par défaut. Les clients qui lisent l'endpoint `GET /billing/subscription` actuellement ne seront pas cassés — les nouveaux champs (`scheduled_plan`, `change_effective_at`, `cancel_at_period_end`, `current_period_end`) seront simplement ignorés par les clients qui ne les attendent pas encore.

### Project Structure Notes

- Migrations Alembic : `backend/alembic/versions/`
- Model DB : `backend/app/infra/db/models/stripe_billing.py`
- Service profil Stripe : `backend/app/services/stripe_billing_profile_service.py`
- Service webhook : `backend/app/services/stripe_webhook_service.py`
- Service billing : `backend/app/services/billing_service.py` (SubscriptionStatusData)
- Tests unitaires profil : `backend/app/tests/unit/test_stripe_billing_profile_service.py` (à créer ou enrichir)
- Tests intégration billing : `backend/app/tests/integration/test_billing_api.py`
- Frontend : `frontend/src/pages/settings/SubscriptionSettings.tsx`
- i18n : `frontend/src/i18n/settings.ts`

### Previous Story Intelligence (61-64)

- La story 61-64 a **déjà configuré** le portail avec `schedule_at_period_end.conditions` et `proration_behavior=always_invoice`. Cette story consomme ce comportement Stripe.
- Le modèle de double barrière (startup + service) de 61-64 ne change pas.
- Le pattern "webhook-first, jamais de droits au clic" reste invariant.
- `StripeBillingProfileModel.cancel_at_period_end` existe déjà (Boolean, default=False) — exploiter sans le recréer.
- `current_period_end` existe déjà dans le modèle — ne pas dupliquer.

### Git Intelligence (commits récents)

- `e4cedbe fix(billing): add missing integration tests and root .env.example update (Story 61-64)`
- `ca3b75c feat(billing): explicit Stripe Customer Portal configuration and startup guard (Story 61-64)`
- `abf0d39 feat(billing): complete legacy commercial and pricing cleanup (Story 61-63)`

Le pattern de la codebase billing : services centralisés, tests d'intégration explicites, pas de mutation locale de droits hors webhook.

### References

- [Source: `backend/app/infra/db/models/stripe_billing.py`] — modèle actuel, champs existants
- [Source: `backend/app/services/stripe_billing_profile_service.py`] — `update_from_event_payload`, `derive_entitlement_plan`
- [Source: `backend/app/services/stripe_webhook_service.py`] — dispatch événements + liste actuelle des events traités
- [Source: `backend/app/services/billing_service.py`] — `SubscriptionStatusData`, `_to_stripe_subscription_data`
- [Source: `backend/app/api/v1/routers/billing.py`] — endpoint `GET /billing/subscription`
- [Source: `frontend/src/pages/settings/SubscriptionSettings.tsx`] — UI subscription, logique handleValidate
- [Source: `frontend/src/i18n/settings.ts`] — clés i18n existantes subscription
- [Source: `_bmad-output/implementation-artifacts/61-64-configuration-explicite-customer-portal-stripe-et-prorata-upgrade.md`] — story précédente, config portail

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Story créée le 2026-03-31 à partir du draft technique fourni, après analyse du code existant (61-64 done).
- Périmètre volontairement réduit vs le draft : pas de migration du modèle de crédits/usage (monthly_credit_limit, consumed_credits) — reporté à une story 61-66 si nécessaire.
- Le mécanisme de détection du downgrade via subscription schedule (`subscription.schedule` + retrieve) est le point technique le plus délicat — voir T2 en détail.
- Les champs `SubscriptionStatusData` sont ajoutés avec defaults pour ne pas casser les clients existants.
- [Review ajustements 2026-03-31] `subscription_schedule.updated` rendu optionnel/non bloquant (AC7, T6).
- [Review ajustements 2026-03-31] Détection phase suivante par `start_date > now` au lieu de `phases[1]` pour plus de robustesse (T2).
- [Review ajustements 2026-03-31] Nettoyage explicite de `cancel_at_period_end=false` sur `subscription.deleted` (AC4).
- [Review ajustements 2026-03-31] Règle invariante `scheduled_plan` = informatif uniquement, jamais de droits runtime (AC5).
- [Code Review 2026-03-31] Revue de code complète effectuée. L'implémentation correspond parfaitement aux ACs. Correction d'une erreur TypeScript liée à des clés i18n manquantes dans les traductions anglaises et espagnoles. Tous les tests backend et frontend sont au vert.
- [Post-review fix 2026-03-31] `SubscriptionSettings` utilise désormais le flow Stripe dédié `subscription_cancel` lors de la sélection du plan Gratuit, au lieu du portail générique.
- [Post-review fix 2026-03-31] La couverture frontend verrouille explicitement le parcours de résiliation dédié.
- [Post-validation fix 2026-03-31] Le retour portail + webhook ont été durcis côté frontend: message de synchronisation visible, bascule automatique en mode réactivation après convergence backend, carte `free` gelée, CTA de réactivation explicites, et mention de résiliation affichée sur le plan encore actif.
- [Post-validation fix 2026-03-31] Root cause backend confirmé sur environnement réel: Stripe test expose une résiliation planifiée via `cancel_at` avec `cancel_at_period_end=false`. Le mapping local ne lisait que `cancel_at_period_end`, ce qui empêchait `GET /v1/billing/subscription` de refléter la résiliation.
- [Post-validation fix 2026-03-31] `StripeBillingProfileService.update_from_event_payload()` traite désormais `cancel_at` comme une résiliation programmée, aligne `pending_cancellation_effective_at` sur cette échéance, puis invalide le cache billing pour la prochaine lecture runtime.
- [Post-validation fix 2026-03-31] Un test unitaire de non-régression couvre explicitement le cas `cancel_at != null && cancel_at_period_end == false`.

### File List

- `_bmad-output/implementation-artifacts/61-65-coherence-plan-effectif-upgrade-immediat-downgrade-cancel-echeance.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/stripe_billing_profile_service.py`
- `backend/app/tests/unit/test_stripe_billing_profile_service_61_65.py`
- `backend/app/api/v1/routers/billing.py`
- `backend/app/services/stripe_customer_portal_service.py`
- `frontend/src/api/billing.ts`
- `frontend/src/i18n/settings.ts`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/tests/SubscriptionSettings.test.tsx`
