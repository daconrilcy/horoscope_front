# Code Review Story 61.56: Idempotence webhook Stripe

Date: 2026-03-29
Statut: corrigé

## Findings

1. `HIGH` `backend/app/tests/unit/test_stripe_webhook_service.py`
   Un test validait encore l'ancien comportement non idempotent en attendant deux traitements `processed` pour le même `event.id`. Ce test contredisait directement l'AC2.

2. `HIGH` `backend/app/tests/integration/test_stripe_webhook_api.py`
   La couverture d'intégration ne prouvait pas le scénario demandé par l'AC8: échec métier persisté en `failed`, puis retry accepté avec incrément de `processing_attempts`.

3. `MEDIUM` `61-56-idempotence-webhook-stripe-deduplication-event-id.md`
   L'artefact d'implémentation ne retraçait pas explicitement la correction de review ni le fichier de test de service ajusté.

## Corrections appliquées

- Mise à jour du test unitaire du service webhook pour vérifier le vrai comportement idempotent: premier passage `processed`, second passage `duplicate_ignored`, une seule mutation métier.
- Ajout d'un test d'intégration qui vérifie la persistance du statut `failed` puis le re-claim réussi au retry avec `processing_attempts == 2`.
- Synchronisation de l'artefact d'implémentation avec les corrections de review.
