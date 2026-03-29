# Documentation : Essais Gratuits et Premier Paiement — Story 61.55

## 1. Contexte et Objectif

La story 61.55 introduit le support des **essais gratuits (Free Trials)** dans le cycle de vie Stripe SaaS.
L'objectif est de permettre aux utilisateurs de s'inscrire à un plan Premium sans paiement immédiat, tout en configurant correctement le backend pour gérer les transitions (fin d'essai, premier paiement réussi ou échoué).

## 2. Configuration Backend (MVP)

La configuration est centralisée dans `backend/app/core/config.py` via des variables d'environnement :

*   `STRIPE_TRIAL_ENABLED` : Active ou désactive globalement le mode essai pour les nouvelles sessions.
*   `STRIPE_TRIAL_PERIOD_DAYS` : Durée de l'essai en jours (ex: 7, 14).
*   `STRIPE_PAYMENT_METHOD_COLLECTION` : 
    *   `always` (défaut) : Exige une carte bancaire même pour l'essai.
    *   `if_required` : Permet un essai sans carte (si activé dans le Dashboard Stripe).
*   `STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR` :
    *   `pause` (recommandé) : Suspend l'abonnement si aucune carte n'est fournie à la fin de l'essai.
    *   `cancel` : Annule l'abonnement.

## 3. Flux Checkout

Lors de l'appel à `POST /v1/billing/stripe-checkout-session` :

1.  Le backend consulte les paramètres `STRIPE_TRIAL_*`.
2.  Si activé, il injecte `trial_period_days` dans `subscription_data`.
3.  Si `payment_method_collection` est `if_required`, il configure Stripe pour autoriser l'essai sans carte.
4.  La `success_url` envoyée à Stripe contient un paramètre `is_trial=true`.

## 4. Expérience Frontend

La page `BillingSuccessPage.tsx` intercepte le paramètre `is_trial=true` pour adapter ses messages :
*   **Mode Paiement** : "Paiement en cours de confirmation..."
*   **Mode Essai** : "Essai gratuit activé !"

## 5. Gestion des Webhooks (États Stripe)

Le `StripeWebhookService` a été étendu pour traiter les événements critiques liés à l'essai :

*   `customer.subscription.trial_will_end` : Envoyé par Stripe 3 jours avant la fin (si configuré). Permet d'anticiper la notification utilisateur.
*   `customer.subscription.paused` : L'abonnement passe en pause à la fin de l'essai (si pas de carte). Le backend doit repasser le `entitlement_plan` à `free`.
*   `customer.subscription.resumed` : L'utilisateur a ajouté une carte, l'abonnement reprend. Le backend réactive le plan payant.

## 6. Vérification Technique

### Audit Log
Vérifier l'action `stripe_checkout_session_created` dans la table d'audit. Les détails doivent contenir `trial_enabled` et `trial_period_days`.

### Entitlements
*   Pendant l'essai : `subscription_status` = `trialing`. `entitlement_plan` = `premium` (ou `basic`).
*   Si essai expire sans carte : `subscription_status` = `paused`. `entitlement_plan` = `free`.
