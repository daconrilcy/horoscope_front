# Story 61.55 : Essais gratuits et premier paiement — états Stripe réels

Status: done

## Story

En tant qu'utilisateur authentifié qui souscrit à un abonnement SaaS,
je veux que le backend et le produit interprètent correctement les états réels d'un abonnement Stripe pendant l'essai gratuit et lors du premier paiement,
afin que l'accès produit, les écrans de retour, le self-service billing et la réconciliation webhook reflètent fidèlement la réalité Stripe, sans réduire la situation à un simple booléen `paid / unpaid`.

---

## Contexte

Les stories 61.52 à 61.54 ont mis en place le Customer Portal, les flows self-service et la fiscalité MVP. Il reste maintenant à traiter la phase ambiguë du démarrage d'un abonnement : quand il y a un essai gratuit ou quand le premier paiement n'est pas immédiatement confirmé.

Stripe distingue plusieurs statuts : `trialing`, `active`, `incomplete`, `incomplete_expired`, `past_due`, `canceled`, `unpaid`, `paused`. Cette story ne change pas la source de vérité (Stripe), mais explicite le mapping statut → accès produit, ajoute la configuration trial dans Checkout, couvre les événements webhook manquants, et met à jour l'UX de retour.

**Bonne nouvelle : la base est déjà en place.** Voir Dev Notes pour ce qui existe vs ce qui reste à faire.

---

## Acceptance Criteria

**AC1 — Le modèle billing canonique ne réduit plus l'abonnement à `paid / unpaid`**

* [x] Une décision explicite est documentée dans `docs/billing-trials-and-first-payment.md` : le backend reconnaît au minimum les statuts Stripe `trialing`, `active`, `incomplete`, `incomplete_expired`, `past_due`, `canceled`, `unpaid` et `paused`
* [x] La documentation précise le sens produit attendu de chacun de ces statuts
* [x] Toute logique locale basée sur un booléen implicite du type `is_paid` ou `paid/unpaid only` est exclue pour la décision d'accès produit
* [x] Le document précise explicitement que `trialing` n'est pas un "paiement réussi", mais un état ouvrant l'accès selon la politique produit choisie

**AC2 — La Checkout Session abonnement peut démarrer un essai gratuit de manière contrôlée**

* [x] La création de Checkout Session supporte une configuration d'essai gratuit MVP via `subscription_data.trial_period_days` ou absence de trial si non configuré
* [x] Le trial n'est ajouté que pour les plans autorisés par la politique produit
* [x] La durée de trial est validée côté configuration applicative avant d'atteindre Stripe
* [x] Aucun trial n'est "déduit" côté backend à partir d'un calcul maison de dates ; si trial il y a, il est demandé explicitement à Stripe via les paramètres Checkout prévus à cet effet

**AC3 — Le comportement "collecter un moyen de paiement pendant le trial ou non" est explicite**

* [x] Une décision MVP explicite est documentée :
  * Option A recommandée : conserver la collecte par défaut du moyen de paiement pendant Checkout
  * Option B dérogatoire : autoriser le trial sans moyen de paiement via `payment_method_collection="if_required"`
* [x] Si l'option B est activée, la Checkout Session inclut `payment_method_collection="if_required"`
* [x] Si l'option B n'est pas activée, ce paramètre n'est pas envoyé ou reste au comportement par défaut Stripe
* [x] Le document décrit clairement la conséquence produit : sans carte collectée au départ, la fin d'essai peut conduire à `paused` ou `canceled` selon le paramétrage choisi
* [x] Seules les valeurs `always` et `if_required` sont acceptées en configuration pour `payment_method_collection` ; toute autre valeur est rejetée au démarrage de l'application

**AC4 — La fin d'essai sans moyen de paiement est gérée explicitement**

