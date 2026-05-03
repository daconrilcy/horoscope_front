# Tests locaux du webhook Stripe avec Stripe CLI

Ce document est le runbook canonique local pour la validation du webhook Stripe avec la Stripe CLI sur un environnement de développement Windows / PowerShell. La Stripe CLI est utilisée ici uniquement comme outil de développement local; elle n'est pas une surface CI, production ou déploiement.

## Prérequis

1. Stripe CLI installée.
2. Backend local démarré sur `http://localhost:8001`.
3. Compte Stripe en mode test.
4. Endpoint Stripe Dashboard aligné sur la version API `2026-04-22.dahlia`.

Installation Windows :

```powershell
winget install Stripe.StripeCLI
```

## 1. Authentification

```powershell
stripe login
```

## 2. Démarrer le listener

### Variante large

Utile pour observer toute la chaîne d'événements réellement émise par Stripe.

```powershell
stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

### Variante filtrée standardisée

Cette variante réduit le bruit et couvre le socle billing standardisé par cette story :

```powershell
stripe listen `
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,invoice.payment_action_required `
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

Scripts fournis :

```powershell
.\scripts\stripe-listen-webhook.ps1
```

### Événements supplémentaires déjà gérés par le backend

Le service backend accepte aussi actuellement :

- `customer.updated`
- `customer.subscription.paused`
- `customer.subscription.resumed`
- `customer.subscription.trial_will_end`

Si vous voulez reproduire exactement ce périmètre élargi, démarrez le listener avec la liste complète :

```powershell
stripe listen `
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,customer.subscription.paused,customer.subscription.resumed,customer.subscription.trial_will_end,customer.updated,invoice.paid,invoice.payment_failed,invoice.payment_action_required `
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

### Utilisation de `--load-from-webhooks-api`

Si un endpoint Stripe est déjà enregistré dans le Dashboard, cette option recharge son chemin et ses événements puis les appende au `--forward-to` local. Cela permet d'aligner le listener local sur la configuration distante existante.

```powershell
stripe listen --load-from-webhooks-api --forward-to http://localhost:8001
```

## 3. Récupérer et injecter le secret

Au démarrage, `stripe listen` affiche un secret local de signature :

```text
Ready! Your webhook signing secret is whsec_XXXX (^C to quit)
```

1. Copier la valeur `whsec_...` affichée par `stripe listen`.
2. La reporter dans `.env.local` :

```dotenv
STRIPE_WEBHOOK_SECRET=whsec_XXXX
```

3. Redémarrer le backend si nécessaire.

Le secret de développement local vient explicitement de `stripe listen`. Il ne faut pas utiliser le secret du Dashboard Stripe pour ce test local, y compris lorsque `--load-from-webhooks-api` est utilisé.

## Version API Stripe

Le backend initialise le SDK Stripe avec `STRIPE_API_VERSION=2026-04-22.dahlia`. Les endpoints webhook configurés dans le Dashboard Stripe doivent utiliser cette même version pour éviter une dérive de forme entre les payloads livrés par Stripe et les contrats validés par les tests backend.

Rollback opérationnel si le Dashboard production ne peut pas être aligné immédiatement :

1. Fixer explicitement `STRIPE_API_VERSION=2024-12-18.acacia` dans l'environnement concerné.
2. Redémarrer le backend pour reconstruire le client SDK Stripe.
3. Rejouer les tests checkout, portail client, invoice preview, subscription upgrade et webhook avant déploiement.
4. Planifier l'alignement Dashboard puis retirer l'override d'environnement.

## 4. Scénario nominal

Le test nominal recommandé passe par un vrai flow Checkout sandbox afin de produire la chaîne d'événements réelle. `stripe trigger` reste utile pour des validations ciblées rapides.

```powershell
stripe trigger invoice.paid
```

Statuts de retour attendus côté endpoint :

| Statut | Signification |
|--------|---------------|
| `processed` | L'événement signé a été traité avec succès. |
| `event_ignored` | L'événement est valide mais non pris en charge. |
| `user_not_resolved` | Le `customer_id` Stripe n'est pas relié à un utilisateur local. |

Avec le bon secret CLI en place, l'événement doit être accepté par l'API et retourner un statut métier HTTP 200.

Si la signature est valide mais que le traitement métier échoue, l'endpoint retourne une enveloppe d'erreur HTTP 500 avec le code `stripe_webhook_processing_failed`. Ce statut est volontairement non-2xx pour laisser Stripe rejouer la livraison automatiquement. La ligne `stripe_webhook_events` reste en `failed` jusqu'à une livraison ultérieure réussie.

## 5. Scénario de signature invalide

1. Remplacer temporairement `STRIPE_WEBHOOK_SECRET` dans `.env.local` par une mauvaise valeur.
2. Relancer le backend.
3. Envoyer un événement, par exemple :

```powershell
stripe trigger invoice.paid
```

Résultat attendu : rejet HTTP 400 avec le code `invalid_signature`.

4. Remettre ensuite le vrai secret affiché par `stripe listen`.
5. Relancer le même test.

Résultat attendu : l'événement est accepté et retourne un statut HTTP 200 avec un résultat métier comme `processed`, `event_ignored` ou `user_not_resolved`.

## 6. Scénario de replay exact

Ce scénario valide l'idempotence introduite en story 61.56 sur un vrai `event.id` Stripe.

1. Envoyer un premier événement réel via Checkout sandbox ou `stripe trigger invoice.paid`.
2. Relever dans les logs Stripe CLI ou applicatifs l'`event.id` et confirmer un premier statut `processed`.
3. Rejouer exactement le même événement :

```powershell
stripe events resend evt_123456
```

4. Vérifier que le second appel retourne `duplicate_ignored` sans mutation métier supplémentaire.

Si vous devez cibler un endpoint Stripe enregistré plutôt que le webhook local CLI par défaut :

```powershell
stripe events resend evt_123456 --webhook-endpoint=we_123456
```

Vérification base de données :

```sql
SELECT status, processing_attempts
FROM stripe_webhook_events
WHERE stripe_event_id = 'evt_123456';
```

Résultat attendu après un replay exact réussi : `status=processed` et `processing_attempts=1`.

## 7. Tests ciblés avec `stripe trigger`

| Commande | Utilité |
|----------|---------|
| `stripe trigger checkout.session.completed` | Valider la création initiale du profil de facturation. |
| `stripe trigger customer.subscription.created` | Valider la création d'abonnement. |
| `stripe trigger customer.subscription.updated` | Valider une mise à jour d'abonnement. |
| `stripe trigger customer.subscription.deleted` | Valider une résiliation. |
| `stripe trigger invoice.paid` | Valider un paiement confirmé. |
| `stripe trigger invoice.payment_failed` | Valider un échec de paiement. |
| `stripe trigger invoice.payment_action_required` | Valider un cas SCA/3DS. |

Pour les événements supplémentaires déjà gérés par le backend :

| Commande | Utilité |
|----------|---------|
| `stripe trigger customer.updated` | Valider la synchronisation des données client Stripe. |

`stripe trigger` génère des objets synthétiques. En local, un `user_not_resolved` peut donc être normal tant qu'aucun `customer_id` correspondant n'existe en base.
