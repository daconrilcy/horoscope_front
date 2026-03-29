# Story 61.57 : Validation locale du webhook Stripe avec Stripe CLI

Status: done

## Story

En tant que développeur backend,
je veux pouvoir tester localement le webhook Stripe avec la Stripe CLI,
afin de valider avant la prod la réception des événements, la vérification de signature, le dispatch billing et le comportement d'idempotence sur replay exact.

---

## Contexte

Stories 61.4 à 61.56 ont mis en place l'endpoint `POST /v1/billing/stripe-webhook` complet :
- vérification de signature HMAC
- dispatch des événements subscription/invoice
- idempotence par `event.id` (table `stripe_webhook_events`, statuts `processing / processed / failed`)

Cette story n'ajoute **aucune logique métier**. Elle crée le runbook et les artefacts permettant de valider localement ce pipeline bout-en-bout avant la mise en production.

**Observation critique** : `.env.example` contient déjà :
```
# Dev  : obtenu avec `stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook`
# Prod : obtenu dans Stripe Dashboard > Developers > Webhooks > Signing secret
STRIPE_WEBHOOK_SECRET=
```
→ La variable est déjà documentée. La story doit vérifier et enrichir ce commentaire si nécessaire — **ne pas dupliquer**.

---

## Acceptance Criteria

**AC1 — Runbook local Stripe CLI**
- [ ] `docs/billing-webhook-local-testing.md` est créé
- [ ] Il documente : `stripe login`, `stripe listen --forward-to`, la récupération du `whsec_...` depuis la sortie CLI, et l'injection dans `.env.local`
- [ ] La doc précise **explicitement** que le secret de signature local vient de `stripe listen`, pas du Dashboard

**AC2 — Listener local reproductible**
- [ ] La doc présente deux variantes de commande listener :
  - mode large : `stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook`
  - mode filtré (`--events`) avec les 7 événements billing supportés
- [ ] La doc mentionne `--load-from-webhooks-api` : ce mode récupère le chemin et les événements d'un endpoint Stripe **déjà enregistré** dans le Dashboard et les appende au `--forward-to` local — utile pour rester calé sur la config de prod