* [x] Si le MVP autorise les trials sans moyen de paiement, la Checkout Session envoie `subscription_data.trial_settings.end_behavior.missing_payment_method`
* [x] Seules les valeurs `cancel` et `pause` sont acceptées en configuration
* [x] La décision MVP entre `cancel` et `pause` est documentée
* [x] Si `pause` est choisi, la documentation précise qu'un abonnement `paused` ne génère pas d'invoices et peut être repris après ajout d'un moyen de paiement
* [x] Si `cancel` est choisi, la documentation précise qu'un nouvel abonnement devra être recréé si le client revient plus tard

**AC5 — Le premier paiement est interprété via les vrais statuts Stripe**

* [x] Lorsqu'un abonnement est créé et que le premier paiement nécessite une action client, échoue, ou reste en attente, le backend conserve l'état `incomplete` tel que renvoyé par Stripe
* [x] Le produit ne considère pas `checkout.session.completed` comme preuve suffisante d'activation définitive de l'abonnement
* [x] L'activation effective du plan payant intervient seulement quand la réconciliation Stripe le justifie, notamment après `invoice.paid` avec abonnement `active`
* [x] Si le premier paiement n'est pas confirmé dans la fenêtre Stripe et que l'abonnement bascule en `incomplete_expired`, cet état est persisté et traité comme un échec terminal d'activation
* [x] La documentation précise que `incomplete_expired` ne doit pas être assimilé à `canceled` ni à `past_due`

**AC6 — Le mapping "billing state Stripe → accès produit" est explicite**

* [x] Une table de vérité documentée décrit au minimum :
  * `trialing` → accès produit autorisé selon les features du trial
  * `active` → accès produit autorisé selon le plan payé
  * `incomplete` → accès payant non accordé tant que le premier paiement n'est pas confirmé
  * `incomplete_expired` → accès refusé, tentative à relancer par une nouvelle souscription
  * `past_due` → conservation du plan courant (grace period — comportement actuel)
  * `paused` → accès suspendu tant qu'aucun moyen de paiement n'a permis la reprise
  * `canceled` / `unpaid` → accès révoqué (plan `free`)
* [x] Le mapping est exploitable par le runtime d'entitlements déjà mis en place en 61.7–61.51
* [x] Le mapping ne dépend pas d'un wording frontend ni d'un nom de price Stripe

**AC7 — Le webhook reste la source de vérité de transition d'état**

