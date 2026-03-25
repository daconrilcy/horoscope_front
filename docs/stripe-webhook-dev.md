# Workflow de Développement - Webhooks Stripe

Ce document décrit comment tester les webhooks Stripe localement en utilisant la Stripe CLI.

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
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted

# Facturation (Invoice) - Supporté depuis Story 61-5
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed

# Autres
stripe trigger customer.updated
```

## 5. Troubleshooting

- **Signature Verification Failed** : Vérifiez que `STRIPE_WEBHOOK_SECRET` dans votre `.env` correspond exactement à ce qui est affiché par `stripe listen`.
- **404 Not Found** : Vérifiez que l'URL `--forward-to` pointe bien vers le bon port et le bon endpoint (`/v1/billing/stripe-webhook`).
- **Connection Refused** : Votre backend n'est probablement pas démarré.