**AC3 — Validation du nominal**
- [ ] La doc décrit un scénario nominal : flow Checkout sandbox **de préférence** (produit la chaîne réelle d'événements), `stripe trigger` en complément pour tests ciblés rapides
- [ ] Les statuts de retour attendus sont documentés : `processed`, `event_ignored`, `user_not_resolved`

**AC4 — Validation de la signature**
- [ ] La doc décrit le test secret invalide → rejet HTTP 400
- [ ] La doc décrit le test secret CLI correct → acceptation
- [ ] `.env.example` à la racine **déjà correct** — vérifier que le commentaire mentionne `stripe listen` (déjà fait) ; aucune modification si le commentaire est satisfaisant

**AC5 — Validation de l'idempotence**
- [ ] La doc décrit le scénario replay exact en 4 étapes :
  1. Premier envoi d'un événement → statut `processed`
  2. Récupération de l'`event.id` dans les logs CLI ou applicatifs
  3. Renvoi avec `stripe events resend <event_id>` (cible par défaut le webhook local CLI)
  4. Second appel → statut `duplicate_ignored`, aucune mutation métier
- [ ] La doc précise que `--webhook-endpoint=<we_123456>` permet de cibler un endpoint Stripe enregistré si nécessaire
- [ ] Ce scénario prouve que l'idempotence de 61.56 fonctionne sur des événements Stripe réels

**AC6 — Commandes standardisées disponibles**
- [ ] Un script `scripts/stripe-listen-webhook.sh` est créé (si répertoire `scripts/` absent, le créer)
- [ ] Le script utilise la variante filtrée `--events` sur le port 8001
- [ ] La doc couvre `stripe trigger <event_type>` pour les tests ciblés

---

## Tasks / Subtasks

- [x] **Créer `docs/billing-webhook-local-testing.md`** (AC: 1, 2, 3, 4, 5, 6)
  - [x] Section "Prérequis" : Stripe CLI installé, API locale sur port 8001
  - [x] Section "1. Authentification" : `stripe login`
  - [x] Section "2. Démarrer le listener" : variante large + variante filtrée `--events` + explication de `--load-from-webhooks-api` (sync depuis endpoint enregistré → append au `--forward-to`)
  - [x] Section "3. Récupérer et injecter le secret" : copier le `whsec_...` affiché par `stripe listen` dans `.env.local` (le secret vient de la CLI, pas du Dashboard, même avec `--load-from-webhooks-api`)
  - [x] Section "4. Scénario nominal" : flow Checkout sandbox de préférence ; `stripe trigger invoice.paid` en complément
  - [x] Section "5. Scénario signature invalide" : tester avec un faux secret
  - [x] Section "6. Scénario replay exact (idempotence)" : étapes 1 à 4 avec `stripe events resend`
  - [x] Section "7. Tests ciblés avec stripe trigger" : tableau des triggers utiles

- [x] **Vérifier `.env.example`** (AC: 4)
  - [x] Confirmer que le commentaire mentionne `stripe listen --forward-to ...` (déjà présent)
  - [x] Enrichir si le commentaire est trop laconique ; ne pas dupliquer si déjà correct

- [x] **Créer `scripts/stripe-listen-webhook.sh`** (AC: 6)
  - [x] Créer le répertoire `scripts/` s'il n'existe pas
  - [x] Script avec shebang, commentaire d'usage, commande `stripe listen --events ... --forward-to http://localhost:8001/v1/billing/stripe-webhook`
  - [x] Rendre exécutable (`chmod +x`)

---

## Dev Notes

### Ce qui EXISTE déjà — NE PAS modifier

- `POST /v1/billing/stripe-webhook` : endpoint complet, signé, idempotent (stories 61.4 – 61.56)
- `backend/app/services/stripe_webhook_service.py` : `handle_event()` retourne `processed | duplicate_ignored | event_ignored | user_not_resolved`
- `backend/app/services/stripe_webhook_idempotency_service.py` : `claim_event / mark_processed / mark_failed`
- `docs/billing-webhook-idempotency.md` : cycle de vie `processing → processed | failed` déjà documenté
- `.env.example` (racine) : `STRIPE_WEBHOOK_SECRET` avec commentaire `stripe listen` déjà présent

### Événements billing supportés (pour `--events`)

```
checkout.session.completed
customer.subscription.created
customer.subscription.updated
customer.subscription.deleted
invoice.paid
invoice.payment_failed
invoice.payment_action_required
```

### Commandes Stripe CLI de référence

```bash
# Authentification
stripe login

# Listener mode large
stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook

# Listener mode filtré (recommandé)
stripe listen \
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,invoice.payment_action_required \
  --forward-to http://localhost:8001/v1/billing/stripe-webhook

# Listener calé sur un endpoint Stripe déjà enregistré (sync chemin + events → append au forward-to)
stripe listen --load-from-webhooks-api --forward-to http://localhost:8001

# Trigger ciblé (événement mock, sans action produit réelle)
stripe trigger invoice.paid

# Replay d'un événement existant vers le webhook local CLI (par défaut)
stripe events resend evt_XXXX

# Replay vers un endpoint Stripe enregistré précis
stripe events resend evt_XXXX --webhook-endpoint=we_123456
```

> `stripe listen` affiche en démarrage :
> `Ready! Your webhook signing secret is whsec_XXXX (^C to quit)`
> → Copier cette valeur dans `.env.local` : `STRIPE_WEBHOOK_SECRET=whsec_XXXX`

### Script `scripts/stripe-listen-webhook.sh`

```bash
#!/usr/bin/env bash
# Usage: ./scripts/stripe-listen-webhook.sh
# Forwarde les événements Stripe billing vers l'API locale (port 8001).
# Le secret whsec_... affiché au démarrage doit être copié dans .env.local.

stripe listen \
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,invoice.payment_action_required \
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
```

### Scénario replay exact — étapes détaillées

1. Démarrer le listener (script ou commande filtrée)
2. Déclencher un abonnement sandbox (flow Checkout de préférence) ou `stripe trigger invoice.paid`
3. Observer dans les logs applicatifs : `outcome=processed`, `event_id=evt_XXXX`
4. Exécuter : `stripe events resend evt_XXXX` (cible le webhook local CLI par défaut)
5. Observer dans les logs : `outcome=duplicate_ignored` — aucune mutation billing supplémentaire
6. Vérifier en DB : `SELECT status, processing_attempts FROM stripe_webhook_events WHERE stripe_event_id='evt_XXXX'` → `status=processed, attempts=1`

### Statuts de retour de l'endpoint (rappel)

| Valeur | Signification |
|--------|--------------|
| `processed` | Traitement réussi |
| `duplicate_ignored` | `event.id` déjà connu — absorbé |
| `event_ignored` | Type d'événement non pris en charge |
| `user_not_resolved` | Stripe `customer_id` inconnu localement |

### Périmètre explicitement hors scope

- Toute modification du code métier (billing.py, StripeWebhookService, etc.)
- Tests automatisés CI (validation manuelle locale uniquement)
- Configuration d'un endpoint webhook dans le Dashboard Stripe pour la prod
- Monitoring, alerting, purge de la table `stripe_webhook_events`

### Project Structure Notes

- Nouveau fichier : `docs/billing-webhook-local-testing.md`
- Nouveau script : `scripts/stripe-listen-webhook.sh` (créer `scripts/` si absent)
- À vérifier (probablement sans modification) : `.env.example` ligne `STRIPE_WEBHOOK_SECRET`
- Aucun fichier backend modifié

### Références

- [Source: docs/billing-webhook-idempotency.md] — cycle de vie processing/processed/failed
- [Source: .env.example] — `STRIPE_WEBHOOK_SECRET` déjà documenté avec commentaire `stripe listen`
- [Source: backend/app/services/stripe_webhook_service.py] — statuts de retour de `handle_event()`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `docs/billing-webhook-local-testing.md` (nouveau)
- `scripts/stripe-listen-webhook.sh` (nouveau)
- `.env.example` (à vérifier — probablement inchangé)