* [x] Le traitement webhook conserve ou étend la prise en charge des transitions utiles au démarrage d'abonnement et à la fin d'essai
* [x] Les événements déjà retenus restent la base de vérité : `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `customer.subscription.paused`, `customer.subscription.resumed`, `customer.subscription.trial_will_end`, `invoice.paid`, `invoice.payment_action_required`, `invoice.payment_failed`
* [x] La logique de réconciliation persiste les changements de statut Stripe pertinents dans le modèle local canonique
* [x] Aucun polling applicatif ad hoc n'est introduit comme mécanisme principal de vérité

**AC8 — UX de retour et self-service cohérents avec les états de démarrage**

* [x] La page retour succès billing ne présente pas systématiquement le paiement comme "réussi"
* [x] Si l'abonnement est en `trialing`, l'interface indique que l'essai est démarré
* [x] Si l'abonnement est en `incomplete` ou si le paiement initial requiert une action supplémentaire, l'interface indique que l'activation est en attente
* [x] Si l'abonnement est `active`, l'interface confirme l'activation
* [x] Si le trial se termine sans moyen de paiement et que le projet choisit `pause`, le Customer Portal permet de reprendre l'abonnement après ajout d'un moyen de paiement

**AC9 — Rappels de fin d'essai cadrés**

* [x] La documentation précise que `customer.subscription.trial_will_end` est émis trois jours avant la fin de trial, ou au déclenchement si le trial dure moins de trois jours
* [x] Le MVP documente ce qui est fait avec cet événement (audit log uniquement dans cette story)
* [x] Si le projet repose sur les emails Stripe, la documentation rappelle que les emails de rappel d'essai ne sont pas envoyés en sandbox

**AC10 — Audit enrichi**

* [x] L'audit de création Checkout inclut les informations trial utiles : `trial_enabled`, `trial_period_days` éventuel, `payment_method_collection`, `missing_payment_method_behavior`
* [x] Les audits webhook rendent visible les transitions clés au démarrage d'abonnement : `trialing`, `incomplete`, `active`, `incomplete_expired`, `paused`, `past_due`
* [x] Les codes d'erreur billing existants restent homogènes avec les stories précédentes

**AC11 — Tests**

* [x] Test unitaire : Checkout Session avec trial activé ajoute `subscription_data.trial_period_days`
* [x] Test unitaire : sans trial, aucun champ trial n'est envoyé
* [x] Test unitaire : `payment_method_collection="if_required"` seulement quand la config l'active
* [x] Test unitaire : validation stricte de la config `missing_payment_method_behavior` (`pause|cancel` uniquement)
* [x] Test unitaire : validation stricte de la config `payment_method_collection` (`always|if_required` uniquement)
* [x] Test unitaire : mapping canonique `trialing/active/incomplete/incomplete_expired/past_due/paused/canceled/unpaid` via `derive_entitlement_plan`
* [x] Test d'intégration : création Checkout trial
* [x] Test d'intégration : webhook `customer.subscription.created` avec statut `incomplete`
* [x] Test d'intégration : webhook `invoice.paid` faisant converger vers activation
* [x] Test d'intégration : webhook `invoice.payment_action_required` ou `invoice.payment_failed` sur première facture conservant un état non actif
* [x] Test d'intégration : webhook `customer.subscription.trial_will_end`
* [x] Test d'intégration : webhook `customer.subscription.paused` et `customer.subscription.resumed`

---

## Tasks / Subtasks

* [ ] **Ajouter la configuration trial MVP dans `config.py`** (AC: 2, 3, 4, 10, 11)
  * [ ] Ajouter après les vars 61.54 (ligne ~354 de `config.py`) : `STRIPE_TRIAL_ENABLED`, `STRIPE_TRIAL_PERIOD_DAYS`, `STRIPE_PAYMENT_METHOD_COLLECTION`, `STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR`
  * [ ] Ajouter la validation `missing_payment_method_behavior` dans une méthode `_parse_` similaire à `_parse_stripe_checkout_billing_address_collection` — rejeter toute valeur hors `pause|cancel`
  * [ ] Ajouter la validation `payment_method_collection` dans une méthode `_parse_stripe_payment_method_collection()` dédiée — rejeter toute valeur hors `always|if_required`
  * [ ] Documenter ces variables dans `backend/.env.example`

* [ ] **Étendre `StripeCheckoutService.create_checkout_session`** (AC: 2, 3, 4, 10, 11)
  * [ ] Ajouter 3 nouveaux paramètres : `trial_enabled: bool = False`, `trial_period_days: int | None = None`, `payment_method_collection: str = "always"`, `missing_payment_method_behavior: str | None = None`
  * [ ] Injecter `subscription_data["trial_period_days"]` si `trial_enabled` et `trial_period_days > 0`
  * [ ] Injecter `payment_method_collection="if_required"` si la config l'exige (option B uniquement)
  * [ ] Injecter `subscription_data["trial_settings"]["end_behavior"]["missing_payment_method"]` si trial + option B
  * [ ] Conserver tous les paramètres existants (fiscalité, customer portal compatibility)

* [ ] **Mettre à jour l'endpoint `POST /v1/billing/stripe-checkout-session`** (AC: 2, 3, 4, 8, 10)
  * [ ] Passer les 4 nouveaux paramètres depuis `settings`
  * [ ] Enrichir le `details` de l'audit succès avec `trial_enabled`, `trial_period_days`, `payment_method_collection`, `missing_payment_method_behavior`

* [ ] **Étendre `StripeWebhookService`** (AC: 5, 7, 9, 10, 11)
  * [ ] Ajouter `customer.subscription.paused`, `customer.subscription.resumed`, `customer.subscription.trial_will_end` au dispatch `handle_event()`
  * [ ] Étendre `_resolve_user_id()` pour ces 3 nouveaux types (même logique que `customer.subscription.created` : lookup par `customer` → `stripe_customer_id`)
  * [ ] Vérifier que `update_from_event_payload` persiste correctement `paused`, `trialing`, `incomplete`, `incomplete_expired` (déjà implémenté — valider uniquement)

* [ ] **Mettre à jour l'UX de retour billing** (AC: 8)
  * [ ] Étendre `BillingTranslation` et `billingData` dans `frontend/src/i18n/billing.ts` — ajouter des clés `subscriptionTrialing`, `subscriptionPending`, `subscriptionActive` (messages neutres sans prétendre au paiement réussi)
  * [ ] Mettre à jour `BillingSuccessPage.tsx` : après retour de Checkout, afficher un message adapté (neutraliser "paiement réussi" → "souscription soumise" / "essai démarré" selon statut récupéré via `GET /v1/billing/subscription`)

* [ ] **Créer la documentation dédiée** (AC: 1 à 9)
  * [ ] Créer `docs/billing-trials-and-first-payment.md`
  * [ ] Documenter la politique MVP trial, le mapping de statuts, la stratégie UX / ops, les rappels de fin d'essai, le triptyque Dashboard requis

* [ ] **Étendre les tests unitaires et d'intégration** (AC: 11)
  * [ ] Tests unitaires dans `backend/app/tests/unit/test_stripe_checkout_service.py`
  * [ ] Tests unitaires `derive_entitlement_plan` dans `backend/app/tests/unit/test_stripe_billing_profile_service.py`
  * [ ] Tests d'intégration dans `backend/app/tests/integration/test_stripe_checkout_api.py`
  * [ ] Tests d'intégration webhook dans `backend/app/tests/integration/test_stripe_webhook_api.py`

---

## Dev Notes

### Ce qui EXISTE déjà — NE PAS réinventer

**Le modèle DB est déjà correct :**
- `StripeBillingProfileModel.subscription_status` → `String(64)`, commentaire dans le modèle : `trialing|active|past_due|canceled|unpaid|paused|incomplete|etc.` — **aucune migration DB nécessaire**
- Fichier : `backend/app/infra/db/models/stripe_billing.py`

**`derive_entitlement_plan()` est déjà correct :**
```python
# backend/app/services/stripe_billing_profile_service.py (lignes 30-55)
def derive_entitlement_plan(subscription_status, stripe_price_id, current_entitlement="free"):
    if subscription_status in ("active", "trialing"):   # → plan mappé
        ...
    if subscription_status == "past_due":               # → grace period, conserve l'entitlement
        return current_entitlement
    # canceled, unpaid, incomplete, incomplete_expired, paused, None → free
    return "free"
