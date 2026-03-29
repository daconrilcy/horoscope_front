# Tests locaux du webhook Stripe avec Stripe CLI

Ce document décrit la procédure pour tester localement la réception et le traitement des événements Stripe, ainsi que la validation de l'idempotence.

## Prérequis

1.  **Stripe CLI installé** : [Documentation d'installation](https://stripe.com/docs/stripe-cli)
2.  **API Backend démarrée** : L'API doit être accessible sur le port 8001 (ou le port configuré pour `BACKEND_PORT`).
3.  **Identifiant Stripe** : Un compte Stripe (en mode Test).

---

## 1. Authentification

Avant toute chose, authentifiez-vous auprès de votre compte Stripe via la CLI :

```bash
stripe login
```

Suivez les instructions dans le navigateur pour autoriser l'accès.

---

## 2. Démarrer le listener

Le listener permet d'intercepter les événements Stripe et de les rediriger vers votre endpoint local.

### Variante large (Tous les événements)

Utile pour découvrir quels événements sont envoyés par Stripe :

```bash
stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

### Variante filtrée (Recommandée)

Cible uniquement les événements supportés par l'application pour réduire le bruit :

```bash
stripe listen \
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,invoice.payment_action_required \
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

### Utilisation de `--load-from-webhooks-api`

Si vous avez déjà configuré un endpoint dans le Dashboard Stripe, vous pouvez synchroniser les événements et le chemin configurés vers votre listener local :

```bash
stripe listen --load-from-webhooks-api --forward-to http://localhost:8001
```
*Note : Cela appende le chemin configuré au `--forward-to` local.*

---

## 3. Récupérer et injecter le secret

Lorsqu'il démarre, `stripe listen` affiche un message comme celui-ci :

`> Ready! Your webhook signing secret is whsec_XXXX (^C to quit)`

1.  Copiez la valeur commençant par `whsec_`.
2.  Collez-la dans votre fichier `.env.local` :
    `STRIPE_WEBHOOK_SECRET=whsec_XXXX`
3.  **Important** : Ce secret est généré dynamiquement par la CLI pour votre session locale. Il est différent du secret de signature configuré dans le Dashboard Stripe (utilisé pour la prod).

---

## 4. Scénario nominal

Pour valider le flux complet :

1.  **Flow Checkout Sandbox (Préféré)** : Déclenchez un achat ou un abonnement depuis votre application ou via un lien Stripe Checkout en mode test. Cela produit la chaîne réelle d'événements.
2.  **Stripe Trigger** : Utilisez la commande trigger pour simuler un événement spécifique :
    ```bash
    stripe trigger invoice.paid
    ```

### Statuts de retour attendus

| Statut | Signification |
| :--- | :--- |
| `processed` | L'événement a été reçu, validé et traité avec succès. |
| `event_ignored` | Le type d'événement n'est pas pris en charge par l'application (normal pour certains événements système). |
| `user_not_resolved` | Le `customer_id` Stripe présent dans l'événement n'existe pas dans la base de données locale. |

---

## 5. Scénario de signature invalide

Pour valider la sécurité HMAC :

1.  Modifiez temporairement `STRIPE_WEBHOOK_SECRET` dans `.env.local` avec une valeur erronée.
2.  Envoyez un événement avec `stripe trigger invoice.paid`.
3.  **Résultat attendu** : L'API doit retourner une erreur HTTP 400 (Bad Request).

---

## 6. Scénario de replay exact (Idempotence)

Ce scénario prouve que le système d'idempotence (Story 61.56) fonctionne correctement.

1.  **Premier envoi** : Envoyez un événement (ex: `stripe trigger invoice.paid`).
2.  **Vérification** : Dans les logs applicatifs, observez `outcome=processed` et notez l'`event.id` (ex: `evt_123...`).
3.  **Renvoi (Replay)** : Utilisez la commande resend pour renvoyer le même événement vers le listener local :
    ```bash
    stripe events resend evt_123...
    ```
4.  **Résultat attendu** :
    - L'API doit retourner `duplicate_ignored`.
    - Aucune action métier (mutation de base de données billing) ne doit être répétée.
    - Dans la base de données : `SELECT status, processing_attempts FROM stripe_webhook_events WHERE stripe_event_id='evt_123...'` doit afficher `status=processed` et `attempts=1`.

---

## 7. Tests ciblés avec stripe trigger

La commande `stripe trigger <event_type>` est utile pour tester des cas précis sans passer par le tunnel de vente complet.

| Commande | Utilité |
| :--- | :--- |
| `stripe trigger checkout.session.completed` | Valider la création initiale d'un profil billing. |
| `stripe trigger customer.subscription.created` | Valider la création d'un abonnement. |
| `stripe trigger customer.subscription.updated` | Valider la mise à jour d'un abonnement. |
| `stripe trigger customer.subscription.deleted` | Valider la résiliation d'un abonnement. |
| `stripe trigger invoice.paid` | Valider la confirmation de paiement. |
| `stripe trigger invoice.payment_failed` | Valider l'échec d'un paiement. |
| `stripe trigger invoice.payment_action_required` | Valider la demande d'action utilisateur (3DS). |

---

## Commandes standardisées

Un script est disponible pour lancer rapidement le listener avec les bons paramètres :

```bash
./scripts/stripe-listen-webhook.sh
```
