# Story 61.54 : Fiscalité MVP et factures Stripe — Stripe Tax, tax IDs et historique de facturation

Status: done

## Story

En tant qu'utilisateur authentifié qui souscrit à un abonnement SaaS,
je veux que la taxe applicable soit calculée correctement et que mes factures Stripe soient exploitables,
afin que le produit puisse vendre proprement dans un périmètre géographique défini sans logique fiscale codée à la main dans le backend.

---

## Contexte

Les stories 61.52 et 61.53 ont mis en place le self-service billing via Stripe Customer Portal. La présente story constitue l'étape suivante : **activer la fiscalité indirecte MVP** en étendant uniquement la Checkout Session d'abonnement existante (story 61.3) pour supporter `automatic_tax`, la collecte d'adresse de facturation, et optionnellement la collecte de tax ID B2B.

La source de vérité fiscale reste Stripe. Le backend ne calcule aucune taxe.

---

## Acceptance Criteria

**AC1 — Décision fiscale MVP explicitement documentée**

* [x] Une décision explicite est documentée dans `docs/billing-tax-and-invoicing-mvp.md` :
  * Option A (recommandée) : `STRIPE_TAX_ENABLED=true`
  * Option B (dérogatoire) : `STRIPE_TAX_ENABLED=false` avec périmètre géographique restreint explicite
* [x] La documentation précise : pays autorisés au lancement, vente B2B oui/non, tax ID activé oui/non, Stripe source de vérité fiscale

**AC2 — Checkout Session abonnement compatible fiscalité**

* [x] Si `STRIPE_TAX_ENABLED=true`, la Checkout Session est créée avec `automatic_tax={"enabled": True}`
* [x] Si `STRIPE_TAX_ENABLED=false`, `automatic_tax` n'est **pas** inclus dans les params Stripe
* [x] La session reste `mode="subscription"`, `client_reference_id`, `metadata` et `subscription_data.metadata` inchangés
* [x] Aucun calcul de TVA/VAT/GST dans le backend applicatif
* [x] La documentation précise que `automatic_tax` côté code ne suffit pas seul : les products/prices Stripe utilisés par le checkout doivent avoir un `tax_code` et un `tax_behavior` cohérents (`inclusive` ou `exclusive`), configurés dans le Dashboard Stripe ou sur les objets Product/Price — c'est une prérequis Dashboard, pas du code applicatif

**AC3 — Collecte d'adresse de facturation**

* [x] Le paramètre `billing_address_collection` est systématiquement inclus dans les params Checkout (valeur `"auto"` par défaut, configurable via `STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION`)
* [x] Seules les valeurs `"auto"` et `"required"` sont acceptées — toute autre valeur est rejetée à la validation de config au démarrage (ou documentée comme invalide) et ne doit jamais atteindre Stripe
* [x] Quand `STRIPE_TAX_ENABLED=true`, Stripe collecte automatiquement via Checkout les informations minimales de localisation nécessaires au calcul fiscal ; `"auto"` suffit techniquement, `"required"` est un choix produit plus strict exposant l'adresse complète à l'utilisateur

**AC4 — Collecte optionnelle du tax ID client (B2B)**

* [x] Si `STRIPE_TAX_ID_COLLECTION_ENABLED=true`, la Checkout Session inclut `tax_id_collection={"enabled": True}`
* [x] Si `STRIPE_TAX_ID_COLLECTION_ENABLED=true` **et** que le customer Stripe existe déjà (`stripe_customer_id` non null), ajouter `customer_update={"name": "auto", "address": "auto"}` pour permettre la mise à jour lors du checkout — **effet de bord assumé** : les valeurs nom et adresse saisies pendant le checkout remplaceront les valeurs précédemment stockées sur le customer Stripe ; ce comportement est documenté et voulu pour permettre la collecte du tax ID B2B
* [x] Si `STRIPE_TAX_ID_COLLECTION_ENABLED=false`, ces paramètres ne sont **pas** inclus

**AC5 — Factures Stripe exploitables sans refonte applicative**

