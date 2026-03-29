# MVP Billing Self-Service — Stripe Customer Portal

Ce document détaille l'implémentation du self-service billing via le **Stripe Customer Portal**.

## Architecture & Philosophie

L'application délègue la gestion avancée des abonnements (upgrade, downgrade, annulation, gestion des moyens de paiement, historique des factures) à l'interface hébergée par Stripe.

### Principes clés
1. **Source de vérité : Stripe**. Tout changement effectué dans le portail est propagé au backend via le **Webhook Stripe** existant.
2. **Snapshot local**. Le backend maintient un snapshot de l'état Stripe dans la table `stripe_billing_profiles`.
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
- La valeur par défaut `http://localhost:5173/settings/subscription` est acceptable uniquement en local. En staging/production, `STRIPE_PORTAL_RETURN_URL` doit être définie explicitement.

## Flux Utilisateur

1. L'utilisateur clique sur "Gérer mon abonnement" dans les paramètres.
2. Le frontend appelle `POST /v1/billing/stripe-customer-portal-session`.
3. Le frontend redirige l'utilisateur vers l'URL retournée.
4. L'utilisateur modifie son abonnement sur Stripe.
5. Stripe envoie un webhook (`customer.subscription.updated`, etc.) au backend.
6. Le backend met à jour le `StripeBillingProfile` et recalcule les entitlements.
7. L'utilisateur revient sur l'application via la `return_url`.
8. L'interface reflète les changements grâce à l'état mis à jour via le webhook.

## Limites du MVP

- Pas de gestion des proratas en temps réel côté backend (géré par l'UI Stripe).
- Pas de polling au retour du portail : il peut y avoir un léger délai (quelques secondes) avant que le webhook ne soit traité et que l'interface ne soit à jour.
- Pas de mutation synchrone du snapshot billing ni de recalcul d'entitlements dans l'endpoint portail. Le webhook Stripe reste l'unique source de vérité pour les changements effectifs.
