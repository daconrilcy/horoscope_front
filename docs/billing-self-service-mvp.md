# MVP Billing Self-Service — Stripe Customer Portal

Ce document détaille l'implémentation du self-service billing via le **Stripe Customer Portal**.

## Architecture & Philosophie

L'application délègue la gestion avancée des abonnements (upgrade, downgrade, annulation, gestion des moyens de paiement, historique des factures) à l'interface hébergée par Stripe.

### Principes clés
1. **Source de vérité : Stripe**. Tout changement effectué dans le portail est propagé au backend via le **Webhook Stripe** existant.
2. **Snapshot local**. Le backend maintient un snapshot de l'état Stripe dans la table `stripe_billing_profiles`.
Ce snapshot est désormais la source canonique de lecture pour le runtime B2C dès qu'il est exploitable.
3. **Synchronisation asynchrone**. Le portail ne redirige pas vers un endpoint de "succès" qui synchronise l'état. C'est le webhook qui garantit la cohérence.
4. **MVP strictly limited**. Le backend ne propose pas d'endpoints `change-plan` ou `cancel-subscription` maison.

## Implémentation Backend

### Endpoint de Session Portal
`POST /v1/billing/stripe-customer-portal-session`

- **Authentification** : JWT obligatoire.
- **Vérification** : L'utilisateur doit avoir un profil Stripe existant avec un `stripe_customer_id`.
- **Réponse** : Retourne une URL de session à usage unique. Le frontend doit rediriger l'utilisateur vers cette URL.

### Configuration
- `STRIPE_PORTAL_RETURN_URL` : URL de retour après la fermeture du portail par l'utilisateur (défaut: `/settings/subscription`).
- `STRIPE_PORTAL_CONFIGURATION_ID` : **Obligatoire**. ID de configuration spécifique pour le portail créé dans le Dashboard Stripe.
  - *Note Story 61.64* : Cette configuration est désormais explicite pour garantir le comportement des upgrades avec prorata immédiat configuré dans Stripe.
  - Le démarrage de l'application échoue si `STRIPE_SECRET_KEY` est présente mais que `STRIPE_PORTAL_CONFIGURATION_ID` est absente.

## Portal Flows dédiés (Upgrade, Downgrade, Cancel)

En plus du portail générique, l'application expose des endpoints pour initier des intentions métier explicites. Ces flux utilisent le paramètre `flow_data` de l'API Stripe Portal Session.

### Endpoints de Session dédiés
1. **Update Subscription** : `POST /v1/billing/stripe-customer-portal-subscription-update-session`
   - Ouvre directement le flux de modification d'abonnement.
   - Nécessite un `stripe_subscription_id` actif sur le profil utilisateur.
2. **Cancel Subscription** : `POST /v1/billing/stripe-customer-portal-subscription-cancel-session`
   - Ouvre directement le flux d'annulation d'abonnement.
   - Nécessite un `stripe_subscription_id` actif sur le profil utilisateur.

### Configuration Stripe Dashboard requise
Pour que ces flux fonctionnent, une configuration de portail dédiée doit être créée dans le Dashboard Stripe. Cette configuration (référencée par `STRIPE_PORTAL_CONFIGURATION_ID`) doit impérativement inclure :
- **Subscription Update** activé.
- **Subscription Cancel** activé.
- Mode d'annulation sur **At period end** (recommandé pour le MVP).
- Les **prix/plans SaaS autorisés** (Basic, Premium) explicitement listés.
- **Proration behavior** : défini sur **Always invoice** pour les modifications d'abonnement.
  - *Note technique* : `always_invoice` garantit que Stripe génère immédiatement une facture pour le prorata de l'upgrade (ex: Basic -> Premium) et tente le paiement. Cela évite d'attendre la fin de période pour facturer l'écart.
  - *Note produit* : L'usage de `always_invoice` n'implique pas une interface de checkout personnalisée ; l'utilisateur reste dans l'interface standard du Stripe Customer Portal.

### Règle d'or : Webhook-First
Bien que `always_invoice` déclenche une facturation immédiate, l'application respecte strictement la règle **webhook-first** :
1. L'utilisateur valide son changement dans le portail.
2. Stripe encaisse (ou planifie) le changement et émet un webhook.
3. Le backend reçoit le webhook et met à jour le profil billing local.
4. Les droits (Premium) sont accordés à l'utilisateur lors de son prochain rafraîchissement d'état.
Aucun droit n'est accordé de manière synchrone lors de la création de la session de portail ou au retour de l'utilisateur sur la `return_url`.

### Annulation et Réactivation
- Le mode d'annulation **At period end** permet à l'utilisateur de conserver ses accès jusqu'à la fin de la période payée.
- Stripe autorise nativement la **réactivation de l'abonnement via le portail** tant que la période n'est pas expirée.
- L'application ne propose pas d'endpoint `resume-subscription` maison pour le MVP ; cette action est déléguée au portail Stripe.

## Flux Utilisateur

1. L'utilisateur clique sur "Gérer mon abonnement" dans les paramètres.
2. Le frontend appelle `POST /v1/billing/stripe-customer-portal-session`.
3. Le frontend redirige l'utilisateur vers l'URL retournée.
4. L'utilisateur modifie son abonnement sur Stripe.
5. Stripe envoie un webhook (`customer.subscription.updated`, etc.) au backend.
6. Le backend met à jour le `StripeBillingProfile`, invalide le cache billing utilisateur, puis le runtime B2C relit ce snapshot canonique pour exposer le plan commercial et les entitlements.
7. L'utilisateur revient sur l'application via la `return_url`.
8. L'interface reflète les changements grâce à l'état mis à jour via le webhook.

## Limites du MVP

- Pas de gestion des proratas en temps réel côté backend (géré par l'UI Stripe).
- Pas de polling au retour du portail : il peut y avoir un léger délai (quelques secondes) avant que le webhook ne soit traité et que l'interface ne soit à jour.
- Pas de mutation synchrone du snapshot billing ni de recalcul d'entitlements dans l'endpoint portail. Le webhook Stripe reste l'unique source de vérité pour les changements effectifs.
- Le contrat `GET /v1/billing/subscription` et le resolver `GET /v1/entitlements/me` ne dépendent plus du seul `UserSubscriptionModel` legacy quand un snapshot Stripe exploitable existe.