```
Le mapping AC6 est **déjà implémenté**. Ajouter un test unitaire pour `incomplete` et `incomplete_expired` (probablement déjà couvert, vérifier avant d'ajouter des doublons).

**`update_from_event_payload()` persiste déjà `subscription_status` :**
```python
# backend/app/services/stripe_billing_profile_service.py (lignes 190-193)
if data_obj.get("object") == "subscription":
    profile.stripe_subscription_id = data_obj.get("id")
    profile.subscription_status = data_obj.get("status")  # ← tous les statuts Stripe
```
Aucune modification nécessaire dans cette méthode.

**Le webhook supporte déjà :**
```python
# backend/app/services/stripe_webhook_service.py (lignes 72-81)
if event_type in (
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.updated",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.payment_action_required",
):
```

**`checkout.session.completed` n'active pas abusivement :** Le flow passe par `update_from_event_payload` qui lit `data_obj.object == "subscription"` — or `checkout.session.completed` a `object == "checkout.session"`, donc le statut d'abonnement n'est pas mis à jour depuis cet événement. L'activation réelle vient de `customer.subscription.created` ou `invoice.paid`.

**L'endpoint GET `/v1/billing/subscription` existe déjà** (ligne 374 de `billing.py`) et retourne le statut courant via `BillingService.get_subscription_status()`. La `BillingSuccessPage.tsx` peut l'appeler après le retour de Checkout pour afficher le bon message.

---

### Ce qui DOIT être ajouté

#### 1. Configuration trial dans `config.py`

Ajouter **après** le bloc 61.54 (lignes ~347-353) :

```python
# Story 61.55 - Trial Configuration
self.stripe_trial_enabled = os.getenv("STRIPE_TRIAL_ENABLED", "false").strip().lower() == "true"
self.stripe_trial_period_days = int(os.getenv("STRIPE_TRIAL_PERIOD_DAYS", "0").strip() or "0")
self.stripe_payment_method_collection = (
    self._parse_stripe_payment_method_collection()
)
self.stripe_trial_missing_payment_method_behavior = (
    self._parse_trial_missing_payment_method_behavior()
)
```

Méthodes de validation :
```python
def _parse_stripe_payment_method_collection(self) -> str:
    value = os.getenv("STRIPE_PAYMENT_METHOD_COLLECTION", "always").strip()
    if value not in ("always", "if_required"):
        raise ValueError(
            f"STRIPE_PAYMENT_METHOD_COLLECTION must be 'always' or 'if_required', got '{value}'"
        )
    return value

