# Story 61.60 : Aligner la documentation webhook Stripe sur le périmètre backend réellement supporté

Status: done

## Story

En tant que développeur ou opérateur,
je veux que la documentation webhook Stripe reflète exactement les événements et comportements
réellement supportés par le backend,
afin d'éviter des validations locales erronées et des conclusions contradictoires entre runbooks.

---

## Contexte

La review de l'epic 61 a trouvé un écart documentaire persistant :

- `docs/billing-webhook-local-testing.md` documente correctement le périmètre réel et le runbook canonique.
- Mais `docs/stripe-webhook-dev.md` affirme encore que
  `customer.subscription.trial_will_end` est "❌ Non traité",
  alors que le backend le gère effectivement et que le runbook local le mentionne dans le périmètre étendu.

Cette story est documentaire et de cohérence des artefacts de validation. Elle ne modifie aucune logique métier.

---

## Acceptance Criteria

**AC1 — La documentation historique ne contredit plus le backend**

- [ ] `docs/stripe-webhook-dev.md` n'affirme plus qu'un événement actuellement géré par le backend
  est non traité.
- [ ] Le statut documentaire de `customer.subscription.trial_will_end` est aligné avec le code réel.
- [ ] Le document continue de préciser ce qui relève de la rationale historique vs du périmètre actuel.

**AC2 — Le périmètre réel des événements est listé de manière explicite**

- [ ] La doc historique ou canonique mentionne clairement :
  - le sous-ensemble standardisé du listener par défaut
  - le périmètre étendu réellement accepté par le backend
- [ ] Les événements additionnels déjà gérés (`customer.updated`, `customer.subscription.paused`,
  `customer.subscription.resumed`, `customer.subscription.trial_will_end`) sont documentés sans ambiguïté.

**AC3 — La doc canonique reste identifiable**

- [ ] `docs/billing-webhook-local-testing.md` reste explicitement le runbook canonique local.
- [ ] `docs/stripe-webhook-dev.md` conserve son rôle historique/rationale sans se substituer au runbook.

**AC4 — Garde-fou automatisé**

- [ ] Ajouter ou étendre un test automatisé qui vérifie la cohérence minimale entre :
  - la documentation de dev locale
  - le runbook canonique
  - le périmètre effectivement supporté par `StripeWebhookService`

**AC5 — Aucun changement runtime**

- [ ] Aucun fichier métier backend n'est modifié dans cette story.
- [ ] Aucun endpoint, migration, service Stripe ou logique de webhook n'est modifié.

---

## Tasks / Subtasks

- [x] **Mettre à jour la documentation historique** (AC: 1, 2, 3)
  - [x] Corriger `docs/stripe-webhook-dev.md`
  - [x] Garder la distinction entre rationale historique et périmètre actuel
  - [x] Vérifier les renvois vers `docs/billing-webhook-local-testing.md`

- [x] **Consolider le vocabulaire du périmètre supporté** (AC: 2)
  - [x] Lister explicitement le sous-ensemble standardisé
  - [x] Lister explicitement le périmètre backend élargi réellement supporté

- [x] **Ajouter un garde-fou de cohérence** (AC: 4)
  - [x] Étendre `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
  - [x] Vérifier la présence des événements additionnels dans les docs appropriées
  - [x] Vérifier que la doc historique ne marque pas à tort un événement géré comme non traité

---

## Dev Notes

### Périmètre documentaire uniquement

Cette story ne doit pas toucher :

- `backend/app/services/stripe_webhook_service.py`
- `backend/app/services/stripe_webhook_idempotency_service.py`
- `backend/app/api/v1/routers/billing.py`
- migrations Alembic

### Événements à aligner

Le backend accepte actuellement :

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `customer.subscription.paused`
- `customer.subscription.resumed`
- `customer.subscription.trial_will_end`
- `customer.updated`
- `invoice.paid`
- `invoice.payment_failed`
- `invoice.payment_action_required`

Le listener standardisé par défaut n'a pas besoin d'inclure tous ces événements, mais la doc
doit expliquer clairement cette différence au lieu de la présenter comme une contradiction.

### Fichiers probablement concernés

- `docs/stripe-webhook-dev.md`
- `docs/billing-webhook-local-testing.md`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`

### Tests attendus

- `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py`

### References

- [Source: `docs/billing-webhook-local-testing.md`] — runbook canonique
- [Source: `docs/stripe-webhook-dev.md`] — doc historique à réaligner
- [Source: `backend/app/services/stripe_webhook_service.py`] — périmètre backend réel

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- Story créée à partir de la review complète Epic 61 workspace actuel.
- Implémentation `bmad-dev-story` limitée à la documentation Stripe et au test documentaire associé.
- Revue `bmad-code-review` exécutée sur le périmètre story ; aucun changement runtime supplémentaire requis après correction des contradictions documentaires.

### Completion Notes List

- `docs/stripe-webhook-dev.md` ne contredit plus le backend et distingue explicitement le sous-ensemble standardisé du listener par défaut du périmètre backend élargi réellement accepté.
- `docs/billing-webhook-local-testing.md` réaffirme son rôle de runbook canonique local pour la validation Stripe CLI.
- Le garde-fou `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` vérifie maintenant l'alignement minimal entre le runbook canonique, la doc historique et les événements réellement supportés par `StripeWebhookService`.
- Validation exécutée dans le venv avec `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` et `ruff check app/tests/unit/test_stripe_webhook_local_dev_assets.py`.
- Aucun fichier métier backend, endpoint ou migration n'a été modifié dans cette story.

### File List

- `docs/stripe-webhook-dev.md`
- `docs/billing-webhook-local-testing.md`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`

### Change Log

- 2026-03-30: Alignement documentaire du webhook Stripe, ajout d'un garde-fou automatisé de cohérence et clôture de la story en `done`.