* [x] Les subscriptions Stripe continuent de générer les invoices Stripe (aucun changement requis)
* [x] Le MVP s'appuie sur les surfaces Stripe d'invoicing (Customer Portal, Hosted Invoice Page) sans endpoint applicatif dédié — la visibilité effective dépend de la configuration `invoice_history` dans la config portail (cf. AC7)
* [x] Aucun endpoint `GET /v1/billing/invoices` n'est créé dans cette story
* [x] Aucun stockage local de PDF de facture

**AC6 — Tax IDs sur les factures et tax registrations**

* [x] La documentation précise la configuration Dashboard Stripe requise pour les account tax IDs
* [x] La documentation précise qu'un invoice finalisé ne peut pas être modifié a posteriori pour corriger un tax ID
* [x] La documentation précise que Stripe Tax nécessite au minimum une **tax registration** configurée dans le Dashboard Stripe pour le périmètre géographique MVP — sans registration, `automatic_tax=true` est accepté par l'API mais ne calcule aucune taxe ; le dev ne peut pas vérifier ce point dans le code applicatif, c'est une action Dashboard pré-lancement obligatoire

**AC7 — Customer Portal factures/billing info**

* [x] La documentation confirme que `invoice_history` doit être activé dans la configuration portail Stripe (Dashboard)
* [x] La documentation confirme que les billing information / tax IDs client sont activables dans la config portail si MVP B2B

**AC8 — Pas de logique fiscale canonique locale**

* [x] Aucune table locale de taux TVA/VAT/GST
* [x] Aucun moteur de règle fiscale par pays
* [x] Aucun recalcul fiscal sur webhook
* [x] Aucun montant de taxe "canonique" stocké comme vérité applicative

**AC9 — Erreurs et dégradation contrôlée**

* [x] Erreur Stripe indisponible → `503 stripe_unavailable` (comportement existant conservé)
* [x] Erreur API Stripe → `502 stripe_api_error` (comportement existant conservé)
* [x] Payload d'erreur homogène avec les endpoints billing existants

**AC10 — Audit enrichi**

* [x] Audit succès `stripe_checkout_session_created` : `details` enrichi avec `automatic_tax_enabled: bool` et `tax_id_collection_enabled: bool`
* [x] Audit échec : code erreur cohérent (comportement existant)

**AC11 — Tests**

* [x] Test unitaire : Checkout Session avec `automatic_tax[enabled]=true` quand `stripe_tax_enabled=True`
* [x] Test unitaire : Checkout Session sans `automatic_tax` quand `stripe_tax_enabled=False`
* [x] Test unitaire : `billing_address_collection` toujours présent dans les params
* [x] Test unitaire : `tax_id_collection[enabled]=true` et `customer_update` si `tax_id_collection_enabled=True` + customer existant
* [x] Test unitaire : `tax_id_collection` absent si `tax_id_collection_enabled=False`
* [x] Test unitaire : `customer_update` absent si pas de `stripe_customer_id` (nouveau customer)
* [x] Test d'intégration : `POST /v1/billing/stripe-checkout-session` avec fiscalité activée — vérifier `automatic_tax` dans les params Stripe
* [x] Test d'intégration : non-régression — session abonnement classique (fiscalité désactivée) toujours fonctionnelle
* [x] Test d'intégration : audit enrichi avec `automatic_tax_enabled`
* [x] Test d'intégration : 401, 503, 502 (non-régression)

---

## Tasks / Subtasks

* [x] **Ajouter la configuration fiscale MVP dans `config.py`** (AC: 1, 2, 3, 4, 9)
  * [x] Ajouter après la ligne `stripe_portal_configuration_id` (ligne ~335)
  * [x] Documenter ces 3 variables dans `backend/.env.example`

* [x] **Étendre `StripeCheckoutService.create_checkout_session`** (AC: 2, 3, 4, 9)
  * [x] Ajouter 3 nouveaux paramètres à la signature
  * [x] Ajouter `"billing_address_collection": billing_address_collection` dans `params`
  * [x] Si `automatic_tax_enabled` : ajouter `"automatic_tax": {"enabled": True}` dans `params`
  * [x] Si `tax_id_collection_enabled` : ajouter `"tax_id_collection": {"enabled": True}` dans `params` ; si `profile.stripe_customer_id` est défini, ajouter aussi `"customer_update": {"name": "auto", "address": "auto"}`
  * [x] Conserver inchangés : `mode`, `line_items`, `success_url`, `cancel_url`, `client_reference_id`, `metadata`, `subscription_data`, `customer` / `customer_email`

