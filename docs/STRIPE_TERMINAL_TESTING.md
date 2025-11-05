# Stripe Terminal Testing Guide

Ce guide documente les tests pour le simulateur Stripe Terminal, conformément à la [documentation officielle Stripe](https://docs.stripe.com/terminal/references/testing).

## Cartes de test standard

### Cartes principales

| Numéro de carte | Type de paiement | Marque |
|----------------|------------------|--------|
| `4242424242424242` | `visa` | Visa |
| `4000056655665556` | `visa_debit` | Visa (débit) |
| `5555555555554444` | `mastercard` | Mastercard |
| `5200828282828210` | `mastercard_debit` | Mastercard (débit) |
| `378282246310005` | `amex` | American Express |
| `6011111111111117` | `discover` | Discover |

### Cartes pour cas de succès spécifiques

| Numéro de carte | Type de paiement | Résultat |
|----------------|------------------|----------|
| `4001007020000002` | `offline_pin_cvm` | Simule la demande d'un PIN offline. Le paiement a `cardholder_verification_method` = `offline_pin`. |
| `4000008260000075` | `offline_pin_sca_retry` | Simule un retry SCA où le paiement sans contact échoue et demande un PIN offline. |
| `4001000360000005` | `online_pin_cvm` | Simule la demande d'un PIN online. Le paiement a `cardholder_verification_method` = `online_pin`. |
| `4000002760000008` | `online_pin_sca_retry` | Simule un retry SCA où le paiement sans contact échoue et demande un PIN online. |

### Cartes pour cas d'erreur spécifiques

| Numéro de carte | Type de paiement | Résultat |
|----------------|------------------|----------|
| `4000000000000002` | `charge_declined` | Paiement refusé avec code `card_declined`. |
| `4000000000009995` | `charge_declined_insufficient_funds` | Paiement refusé avec code `card_declined` et `decline_code` = `insufficient_funds`. |
| `4000000000009987` | `charge_declined_lost_card` | Paiement refusé avec `decline_code` = `lost_card`. |
| `4000000000009979` | `charge_declined_stolen_card` | Paiement refusé avec `decline_code` = `stolen_card`. |
| `4000000000000069` | `charge_declined_expired_card` | Paiement refusé avec code `expired_card`. |
| `4000000000000119` | `charge_declined_processing_error` | Paiement refusé avec code `processing_error`. |
| `4000000000005126` | `refund_fail` | Le paiement réussit, mais le remboursement échoue de manière asynchrone avec `failure_reason` = `expired_or_canceled_card`. |

## Montants de test (cartes physiques)

Lors de l'utilisation d'une carte physique de test, les montants finissant par des décimales spécifiques produisent différents résultats :

| Décimales | Résultat |
|-----------|----------|
| **.00** | Paiement approuvé |
| **.01** | Paiement refusé avec code `call_issuer` |
| **.02** | Demande de PIN offline. Si la carte nécessite un PIN, le paiement est refusé avec `offline_pin_required` et demande l'entrée du PIN. Entrer `1234` pour compléter le paiement test. |
| **.03** | Demande de PIN online. Si la carte nécessite un PIN, le paiement est refusé avec `online_or_offline_pin_required` et demande l'entrée du PIN. Entrer n'importe quel PIN à 4 chiffres pour compléter le paiement test. |
| **.05** | Paiement refusé avec code `generic_decline` |
| **.55** | Paiement refusé avec code `incorrect_pin` |
| **.65** | Paiement refusé avec code `withdrawal_count_limit_exceeded` |
| **.75** | Paiement refusé avec code `pin_try_exceeded` |

### Exemples

- Montant `25.00 EUR` (2500 centimes) : **Paiement approuvé**
- Montant `10.01 EUR` (1001 centimes) : **Paiement refusé avec `call_issuer`**
- Montant `20.02 EUR` (2002 centimes) : **Demande de PIN offline**
- Montant `50.05 EUR` (5005 centimes) : **Paiement refusé avec `generic_decline`**

## Flow de test recommandé

### 1. Test de connexion

```typescript
// Connecter au terminal
const connection = await terminalService.connect();
// Attendu : connection_token et terminal_id
```

### 2. Test de création de Payment Intent

```typescript
// Créer un PI avec montant approuvé (25.00 EUR)
const pi = await terminalService.createPaymentIntent(2500, 'eur');
// Attendu : payment_intent_id avec status 'requires_payment_method'
```

### 3. Test de traitement avec différents montants

```typescript
// Test avec montant approuvé
await terminalService.process('pi_test_approved');
// Attendu : status 'succeeded'

// Test avec montant refusé
await terminalService.process('pi_test_declined');
// Attendu : ApiError avec code 'card_declined'
```

### 4. Test de capture

```typescript
// Capturer un paiement traité avec succès
const capture = await terminalService.capture('pi_test_success');
// Attendu : status 'succeeded' avec amount_captured
```

### 5. Test de remboursement

```typescript
// Remboursement total
await terminalService.refund('pi_test_success');

// Remboursement partiel
await terminalService.refund('pi_test_success', 1000);
```

### 6. Test d'annulation

```typescript
// Annuler un paiement
await terminalService.cancel('pi_test_pending');
// Attendu : status 'canceled'
```

## Tests dans le codebase

### Tests unitaires

- `src/shared/api/terminal.service.stripe-tests.test.ts` : Tests conformes à la documentation Stripe pour les différents scénarios de montants et d'erreurs.

### Tests du composant

- `src/widgets/DevTerminalConsole/DevTerminalConsole.test.tsx` : Tests du composant console avec les différents flows.

### Tests E2E

Pour tester le flow complet Terminal :

1. Naviguer vers `/dev/terminal` (en mode développement)
2. Connecter au terminal
3. Créer un Payment Intent avec différents montants
4. Traiter le paiement
5. Capturer ou annuler selon le résultat
6. Tester le remboursement si nécessaire

## Notes importantes

- **Mode développement uniquement** : Le simulateur Terminal n'est disponible qu'en mode développement (`VITE_DEV_TERMINAL=true`).
- **Backend requis** : Le backend doit exposer les endpoints `/v1/terminal/*` pour que les tests fonctionnent.
- **Authentification** : Les endpoints Terminal nécessitent une authentification JWT valide.
- **Cartes physiques** : Les montants avec décimales spécifiques fonctionnent uniquement avec des cartes physiques de test Stripe, pas avec le simulateur.

## Références

- [Documentation Stripe Terminal Testing](https://docs.stripe.com/terminal/references/testing)
- [Guide de test Stripe général](https://stripe.com/docs/testing)

