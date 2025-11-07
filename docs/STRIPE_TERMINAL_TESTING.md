# Guide de Test Stripe Terminal

Ce document décrit comment utiliser le simulateur Stripe Terminal en développement pour tester les flux de paiement.

## Accès

Le simulateur Terminal est accessible uniquement en développement via la route `/dev/terminal`.

**Prérequis** :

- `VITE_DEV_TERMINAL=true` dans `.env` (optionnel, vérifie aussi `import.meta.env.DEV`)
- Backend avec endpoints Terminal disponibles (`/v1/terminal/*`)

## Montants de Test

Les montants suivants déclenchent différents scénarios selon la documentation Stripe Terminal :

| Montant (centimes) | Montant (EUR) | Scénario                           |
| ------------------ | ------------- | ---------------------------------- |
| `100`              | 1.00          | Succès standard                    |
| `101`              | 1.01          | Succès avec PIN offline            |
| `102`              | 1.02          | Succès avec PIN online             |
| `103`              | 1.03          | Succès avec signature              |
| `105`              | 1.05          | Succès avec 3D Secure              |
| `200`              | 2.00          | Carte refusée                      |
| `201`              | 2.01          | Fonds insuffisants                 |
| `202`              | 2.02          | Carte expirée                      |
| `203`              | 2.03          | Erreur de traitement               |
| `255`              | 2.55          | PIN offline requis                 |
| `265`              | 2.65          | PIN online requis                  |
| `275`              | 2.75          | Montant pour test de remboursement |

## Cartes de Test

| Numéro             | Scénario             |
| ------------------ | -------------------- |
| `4242424242424242` | Succès               |
| `4000000000000002` | Carte refusée        |
| `4000000000009995` | Fonds insuffisants   |
| `4000000000000069` | Carte expirée        |
| `4000000000000119` | Erreur de traitement |
| `4000000000000010` | PIN offline requis   |
| `4000000000000028` | PIN online requis    |

## Flux de Test

### Scénario 1 : Paiement Réussi

1. **Connecter** : Cliquer sur "Connecter Terminal"
2. **Créer PaymentIntent** : Sélectionner montant `100` (1.00 EUR) et carte `4242...4242`
3. **Traiter** : Cliquer sur "Traiter Paiement"
4. **Résultat** : État `captured` (succès)

### Scénario 2 : Carte Refusée

1. **Connecter** : Cliquer sur "Connecter Terminal"
2. **Créer PaymentIntent** : Sélectionner montant `200` (2.00 EUR) et carte `4000...0002`
3. **Traiter** : Cliquer sur "Traiter Paiement"
4. **Résultat** : État `failed` avec message d'erreur "Your card was declined."

### Scénario 3 : PIN Offline Requis

1. **Connecter** : Cliquer sur "Connecter Terminal"
2. **Créer PaymentIntent** : Sélectionner montant `255` (2.55 EUR) et carte `4000...0010`
3. **Traiter** : Cliquer sur "Traiter Paiement"
4. **Résultat** : État `processing` (PIN offline requis)
5. **Capturer** : Cliquer sur "Capturer" après saisie PIN
6. **Résultat** : État `captured` (succès)

### Scénario 4 : Remboursement

1. Suivre le **Scénario 1** jusqu'à l'état `captured`
2. **Rembourser** : Cliquer sur "Rembourser"
3. **Résultat** : État `refunded` (remboursement total)

Pour un remboursement partiel, le backend doit supporter le paramètre `amount` dans `/v1/terminal/refund`.

## États de la Machine à États

```
disconnected → connected → intent_created → processing → captured
                                              ↓
                                           canceled
                                              ↓
                                           failed
                                              ↓
                                           refunded
```

## Erreurs Courantes

### Erreur de Connexion

- Vérifier que le backend expose `/v1/terminal/connect`
- Vérifier que `VITE_API_BASE_URL` est correctement configuré

### Erreur de Création PaymentIntent

- Vérifier que le montant est en centimes (ex: `100` pour 1.00 EUR)
- Vérifier que la devise est supportée (`eur` par défaut)

### Erreur de Traitement

- Vérifier que la carte de test correspond au montant sélectionné
- Vérifier que le `payment_intent_id` est valide

## Intégration Backend

Le backend doit implémenter les endpoints suivants :

- `POST /v1/terminal/connect` → `{ connection_token: string }`
- `POST /v1/terminal/payment-intent` → `{ client_secret: string, payment_intent_id: string }`
- `POST /v1/terminal/process` → `{ status: 'succeeded' | 'requires_payment_method' | 'requires_action', payment_intent_id: string, error_code?: string, error_message?: string }`
- `POST /v1/terminal/capture` → `{ status: 'succeeded' | 'processing' | 'failed', payment_intent_id: string }`
- `POST /v1/terminal/cancel` → `{ status: 'canceled' | 'failed', payment_intent_id: string }`
- `POST /v1/terminal/refund` → `{ refund_id: string, amount: number, status: 'succeeded' | 'pending' | 'failed' }`

Tous les endpoints doivent être protégés par authentification JWT et disponibles uniquement en développement.

## Notes de Sécurité

⚠️ **Important** : Ce simulateur est **dev-only** et ne doit jamais être compilé en production. Le gating est assuré par :

- `import.meta.env.DEV` dans le composant
- Vérification dans `terminalService` (throw si `!import.meta.env.DEV`)
- Route conditionnelle dans le router

Les cartes de test Stripe ne fonctionnent qu'en mode test et ne génèrent pas de transactions réelles.