* [x] **Mettre à jour l'endpoint `POST /stripe-checkout-session` dans `billing.py`** (AC: 2, 3, 4, 10)
  * [x] Passer les 3 nouveaux paramètres depuis `settings`
  * [x] Enrichir le `details` de l'audit succès

* [x] **Documenter la configuration Stripe Dashboard** (AC: 1, 5, 6, 7)
  * [x] Créer `docs/billing-tax-and-invoicing-mvp.md`

* [x] **Étendre les tests unitaires** dans `backend/app/tests/unit/test_stripe_checkout_service.py` (AC: 11)
  * [x] `test_create_checkout_session_with_automatic_tax`
  * [x] `test_create_checkout_session_without_automatic_tax`
  * [x] `test_create_checkout_session_billing_address_collection_present`
  * [x] `test_create_checkout_session_tax_id_collection_with_existing_customer`
  * [x] `test_create_checkout_session_tax_id_collection_new_customer`
  * [x] `test_create_checkout_session_no_tax_id_collection`

* [x] **Étendre les tests d'intégration** dans `backend/app/tests/integration/test_stripe_checkout_api.py` (AC: 11)
  * [x] `test_stripe_checkout_with_tax_enabled`
  * [x] `test_stripe_checkout_tax_disabled_no_regression`
  * [x] `test_stripe_checkout_audit_enriched_with_tax_flags`

---

## Dev Notes

### Position dans l'Epic 61

```text
61-1 (done)  : stripe_billing_profiles + service pivot
61-2 (done)  : SDK Stripe + config + secrets
61-3 (done)  : POST /v1/billing/stripe-checkout-session  ← modifié ici
61-4 à 61-6 (done) : webhook Stripe signé + sélection événements
61-7 à 61-51 (done) : entitlements canoniques + clôture
61-52 (done) : Customer Portal Session
61-53 (done) : portal flows dédiés update / cancel
61-54 (cette story) : fiscalité MVP et factures Stripe
```

### Ce que cette story modifie — périmètre exact

**1 seul fichier de service modifié** : `backend/app/services/stripe_checkout_service.py`
**1 seul endpoint modifié** : `billing.py` ligne ~893 `create_stripe_checkout_session`
**1 fichier config modifié** : `backend/app/core/config.py` — 3 nouvelles vars après la ligne ~335
**1 doc créée** : `docs/billing-tax-and-invoicing-mvp.md`
**2 fichiers de tests étendus** : unit + intégration checkout

### Extension de `create_checkout_session` — shape cible

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
    billing_address_collection: str = "auto",
    automatic_tax_enabled: bool = False,
    tax_id_collection_enabled: bool = False,
) -> str:
    # ... validation inchangée (client Stripe, price_id, profile) ...

    params: dict = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": str(user_id),
        "metadata": {"app_user_id": str(user_id)},
        "subscription_data": {"metadata": {"app_user_id": str(user_id), "plan": plan}},
        "billing_address_collection": billing_address_collection,
    }

    if profile.stripe_customer_id:
        params["customer"] = profile.stripe_customer_id
    elif user_email:
        params["customer_email"] = user_email
    else:
        raise StripeCheckoutServiceError(...)

    if automatic_tax_enabled:
        params["automatic_tax"] = {"enabled": True}

    if tax_id_collection_enabled:
        params["tax_id_collection"] = {"enabled": True}
        if profile.stripe_customer_id:
            params["customer_update"] = {"name": "auto", "address": "auto"}

    try:
        session = client.checkout.sessions.create(params=params)
        return session.url
    except stripe.StripeError as error:
        ...
