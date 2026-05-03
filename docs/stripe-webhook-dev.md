# Workflow de Développement - Webhooks Stripe

Ce document conserve la rationale historique de sélection des événements Stripe. Pour la procédure locale opérationnelle à jour, utiliser d'abord [docs/billing-webhook-local-testing.md](./billing-webhook-local-testing.md), qui fait désormais office de runbook canonique pour les tests Stripe CLI en local. Ce document ne remplace donc pas le runbook canonique ; il explique pourquoi le sous-ensemble standardisé historique du listener a convergé vers le périmètre backend élargi réellement accepté aujourd'hui.

## 1. Prérequis

### Installation de Stripe CLI
Sur Windows :
```powershell
winget install Stripe.StripeCLI
```

### Authentification
Une seule fois par machine :
```powershell
stripe login
```

## 2. Configuration du Forwarding Local

Pour que Stripe puisse envoyer des événements à votre backend local, vous devez lancer un forwarder.

1. Assurez-vous que votre backend tourne (généralement sur le port 8001).
2. Dans un terminal séparé, lancez :
   ```powershell
   stripe listen --forward-to localhost:8001/v1/billing/stripe-webhook
   ```
3. La commande va afficher votre **Webhook Signing Secret** pour le mode dev :
   `> Your webhook signing secret is whsec_xxxx`
4. Copiez cette valeur dans votre fichier `backend/.env` :
   `STRIPE_WEBHOOK_SECRET=whsec_xxxx`

## 3. Distinction des Secrets (DEV vs PROD)

| Mode | Source du secret | Stabilité | Usage |
|------|-----------------|-----------|-------|
| **DEV (Stripe CLI)** | Terminal `stripe listen` | Stable entre les redémarrages de la commande sur une même machine. | Développement local uniquement. |
| **PROD (Dashboard)** | Dashboard Stripe > Développeurs > Webhooks > [votre endpoint] | Permanent. | Environnements déployés (Staging, Production). |

> [!IMPORTANT]
> Le secret fourni par la CLI est différent de celui du Dashboard. Ils ne sont pas interchangeables.

## 4. Déclencher des événements de test

Vous pouvez simuler des événements Stripe directement depuis votre terminal :

```powershell
# Checkout et Abonnements
stripe trigger checkout.session.completed
stripe trigger checkout.session.async_payment_succeeded
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger customer.subscription.paused
stripe trigger customer.subscription.resumed
stripe trigger customer.subscription.trial_will_end
stripe trigger subscription_schedule.created
stripe trigger subscription_schedule.updated
stripe trigger subscription_schedule.canceled
stripe trigger subscription_schedule.completed

# Facturation (Invoice) - État cible Story 61-6
stripe trigger invoice.paid                         # Remplace invoice.payment_succeeded
stripe trigger invoice.payment_failed
stripe trigger invoice.payment_action_required      # Nouveau (SCA/3DS)

# Autres
stripe trigger customer.updated
```

> [!NOTE]
> **Limites de `stripe trigger`** : Ces commandes génèrent des objets synthétiques (ex: `cus_00000000000000`).
> En développement local, à moins d'avoir un profil de facturation correspondant déjà en base, le backend retournera `user_not_resolved`. C'est un comportement normal pour valider le flux technique. Pour un test complet de réconciliation, préférez un vrai flux de checkout via l'UI et `stripe listen`.

## 5. Rationale — sélection des événements

> [!NOTE]
> Le tableau ci-dessous documente principalement la décision initiale de la story 61-6. Le périmètre effectivement géré aujourd'hui par le backend et la procédure locale de validation courante sont décrits dans le runbook canonique `docs/billing-webhook-local-testing.md`.

### Sous-ensemble standardisé historique

Le listener par défaut standardisé a d'abord été limité aux événements suivants pour réduire le bruit local :

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `invoice.payment_action_required`

### Périmètre backend élargi réellement accepté

Le backend accepte actuellement le sous-ensemble standardisé ci-dessus, plus les événements additionnels suivants. Le registre canonique de ce périmètre est `app.services.billing.stripe_webhook_events` :

- `checkout.session.async_payment_succeeded`
- `customer.updated`
- `customer.subscription.paused`
- `customer.subscription.resumed`
- `customer.subscription.trial_will_end`
- `subscription_schedule.created`
- `subscription_schedule.updated`
- `subscription_schedule.canceled`
- `subscription_schedule.completed`

Ces événements additionnels appartiennent au périmètre backend élargi réellement supporté. Pour les reproduire localement, se référer au runbook canonique `docs/billing-webhook-local-testing.md`, qui documente la commande Stripe CLI complète.

Le tableau suivant justifie la sélection des événements Stripe traités par le webhook pour une stratégie SaaS robuste.