def _parse_trial_missing_payment_method_behavior(self) -> str | None:
    value = os.getenv("STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR", "").strip()
    if not value:
        return None
    if value not in ("pause", "cancel"):
        raise ValueError(
            f"STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR must be 'pause' or 'cancel', got '{value}'"
        )
    return value
```

Dans `backend/.env.example` :
```
STRIPE_TRIAL_ENABLED=false
STRIPE_TRIAL_PERIOD_DAYS=0
STRIPE_PAYMENT_METHOD_COLLECTION=always
# STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR=cancel
```

#### 2. Extension de `StripeCheckoutService.create_checkout_session`

Shape cible (ajouter après les 3 params 61.54) :
```python
@staticmethod
def create_checkout_session(
    db: Session,
    *,
    user_id: int,
    user_email: str | None,
    plan: str,
    success_url: str,
    cancel_url: str,
    billing_address_collection: str = "auto",      # 61.54
    automatic_tax_enabled: bool = False,            # 61.54
    tax_id_collection_enabled: bool = False,        # 61.54
    trial_enabled: bool = False,                    # 61.55 NEW
    trial_period_days: int | None = None,           # 61.55 NEW
    payment_method_collection: str = "always",      # 61.55 NEW
    missing_payment_method_behavior: str | None = None,  # 61.55 NEW
) -> str:
    ...
    # Injecter après les blocs 61.54 existants :
    if trial_enabled and trial_period_days and trial_period_days > 0:
        params["subscription_data"]["trial_period_days"] = trial_period_days

    if payment_method_collection == "if_required":
        params["payment_method_collection"] = "if_required"

    if trial_enabled and payment_method_collection == "if_required" and missing_payment_method_behavior:
        params["subscription_data"].setdefault("trial_settings", {})
        params["subscription_data"]["trial_settings"]["end_behavior"] = {
            "missing_payment_method": missing_payment_method_behavior
        }