```

### Configuration Stripe — variables à ajouter

Ajouter dans `backend/app/core/config.py` **après** `self.stripe_portal_configuration_id` (ligne ~335) :

```python
self.stripe_tax_enabled = os.getenv("STRIPE_TAX_ENABLED", "false").strip().lower() == "true"
self.stripe_tax_id_collection_enabled = (
    os.getenv("STRIPE_TAX_ID_COLLECTION_ENABLED", "false").strip().lower() == "true"
)
self.stripe_checkout_billing_address_collection = os.getenv(
    "STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION", "auto"
).strip()
```

Dans `backend/.env.example`, ajouter :
```
STRIPE_TAX_ENABLED=false
STRIPE_TAX_ID_COLLECTION_ENABLED=false
STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION=auto
```

### Audit enrichi — détails attendus

Modifier dans `billing.py` l'appel `_record_audit_event` succès :

```python
details={
    "plan": parsed.plan,
    "automatic_tax_enabled": settings.stripe_tax_enabled,
    "tax_id_collection_enabled": settings.stripe_tax_id_collection_enabled,
}
```

L'audit d'échec (`stripe_checkout_session_failed`) reste inchangé.

### Mapping d'erreur — inchangé

| `error.code`                  | HTTP |
|-------------------------------|------|
| `stripe_unavailable`          | 503  |
| `stripe_api_error`            | 502  |
| `plan_price_not_configured`   | 422  |
| `invalid_checkout_request`    | 422  |

### Factures : aucun code backend requis pour le MVP

Le Customer Portal Stripe (déjà configuré en 61.52/61.53) expose nativement l'historique de facturation, le téléchargement PDF et la page de facture hébergée. Aucun endpoint `GET /v1/billing/invoices`, aucun proxy `hosted_invoice_url`, aucun stockage local de PDF.

### Triptyque obligatoire pour que Stripe Tax fonctionne réellement

L'activation applicative de `automatic_tax=true` ne suffit pas seule. Stripe Tax requiert les trois conditions suivantes, qui sont toutes des actions Dashboard / catalogue Stripe, pas du code applicatif :

1. **`automatic_tax[enabled]=true`** sur la Checkout Session — c'est ce que cette story code.
2. **`tax_code` et `tax_behavior`** cohérents sur les Product/Price utilisés — `tax_behavior` doit être `inclusive` ou `exclusive` (jamais `unspecified`) ; `tax_code` doit correspondre à la catégorie fiscale du service (ex. `txcd_10000000` pour un SaaS). Sans ce point, Stripe peut retourner une taxe nulle ou une erreur silencieuse.
3. **Tax registrations** configurées dans le Dashboard Stripe Taxes > Registrations — au moins une registration pour chaque juridiction fiscale où le produit vend. Sans registration, `automatic_tax=true` est accepté par l'API mais aucune taxe n'est calculée.

Ce triptyque doit être documenté dans `docs/billing-tax-and-invoicing-mvp.md` comme prérequis pré-lancement, et la checklist de mise en production doit inclure une vérification manuelle de ces trois points.

### Compatibilité avec `subscription_update` (61.53)

La story 61.53 note que les abonnements avec `tax_behavior` incompatible peuvent bloquer `subscription_update`. En activant `automatic_tax`, s'assurer que les prices Stripe exposés dans le portail ont un `tax_behavior` cohérent (`inclusive` ou `exclusive`). C'est une configuration Dashboard Stripe, pas du code applicatif.

### Hors périmètre explicite

* Déclarations fiscales et remittance hors Stripe
* Moteur fiscal interne multi-pays
* Validation juridique pays par pays
* Génération / stockage local de factures PDF
* Affichage applicatif custom des lignes de taxe
* Correction rétroactive des abonnements créés sans `automatic_tax`
* Endpoint `GET /v1/billing/invoices`
* Endpoint de réactivation d'abonnement (hors périmètre, cf. 61.53 AC7)

### Pattern de test unitaire à reproduire

S'appuyer sur `test_stripe_checkout_service.py` (61.3) comme base directe. Pour vérifier les nouveaux params :

```python
call_args = mock_stripe_client.checkout.sessions.create.call_args
params = call_args[1]["params"] if "params" in call_args[1] else call_args[0][0]
assert params["automatic_tax"]["enabled"] is True
assert params["billing_address_collection"] == "auto"
assert params["tax_id_collection"]["enabled"] is True
assert params["customer_update"] == {"name": "auto", "address": "auto"}
```

### Pattern de test d'intégration à reproduire

S'appuyer sur `test_stripe_checkout_api.py` (61.3) — mêmes helpers `_cleanup_tables`, `_register_user_with_role`, `clean_db`. Pour tester les flags fiscaux, patcher `app.core.config.settings` ou utiliser `monkeypatch` selon la convention du projet :

```python
with patch("app.api.v1.routers.billing.settings") as mock_settings:
    mock_settings.stripe_tax_enabled = True
    mock_settings.stripe_tax_id_collection_enabled = False
    mock_settings.stripe_checkout_billing_address_collection = "auto"
    mock_settings.stripe_checkout_success_url = "http://s"
    mock_settings.stripe_checkout_cancel_url = "http://c"
    # ... appel + vérification params
