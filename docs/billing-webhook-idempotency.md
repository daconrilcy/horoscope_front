# Idempotence du Webhook Stripe

Ce document décrit le mécanisme d'idempotence mis en place pour garantir qu'un événement Stripe n'est traité qu'une seule fois avec succès.

## Architecture

Le mécanisme repose sur une table dédiée `stripe_webhook_events` qui fait office de registre de traitement. L'idempotence est garantie par une contrainte `UNIQUE` sur le champ `stripe_event_id`.

### Cycle de vie d'un événement

1. **Claim (`processing`)** : Lorsqu'un webhook arrive, le système tente d'insérer une ligne dans `stripe_webhook_events` avec le statut `processing`.
    - Si l'insertion réussit, le traitement métier commence.
    - Si l'insertion échoue (doublon DB), le système vérifie le statut existant.
    - Si le statut est `processed` ou `processing`, l'événement est ignoré (`duplicate_ignored`).
    - Si le statut est `failed`, l'événement est "re-claimé" : son statut repasse à `processing` et le compteur de tentatives est incrémenté.

2. **Succès (`processed`)** : Une fois la logique métier terminée avec succès, l'événement est marqué comme `processed`. Toute livraison ultérieure du même `event.id` sera ignorée avec un code 200 (pour acquitter Stripe).

3. **Échec (`failed`)** : En cas d'exception durant le traitement métier, l'événement est marqué comme `failed` et l'erreur est stockée. Après commit de cette ligne, l'endpoint retourne un HTTP non-2xx retryable afin que Stripe retente automatiquement la livraison et déclenche un nouveau cycle de claim.

### Contrat de retry Stripe

Les statuts `processed`, `event_ignored`, `user_not_resolved` et `duplicate_ignored` sont acquittés en HTTP 200. Une erreur de signature reste rejetée en HTTP 400. Une erreur interne après signature valide et tentative de traitement retourne une enveloppe d'erreur HTTP 500 avec le code `stripe_webhook_processing_failed`.

Ce code 500 est volontaire: il indique à Stripe que la livraison ne doit pas être considérée comme terminée. La ligne `stripe_webhook_events` conserve l'état `failed`, puis une livraison ultérieure du même `event.id` repasse cette ligne en `processing`, vide `last_error` et incrémente `processing_attempts`.

### Chemin opérateur pour une ligne `failed`

Pour identifier les événements à réconcilier:

```sql
SELECT stripe_event_id, event_type, processing_attempts, last_error
FROM stripe_webhook_events
WHERE status = 'failed'
ORDER BY received_at DESC;
```

Si Stripe n'a pas encore rejoué l'événement automatiquement, l'opérateur peut relancer la livraison depuis Stripe CLI ou le Dashboard Stripe avec l'`event.id` concerné. Le backend ne requiert pas de mutation manuelle de la ligne: le reclaim d'une ligne `failed` est pris en charge par `StripeWebhookIdempotencyService.claim_event`.

## Schéma de données

La table `stripe_webhook_events` contient :
- `stripe_event_id` (Unique) : L'ID fourni par Stripe (`evt_...`).
- `status` : `processing`, `processed`, `failed`.
- `event_type` : Le type d'événement Stripe (ex: `invoice.paid`).
- `stripe_object_id` : L'ID de l'objet concerné (ex: `in_...`, `sub_...`).
- `processing_attempts` : Nombre de tentatives de traitement.
- `last_error` : Message d'erreur de la dernière tentative échouée.

## Pourquoi `event.id` suffit ?

Stripe garantit qu'un `event.id` est unique pour une livraison donnée. Si Stripe rejoue exactement le même événement (même contenu, même ID), notre garde l'absorbe.
Si Stripe émet deux événements différents pour un même changement d'état (peu probable mais possible sur certains objets complexes), ils auront deux `event.id` distincts.

## Évolutions futures

Actuellement, nous ne dédupliquons pas par `(event_type, stripe_object_id)`. Si deux événements Stripe distincts arrivent pour le même objet, ils seront tous deux traités. Une garde complémentaire pourra être ajoutée si des incohérences métier sont constatées sur des livraisons multiples d'états proches.