```

#### 3. Événements webhook manquants

Dans `StripeWebhookService.handle_event()`, étendre le tuple de dispatch :
```python
if event_type in (
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.paused",       # NEW 61.55
    "customer.subscription.resumed",      # NEW 61.55
    "customer.subscription.trial_will_end",  # NEW 61.55
    "customer.updated",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.payment_action_required",
):
```

Dans `_resolve_user_id()`, étendre le bloc subscription :
```python
if event_type in (
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.paused",       # NEW
    "customer.subscription.resumed",      # NEW
    "customer.subscription.trial_will_end",  # NEW
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.payment_action_required",
):
```

**Note :** `customer.subscription.trial_will_end` doit être dispatché, résolu côté user et audité, mais ne doit pas être interprété comme une transition d'entitlement à lui seul. Cet événement sert principalement d'alerte de fin d'essai émise quelques jours avant l'échéance ; le statut produit final continue d'être dérivé des vrais statuts d'abonnement et des événements de paiement Stripe (`invoice.paid`, `customer.subscription.updated`).

#### 4. UX de retour billing

**`frontend/src/i18n/billing.ts`** — étendre `BillingTranslation.success` :
```typescript
success: {
  // ... existant
  trialStarted: string       // "Essai gratuit démarré"
  activationPending: string  // "Activation en cours de confirmation"
  subscriptionActive: string // "Abonnement activé"
}
```

**`frontend/src/pages/billing/BillingSuccessPage.tsx`** — appeler `GET /v1/billing/subscription` au montage et afficher le message adapté selon `subscription_status` :
- `trialing` → `t.trialStarted`
- `incomplete` ou `null` → `t.activationPending` (défaut pendant l'attente webhook)
- `active` → `t.subscriptionActive`

Le composant garde un état `loading` pendant la requête, puis affiche le message approprié. Pas de polling — un seul appel suffit (le webhook aura généralement déjà traité avant que l'utilisateur lise la page).

---

### Mapping d'erreur — inchangé

| `error.code`                  | HTTP |
|-------------------------------|------|
| `stripe_unavailable`          | 503  |
| `stripe_api_error`            | 502  |
| `plan_price_not_configured`   | 422  |
| `invalid_checkout_request`    | 422  |

### `paused` au sens Stripe ≠ "pause payment collection"

Le statut `subscription.status = "paused"` (couvert par cette story) intervient uniquement quand un essai se termine sans moyen de paiement et que `trial_settings.end_behavior.missing_payment_method = "pause"` a été configuré. Un abonnement `paused` ne génère pas de factures et peut être repris après ajout d'un moyen de paiement.

Ne pas confondre avec la fonctionnalité Stripe "pause payment collection" (`pause_collection`) qui met en veille la collecte sur un abonnement actif **tout en maintenant** `subscription.status = "active"` et en continuant à générer des invoices. Ce second cas est hors périmètre de cette story.

### Pourquoi `checkout.session.completed` ne suffit pas

Stripe peut créer un abonnement en `incomplete` si le premier paiement nécessite une authentification supplémentaire (3DS), échoue, ou reste en traitement. Le flow `checkout.session.completed` → `customer.subscription.created` (status=`incomplete`) → `invoice.paid` (status=`active`) est le chemin réel. Ne jamais déduire l'activation depuis le seul retour navigateur.

### Hors périmètre explicite

* Coupons / promotions complexes sur trials
* Subscription schedules
* Dunning avancé au-delà des comportements Stripe standards
* Système maison de relance email
* Réactivation manuelle custom hors Customer Portal
* Entitlements Stripe natifs comme source directe de vérité produit
* Refonte totale UX billing frontend

### Project Structure Notes

- Config : `backend/app/core/config.py` — ajouter après le bloc 61.54 (~ligne 354)
- Env : `backend/.env.example`
- Service Checkout : `backend/app/services/stripe_checkout_service.py`
- Service Webhook : `backend/app/services/stripe_webhook_service.py`
- Service BillingProfile : `backend/app/services/stripe_billing_profile_service.py` — `derive_entitlement_plan` à valider/tester, pas à modifier
- Endpoint billing : `backend/app/api/v1/routers/billing.py` (lignes ~915-941)
- Modèle DB : `backend/app/infra/db/models/stripe_billing.py` — aucune migration DB nécessaire
- Tests unitaires : `backend/app/tests/unit/test_stripe_checkout_service.py`
- Tests unitaires billing profile : `backend/app/tests/unit/test_stripe_billing_profile_service.py`
- Tests intégration checkout : `backend/app/tests/integration/test_stripe_checkout_api.py`
- Tests intégration webhook : `backend/app/tests/integration/test_stripe_webhook_api.py`
- i18n billing : `frontend/src/i18n/billing.ts`
- Page succès : `frontend/src/pages/billing/BillingSuccessPage.tsx`
- CSS retour billing : `frontend/src/pages/billing/billing-return.css`
- Nouvelle doc : `docs/billing-trials-and-first-payment.md`

### Pattern de test unitaire (checkout service)

```python
# test_create_checkout_session_with_trial
call_args = mock_stripe_client.checkout.sessions.create.call_args
params = call_args[1]["params"] if "params" in call_args[1] else call_args[0][0]
assert params["subscription_data"]["trial_period_days"] == 14

