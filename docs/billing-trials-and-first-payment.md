# Documentation : Essais gratuits et premier paiement Stripe

## Objectif MVP

Le produit ne décide jamais l'accès premium à partir d'un simple booléen `paid/unpaid`.
La source de vérité reste Stripe, réconciliée par webhook puis exposée au runtime produit via `subscription_status` et `entitlement_plan`.

## Statuts Stripe reconnus

Le backend persiste au minimum les statuts suivants : `trialing`, `active`, `incomplete`, `incomplete_expired`, `past_due`, `paused`, `canceled`, `unpaid`.

Le sens produit retenu est :

| Statut Stripe | Sens produit | Accès |
|---|---|---|
| `trialing` | Essai démarré, sans premier paiement réussi | autorisé selon le plan mappé |
| `active` | Abonnement réellement actif | autorisé selon le plan mappé |
| `incomplete` | Premier paiement non confirmé | accès payant refusé |
| `incomplete_expired` | Première tentative expirée côté Stripe | accès refusé |
| `past_due` | Défaut temporaire après activation | conservation du plan courant |
| `paused` | Fin d'essai sans moyen de paiement avec politique `pause` | accès suspendu |
| `canceled` | Abonnement résilié | retour `free` |
| `unpaid` | Factures impayées, accès révoqué | retour `free` |

`trialing` n'est pas un paiement réussi. C'est un état d'accès autorisé selon la politique produit.

## Configuration checkout

Variables supportées dans `backend/app/core/config.py` :

- `STRIPE_TRIAL_ENABLED`
- `STRIPE_TRIAL_PERIOD_DAYS`
- `STRIPE_PAYMENT_METHOD_COLLECTION` avec validation stricte `always|if_required`
- `STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR` avec validation stricte `pause|cancel`

La session Stripe :

- ajoute `subscription_data.trial_period_days` seulement si le trial est activé et strictement positif
- ajoute `payment_method_collection="if_required"` seulement si la configuration l'impose
- ajoute `subscription_data.trial_settings.end_behavior.missing_payment_method` seulement dans le cas trial + `if_required`
- ne dérive aucun état produit depuis l'URL de retour navigateur

## Webhooks retenus

Le backend traite et audite notamment :

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `customer.subscription.paused`
- `customer.subscription.resumed`
- `customer.subscription.trial_will_end`
- `invoice.paid`
- `invoice.payment_action_required`
- `invoice.payment_failed`

`customer.subscription.trial_will_end` sert d'alerte opérationnelle et d'audit. Il ne suffit pas à lui seul pour changer l'accès produit.

## UX de retour billing

La page `BillingSuccessPage.tsx` lit `GET /v1/billing/subscription` et affiche un message neutre selon `data.subscription_status` :

- `trialing` : essai démarré
- `active` : abonnement activé
- `incomplete` : activation en attente
- autre statut ou absence de statut : attente de réconciliation Stripe

Le frontend ne se base plus sur un drapeau `is_trial` dans l'URL de retour. Le statut API est la seule source de vérité affichée.

## Contrat API utile au frontend

`GET /v1/billing/subscription` expose désormais :

- `status` : résumé applicatif historique (`active|inactive`)
- `subscription_status` : statut Stripe brut utile pour l'UX de retour
- `plan`
- `failure_reason`
- `updated_at`

## Vérification opérationnelle

À contrôler après déploiement :

- l'audit `stripe_checkout_session_created` contient `trial_enabled`, `trial_period_days`, `payment_method_collection`, `missing_payment_method_behavior`
- un abonnement `trialing` ouvre bien l'accès via `entitlement_plan`
- un abonnement `incomplete` reste sans accès payant tant que `invoice.paid` n'a pas convergé vers `active`
- un abonnement `paused` retombe sur `free`