| Événement | Traité | Raison |
|-----------|--------|--------|
| `checkout.session.completed` | ✅ Oui | Réconciliation initiale : lie le `customer_id` Stripe à l'`user_id` local via `client_reference_id`. Point d'entrée obligatoire de tout abonnement. |
| `checkout.session.async_payment_succeeded` | ✅ Oui | Checkout asynchrone explicitement supporté. Il peut appliquer une montée d'abonnement payée ou réconcilier le profil via le `customer_id`. |
| `invoice.paid` | ✅ Oui | Confirmation de référence qu'une invoice est soldée. Préféré à `invoice.payment_succeeded` car couvre aussi le cas où une invoice est marquée paid out-of-band, en plus des succès de tentative de paiement. `invoice.payment_succeeded` ne couvre que le succès d'une tentative de paiement Stripe. Source : [Stripe API Events](https://docs.stripe.com/api/events/types). |
| `invoice.payment_failed` | ✅ Oui | Échec de paiement récurrent. Permet de déclencher des alertes, du dunning, et de tenir le statut interne à jour. Note : `invoice.payment_failed` peut aussi survenir dans les flux SCA/3DS si la tentative échoue après une action requise. |
| `invoice.payment_action_required` | ✅ Oui | Identifie explicitement le cas "customer authentication required" (3DS/SCA). Permet de distinguer le cas "action client nécessaire" d'un simple échec, et de notifier l'utilisateur en conséquence. Note : ce n'est pas l'unique signal possible dans les scénarios SCA — `invoice.payment_failed` peut également survenir dans ces flux. |
| `customer.subscription.updated` | ✅ Oui | Tout changement de plan, de statut ou de période. Source de vérité pour `subscription_status` et `cancel_at_period_end`. |
| `customer.subscription.deleted` | ✅ Oui | Fin d'abonnement (résiliation ou non-renouvellement). Met à jour `subscription_status = "canceled"` et recalcule `entitlement_plan`. |
| `customer.subscription.paused` | ✅ Oui | Fait partie du périmètre backend élargi accepté aujourd'hui. Permet d'aligner la documentation avec le statut Stripe réellement géré lors des validations locales. |
| `customer.subscription.resumed` | ✅ Oui | Fait partie du périmètre backend élargi accepté aujourd'hui. Permet de documenter explicitement la reprise d'abonnement déjà supportée par le backend. |
| `customer.updated` | ✅ Oui | Mise à jour des données client (email de facturation). Maintient `billing_email` cohérent. |
| `customer.subscription.created` | ✅ Oui (passif) | Reçu lors de la création via checkout, mais `checkout.session.completed` est l'événement de réconciliation principal. Traité pour cohérence, mais ne porte pas d'information que `checkout.session.completed` n'a pas. |
| `customer.subscription.trial_will_end` | ✅ Oui (périmètre étendu) | Événement actuellement accepté par le backend et documenté dans le runbook canonique local. Il reste principalement utile pour la cohérence de validation et les notifications autour de la fin d'essai. |
| `subscription_schedule.created` | ✅ Oui (périmètre étendu) | Événement schedule explicitement classé comme supporté car le service de profil billing sait réconcilier les objets `subscription_schedule`. |
| `subscription_schedule.updated` | ✅ Oui (périmètre étendu) | Événement schedule explicitement classé comme supporté car le service de profil billing sait réconcilier les objets `subscription_schedule`. |
| `subscription_schedule.canceled` | ✅ Oui (périmètre étendu) | Événement schedule explicitement classé comme supporté car le service de profil billing sait réconcilier les objets `subscription_schedule`. |
| `subscription_schedule.completed` | ✅ Oui (périmètre étendu) | Événement schedule explicitement classé comme supporté car le service de profil billing sait réconcilier les objets `subscription_schedule`. |
| `invoice.payment_succeeded` | ❌ Remplacé | Remplacé par `invoice.paid` à partir de la story 61-6. `invoice.paid` couvre un ensemble de cas strictement plus large. Désormais traité comme `event_ignored`. |
| `payment_intent.*` | ❌ Non traité | Granularité inférieure au niveau facturation. Pour un SaaS abonnement, les événements `invoice.*` et `subscription.*` sont suffisants. |
| `invoice.upcoming` | ❌ Non traité | Pré-notification avant facturation. Utile pour alertes mais sans impact sur le profil de facturation. Hors scope. |

## 6. Troubleshooting

- **Signature Verification Failed** : Vérifiez que `STRIPE_WEBHOOK_SECRET` dans votre `.env` correspond exactement à ce qui est affiché par `stripe listen`.
- **404 Not Found** : Vérifiez que l'URL `--forward-to` pointe bien vers le bon port et le bon endpoint (`/v1/billing/stripe-webhook`).
- **Connection Refused** : Votre backend n'est probablement pas démarré.