# test_create_checkout_session_without_trial
assert "trial_period_days" not in params.get("subscription_data", {})

# test_payment_method_collection_if_required
assert params["payment_method_collection"] == "if_required"

# test_missing_payment_method_behavior
assert params["subscription_data"]["trial_settings"]["end_behavior"]["missing_payment_method"] == "cancel"
```

### Pattern de test unitaire (derive_entitlement_plan — vérifier les cas manquants)

```python
# Ces cas doivent déjà être couverts — vérifier avant d'ajouter des doublons
assert derive_entitlement_plan("trialing", "price_basic_123") == "basic"
assert derive_entitlement_plan("incomplete", "price_basic_123") == "free"
assert derive_entitlement_plan("incomplete_expired", "price_basic_123") == "free"
assert derive_entitlement_plan("paused", "price_basic_123") == "free"
```

### Pattern de test d'intégration (webhook)

```python
# customer.subscription.created avec status=incomplete
payload = build_subscription_event("customer.subscription.created", status="incomplete")
response = client.post("/v1/billing/stripe/webhook", ...)
assert response.status_code == 200
# Vérifier que profile.subscription_status == "incomplete"
# Vérifier que profile.entitlement_plan == "free"

# customer.subscription.paused
payload = build_subscription_event("customer.subscription.paused", status="paused")
...
# Vérifier que profile.subscription_status == "paused"
# Vérifier que profile.entitlement_plan == "free"
```

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Code review menée sur le commit d'implémentation initial.
- Correction d'un écart critique : `GET /v1/billing/subscription` n'exposait pas `subscription_status`, ce qui empêchait l'UX de distinguer `trialing`, `incomplete` et `active`.
- Suppression du contournement `is_trial=true` injecté dans `success_url` Stripe ; la page succès dépend maintenant uniquement du statut API.
- Couverture de test complétée pour `customer.subscription.resumed` et pour le contrat API `subscription_status`.

### File List

- `backend/app/core/config.py`
- `backend/.env.example`
- `backend/app/services/stripe_checkout_service.py`
- `backend/app/services/billing_service.py`
- `backend/app/api/v1/routers/billing.py`
- `backend/app/services/stripe_webhook_service.py`
- `backend/app/tests/unit/test_billing_service.py`
- `frontend/src/i18n/billing.ts`
- `frontend/src/i18n/settings.ts`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `docs/billing-trials-and-first-payment.md` (new)
- `backend/app/tests/unit/test_stripe_trial_config.py` (new)
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/unit/test_stripe_webhook_service.py`
- `backend/app/tests/integration/test_billing_api.py`
- `backend/app/tests/integration/test_stripe_checkout_api.py`
- `backend/app/tests/integration/test_stripe_webhook_api.py`
- `frontend/src/tests/BillingSuccessPage.test.tsx` (new)

### Change Log

- Added trial configuration to `Settings` and `.env.example`.
- Extended `StripeCheckoutService.create_checkout_session` to handle trial parameters without mutating the configured `success_url`.
- Updated `POST /v1/billing/stripe-checkout-session` to pass trial settings and enrich audit logs.
- Added `customer.subscription.paused/resumed/trial_will_end` to `StripeWebhookService`.
- Exposed raw `subscription_status` in `GET /v1/billing/subscription` for billing return UX.
- Added trial and paused status translations to `billing.ts` and `settings.ts`.
- Updated `BillingSuccessPage.tsx` to rely on API status only, with neutral messaging for `trialing`, `incomplete`, and `active`.
- Created `docs/billing-trials-and-first-payment.md` with status mapping and policy.
- Added review follow-up tests for the API contract and resumed webhook coverage.