```

### Project Structure Notes

- Service Checkout : `backend/app/services/stripe_checkout_service.py`
- Endpoint billing : `backend/app/api/v1/routers/billing.py` (lignes ~882-999)
- Config Stripe : `backend/app/core/config.py` — ajouter après `stripe_portal_configuration_id` (~ligne 335)
- Env : `backend/.env.example`
- Tests unitaires : `backend/app/tests/unit/test_stripe_checkout_service.py`
- Tests intégration : `backend/app/tests/integration/test_stripe_checkout_api.py`
- Doc billing existante : `docs/billing-self-service-mvp.md` (créée en 61.52, ne pas supprimer)
- Nouvelle doc : `docs/billing-tax-and-invoicing-mvp.md` (à créer)

---

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Configuration fiscale MVP ajoutée à config.py et .env.example.
- StripeCheckoutService.create_checkout_session étendu avec automatic_tax, tax_id_collection et billing_address_collection.
- Endpoint POST /stripe-checkout-session mis à jour pour passer les nouveaux paramètres et enrichir l'audit.
- Documentation docs/billing-tax-and-invoicing-mvp.md créée.
- Tests unitaires et d'intégration ajoutés et vérifiés.
- Review AI post-implémentation: validation stricte de `STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION` ajoutée dans `Settings`.
- Review AI post-implémentation: documentation MVP complétée pour couvrir l'option B, `invoice_history`, les tax IDs de compte Stripe et les prérequis Dashboard.

### File List

- `backend/app/core/config.py`
- `backend/.env.example`
- `backend/app/services/stripe_checkout_service.py`
- `backend/app/api/v1/routers/billing.py`
- `docs/billing-tax-and-invoicing-mvp.md`
- `backend/app/tests/unit/test_stripe_checkout_service.py`
- `backend/app/tests/integration/test_stripe_checkout_api.py`
- `backend/app/tests/unit/test_settings.py`

### Change Log

- 2026-03-29: Mise en oeuvre initiale de la story 61.54.
- 2026-03-29: Ajout de la configuration fiscale.
- 2026-03-29: Extension du service StripeCheckoutService.
- 2026-03-29: Mise à jour de l'endpoint billing.
- 2026-03-29: Création de la documentation.
- 2026-03-29: Ajout et passage des tests.
- 2026-03-29: Code review AI puis correctifs sur validation de configuration et documentation MVP.

---

## Senior Developer Review (AI)

**Review Outcome:** Approved after fixes
**Review Date:** 2026-03-29

### Findings Identified During Review
- 🔴 Critical: 0
- 🟡 High: 1
- 🟠 Medium: 1
- 🟢 Low: 0

### Remaining Unresolved Issues
- 🔴 Critical: 0
- 🟡 High: 0
- 🟠 Medium: 0
- 🟢 Low: 0

### Action Items
* [x] [AI-Review][High] Valider `STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION` au démarrage pour empêcher toute valeur hors `auto|required` d’atteindre Stripe, conformément à l’AC3.
* [x] [AI-Review][Medium] Compléter `docs/billing-tax-and-invoicing-mvp.md` pour documenter explicitement l’option B, `invoice_history`, les billing information / tax IDs portail et les account tax IDs Stripe, conformément aux AC1, AC6 et AC7.
* [x] [AI-Review][Medium] Ajouter des tests unitaires `Settings` pour couvrir la validation de `STRIPE_CHECKOUT_BILLING_ADDRESS_COLLECTION`.

### Summary
La review a identifié un écart fonctionnel sur la validation de configuration et une documentation incomplète par rapport aux AC. Les écarts ont été corrigés, la couverture de tests a été étendue et la story est maintenant alignée avec son périmètre annoncé.

